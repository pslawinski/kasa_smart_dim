import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.light import ColorMode
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import selector

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class KasaSmartDimConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Kasa Smart Dimmer Off-Brightness."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        entity_registry = er.async_get(self.hass)

        kasa_dimmer_options = {}

        configured_entries = self._async_current_entries()
        configured_entity_ids = {
            entry.data.get("entity_id") for entry in configured_entries
        }

        # --- MANUAL CHECK FOR EXISTING ENTRIES ---
        all_possible_entities = [
            entity_entry.entity_id
            for entity_entry in entity_registry.entities.values()
            if (entity_entry.platform == "tplink" and entity_entry.domain == "light")
        ]

        # If all compatible entities are already configured, we can abort the flow
        if set(all_possible_entities) == configured_entity_ids:
            return self.async_abort(reason="all_kasa_dimmers_configured")

        for entity_entry in entity_registry.entities.values():
            if (
                entity_entry.platform == "tplink"
                and entity_entry.domain == "light"
                and entity_entry.entity_id not in configured_entity_ids
            ):
                state = self.hass.states.get(entity_entry.entity_id)
                if state and "brightness" in state.attributes:
                    supported_modes = state.attributes.get("supported_color_modes")
                    if supported_modes and supported_modes == [ColorMode.BRIGHTNESS]:
                        kasa_dimmer_options[entity_entry.entity_id] = (
                            entity_entry.entity_id
                        )

        _LOGGER.debug("Found Kasa dimmers: %s", kasa_dimmer_options)

        if not kasa_dimmer_options:
            return self.async_abort(reason="no_kasa_dimmers")

        if user_input is not None:
            selected_entity_id = user_input["entity_id"]
            name = f"{selected_entity_id}_off_dim"

            await self.async_set_unique_id(f"{DOMAIN}_{selected_entity_id}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=name, data={"entity_id": selected_entity_id, "name": name}
            )

        schema = vol.Schema(
            {
                vol.Required("entity_id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=list(kasa_dimmer_options.keys()),
                        multiple=False,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    ),
                )
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
