from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, run_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[run_id].add(websocket)

    def disconnect(self, run_id: int, websocket: WebSocket) -> None:
        if run_id in self.connections:
            self.connections[run_id].discard(websocket)
            if not self.connections[run_id]:
                self.connections.pop(run_id, None)

    async def broadcast(self, run_id: int, payload: dict) -> None:
        dead: list[WebSocket] = []
        for ws in self.connections.get(run_id, set()):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)

        for ws in dead:
            self.disconnect(run_id, ws)
