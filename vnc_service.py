"""
Service layer for VNC operations
Handles business logic and connection management
"""

from typing import Optional, Dict, Any
from vnc import VNCClient


class VNCService:
    """Service for managing VNC operations"""

    def __init__(self):
        self.client: Optional[VNCClient] = None
        self.connected: bool = False
        self.host: str = ""
        self.port: int = 5900

    def connect(self, host: str = "localhost", port: int = 5900, password: Optional[str] = None) -> Dict[str, Any]:
        """Connect to VNC server"""
        try:
            # Disconnect existing connection if any
            if self.client:
                self.disconnect()

            self.client = VNCClient(host, port, password)
            self.client.connect()
            self.connected = True
            self.host = host
            self.port = port

            return {
                "status": "connected",
                "host": host,
                "port": port
            }
        except Exception as e:
            self.connected = False
            return {
                "status": "error",
                "error": str(e)
            }

    def disconnect(self) -> Dict[str, Any]:
        """Disconnect from VNC server"""
        if self.client:
            self.client.disconnect()
            self.client = None
        self.connected = False

        return {
            "status": "disconnected"
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current connection status"""
        return {
            "connected": self.connected,
            "host": self.host if self.connected else None,
            "port": self.port if self.connected else None
        }

    def screenshot(self) -> Dict[str, Any]:
        """Capture screenshot"""
        if not self.connected:
            return {
                "error": "Not connected to VNC server"
            }

        try:
            # Try to capture with current connection
            if self.client:
                image_base64 = self.client.screenshot_base64()
                return {
                    "status": "success",
                    "image": image_base64,
                    "format": "png",
                    "encoding": "base64"
                }
        except Exception as e:
            # If the current connection fails, try reconnecting and trying again
            # This handles cases where the server doesn't handle multiple requests well
            try:
                # Disconnect the bad connection
                if self.client:
                    self.client.disconnect()
                    self.client = None

                # Create a fresh connection
                new_client = VNCClient(self.host, self.port, None)
                new_client.connect()
                image_base64 = new_client.screenshot_base64()

                # Update the service with the new client
                self.client = new_client
                self.connected = True

                return {
                    "status": "success",
                    "image": image_base64,
                    "format": "png",
                    "encoding": "base64"
                }
            except Exception as reconnect_error:
                self.connected = False
                return {
                    "error": f"Screenshot failed: {str(e)}. Reconnection also failed: {str(reconnect_error)}"
                }

    def mouse_move(self, x: int, y: int) -> Dict[str, Any]:
        """Move mouse to position"""
        if not self.connected or not self.client:
            return {
                "error": "Not connected to VNC server"
            }

        try:
            self.client.mouse_move(x, y)
            return {
                "status": "success",
                "action": "mouse_move",
                "x": x,
                "y": y
            }
        except Exception as e:
            return {
                "error": str(e)
            }

    def mouse_click(self, x: Optional[int] = None, y: Optional[int] = None, button: int = 1) -> Dict[str, Any]:
        """Click mouse at position"""
        if not self.connected or not self.client:
            return {
                "error": "Not connected to VNC server"
            }

        try:
            self.client.mouse_click(x, y, button)
            result = {
                "status": "success",
                "action": "mouse_click",
                "button": button
            }
            if x is not None and y is not None:
                result["x"] = x
                result["y"] = y
            return result
        except Exception as e:
            return {
                "error": str(e)
            }


# Singleton instance
vnc_service = VNCService()
