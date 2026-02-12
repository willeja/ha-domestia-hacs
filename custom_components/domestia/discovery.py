import asyncio
from .protocol import CMD_ATRSTYPE, ATRNOMS


# Domestia output types
TOGGLE = 0
RELAIS = 1
TIMER_TOGGLE_MIN = 2
TIMER_TOGGLE_SEC = 3
TIMER_RELANCE_MIN = 4
TIMER_RELANCE_SEC = 5
DIMMER_STOP = 6
DIMMER_CONTINU = 7
VOLET_DESCENTE = 8
VOLET_MONTE = 9
VOLET_UN_BP = 10
RELAIS_CAPTEUR = 11
RGB_R = 12
RGB_G = 13
RGB_B = 14
RGB_W = 15
UNUSED = 255


class DomestiaDiscovery:
    def __init__(self, network):
        self.network = network

    async def load_all(self):
        outputs = await self.load_outputs()
        outputs = await self.load_output_names(outputs)
        return outputs

    # ---------------------------------------------------------
    # LOAD TYPES
    # ---------------------------------------------------------
    async def load_outputs(self):
        result = []

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        def cb(data):
            if not future.done():
                future.set_result(data)

        await self.network.send(CMD_ATRSTYPE, cb)
        data = await future

        if not data or len(data) < 4:
            return result

        count = data[3]

        for i in range(count):
            t = data[4 + i]

            if t in (
                TOGGLE, RELAIS, TIMER_TOGGLE_MIN, TIMER_TOGGLE_SEC,
                TIMER_RELANCE_MIN, TIMER_RELANCE_SEC,
                DIMMER_STOP, DIMMER_CONTINU
            ):
                category = "light"

            elif t in (VOLET_DESCENTE, VOLET_UN_BP):
                category = "cover"
            
            elif t == VOLET_MONTE:
                # VOLET_MONTE (up button) is paired with VOLET_DESCENTE, ignore it
                category = "ignore"

            else:
                category = "ignore"

            result.append({
                "id": i,
                "type": t,
                "category": category,
                "name": None
            })

        return result

    # ---------------------------------------------------------
    # LOAD NAMES
    # ---------------------------------------------------------
    async def load_output_names(self, outputs):
        for acc in outputs:
            if acc["category"] == "ignore":
                continue

            loop = asyncio.get_running_loop()
            future = loop.create_future()

            def cb(data):
                if not future.done():
                    future.set_result(data)

            # ATRNOMS = 62
            # Domestia uses 1-based output numbering
            await self.network.send([255,0,0,2, ATRNOMS, acc["id"] + 1], cb)
            data = await future

            # decode name
            try:
                name = ""
                for b in data[4:]:
                    if b == 255:
                        break
                    name += chr(b)
                name = name.strip()
                if name == "":
                    name = f"Domestia {acc['id']}"
                acc["name"] = name
            except:
                acc["name"] = f"Domestia {acc['id']}"

        return outputs