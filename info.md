# Domestia Integration

Control your Domestia home automation system directly from Home Assistant.

## What you get

- **Lights**: Full control of all light outputs including dimmers
- **Covers**: Control shutters with position tracking and status feedback  
- **Climate**: Basic thermostat support
- **Real-time sync**: Automatic state updates when devices are controlled physically

## Quick Setup

1. Install via HACS
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Domestia"
5. Enter IP and MAC address of your Domestia controller

## Configuration

After installation, you can configure the polling interval (how often Home Assistant checks for updates):
- Default: 5 seconds
- Range: 1-60 seconds
- Lower values = more responsive but more network traffic

## Requirements

- Domestia home automation controller on your network
- IP address and MAC address of the controller
- Home Assistant 2024.1.0 or newer
