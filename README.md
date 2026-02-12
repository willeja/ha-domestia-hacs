# Domestia Home Assistant Integration

Home Assistant integration for Domestia home automation systems.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

## Features

- ✅ **Lights**: Control all light outputs including dimmers
- ✅ **Covers**: Control shutters/blinds with position feedback
- ✅ **Climate**: Control thermostats (basic support)
- ✅ **Real-time updates**: Automatic state synchronization
- ✅ **Configurable polling**: Adjust update interval (1-60 seconds)

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL
6. Select "Integration" as the category
7. Click "Add"
8. Find "Domestia" in the integration list and click "Download"
9. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/domestia` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Domestia"
4. Enter your Domestia system details:
   - **IP Address**: The IP address of your Domestia controller
   - **MAC Address**: The MAC address of your Domestia controller (format: `AA:BB:CC:DD:EE:FF` or `AA-BB-CC-DD-EE-FF`)

## Options

After adding the integration, you can configure:

- **Scan Interval**: How often to poll the Domestia system (1-60 seconds, default: 5)

To change options:
1. Go to **Settings** → **Devices & Services**
2. Find your Domestia integration
3. Click **Configure**

## Supported Devices

### Lights
- Toggle switches (Type 0)
- Relays (Type 1)
- Timers (Types 2-5)
- Dimmers (Types 6-7)

### Covers
- Shutters with down button (Type 8)
- Single button shutters (Type 10)

### Climate
- Thermostats with temperature sensors (Type 11)

## Troubleshooting

### Enable Debug Logging

Add to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.domestia: debug
```

### Common Issues

**Devices not responding:**
- Verify the IP address is correct
- Check network connectivity
- Ensure the Domestia controller is powered on

**State not updating:**
- Decrease the scan interval in options
- Check logs for connection errors

**Wrong device states:**
- Reload the integration
- Check for firmware updates on your Domestia controller

## Credits

Based on the [homebridge-domestia](https://github.com/vdhicts/homebridge-domestia) plugin.

## License

MIT License - see LICENSE file for details

## Support

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/YOUR_USERNAME/domestia-homeassistant/issues).
