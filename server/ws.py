from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect
from typing import List

class LogBroadcaster:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)

    def disconnect(self, ws: WebSocket):
        # It's important to handle potential ValueError if ws is not in list (e.g. double disconnect)
        try:
            self.connections.remove(ws)
        except ValueError:
            pass # Or log this occurrence

    async def broadcast(self, message: str):
        # Iterate over a copy of the list in case of disconnections during broadcast
        for ws in list(self.connections):
            try:
                await ws.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(ws)
            except RuntimeError as e:
                # Handle cases where websocket might be closed unexpectedly
                print(f"RuntimeError sending to websocket: {e}")
                self.disconnect(ws)

broadcaster = LogBroadcaster() 