import logging
from binascii import hexlify
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, PLATFORMS
from .kasa_vendored.discover import Discover
from .kasa_vendored.smartdimmer import SmartDimmer as VendoredSmartDimmer

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Kasa Smart Dimmer from a config entry."""
    entity_id = entry.data.get("entity_id")

    entity_registry = er.async_get(hass)
    entity_entry = entity_registry.async_get(entity_id)

    if not entity_entry:
        _LOGGER.error("Could not find entity entry for %s. Aborting setup.", entity_id)
        return False

    device_registry = dr.async_get(hass)
    device_entry = device_registry.async_get(entity_entry.device_id)

    mac_address_tuple: tuple[str, str] | None = next(
        (
            conn
            for conn in device_entry.connections
            if conn[0] == dr.CONNECTION_NETWORK_MAC
        ),
        None,
    )

    if not mac_address_tuple:
        _LOGGER.error("Could not find MAC address for entity %s.", entity_id)
        return False

    mac_address = mac_address_tuple[1]

    coordinator = KasaSmartDimmerCoordinator(hass, mac_address)
    try:
        await coordinator.async_config_entry_first_refresh()
    except UpdateFailed:
        _LOGGER.exception("Initial refresh failed for coordinator. Aborting setup.")
        return False

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class KasaSmartDimmerCoordinator(DataUpdateCoordinator):
    """Kasa Smart Dimmer coordinator."""

    def __init__(self, hass: HomeAssistant, mac_address: str):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
        )
        self._mac_address = mac_address.replace(":", "").lower()
        self.device: VendoredSmartDimmer | None = None

    async def _async_get_device(self) -> VendoredSmartDimmer | None:
        """Dynamically discover, patch, and set the device based on MAC address."""
        _LOGGER.debug("Starting discovery for MAC %s", self._mac_address)
        try:
            discovered_devices = await Discover.discover(timeout=5)
            _LOGGER.debug(
                "Discovered %s devices: %s", len(discovered_devices), discovered_devices
            )

            for ip, device in discovered_devices.items():
                device_mac = None
                if hasattr(device, "mac_normalized"):
                    device_mac = device.mac_normalized
                elif hasattr(device, "sys_info") and "mac" in device.sys_info:
                    device_mac = device.sys_info["mac"].replace(":", "").lower()
                elif hasattr(device, "mac"):
                    device_mac_bytes = device.mac
                    if isinstance(device_mac_bytes, str):
                        device_mac_bytes = device_mac_bytes.encode()
                    device_mac = hexlify(device_mac_bytes).decode().lower()

                if device_mac and device_mac == self._mac_address:
                    _LOGGER.info(
                        "Successfully discovered device with MAC %s at IP %s.",
                        self._mac_address,
                        ip,
                    )

                    # Patch features to remove emeter support to prevent errors.
                    if hasattr(device, "_features") and "ENE" in device._features:
                        device._features.remove("ENE")
                        _LOGGER.debug(
                            "Patched device to remove emeter ('ENE') feature."
                        )

                    unsupported_modules = [
                        "schedule",
                        "antitheft",
                        "emeter",
                        "smartlife.iot.PIR",
                        "smartlife.iot.LAS",
                    ]
                    if hasattr(device, "_modules"):
                        device._modules = {
                            name: mod
                            for name, mod in device._modules.items()
                            if name not in unsupported_modules
                        }
                        _LOGGER.debug(
                            "Patched device %s, remaining modules: %s",
                            ip,
                            list(device._modules.keys()),
                        )

                    return device

        except Exception:
            _LOGGER.exception(
                "Failed to discover and patch device with MAC %s", self._mac_address
            )

        _LOGGER.warning("Could not find device with MAC %s", self._mac_address)
        return None

    async def _async_update_data(self):
        """Fetch data from device."""
        if not self.device:
            self.device = await self._async_get_device()

        if not self.device:
            msg = f"Could not connect to device {self._mac_address}"
            raise UpdateFailed(msg)

        try:
            await self.device.update()
        except Exception as e:
            _LOGGER.warning(
                "Error communicating with device %s: %s", self._mac_address, e
            )
            self.device = None
            msg = f"Error communicating with device {self._mac_address}: {e}"
            raise UpdateFailed(msg) from e
        else:
            return {"is_on": self.device.is_on, "brightness": self.device.brightness}
