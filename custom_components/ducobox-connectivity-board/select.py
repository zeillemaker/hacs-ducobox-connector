from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .model.utils import safe_get

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ducobox select entities from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]['coordinator']

    # Retrieve MAC address and format device ID and name
    mac_address = (
        safe_get(coordinator.data, "info", "General", "Lan", "Mac", "Val") or "unknown_mac"
    )
    device_id = mac_address.replace(":", "").lower() if mac_address else "unknown_mac"
    device_name = f"{device_id}"

    box_name = safe_get(coordinator.data, "info", "General", "Board", "BoxName", "Val") or "Unknown Model"
    box_subtype = safe_get(coordinator.data, "info", "General", "Board", "BoxSubTypeName", "Val") or ""
    box_model = f"{box_name} {box_subtype}".replace('_', ' ').strip()

    device_info = DeviceInfo(
        identifiers={(DOMAIN, device_id)},
        name=device_name,
        manufacturer="Ducobox",
        model=box_model,
        sw_version=safe_get(coordinator.data, "info", "General", "Board", "SwVersionBox", "Val") or "Unknown Version",
    )

    entities: list[SelectEntity] = []

    action_nodes = safe_get(coordinator.data, 'action_nodes', 'Nodes')
    for node in action_nodes:
        node_id = node['Node']
        node_type = safe_get(coordinator.data, 'mappings', 'node_id_to_type', node_id) or 'Unknown'
        mapped_node_name = safe_get(coordinator.data, 'mappings', 'node_id_to_name', node_id)
        node_name = f'{device_id}:{mapped_node_name}'


        # Create device info for the node
        node_device_id = f"{device_id}-{node_id}"
        node_device_info = DeviceInfo(
            identifiers={(DOMAIN, node_device_id)},
            name=node_name,
            manufacturer="Ducobox",
            model=node_type,
            via_device=(DOMAIN, device_id),
        )

        # Check for SetVentilationState action
        for action in node.get('Actions', []):
            if action['Action'] == 'SetVentilationState':
                entities.append(
                    DucoboxVentilationStateSelectEntity(
                        coordinator=coordinator,
                        node_id=node_id,
                        device_info=node_device_info,
                        unique_id=f"{node_device_id}-SetVentilationState",
                        options=action['Enum'],
                        action=action['Action']
                    )
                )

    async_add_entities(entities)

class DucoboxVentilationStateSelectEntity(SelectEntity):
    """Representation of a Ducobox ventilation state select entity."""

    def __init__(self, coordinator, node_id, device_info, unique_id, options, action):
        """Initialize the Ducobox ventilation state select entity."""
        self._coordinator = coordinator
        self._node_id = node_id
        self._action = action
        self._device_info = device_info
        self._attr_unique_id = unique_id
        self._attr_name = f"{device_info['name']} Ventilation State"
        self._attr_options = options
        self._attr_current_option = None  # You might want to fetch the current state from the coordinator

    @property
    def device_info(self):
        """Return the device info."""
        return self._device_info

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        return self._attr_current_option

    @property
    def options(self) -> list[str]:
        """Return the available options."""
        return self._attr_options

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._attr_current_option = option
        await self._coordinator.async_set_ventilation_state(self._node_id, option, self._action)
        self.async_write_ha_state()
