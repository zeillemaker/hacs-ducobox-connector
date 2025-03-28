from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.number import NumberEntity

from .const import DOMAIN
from .model.utils import safe_get

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ducobox numbers from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]['coordinator']
    await coordinator.async_config_entry_first_refresh()

    # Retrieve MAC address and format device ID and name
    mac_address = (
        safe_get(coordinator.data, "info", "General", "Lan", "Mac", "Val") or "unknown_mac"
    )
    device_id = mac_address.replace(":", "").lower() if mac_address else "unknown_mac"
    device_name = f"{device_id}" 

    entities: list[NumberEntity] = []

    number_nodes = safe_get(coordinator.data, 'config_nodes', 'Nodes')
    for node in number_nodes:
        node_id = node['Node']
        node_name = safe_get(coordinator.data, 'mappings', 'node_id_to_name', node_id)
        node_name = f'{device_name}:{node_name}'
        _LOGGER.warning(node_name)

    async_add_entities(entities)
