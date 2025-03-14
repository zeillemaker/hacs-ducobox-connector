# Ducobox Connectivity Board

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

This is a Home Assistant custom integration that provides sensor entities for a Ducobox Connectivity Board. It uses the `ducopy` library (version 16) to communicate with your DucoBox ventilation system and exposes relevant data to Home Assistant sensors.

## Features

- Fetch real-time data from your DucoBox ventilation unit
- Expose temperature, humidity, CO₂, pressure, fan speeds, and more as Home Assistant sensors
- Includes support for multiple node types (e.g., BOX, UCCO2, BSRH, etc.)

## Installation

### Installation via HACS

1. In Home Assistant, navigate to **HACS** > **Integrations**.
2. Click the three-dot menu in the top-right corner and select **Custom repositories**.
3. In the **Add custom repository** dialog:
   - **Repository**: `[https://github.com/Sikerdebaard/hacs-ducobox-connector](https://github.com/Sikerdebaard/hacs-ducobox-connector)`  
   - **Category**: `Integration`
4. Click **Add** to save.
5. After adding the custom repository, search for **Ducobox Connectivity Board** in HACS.
6. Click **Download** and follow the prompts to install.
7. Restart Home Assistant when prompted.

### Manual Installation (Alternative)

1. Download or clone this repository.
2. Copy the `ducobox_connectivity_board` folder into your Home Assistant `config/custom_components` directory, so that you end up with:
   ```
   custom_components
   └── ducobox_connectivity_board
       ├── __init__.py
       ├── sensor.py
       ├── manifest.json
       └── ...
   ```
3. Restart Home Assistant.

## Configuration

Often, the Ducobox Connectivity Board add-on can detect your DucoBox automatically. If so, Home Assistant will display a “New Device Discovered” notification or you’ll see **Ducobox Connectivity Board** under **Settings** > **Devices & Services** awaiting configuration. In that case, simply follow the on-screen steps to finish setup.

If auto-detection does not occur or you prefer to do it manually, follow these steps:

1. After installing and restarting Home Assistant, go to **Settings** > **Devices & Services** > **Integrations**.
2. Click **Add Integration** and search for **Ducobox Connectivity Board**.
3. Follow the on-screen instructions to provide necessary connection details (e.g., IP address, credentials).
4. Once configured, your Ducobox sensors will appear in Home Assistant under the newly created integration.


## Contributing

- Contributions, pull requests, and suggestions are always welcome!
- Feel free to open an [issue](https://github.com/Sikerdebaard/hacs-ducobox-connector/issues) or submit a PR for improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Enjoy your better-connected DucoBox ventilation system in Home Assistant!**
