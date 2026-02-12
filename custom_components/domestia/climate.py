from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature

from .const import DOMAIN


async def async_setup_entry(hass, entry, add_entities):
    """Set up Domestia climate devices."""
    data = hass.data[DOMAIN][entry.entry_id]
    network = data["network"]
    accessories = data["accessories"]

    climates = []

    for acc in accessories:
        # Domestia thermostaat = RELAIS_CAPTEUR (type 11)
        if acc["type"] == 11:
            climates.append(DomestiaClimate(network, acc))

    add_entities(climates)


class DomestiaClimate(ClimateEntity):
    """Representation of a Domestia thermostat."""

    def __init__(self, network, acc):
        self.network = network
        self.acc = acc

        self._hvac_mode = HVACMode.HEAT
        self._target_temp = 20
        self._current_temp = 20

    @property
    def name(self):
        return f"Domestia Thermostat {self.acc['id']}"

    @property
    def unique_id(self):
        return f"domestia_climate_{self.acc['id']}"

    @property
    def temperature_unit(self):
        return UnitOfTemperature.CELSIUS

    @property
    def supported_features(self):
        return ClimateEntityFeature.TARGET_TEMPERATURE

    @property
    def hvac_modes(self):
        return [HVACMode.OFF, HVACMode.HEAT]

    @property
    def hvac_mode(self):
        return self._hvac_mode

    @property
    def current_temperature(self):
        return self._current_temp

    @property
    def target_temperature(self):
        return self._target_temp

    # ---------------------------------------------------------
    # ACTIONS
    # ---------------------------------------------------------
    async def async_set_temperature(self, **kwargs):
        if "temperature" in kwargs:
            self._target_temp = kwargs["temperature"]

            # Domestia expects target temp * 2
            value = round(self._target_temp * 2)

            await self.network.send([
                255,0,0,3,
                58,  # ATWTEMPMODE
                self.acc["id"] + 1,
                value
            ])

        self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode):
        self._hvac_mode = hvac_mode

        if hvac_mode == HVACMode.OFF:
            # Domestia: CHAUD_VEROUILLE (2)
            await self.network.send([
                255,0,0,3,
                85,  # ATWCAPTEURMODE
                self.acc["id"] + 1,
                2
            ])
        else:
            # Domestia: CHAUD_AUTO (0)
            await self.network.send([
                255,0,0,3,
                85,
                self.acc["id"] + 1,
                0
            ])

        self.async_write_ha_state()