import logging
from typing import Any, ClassVar

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_TRANSITION,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import KasaSmartDimmerCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Kasa Smart Dimmer light platform from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [KasaSmartDimmer(coordinator, entry.title)], update_before_add=True
    )


class KasaSmartDimmer(CoordinatorEntity, LightEntity):
    """Representation of a Kasa Smart Dimmer with off-brightness control."""

    _attr_color_mode: ClassVar[ColorMode] = ColorMode.BRIGHTNESS
    _attr_supported_color_modes: ClassVar[set[ColorMode]] = {ColorMode.BRIGHTNESS}
    _attr_supported_features: ClassVar[LightEntityFeature] = (
        LightEntityFeature.TRANSITION
    )

    def __init__(self, coordinator: KasaSmartDimmerCoordinator, name: str):
        """Initialize the light."""
        super().__init__(coordinator)
        self._mac_address = coordinator._mac_address
        self._attr_name = name

        mac_with_colons = ":".join(
            self._mac_address[i : i + 2] for i in range(0, 12, 2)
        )

        self._attr_unique_id = f"{DOMAIN}_{self._mac_address}"
        self._attr_device_info = {
            "connections": {(device_registry.CONNECTION_NETWORK_MAC, mac_with_colons)}
        }

    @property
    def is_on(self) -> bool:
        """Return true as this light is always on."""
        return True

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light."""
        if self.coordinator.data and "brightness" in self.coordinator.data:
            kasa_brightness = self.coordinator.data["brightness"]
            return int(kasa_brightness * 2.55)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attrs = super().extra_state_attributes or {}
        if self.coordinator.data and "is_on" in self.coordinator.data:
            attrs["physical_is_on"] = self.coordinator.data["is_on"]
        else:
            attrs["physical_is_on"] = None
        return attrs

    async def async_update(self) -> None:
        """Update the entity."""
        await self.coordinator.async_refresh()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Adjust brightness using the vendored kasa library."""
        _LOGGER.debug("async_turn_on called with kwargs: %s", kwargs)

        if not self.coordinator.device:
            _LOGGER.error("Device not available. Cannot set brightness.")
            return

        _LOGGER.debug(
            "Coordinator device: %s, host: %s",
            self.coordinator.device,
            self.coordinator.device.host,
        )

        if ATTR_BRIGHTNESS not in kwargs:
            _LOGGER.debug("Exiting async_turn_on because ATTR_BRIGHTNESS not in kwargs")
            return

        brightness_pct = int(kwargs[ATTR_BRIGHTNESS] / 2.55)
        if brightness_pct == 0:
            brightness_pct = 1

        physical_is_on = (
            self.coordinator.data.get("is_on", False)
            if self.coordinator.data
            else False
        )

        try:
            # Only apply a transition if the light is physically on.
            if ATTR_TRANSITION in kwargs and physical_is_on:
                transition_s = kwargs[ATTR_TRANSITION]
                transition_ms = int(transition_s * 1000)
                _LOGGER.debug(
                    "Setting brightness to %s%% with transition %sms for %s",
                    brightness_pct,
                    transition_ms,
                    self.name,
                )
                await self.coordinator.device.set_dimmer_transition(
                    brightness=brightness_pct, transition=transition_ms
                )
            else:
                # If transition requested but light off, log and set brightness.
                if ATTR_TRANSITION in kwargs:
                    _LOGGER.debug(
                        "Ignoring transition for %s because physical light is off.",
                        self.name,
                    )
                _LOGGER.debug(
                    "Setting brightness to %s%% for %s", brightness_pct, self.name
                )
                await self.coordinator.device.set_brightness(brightness_pct)

            # Instead of an optimistic update, we'll force a refresh to get the
            # actual brightness from the device. The `python-kasa` library does not
            # have a `get_brightness` method, so we use the coordinator's
            # `async_refresh` which handles updating the device state.
            await self.coordinator.async_refresh()

        except Exception:
            _LOGGER.exception("Failed to set brightness for %s", self.name)
            # Refresh state to ensure correct data after failed update.
            await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Do nothing, as the dimmer is always on."""
