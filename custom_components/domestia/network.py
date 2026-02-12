import asyncio
from .protocol import build_crc
from .const import PORT_TCP


class DomestiaNetwork:
    def __init__(self, ip, mac):
        self.ip = ip
        self.mac = mac.upper().replace("-", ":")
        self.reader = None
        self.writer = None

        self.request_id = 0
        self.callbacks = {}
        self._connected = False

    # ---------------------------------------------------------
    # CONNECTIE
    # ---------------------------------------------------------
    async def connect(self):
        await self._open_connection()
        asyncio.create_task(self._listen_loop())

    async def _open_connection(self):
        self.reader, self.writer = await asyncio.open_connection(self.ip, PORT_TCP)
        self._connected = True

    async def _reconnect(self):
        self._connected = False
        try:
            if self.writer:
                self.writer.close()
        except:
            pass

        await asyncio.sleep(1)
        await self._open_connection()

    # ---------------------------------------------------------
    # LISTENER LOOP
    # ---------------------------------------------------------
    async def _listen_loop(self):
        """Continuously read data from Domestia without blocking HA."""
        while True:
            try:
                # Timeout so HA can shut down cleanly
                data = await asyncio.wait_for(self.reader.read(1024), timeout=5)

                # Empty read = Domestia closed connection
                if not data:
                    await self._reconnect()
                    continue

                self._handle_incoming(list(data))

            except asyncio.TimeoutError:
                # No data received → normal, Domestia only replies on request
                continue

            except Exception:
                # Any other error → reconnect
                await self._reconnect()

    # ---------------------------------------------------------
    # CALLBACK HANDLING
    # ---------------------------------------------------------
    def _handle_incoming(self, data):
        if len(data) == 0:
            return

        req_id = data[-1]
        callback = self.callbacks.pop(req_id, None)

        if callback:
            payload = data[:-1]
            result = callback(payload)
            if asyncio.iscoroutine(result):
                asyncio.create_task(result)

    # ---------------------------------------------------------
    # SEND COMMAND
    # ---------------------------------------------------------
    async def send(self, values, callback=None):
        if not self._connected:
            await self._reconnect()

        self.request_id = (self.request_id + 1) % 255

        if callback:
            self.callbacks[self.request_id] = callback

        frame = values.copy()
        crc = build_crc(frame)
        frame.append(crc)
        frame.append(self.request_id)

        try:
            self.writer.write(bytes(frame))
            await self.writer.drain()
        except Exception:
            await self._reconnect()

    # ---------------------------------------------------------
    # READ RELAY STATUS
    # ---------------------------------------------------------
    async def read_relais_status(self, callback):
        frame = [255,0,0,1,156]  # ATRRELAIS
        await self.send(frame, callback)