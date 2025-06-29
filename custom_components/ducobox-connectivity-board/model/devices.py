from .utils import (
    process_node_temperature,
    process_node_humidity,
    process_node_co2,
    process_node_iaq,
    process_temperature,
    process_speed,
    process_pressure,
    process_rssi,
    process_uptime,
    process_timefilterremain,
    process_bypass_position,
    safe_get,
)

from collections.abc import Callable
from dataclasses import dataclass
from homeassistant.components.sensor import (
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfTime,
    PERCENTAGE,
    CONCENTRATION_PARTS_PER_MILLION,
)


@dataclass(frozen=True, kw_only=True)
class DucoboxSensorEntityDescription(SensorEntityDescription):
    """Describes a Ducobox sensor entity."""

    value_fn: Callable[[dict], float | None]


@dataclass(frozen=True, kw_only=True)
class DucoboxNodeSensorEntityDescription(SensorEntityDescription):
    """Describes a Ducobox node sensor entity."""

    value_fn: Callable[[dict], float | None]
    sensor_key: str
    node_type: str


SENSORS: tuple[DucoboxSensorEntityDescription, ...] = (
    # Temperature sensors
    # relevant ducobox documentation: https://www.duco.eu/Wes/CDN/1/Attachments/installation-guide-DucoBox-Energy-Comfort-(Plus)-(en)_638635518879333838.pdf
    # Oda = outdoor -> box
    DucoboxSensorEntityDescription(
        key="TempOda",
        name="Outdoor Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        value_fn=lambda data: process_temperature(
            safe_get(data, 'info', 'Ventilation', 'Sensor', 'TempOda', 'Val')
        ),
    ),
    # Sup = box -> house
    DucoboxSensorEntityDescription(
        key="TempSup",
        name="Supply Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        value_fn=lambda data: process_temperature(
            safe_get(data, 'info', 'Ventilation', 'Sensor', 'TempSup', 'Val')
        ),
    ),
    # Eta = house -> box
    DucoboxSensorEntityDescription(
        key="TempEta",
        name="Extract Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        value_fn=lambda data: process_temperature(
            safe_get(data, 'info', 'Ventilation', 'Sensor', 'TempEta', 'Val')
        ),
    ),
    # Eha = box -> outdoor
    DucoboxSensorEntityDescription(
        key="TempEha",
        name="Exhaust Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        value_fn=lambda data: process_temperature(
            safe_get(data, 'info', 'Ventilation', 'Sensor', 'TempEha', 'Val')
        ),
    ),
    # Fan speed sensors
    DucoboxSensorEntityDescription(
        key="SpeedSup",
        name="Supply Fan Speed",
        native_unit_of_measurement="RPM",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.SPEED,
        value_fn=lambda data: process_speed(
            safe_get(data, 'info', 'Ventilation', 'Fan', 'SpeedSup', 'Val')
        ),
    ),
    DucoboxSensorEntityDescription(
        key="SpeedEha",
        name="Exhaust Fan Speed",
        native_unit_of_measurement="RPM",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.SPEED,
        value_fn=lambda data: process_speed(
            safe_get(data, 'info', 'Ventilation', 'Fan', 'SpeedEha', 'Val')
        ),
    ),
    # Pressure sensors
    DucoboxSensorEntityDescription(
        key="PressSup",
        name="Supply Pressure",
        native_unit_of_measurement=UnitOfPressure.PA,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PRESSURE,
        value_fn=lambda data: process_pressure(
            safe_get(data, 'info', 'Ventilation', 'Fan', 'PressSup', 'Val')
        ),
    ),
    DucoboxSensorEntityDescription(
        key="PressEha",
        name="Exhaust Pressure",
        native_unit_of_measurement=UnitOfPressure.PA,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PRESSURE,
        value_fn=lambda data: process_pressure(
            safe_get(data, 'info', 'Ventilation', 'Fan', 'PressEha', 'Val')
        ),
    ),
    # Wi-Fi signal strength
    DucoboxSensorEntityDescription(
        key="RssiWifi",
        name="Wi-Fi Signal Strength",
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        value_fn=lambda data: process_rssi(
            safe_get(data, 'info', 'General', 'Lan', 'RssiWifi', 'Val')
        ),
    ),
    # Device uptime
    DucoboxSensorEntityDescription(
        key="UpTime",
        name="Device Uptime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.DURATION,
        value_fn=lambda data: process_uptime(
            safe_get(data, 'info', 'General', 'Board', 'UpTime', 'Val')
        ),
    ),
    # Filter time remaining
    DucoboxSensorEntityDescription(
        key="TimeFilterRemain",
        name="Filter Time Remaining",
        native_unit_of_measurement=UnitOfTime.DAYS,  # Assuming the value is in days
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DURATION,
        value_fn=lambda data: process_timefilterremain(
            safe_get(data, 'info', 'HeatRecovery', 'General', 'TimeFilterRemain', 'Val')
        ),
    ),
    # Bypass position
    DucoboxSensorEntityDescription(
        key="BypassPos",
        name="Bypass Position",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: process_bypass_position(
            safe_get(data, 'info', 'HeatRecovery', 'Bypass', 'Pos', 'Val')
        ),
    ),
    # Add additional sensors here if needed
)

# Define sensors for nodes based on their type
NODE_SENSORS: dict[str, list[DucoboxNodeSensorEntityDescription]] = {
    'BOX': [
        DucoboxNodeSensorEntityDescription(
            key='Mode',
            name='Ventilation Mode',
            value_fn=lambda node: safe_get(node, 'Ventilation', 'Mode'),
            sensor_key='Mode',
            node_type='BOX',
        ),
        DucoboxNodeSensorEntityDescription(
            key='State',
            name='Ventilation State',
            value_fn=lambda node: safe_get(node, 'Ventilation', 'State'),
            sensor_key='State',
            node_type='BOX',
        ),
        DucoboxNodeSensorEntityDescription(
            key='FlowLvlTgt',
            name='Flow Level Target',
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: safe_get(node, 'Ventilation', 'FlowLvlTgt'),
            sensor_key='FlowLvlTgt',
            node_type='BOX',
        ),
        DucoboxNodeSensorEntityDescription(
            key='TimeStateRemain',
            name='Time State Remaining',
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value_fn=lambda node: safe_get(node, 'Ventilation', 'TimeStateRemain'),
            sensor_key='TimeStateRemain',
            node_type='BOX',
        ),
        DucoboxNodeSensorEntityDescription(
            key='TimeStateEnd',
            name='Time State End',
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value_fn=lambda node: safe_get(node, 'Ventilation', 'TimeStateEnd'),
            sensor_key='TimeStateEnd',
            node_type='BOX',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Temp',
            name='Temperature',
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda node: process_node_temperature(
                safe_get(node, 'Sensor', 'data', 'Temp')
            ),
            sensor_key='Temp',
            node_type='BOX',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Rh',
            name='Relative Humidity',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.HUMIDITY,
            value_fn=lambda node: process_node_humidity(
                safe_get(node, 'Sensor', 'data', 'Rh')
            ),
            sensor_key='Rh',
            node_type='BOX',
        ),
        DucoboxNodeSensorEntityDescription(
            key='IaqRh',
            name='Humidity Air Quality',
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: process_node_iaq(
                safe_get(node, 'Sensor', 'data', 'IaqRh')
            ),
            sensor_key='IaqRh',
            node_type='BOX',
        ),
    ],
    'UCCO2': [
        DucoboxNodeSensorEntityDescription(
            key='Temp',
            name='Temperature',
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda node: process_node_temperature(
                safe_get(node, 'Sensor', 'data', 'Temp')
            ),
            sensor_key='Temp',
            node_type='UCCO2',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Co2',
            name='CO₂',
            native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
            device_class=SensorDeviceClass.CO2,
            value_fn=lambda node: process_node_co2(
                safe_get(node, 'Sensor', 'data', 'Co2')
            ),
            sensor_key='Co2',
            node_type='UCCO2',
        ),
        DucoboxNodeSensorEntityDescription(
            key='IaqCo2',
            name='CO₂ Air Quality',
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: process_node_iaq(
                safe_get(node, 'Sensor', 'data', 'IaqCo2')
            ),
            sensor_key='IaqCo2',
            node_type='UCCO2',
        ),
    ],
    'BSRH': [
        DucoboxNodeSensorEntityDescription(
            key='Temp',
            name='Temperature',
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda node: process_node_temperature(
                safe_get(node, 'Sensor', 'data', 'Temp')
            ),
            sensor_key='Temp',
            node_type='BSRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Rh',
            name='Relative Humidity',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.HUMIDITY,
            value_fn=lambda node: process_node_humidity(
                safe_get(node, 'Sensor', 'data', 'Rh')
            ),
            sensor_key='Rh',
            node_type='BSRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='IaqRh',
            name='Humidity Air Quality',
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: process_node_iaq(
                safe_get(node, 'Sensor', 'data', 'IaqRh')
            ),
            sensor_key='IaqRh',
            node_type='BSRH',
        ),
    ],
    'VLVRH': [
        DucoboxNodeSensorEntityDescription(
            key='State',
            name='Ventilation State',
            value_fn=lambda node: safe_get(node, 'Ventilation', 'State'),
            sensor_key='State',
            node_type='VLVRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='TimeStateRemain',
            name='Time State Remaining',
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value_fn=lambda node: safe_get(node, 'Ventilation', 'TimeStateRemain'),
            sensor_key='TimeStateRemain',
            node_type='VLVRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='TimeStateEnd',
            name='Time State End',
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value_fn=lambda node: safe_get(node, 'Ventilation', 'TimeStateEnd'),
            sensor_key='TimeStateEnd',
            node_type='VLVRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Mode',
            name='Ventilation Mode',
            value_fn=lambda node: safe_get(node, 'Ventilation', 'Mode'),
            sensor_key='Mode',
            node_type='VLVRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='FlowLvlTgt',
            name='Flow Level Target',
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: safe_get(node, 'Ventilation', 'FlowLvlTgt'),
            sensor_key='FlowLvlTgt',
            node_type='VLVRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='IaqRh',
            name='Humidity Air Quality',
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: process_node_iaq(
                safe_get(node, 'Sensor', 'data', 'IaqRh')
            ),
            sensor_key='IaqRh',
            node_type='VLVRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Rh',
            name='Relative Humidity',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.HUMIDITY,
            value_fn=lambda node: process_node_iaq(
                safe_get(node, 'Sensor', 'data', 'Rh')
            ),
            sensor_key='Rh',
            node_type='VLVRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Temp',
            name='Temperature',
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda node: process_node_temperature(
                safe_get(node, 'Sensor', 'data', 'Temp')
            ),
            sensor_key='Temp',
            node_type='VLVRH',
        ),
    ],
    'VLVCO2': [
        DucoboxNodeSensorEntityDescription(
            key='State',
            name='Ventilation State',
            value_fn=lambda node: safe_get(node, 'Ventilation', 'State'),
            sensor_key='State',
            node_type='VLVCO2',
        ),
        DucoboxNodeSensorEntityDescription(
            key='TimeStateRemain',
            name='Time State Remaining',
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value_fn=lambda node: safe_get(node, 'Ventilation', 'TimeStateRemain'),
            sensor_key='TimeStateRemain',
            node_type='VLVCO2',
        ),
        DucoboxNodeSensorEntityDescription(
            key='TimeStateEnd',
            name='Time State End',
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value_fn=lambda node: safe_get(node, 'Ventilation', 'TimeStateEnd'),
            sensor_key='TimeStateEnd',
            node_type='VLVCO2',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Mode',
            name='Ventilation Mode',
            value_fn=lambda node: safe_get(node, 'Ventilation', 'Mode'),
            sensor_key='Mode',
            node_type='VLVCO2',
        ),
        DucoboxNodeSensorEntityDescription(
            key='FlowLvlTgt',
            name='Flow Level Target',
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: safe_get(node, 'Ventilation', 'FlowLvlTgt'),
            sensor_key='FlowLvlTgt',
            node_type='VLVCO2',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Co2',
            name='CO₂',
            native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
            device_class=SensorDeviceClass.CO2,
            value_fn=lambda node: process_node_co2(
                safe_get(node, 'Sensor', 'data', 'Co2')
            ),
            sensor_key='Co2',
            node_type='VLVCO2',
        ),
        DucoboxNodeSensorEntityDescription(
            key='IaqCo2',
            name='CO₂ Air Quality',
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: process_node_iaq(
                safe_get(node, 'Sensor', 'data', 'IaqCo2')
            ),
            sensor_key='IaqCo2',
            node_type='VLVCO2',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Temp',
            name='Temperature',
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda node: process_node_temperature(
                safe_get(node, 'Sensor', 'data', 'Temp')
            ),
            sensor_key='Temp',
            node_type='VLVCO2',
        ),
    ],
    'VLVCO2RH': [
        DucoboxNodeSensorEntityDescription(
            key='State',
            name='Ventilation State',
            value_fn=lambda node: safe_get(node, 'Ventilation', 'State'),
            sensor_key='State',
            node_type='VLVCO2RH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='TimeStateRemain',
            name='Time State Remaining',
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value_fn=lambda node: safe_get(node, 'Ventilation', 'TimeStateRemain'),
            sensor_key='TimeStateRemain',
            node_type='VLVCO2RH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='TimeStateEnd',
            name='Time State End',
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value_fn=lambda node: safe_get(node, 'Ventilation', 'TimeStateEnd'),
            sensor_key='TimeStateEnd',
            node_type='VLVCO2RH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Mode',
            name='Ventilation Mode',
            value_fn=lambda node: safe_get(node, 'Ventilation', 'Mode'),
            sensor_key='Mode',
            node_type='VLVCO2RH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='FlowLvlTgt',
            name='Flow Level Target',
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: safe_get(node, 'Ventilation', 'FlowLvlTgt'),
            sensor_key='FlowLvlTgt',
            node_type='VLVCO2RH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Co2',
            name='CO₂',
            native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
            device_class=SensorDeviceClass.CO2,
            value_fn=lambda node: process_node_co2(
                safe_get(node, 'Sensor', 'data', 'Co2')
            ),
            sensor_key='Co2',
            node_type='VLVCO2RH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='IaqCo2',
            name='CO₂ Air Quality',
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: process_node_iaq(
                safe_get(node, 'Sensor', 'data', 'IaqCo2')
            ),
            sensor_key='IaqCo2',
            node_type='VLVCO2RH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Rh',
            name='Relative Humidity',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.HUMIDITY,
            value_fn=lambda node: process_node_iaq(
                safe_get(node, 'Sensor', 'data', 'Rh')
            ),
            sensor_key='Rh',
            node_type='VLVCO2RH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='IaqRh',
            name='Humidity Air Quality',
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: process_node_iaq(
                safe_get(node, 'Sensor', 'data', 'IaqRh')
            ),
            sensor_key='IaqRh',
            node_type='VLVCO2RH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Temp',
            name='Temperature',
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda node: process_node_temperature(
                safe_get(node, 'Sensor', 'data', 'Temp')
            ),
            sensor_key='Temp',
            node_type='VLVCO2RH',
        ),
    ],
    'VLV': [
        DucoboxNodeSensorEntityDescription(
            key='State',
            name='Ventilation State',
            value_fn=lambda node: safe_get(node, 'Ventilation', 'State'),
            sensor_key='State',
            node_type='VLV',
        ),

        DucoboxNodeSensorEntityDescription(
            key='Mode',
            name='Ventilation Mode',
            value_fn=lambda node: safe_get(node, 'Ventilation', 'Mode'),
            sensor_key='Mode',
            node_type='VLV',
        ),
        DucoboxNodeSensorEntityDescription(
            key='FlowLvlTgt',
            name='Flow Level Target',
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: safe_get(node, 'Ventilation', 'FlowLvlTgt'),
            sensor_key='FlowLvlTgt',
            node_type='VLV',
        ),
    ],
    'SWITCH': [
        DucoboxNodeSensorEntityDescription(
            key='State',
            name='Ventilation State',
            value_fn=lambda node: safe_get(node, 'Ventilation', 'State'),
            sensor_key='State',
            node_type='SWITCH',
        ),

        DucoboxNodeSensorEntityDescription(
            key='Mode',
            name='Ventilation Mode',
            value_fn=lambda node: safe_get(node, 'Ventilation', 'Mode'),
            sensor_key='Mode',
            node_type='SWITCH',
        ), 
    ],
    'UCBAT': [
        DucoboxNodeSensorEntityDescription(
            key='State',
            name='Ventilation State',
            value_fn=lambda node: safe_get(node, 'Ventilation', 'State'),
            sensor_key='State',
            node_type='UCBAT',
        ),
        DucoboxNodeSensorEntityDescription(
            key='TimeStateRemain',
            name='Time State Remaining',
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value_fn=lambda node: safe_get(node, 'Ventilation', 'TimeStateRemain'),
            sensor_key='TimeStateRemain',
            node_type='UCBAT',
        ),
        DucoboxNodeSensorEntityDescription(
            key='TimeStateEnd',
            name='Time State End',
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value_fn=lambda node: safe_get(node, 'Ventilation', 'TimeStateEnd'),
            sensor_key='TimeStateEnd',
            node_type='UCBAT',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Mode',
            name='Ventilation Mode',
            value_fn=lambda node: safe_get(node, 'Ventilation', 'Mode'),
            sensor_key='Mode',
            node_type='UCBAT',
        ),
    ],
    'UCRH': [
        DucoboxNodeSensorEntityDescription(
            key='State',
            name='Ventilation State',
            value_fn=lambda node: safe_get(node, 'Ventilation', 'State'),
            sensor_key='State',
            node_type='UCRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='TimeStateRemain',
            name='Time State Remaining',
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value_fn=lambda node: safe_get(node, 'Ventilation', 'TimeStateRemain'),
            sensor_key='TimeStateRemain',
            node_type='UCRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='TimeStateEnd',
            name='Time State End',
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value_fn=lambda node: safe_get(node, 'Ventilation', 'TimeStateEnd'),
            sensor_key='TimeStateEnd',
            node_type='UCRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Mode',
            name='Ventilation Mode',
            value_fn=lambda node: safe_get(node, 'Ventilation', 'Mode'),
            sensor_key='Mode',
            node_type='ICRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='FlowLvlTgt',
            name='Flow Level Target',
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: safe_get(node, 'Ventilation', 'FlowLvlTgt'),
            sensor_key='FlowLvlTgt',
            node_type='UCRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='IaqRh',
            name='Humidity Air Quality',
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: process_node_iaq(
                safe_get(node, 'Sensor', 'data', 'IaqRh')
            ),
            sensor_key='IaqRh',
            node_type='UCRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Rh',
            name='Relative Humidity',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.HUMIDITY,
            value_fn=lambda node: process_node_iaq(
                safe_get(node, 'Sensor', 'data', 'Rh')
            ),
            sensor_key='Rh',
            node_type='UCRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Temp',
            name='Temperature',
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda node: process_node_temperature(
                safe_get(node, 'Sensor', 'data', 'Temp')
            ),
            sensor_key='Temp',
            node_type='UCRH',
        ),
        
    ],
    # Add other node types and their sensors if needed
}
