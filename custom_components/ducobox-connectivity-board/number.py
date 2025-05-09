from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.number import NumberEntity, NumberMode

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .model.utils import safe_get
from .model.coordinator import DucoboxCoordinator

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ducobox numbers from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]['coordinator']

    # Retrieve MAC address and format device ID and name
    mac_address = (
        safe_get(coordinator.data, "info", "General", "Lan", "Mac", "Val") or "unknown_mac"
    )

    if mac_address == 'unknown_mac':
        # if no data -> stop adding device
        return

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

    entities: list[NumberEntity] = []

    # Add node numbers if data is available
    number_nodes = safe_get(coordinator.data, 'config_nodes', 'Nodes')
    for node in number_nodes:
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

        for key, value in node.items():
            if isinstance(value, dict) and 'Val' in value and 'Min' in value and 'Max' in value and 'Inc' in value:
                unique_id = f"{node_device_id}-{key}"
                entities.append(
                    DucoboxNumberEntity(
                        coordinator=coordinator,
                        node_id=node_id,
                        description=key,
                        device_info=node_device_info,
                        unique_id=unique_id,
                        value=int(value['Val']),
                        min_value=int(value['Min']),
                        max_value=int(value['Max']),
                        step=int(value['Inc'])
                    )
                )

    async_add_entities(entities)


class DucoboxNumberEntity(CoordinatorEntity, NumberEntity):
    """Representation of a Ducobox number entity."""

    def __init__(self, coordinator, node_id, description, device_info, unique_id, value, min_value, max_value, step):
        """Initialize the Ducobox number entity."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._node_id = node_id
        self._description = description
        self._device_info = device_info
        self._attr_unique_id = unique_id
        self._attr_name = f"{device_info['name']} {description}"
        self._attr_native_value = value
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        self._attr_mode = NumberMode.AUTO

    @property
    def device_info(self):
        """Return the device info."""
        return self._device_info

    @property
    def native_value(self):
        """Return the current value."""
        return self._attr_native_value

    async def async_set_native_value(self, value: float):
        """Update the current value."""
        self._attr_native_value = value
        # Call the coordinator's update method
        await self._coordinator.async_set_value(self._node_id, self._description, value)
        self.async_write_ha_state()
