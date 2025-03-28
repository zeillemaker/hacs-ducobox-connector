from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.core import HomeAssistant
from ..const import SCAN_INTERVAL
from .devices import DucoboxSensorEntityDescription, DucoboxNodeSensorEntityDescription
from .utils import safe_get
from typing import Any
from ducopy import DucoPy
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo


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

        data = {}

        if duco_client is None:
            raise Exception("Duco client is not initialized")

        try:
            data['info'] = duco_client.get_info()
            _LOGGER.debug(f"Data received from /info: {data}")

            nodes_response = duco_client.get_nodes()
            _LOGGER.debug(f"Data received from /info/nodes: {nodes_response}")

            if nodes_response and hasattr(nodes_response, 'Nodes'):
                data['nodes'] = [node.dict() for node in nodes_response.Nodes]
            else:
                data['nodes'] = []

            config_nodes = duco_client.raw_get('/config/nodes')
            data['config_nodes'] = config_nodes
            _LOGGER.debug(f"Data received from /config/nodes = {data['config_nodes']}")

            data['mappings'] = {'node_id_to_name': {}}
            for node in data['nodes']:
                node_id = node.get('Node')
                node_type = safe_get(node, 'General', 'Type', 'Val') or 'Unknown'
                node_addr = safe_get(node, 'General', 'Addr') or 'Unknown'
                node_name = f"{node_id}:{node_type}"

                data['mappings']['node_id_to_name'][node_id] = node_name


            return data
        except Exception as e:
            _LOGGER.error("Error fetching data from Ducobox API: %s", e)
            raise

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
        nodes = self.coordinator.data.get('nodes', [])
        for node in nodes:
            if node.get('Node') == self._node_id:
                try:
                    return self.entity_description.value_fn(node)
                except Exception as e:
                    _LOGGER.debug(f"Error getting value for {self.name}: {e}")
                    return None
        return None
