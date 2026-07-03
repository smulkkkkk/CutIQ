import json
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_id: str) -> None:
        await websocket.accept()
        self._connections.setdefault(project_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, project_id: str) -> None:
        connections = self._connections.get(project_id, [])
        if websocket in connections:
            connections.remove(websocket)

    async def send_to_project(self, project_id: str, event: dict) -> None:
        for ws in list(self._connections.get(project_id, [])):
            try:
                await ws.send_text(json.dumps(event))
            except Exception:
                self.disconnect(ws, project_id)


ws_manager = ConnectionManager()
