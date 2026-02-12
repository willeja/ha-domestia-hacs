import asyncio
import logging
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, DEFAULT_DEBUG_MODE
from .network import DomestiaNetwork
from .discovery import DomestiaDiscovery

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["light", "cover", "climate"]


async def async_setup(hass, config):
    """Needed so HA treats this as a fully async integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.info("Domestia: Setup starting")
    
    try:
        ip = entry.data["ip"]
        mac = entry.data["mac"]
        
        # Get options
        scan_interval = entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
        debug_mode = entry.options.get("debug_mode", DEFAULT_DEBUG_MODE)
        
        _LOGGER.info(f"Domestia: Connecting to {ip}, scan interval: {scan_interval}s, debug: {debug_mode}")

        network = DomestiaNetwork(ip, mac)
        await network.connect()
        _LOGGER.info("Domestia: Connected")

        discovery = DomestiaDiscovery(network)
        accessories = await discovery.load_all()
        _LOGGER.info(f"Domestia: Found {len(accessories)} accessories")

        if debug_mode:
            for acc in accessories:
                _LOGGER.debug(f"  - ID={acc['id']}, Type={acc['type']}, Cat={acc['category']}, Name={acc.get('name', '?')}")

        # Create coordinator for state updates
        async def async_update_data():
            """Fetch data from Domestia."""
            if debug_mode:
                _LOGGER.debug("Polling states...")
            
            loop = asyncio.get_running_loop()
            future = loop.create_future()
            
            def cb(data):
                if not future.done():
                    future.set_result(data)
            
            await network.read_relais_status(cb)
            
            try:
                data = await asyncio.wait_for(future, timeout=3.0)
                
                if len(data) > 3:
                    # CRITICAL: JS implementation uses message.slice(3), which is data[3:] in Python!
                    states = data[3:]
                    
                    if debug_mode:
                        _LOGGER.debug(f"States length={len(states)}, first 20: {list(states[:20])}")
                    
                    # Update accessory states
                    changed = False
                    for acc in accessories:
                        if acc["category"] == "light" and acc["id"] < len(states):
                            old_state = acc.get("state", False)
                            new_state = states[acc["id"]] != 0
                            acc["state"] = new_state
                            
                            if old_state != new_state:
                                changed = True
                                if debug_mode:
                                    _LOGGER.debug(f"Light {acc['id']} ({acc.get('name')}): {old_state} -> {new_state}")
                        
                        elif acc["category"] == "cover" and acc["id"] < len(states):
                            old_pos = acc.get("position", 50)
                            old_closing = acc.get("closing", False)
                            old_opening = acc.get("opening", False)
                            
                            new_pos = states[acc["id"]] % 128
                            new_closing = states[acc["id"]] >= 128
                            new_opening = (acc["id"] + 1 < len(states) and states[acc["id"] + 1] >= 128)
                            
                            acc["position"] = new_pos
                            acc["closing"] = new_closing
                            acc["opening"] = new_opening
                            
                            if old_pos != new_pos or old_closing != new_closing or old_opening != new_opening:
                                changed = True
                                if debug_mode:
                                    _LOGGER.debug(f"Cover {acc['id']} ({acc.get('name')}): pos {old_pos}->{new_pos}")
                    
                    return states
                else:
                    if debug_mode:
                        _LOGGER.warning(f"Response too short, length={len(data)}")
                    return []
            except asyncio.TimeoutError:
                _LOGGER.warning("Timeout waiting for state response")
                return []
            except Exception as e:
                _LOGGER.error(f"Error in update: {e}", exc_info=True)
                return []
        
        _LOGGER.info("Creating coordinator...")
        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name="domestia",
            update_method=async_update_data,
            update_interval=timedelta(seconds=scan_interval),
        )
        
        coordinator.always_update = True
        
        _LOGGER.info("Fetching initial data...")
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.info("Initial data OK")

        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = {
            "network": network,
            "accessories": accessories,
            "coordinator": coordinator
        }
        
        _LOGGER.info("Setting up platforms...")
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        
        # Listen for option updates
        entry.async_on_unload(entry.add_update_listener(update_listener))
        
        _LOGGER.info("Domestia setup complete")
        return True
        
    except Exception as e:
        _LOGGER.error(f"Setup failed: {e}", exc_info=True)
        raise


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    _LOGGER.info("Options updated, reloading integration")
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.info("Unloading...")
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
