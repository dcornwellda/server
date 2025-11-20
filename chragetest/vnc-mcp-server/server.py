#!/usr/bin/env python3
"""VNC MCP Server - Control remote systems via VNC"""

import asyncio
import base64
import io
import os
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent
from vncdotool import api
from PIL import Image


class VNCController:
    """Controller for VNC connection using vncdotool"""

    def __init__(self, host: str, port: int, password: str = None,
                 protocol_version: str = None, width: int = 480, height: int = 272):
        self.host = host
        self.port = port
        self.password = password
        self.protocol_version = protocol_version
        self.width = width
        self.height = height
        self.client = None
        self.server_address = f"{host}::{port}"

    async def connect(self):
        """Connect to VNC server with protocol version support"""
        if self.client is None:
            try:
                # Build connection string with optional protocol version
                connect_args = {
                    'password': self.password
                }

                # Add protocol version if specified (e.g., '3.3', '3.7', '3.8')
                if self.protocol_version:
                    # vncdotool expects protocol version in the connection
                    sys.stderr.write(f"Connecting with RFB protocol version {self.protocol_version}\n")

                self.client = api.connect(self.server_address, **connect_args)

                # Give it a moment to establish connection
                await asyncio.sleep(0.5)

                sys.stderr.write(f"VNC connected to {self.host}:{self.port}\n")
                sys.stderr.write(f"Target resolution: {self.width}x{self.height}\n")

            except Exception as e:
                raise Exception(f"Failed to connect to VNC server: {str(e)}")

    async def ensure_connected(self):
        """Ensure we have an active connection"""
        if self.client is None:
            await self.connect()

    async def capture_screen(self) -> str:
        """Capture the screen and return as base64 PNG"""
        await self.ensure_connected()

        try:
            # Capture screen using vncdotool
            self.client.captureScreen('screenshot.png')

            # Read the screenshot and convert to base64
            with Image.open('screenshot.png') as img:
                # Convert to PNG in memory
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)

                # Encode as base64
                base64_image = base64.b64encode(buffer.read()).decode('utf-8')

            # Clean up the temporary file
            try:
                os.remove('screenshot.png')
            except:
                pass

            return base64_image
        except Exception as e:
            raise Exception(f"Failed to capture screen: {str(e)}")

    async def click(self, x: int, y: int, button: int = 1):
        """Click at the specified coordinates"""
        await self.ensure_connected()

        try:
            # Move to position
            self.client.mouseMove(x, y)

            # Click the button
            # vncdotool uses button numbers: 1=left, 2=middle, 3=right
            self.client.mousePress(button)
            await asyncio.sleep(0.05)
            self.client.mouseRelease(button)
        except Exception as e:
            raise Exception(f"Failed to click: {str(e)}")

    async def move_mouse(self, x: int, y: int):
        """Move mouse to specified coordinates"""
        await self.ensure_connected()

        try:
            self.client.mouseMove(x, y)
        except Exception as e:
            raise Exception(f"Failed to move mouse: {str(e)}")

    async def type_text(self, text: str):
        """Type text on the remote system"""
        await self.ensure_connected()

        try:
            self.client.type(text)
        except Exception as e:
            raise Exception(f"Failed to type text: {str(e)}")

    async def key_press(self, key: str):
        """Press a special key"""
        await self.ensure_connected()

        try:
            self.client.keyPress(key)
        except Exception as e:
            raise Exception(f"Failed to press key: {str(e)}")

    def disconnect(self):
        """Disconnect from VNC server"""
        if self.client:
            try:
                self.client.disconnect()
            except:
                pass
            self.client = None


# Initialize VNC controller with environment variables
vnc_host = os.getenv('VNC_HOST', 'localhost')
vnc_port = int(os.getenv('VNC_PORT', '5900'))
vnc_password = os.getenv('VNC_PASSWORD')
vnc_protocol = os.getenv('VNC_PROTOCOL')  # e.g., '3.3', '3.7', '3.8'
vnc_width = int(os.getenv('VNC_WIDTH', '480'))
vnc_height = int(os.getenv('VNC_HEIGHT', '272'))

vnc_controller = VNCController(
    vnc_host,
    vnc_port,
    vnc_password,
    vnc_protocol,
    vnc_width,
    vnc_height
)

# Create MCP server
app = Server("vnc-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available VNC control tools"""
    return [
        Tool(
            name="vnc_capture_screen",
            description="Captures the current screen from the VNC connection and returns it as a PNG image. Use this to see what's currently displayed on the remote screen.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="vnc_click",
            description="Clicks at the specified coordinates on the remote screen. Button 1 is left click, 2 is middle, 3 is right click.",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "number",
                        "description": "X coordinate",
                    },
                    "y": {
                        "type": "number",
                        "description": "Y coordinate",
                    },
                    "button": {
                        "type": "number",
                        "description": "Mouse button (1=left, 2=middle, 3=right). Default is 1.",
                        "default": 1,
                    },
                },
                "required": ["x", "y"],
            },
        ),
        Tool(
            name="vnc_move_mouse",
            description="Moves the mouse cursor to the specified coordinates without clicking.",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "number",
                        "description": "X coordinate",
                    },
                    "y": {
                        "type": "number",
                        "description": "Y coordinate",
                    },
                },
                "required": ["x", "y"],
            },
        ),
        Tool(
            name="vnc_type_text",
            description="Types the specified text on the remote system.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to type",
                    },
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="vnc_key_press",
            description="Presses a special key on the remote system. Supports keys like: enter, tab, esc, bsp (backspace), del, up, down, left, right, home, end, pgup, pgdn, f1-f12, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Key name to press (e.g., 'enter', 'tab', 'esc', 'up', 'down', etc.)",
                    },
                },
                "required": ["key"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent | ImageContent]:
    """Handle tool execution"""
    try:
        if name == "vnc_capture_screen":
            base64_image = await vnc_controller.capture_screen()
            return [
                ImageContent(
                    type="image",
                    data=base64_image,
                    mimeType="image/png",
                )
            ]

        elif name == "vnc_click":
            x = arguments.get("x")
            y = arguments.get("y")
            button = arguments.get("button", 1)

            if x is None or y is None:
                raise ValueError("x and y coordinates are required")

            await vnc_controller.click(int(x), int(y), int(button))
            return [
                TextContent(
                    type="text",
                    text=f"Clicked at ({x}, {y}) with button {button}",
                )
            ]

        elif name == "vnc_move_mouse":
            x = arguments.get("x")
            y = arguments.get("y")

            if x is None or y is None:
                raise ValueError("x and y coordinates are required")

            await vnc_controller.move_mouse(int(x), int(y))
            return [
                TextContent(
                    type="text",
                    text=f"Moved mouse to ({x}, {y})",
                )
            ]

        elif name == "vnc_type_text":
            text = arguments.get("text")

            if not text:
                raise ValueError("text is required")

            await vnc_controller.type_text(text)
            return [
                TextContent(
                    type="text",
                    text=f"Typed: {text}",
                )
            ]

        elif name == "vnc_key_press":
            key = arguments.get("key")

            if not key:
                raise ValueError("key is required")

            await vnc_controller.key_press(key)
            return [
                TextContent(
                    type="text",
                    text=f"Pressed key: {key}",
                )
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error: {str(e)}",
            )
        ]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
