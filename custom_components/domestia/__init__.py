import asyncio
import logging
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .network import DomestiaNetwork
from .discovery import DomestiaDiscovery

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["light", "cover", "climate"]


async def async_setup(hass, config):
    """Needed so HA treats this as a fully async integration."""
    _LOGGER.warning("Domestia: async_setup called")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.warning("Domestia: === SETUP ENTRY STARTING ===")
    
    try:
        ip = entry.data["ip"]
        mac = entry.data["mac"]
        
        # Get scan interval from options, fallback to default
        scan_interval = entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
        _LOGGER.warning(f"Domestia: Connecting to {ip} (MAC: {mac}), scan interval: {scan_interval}s")

        network = DomestiaNetwork(ip, mac)
        await network.connect()
        _LOGGER.warning("Domestia: Network connected")

        discovery = DomestiaDiscovery(network)
        accessories = await discovery.load_all()
        _LOGGER.warning(f"Domestia: Found {len(accessories)} accessories")

        for acc in accessories:
            _LOGGER.warning(f"Domestia:   - ID={acc['id']}, Type={acc['type']}, Cat={acc['category']}, Name={acc.get('name', '?')}")

        # Create coordinator for state updates
        async def async_update_data():
            """Fetch data from Domestia."""
            _LOGGER.warning("Domestia: >>> POLLING STATES <<<")
            loop = asyncio.get_running_loop()
            future = loop.create_future()
            
            def cb(data):
                if not future.done():
                    _LOGGER.warning(f"Domestia: Got callback, len={len(data)}")
                    future.set_result(data)
            
            await network.read_relais_status(cb)
            
            try:
                data = await asyncio.wait_for(future, timeout=3.0)
                _LOGGER.warning(f"Domestia: Raw data length={len(data)}, first 10 bytes: {list(data[:10])}")
                
                if len(data) > 3:
                    # CRITICAL: JS implementation uses message.slice(3), which is data[3:] in Python!
                    # NOT data[4:]!
                    states = data[3:]
                    
                    _LOGGER.warning(f"Domestia: States array length={len(states)}, first 25: {list(states[:25])}")
                    
                    # Update accessory states
                    changed = False
                    for acc in accessories:
                        if acc["category"] == "light" and acc["id"] < len(states):
                            old_state = acc.get("state", False)
                            new_state = states[acc["id"]] != 0
                            acc["state"] = new_state
                            
                            # Log every light's state for debugging
                            _LOGGER.warning(f"Domestia: Light acc[{acc['id']}] '{acc.get('name')}': states[{acc['id']}]={states[acc['id']]} -> {new_state}")
                            
                            if old_state != new_state:
                                changed = True
                                _LOGGER.warning(f"Domestia: !!! STATE CHANGE !!! Light {acc['id']} ({acc.get('name')}): {old_state} -> {new_state}")
                        
                        elif acc["category"] == "cover" and acc["id"] < len(states):
                            # For covers, track position and movement state
                            old_pos = acc.get("position", 50)
                            old_closing = acc.get("closing", False)
                            old_opening = acc.get("opening", False)
                            
                            # Position is in lower 7 bits
                            new_pos = states[acc["id"]] % 128
                            
                            # Movement flags are in bit 7
                            new_closing = states[acc["id"]] >= 128
                            new_opening = (acc["id"] + 1 < len(states) and states[acc["id"] + 1] >= 128)
                            
                            acc["position"] = new_pos
                            acc["closing"] = new_closing
                            acc["opening"] = new_opening
                            
                            _LOGGER.debug(f"Domestia: Cover acc[{acc['id']}] '{acc.get('name')}': pos={new_pos}, closing={new_closing}, opening={new_opening}")
                            
                            if old_pos != new_pos or old_closing != new_closing or old_opening != new_opening:
                                changed = True
                                _LOGGER.warning(f"Domestia: !!! COVER CHANGE !!! Cover {acc['id']} ({acc.get('name')}): pos {old_pos}->{new_pos}, closing {old_closing}->{new_closing}, opening {old_opening}->{new_opening}")
                    
                    if changed:
                        _LOGGER.warning("Domestia: Changes detected, returning new data to trigger entity updates")
                    
                    # Return the states data - this triggers entity updates
                    return {"states": list(states), "timestamp": asyncio.get_event_loop().time()}
                else:
                    _LOGGER.error(f"Domestia: Response too short, len={len(data)}")
                    return {}
            except asyncio.TimeoutError:
                _LOGGER.error("Domestia: TIMEOUT waiting for response")
                return {}
            except Exception as e:
                _LOGGER.error(f"Domestia: ERROR in update: {e}", exc_info=True)
                return {}
        
        _LOGGER.warning("Domestia: Creating coordinator...")
        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name="domestia",
            update_method=async_update_data,
            update_interval=timedelta(seconds=scan_interval),
        )
        
        # Force always_update so entities get notified even if data looks the same
        coordinator.always_update = True
        
        _LOGGER.warning(f"Domestia: Coordinator will poll every {scan_interval} seconds")
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.warning("Domestia: Initial data OK")

        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = {
            "network": network,
            "accessories": accessories,
            "coordinator": coordinator
        }
        
        _LOGGER.warning("Domestia: Forwarding to platforms...")
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        
        # Listen for option updates
        entry.async_on_unload(entry.add_update_listener(update_listener))
        
        _LOGGER.warning("Domestia: === SETUP COMPLETE ===")
        return True
        
    except Exception as e:
        _LOGGER.error(f"Domestia: SETUP FAILED: {e}", exc_info=True)
        raise


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    _LOGGER.info("Domestia: Options updated, reloading integration")
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.warning("Domestia: Unloading...")
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
