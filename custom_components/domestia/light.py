import logging
from homeassistant.components.light import (
    LightEntity,
    ColorMode,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, add_entities):
    _LOGGER.warning("Domestia Light: async_setup_entry called")
    
    data = hass.data[DOMAIN][entry.entry_id]
    network = data["network"]
    accessories = data["accessories"]
    coordinator = data["coordinator"]

    lights = [
        DomestiaLight(coordinator, network, acc)
        for acc in accessories
        if acc["category"] == "light"
    ]

    _LOGGER.warning(f"Domestia Light: Adding {len(lights)} entities")
    add_entities(lights)


class DomestiaLight(CoordinatorEntity, LightEntity):
    def __init__(self, coordinator, network, acc):
        super().__init__(coordinator)
        self.network = network
        self.acc = acc

        self._brightness = 255
        self._is_dimmer = acc["type"] in (6, 7)
        
        _LOGGER.warning(f"Domestia Light: Created entity ID={acc['id']}, Name={acc.get('name')}")

    @property
    def name(self):
        return self.acc.get("name", f"Domestia Light {self.acc['id']}")

    @property
    def unique_id(self):
        return f"domestia_light_{self.acc['id']}"

    @property
    def supported_color_modes(self):
        if self._is_dimmer:
            return {ColorMode.BRIGHTNESS}
        return {ColorMode.ONOFF}

    @property
    def color_mode(self):
        if self._is_dimmer:
            return ColorMode.BRIGHTNESS
        return ColorMode.ONOFF

    @property
    def is_on(self):
        state = self.acc.get("state", False)
        return state

    @property
    def brightness(self):
        if self._is_dimmer:
            return self._brightness
        return None

    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        _LOGGER.warning(f"Domestia Light {self.acc['id']}: COORDINATOR UPDATE! state={self.acc.get('state')}")
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        _LOGGER.warning(f"Domestia Light {self.acc['id']} '{self.acc.get('name')}': TURN ON command")
        
        if self._is_dimmer:
            if "brightness" in kwargs:
                self._brightness = kwargs["brightness"]
            value = round(self._brightness * 64 / 255)
            _LOGGER.warning(f"Domestia: Sending dimmer command: output={self.acc['id']+1}, value={value}")
            await self.network.send([255,0,0,3,150, self.acc["id"]+1, value])
        else:
            _LOGGER.warning(f"Domestia: Sending ON command: output={self.acc['id']+1}")
            await self.network.send([255,0,0,3,150, self.acc["id"]+1, 0xFE])

        self.acc["state"] = True
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        _LOGGER.warning(f"Domestia Light {self.acc['id']} '{self.acc.get('name')}': TURN OFF command")
        _LOGGER.warning(f"Domestia: Sending OFF command: output={self.acc['id']+1}")
        
        await self.network.send([255,0,0,3,150, self.acc["id"]+1, 0])
        
        self.acc["state"] = False
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()
