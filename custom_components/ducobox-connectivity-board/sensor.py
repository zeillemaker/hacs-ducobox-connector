from __future__ import annotations

import logging

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN, SCAN_INTERVAL

from .utils import safe_get
from .devices import SENSORS, NODE_SENSORS, DucoboxSensorEntityDescription
from ducopy import DucoPy

_LOGGER = logging.getLogger(__name__)

class DucoboxCoordinator(DataUpdateCoordinator):
    """Coordinator to manage data updates for Ducobox sensors."""

    def __init__(self, hass: HomeAssistant, duco_client: DucoPy):
        super().__init__(
            hass,
            _LOGGER,
            name="Ducobox Connectivity Board",
            update_interval=SCAN_INTERVAL,
        )

        self.duco_client = duco_client

    async def _async_update_data(self) -> dict:
        """Fetch data from the Ducobox API."""
        try:
            return await self.hass.async_add_executor_job(self._fetch_data)
        except Exception as e:
            _LOGGER.error("Failed to fetch data from Ducobox API: %s", e)
            raise UpdateFailed(f"Failed to fetch data from Ducobox API: {e}") from e

    def _fetch_data(self) -> dict:
        duco_client = self.duco_client

        if duco_client is None:
            raise Exception("Duco client is not initialized")

        try:
            data = duco_client.get_info()
            _LOGGER.debug(f"Data received from /info: {data}")

            if data is None:
                data = {}

            nodes_response = duco_client.get_nodes()
            _LOGGER.debug(f"Data received from /nodes: {nodes_response}")

            if nodes_response and hasattr(nodes_response, 'Nodes'):
                data['Nodes'] = [node.dict() for node in nodes_response.Nodes]
            else:
                data['Nodes'] = []

            return data
        except Exception as e:
            _LOGGER.error("Error fetching data from Ducobox API: %s", e)
            raise

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ducobox sensors from a config entry."""
    duco_client = hass.data[DOMAIN][entry.entry_id]

    coordinator = DucoboxCoordinator(hass, duco_client)
    await coordinator.async_config_entry_first_refresh()

    # Retrieve MAC address and format device ID and name
    mac_address = (
        safe_get(coordinator.data, "General", "Lan", "Mac", "Val") or "unknown_mac"
    )
    device_id = mac_address.replace(":", "").lower() if mac_address else "unknown_mac"
    device_name = f"{device_id}"

    box_name = safe_get(coordinator.data, "General", "Board", "BoxName", "Val") or "Unknown Model"
    box_subtype = safe_get(coordinator.data, "General", "Board", "BoxSubTypeName", "Val") or ""
    box_model = f"{box_name} {box_subtype}".replace('_', ' ').strip()

    device_info = DeviceInfo(
        identifiers={(DOMAIN, device_id)},
        name=device_name,
        manufacturer="Ducobox",
        model=box_model,
        sw_version=safe_get(coordinator.data, "General", "Board", "SwVersionBox", "Val") or "Unknown Version",
    )

    entities: list[SensorEntity] = []

    # Add main Ducobox sensors
    for description in SENSORS:
        unique_id = f"{device_id}-{description.key}"
        entities.append(
            DucoboxSensorEntity(
                coordinator=coordinator,
                description=description,
                device_info=device_info,
                unique_id=unique_id,
            )
        )

    # Add node sensors if data is available
    nodes = coordinator.data.get('Nodes', [])
    for node in nodes:
        node_id = node.get('Node')
        node_type = safe_get(node, 'General', 'Type', 'Val') or 'Unknown'
        node_addr = safe_get(node, 'General', 'Addr') or 'Unknown'
        node_name = f"{device_id}:{node_id}:{node_type}"

        # Create device info for the node
        node_device_id = f"{device_id}-{node_id}"
        node_device_info = DeviceInfo(
            identifiers={(DOMAIN, node_device_id)},
            name=node_name,
            manufacturer="Ducobox",
            model=node_type,
            via_device=(DOMAIN, device_id),
        )

        # Get the sensors for this node type
        node_sensors = NODE_SENSORS.get(node_type, [])
        for description in node_sensors:
            unique_id = f"{node_device_id}-{description.key}"
            entities.append(
                DucoboxNodeSensorEntity(
                    coordinator=coordinator,
                    node_id=node_id,
                    description=description,
                    device_info=node_device_info,
                    unique_id=unique_id,
                    device_id=device_id,
                    node_name=node_name,
                )
            )

    async_add_entities(entities)

class DucoboxSensorEntity(CoordinatorEntity[DucoboxCoordinator], SensorEntity):
    """Representation of a Ducobox sensor entity."""
    entity_description: DucoboxSensorEntityDescription

    def __init__(
        self,
        coordinator: DucoboxCoordinator,
        description: DucoboxSensorEntityDescription,
        device_info: DeviceInfo,
        unique_id: str,
    ) -> None:
        """Initialize a Ducobox sensor entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_device_info = device_info
        self._attr_unique_id = unique_id
        self._attr_name = f"{device_info['name']} {description.name}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        try:
            return self.entity_description.value_fn(self.coordinator.data)
        except Exception as e:
            _LOGGER.debug(f"Error getting value for {self.name}: {e}")
            return None

class DucoboxNodeSensorEntity(CoordinatorEntity[DucoboxCoordinator], SensorEntity):
    """Representation of a Ducobox node sensor entity."""
    entity_description: DucoboxNodeSensorEntityDescription

    def __init__(
        self,
        coordinator: DucoboxCoordinator,
        node_id: int,
        description: DucoboxNodeSensorEntityDescription,
        device_info: DeviceInfo,
        unique_id: str,
        device_id: str,
        node_name: str,
    ) -> None:
        """Initialize a Ducobox node sensor entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_device_info = device_info
        self._attr_unique_id = unique_id
        self._node_id = node_id
        self._attr_name = f"{node_name} {description.name}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        nodes = self.coordinator.data.get('Nodes', [])
        for node in nodes:
            if node.get('Node') == self._node_id:
                try:
                    return self.entity_description.value_fn(node)
                except Exception as e:
                    _LOGGER.debug(f"Error getting value for {self.name}: {e}")
                    return None
        return None
