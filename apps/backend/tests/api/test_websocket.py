import pytest
import json
from unittest.mock import MagicMock, AsyncMock
from app.websocket.manager import ConnectionManager


@pytest.mark.asyncio
async def test_connect_and_send():
    manager = ConnectionManager()
    mock_ws = MagicMock()
    mock_ws.accept = AsyncMock()
    mock_ws.send_text = AsyncMock()

    await manager.connect(mock_ws, "proj-1")
    await manager.send_to_project("proj-1", {"stage": "transcribing", "progress": 50})

    mock_ws.accept.assert_awaited_once()
    mock_ws.send_text.assert_awaited_once_with(
        json.dumps({"stage": "transcribing", "progress": 50})
    )


@pytest.mark.asyncio
async def test_disconnect_removes_connection():
    manager = ConnectionManager()
    mock_ws = MagicMock()
    mock_ws.accept = AsyncMock()
    mock_ws.send_text = AsyncMock()
    await manager.connect(mock_ws, "proj-1")
    manager.disconnect(mock_ws, "proj-1")
    await manager.send_to_project("proj-1", {"stage": "completed"})
    # after disconnect, no send should happen
    assert mock_ws.send_text.call_count == 0


@pytest.mark.asyncio
async def test_send_to_unknown_project():
    manager = ConnectionManager()
    # should not raise
    await manager.send_to_project("unknown", {"stage": "completed"})


@pytest.mark.asyncio
async def test_send_removes_dead_connection():
    manager = ConnectionManager()
    dead_ws = MagicMock()
    dead_ws.send_text = AsyncMock(side_effect=Exception("disconnected"))
    manager._connections["proj-1"] = [dead_ws]
    await manager.send_to_project("proj-1", {"stage": "failed"})
    assert dead_ws not in manager._connections.get("proj-1", [])
