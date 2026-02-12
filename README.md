# Domestia Home Assistant Integration

Home Assistant integration for Domestia home automation systems.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

## Features

- ✅ **Lights**: Control all light outputs including dimmers
- ✅ **Covers**: Control shutters/blinds with position feedback
- ✅ **Climate**: Control thermostats (basic support)
- ✅ **Real-time updates**: Automatic state synchronization
- ✅ **Configurable polling**: Adjust update interval (1-60 seconds)
- ✅ **Debug mode**: Optional detailed logging for troubleshooting

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

1. Download the latest release
2. Copy the `custom_components/domestia` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

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
- **Debug Mode**: Enable detailed logging for troubleshooting (default: OFF)

To change options:
1. Go to **Settings** → **Devices & Services**
2. Find your Domestia integration
3. Click **Configure**

## Logging

By default, the integration uses minimal logging (INFO level). 

### Enable Debug Mode via UI
1. Go to Settings → Devices & Services → Domestia → Configure
2. Enable "Debug Mode"
3. Check logs for detailed information

### Enable Debug Logging via configuration.yaml

```yaml
logger:
  default: info
  logs:
    custom_components.domestia: debug
```

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

## Performance Tips

- **Fast polling (1-2s)**: More responsive, higher network load
- **Normal polling (5s)**: Good balance (default)
- **Slow polling (10-30s)**: Lower network load, less responsive
- **Debug mode**: Only enable when troubleshooting, then disable to reduce log size

## Troubleshooting

**Devices not responding:**
- Verify the IP address is correct
- Check network connectivity
- Ensure the Domestia controller is powered on

**State not updating:**
- Decrease the scan interval in options
- Enable debug mode and check logs for connection errors

**Wrong device states:**
- Reload the integration
- Check for firmware updates on your Domestia controller

**Too much logging:**
- Disable debug mode in integration options
- Set logger level to INFO in configuration.yaml

## Credits

Based on the [homebridge-domestia](https://github.com/vdhicts/homebridge-domestia) plugin.

## License

MIT License - see LICENSE file for details

## Support

For issues and feature requests, please use the GitHub issue tracker.
