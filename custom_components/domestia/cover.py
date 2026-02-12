import logging
from homeassistant.components.cover import (
    CoverEntity,
    CoverEntityFeature,
    CoverDeviceClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, add_entities):
    _LOGGER.warning("Domestia Cover: async_setup_entry called")
    
    data = hass.data[DOMAIN][entry.entry_id]
    network = data["network"]
    accessories = data["accessories"]
    coordinator = data["coordinator"]

    covers = [
        DomestiaCover(coordinator, network, acc)
        for acc in accessories
        if acc["category"] == "cover"
    ]

    _LOGGER.warning(f"Domestia Cover: Adding {len(covers)} cover entities")
    add_entities(covers)


class DomestiaCover(CoordinatorEntity, CoverEntity):
    """Representation of a Domestia cover/shutter."""
    
    def __init__(self, coordinator, network, acc):
        super().__init__(coordinator)
        self.network = network
        self.acc = acc
        self._target_position = 50
        
        _LOGGER.warning(f"Domestia Cover: Created entity ID={acc['id']}, Name={acc.get('name')}")

    @property
    def name(self):
        return self.acc.get("name", f"Domestia Cover {self.acc['id']}")

    @property
    def unique_id(self):
        return f"domestia_cover_{self.acc['id']}"

    @property
    def device_class(self):
        return CoverDeviceClass.SHUTTER

    @property
    def supported_features(self):
        return (
            CoverEntityFeature.OPEN |
            CoverEntityFeature.CLOSE |
            CoverEntityFeature.STOP |
            CoverEntityFeature.SET_POSITION
        )

    @property
    def current_cover_position(self):
        """Return current position (0=closed, 100=open)."""
        # First try to get from accessory dict (updated by coordinator)
        if "position" in self.acc:
            return self.acc["position"]
        
        # Fallback to reading from coordinator data
        if not self.coordinator.data or len(self.coordinator.data) <= self.acc["id"]:
            return 50
        
        # Position is stored in lower 7 bits (0-127, but reported as 0-100)
        position = self.coordinator.data[self.acc["id"]] % 128
        return position

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return self.current_cover_position == 0

    @property
    def is_closing(self):
        """Return if the cover is closing."""
        # First check accessory dict
        if "closing" in self.acc:
            return self.acc["closing"]
            
        if not self.coordinator.data or len(self.coordinator.data) <= self.acc["id"]:
            return False
        
        # Bit 7 set on first byte = closing/decreasing
        return self.coordinator.data[self.acc["id"]] >= 128

    @property
    def is_opening(self):
        """Return if the cover is opening."""
        # First check accessory dict
        if "opening" in self.acc:
            return self.acc["opening"]
            
        if not self.coordinator.data or len(self.coordinator.data) <= self.acc["id"] + 1:
            return False
        
        # Bit 7 set on second byte = opening/increasing
        return self.coordinator.data[self.acc["id"] + 1] >= 128

    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        position = self.current_cover_position
        closing = self.is_closing
        opening = self.is_opening
        _LOGGER.warning(f"Domestia Cover {self.acc['id']} '{self.acc.get('name')}': Update received - pos={position}, closing={closing}, opening={opening}")
        self.async_write_ha_state()

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = kwargs.get("position", 50)
        self._target_position = position
        
        _LOGGER.warning(f"Domestia Cover {self.acc['id']} '{self.acc.get('name')}': Set position to {position}")
        
        # Send position + 128 as per JS implementation
        # ATWRELAIS command: [255, 0, 0, 3, 150, id+1, position+128]
        await self.network.send([255, 0, 0, 3, 150, self.acc["id"] + 1, position + 128])
        
        # Request coordinator refresh
        await self.coordinator.async_request_refresh()

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        _LOGGER.warning(f"Domestia Cover {self.acc['id']} '{self.acc.get('name')}': OPEN")
        await self.async_set_cover_position(position=100)

    async def async_close_cover(self, **kwargs):
        """Close the cover."""
        _LOGGER.warning(f"Domestia Cover {self.acc['id']} '{self.acc.get('name')}': CLOSE")
        await self.async_set_cover_position(position=0)

    async def async_stop_cover(self, **kwargs):
        """Stop the cover."""
        _LOGGER.warning(f"Domestia Cover {self.acc['id']} '{self.acc.get('name')}': STOP")
        
        # Send current position to stop (without +128 flag)
        current_pos = self.current_cover_position
        await self.network.send([255, 0, 0, 3, 150, self.acc["id"] + 1, current_pos])
        
        # Request coordinator refresh
        await self.coordinator.async_request_refresh()
