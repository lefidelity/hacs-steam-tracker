"""Config flow for the Steam Tracker integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_STEAM_ID, DEFAULT_NAME, DOMAIN


DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_STEAM_ID): str,
        vol.Required(CONF_API_KEY): str,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
    }
)


class SteamTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow to create a Steam Tracker entry."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            data = self._sanitize_user_input(user_input)

            if not data[CONF_STEAM_ID]:
                errors[CONF_STEAM_ID] = "steam_id_required"
            elif not data[CONF_API_KEY]:
                errors[CONF_API_KEY] = "api_key_required"
            else:
                return await self._async_create_entry(data)

            user_input = data
        else:
            user_input = {}

        schema = self.add_suggested_values_to_schema(DATA_SCHEMA, user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_import(self, user_input: dict[str, str]) -> FlowResult:
        """Handle YAML import by creating a config entry."""
        data = self._sanitize_user_input(user_input)
        if not data[CONF_STEAM_ID] or not data[CONF_API_KEY]:
            return self.async_abort(reason="missing_import_data")
        return await self._async_create_entry(data)

    async def _async_create_entry(self, data: dict[str, str]) -> FlowResult:
        """Create a config entry from validated data."""
        await self.async_set_unique_id(data[CONF_STEAM_ID])
        self._abort_if_unique_id_configured(
            updates=data,
        )

        return self.async_create_entry(
            title=data[CONF_NAME],
            data=data,
        )

    @staticmethod
    def _sanitize_user_input(user_input: dict[str, str]) -> dict[str, str]:
        """Strip whitespace and provide defaults."""
        steam_id = str(user_input.get(CONF_STEAM_ID, "")).strip()
        api_key = str(user_input.get(CONF_API_KEY, "")).strip()
        name = str(user_input.get(CONF_NAME, "")).strip() or DEFAULT_NAME

        return {
            CONF_STEAM_ID: steam_id,
            CONF_API_KEY: api_key,
            CONF_NAME: name,
        }
