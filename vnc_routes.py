"""
API endpoints for VNC remote control
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional
from vnc_service import vnc_service

router = APIRouter(prefix="/vnc", tags=["VNC Remote Control"])


class ConnectionRequest(BaseModel):
    """Request model for VNC connection"""
    host: str = Field(
        default="192.168.4.82",
        description="VNC server hostname or IP address"
    )
    port: int = Field(
        default=5900,
        description="VNC server port"
    )
    password: Optional[str] = Field(
        default=None,
        description="VNC password (if required)"
    )


class MouseMoveRequest(BaseModel):
    """Request model for mouse move"""
    x: int = Field(description="X coordinate")
    y: int = Field(description="Y coordinate")


class MouseClickRequest(BaseModel):
    """Request model for mouse click"""
    x: Optional[int] = Field(
        default=None,
        description="X coordinate (None to click at current position)"
    )
    y: Optional[int] = Field(
        default=None,
        description="Y coordinate (None to click at current position)"
    )
    button: int = Field(
        default=1,
        description="Mouse button (1=left, 2=middle, 3=right)"
    )


@router.post("/connect")
async def connect(request: ConnectionRequest = ConnectionRequest()):
    """
    Connect to VNC server

    - **host**: VNC server hostname or IP (default: localhost)
    - **port**: VNC server port (default: 5900)
    - **password**: VNC password if required
    """
    result = vnc_service.connect(request.host, request.port, request.password)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


@router.post("/disconnect")
async def disconnect():
    """Disconnect from VNC server"""
    return vnc_service.disconnect()


@router.get("/status")
async def get_status():
    """Get VNC connection status"""
    return vnc_service.get_status()


@router.post("/screenshot")
async def screenshot():
    """
    Capture screenshot from VNC server

    Returns base64 encoded PNG image
    """
    result = vnc_service.screenshot()
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/screenshot/raw")
async def screenshot_raw():
    """
    Capture screenshot and return as raw PNG image

    Returns PNG image directly (for viewing in browser)
    """
    result = vnc_service.screenshot()
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    # Decode base64 image and return as PNG
    import base64
    image_bytes = base64.b64decode(result["image"])
    return Response(content=image_bytes, media_type="image/png")


@router.post("/mouse/move")
async def mouse_move(request: MouseMoveRequest):
    """
    Move mouse to absolute position

    - **x**: X coordinate
    - **y**: Y coordinate
    """
    result = vnc_service.mouse_move(request.x, request.y)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/mouse/click")
async def mouse_click(request: MouseClickRequest = MouseClickRequest()):
    """
    Click mouse button

    - **x**: X coordinate (optional, None for current position)
    - **y**: Y coordinate (optional, None for current position)
    - **button**: Mouse button (1=left, 2=middle, 3=right)
    """
    result = vnc_service.mouse_click(request.x, request.y, request.button)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result
