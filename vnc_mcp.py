"""
VNC MCP Server using vncdotool
Provides VNC remote control capabilities via Model Context Protocol
"""

import asyncio
import base64
import io
import time
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent

from vncdotool import api

# Global VNC client
vnc_client = None
vnc_host = ""
vnc_port = 5900

app = Server("vnc-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available VNC tools"""
    return [
        Tool(
            name="vnc_connect",
            description="Connect to a VNC server",
            inputSchema={
                "type": "object",
                "properties": {
                    "host": {
                        "type": "string",
                        "description": "VNC server hostname or IP",
                        "default": "192.168.4.82"
                    },
                    "port": {
                        "type": "integer",
                        "description": "VNC server port",
                        "default": 5900
                    },
                    "password": {
                        "type": "string",
                        "description": "VNC password (optional)"
                    }
                }
            }
        ),
        Tool(
            name="vnc_disconnect",
            description="Disconnect from VNC server",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="vnc_screenshot",
            description="Capture screenshot from VNC server",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Filename to save screenshot (optional)"
                    }
                }
            }
        ),
        Tool(
            name="vnc_mouse_move",
            description="Move mouse to absolute position",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate"
                    }
                },
                "required": ["x", "y"]
            }
        ),
        Tool(
            name="vnc_mouse_click",
            description="Click mouse button at position",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate"
                    },
                    "button": {
                        "type": "integer",
                        "description": "Mouse button (1=left, 2=middle, 3=right)",
                        "default": 1
                    }
                },
                "required": ["x", "y"]
            }
        ),
        Tool(
            name="vnc_key_type",
            description="Type text on VNC server",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to type"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="vnc_key_press",
            description="Press a specific key",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Key to press (e.g., 'enter', 'tab', 'escape', 'f1')"
                    }
                },
                "required": ["key"]
            }
        ),
        Tool(
            name="vnc_status",
            description="Get VNC connection status",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent | ImageContent]:
    """Handle tool calls"""
    global vnc_client, vnc_host, vnc_port

    try:
        if name == "vnc_connect":
            host = arguments.get("host", "192.168.4.82")
            port = arguments.get("port", 5900)
            password = arguments.get("password")

            # Disconnect existing connection
            if vnc_client:
                try:
                    vnc_client.disconnect()
                except:
                    pass

            # Connect
            server = f"{host}::{port}"
            vnc_client = api.connect(server, password=password)
            vnc_host = host
            vnc_port = port

            return [TextContent(
                type="text",
                text=f"Connected to VNC server at {host}:{port}"
            )]

        elif name == "vnc_disconnect":
            if vnc_client:
                vnc_client.disconnect()
                vnc_client = None
                return [TextContent(type="text", text="Disconnected from VNC server")]
            else:
                return [TextContent(type="text", text="Not connected to VNC server")]

        elif name == "vnc_screenshot":
            if not vnc_client:
                return [TextContent(type="text", text="Error: Not connected to VNC server")]

            filename = arguments.get("filename", f"screenshot_{int(time.time())}.png")

            # Capture screenshot
            vnc_client.captureScreen(filename)

            # Read and encode as base64
            with open(filename, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            return [
                TextContent(type="text", text=f"Screenshot saved to {filename}"),
                ImageContent(
                    type="image",
                    data=image_data,
                    mimeType="image/png"
                )
            ]

        elif name == "vnc_mouse_move":
            if not vnc_client:
                return [TextContent(type="text", text="Error: Not connected to VNC server")]

            x = arguments["x"]
            y = arguments["y"]
            vnc_client.mouseMove(x, y)

            return [TextContent(type="text", text=f"Mouse moved to ({x}, {y})")]

        elif name == "vnc_mouse_click":
            if not vnc_client:
                return [TextContent(type="text", text="Error: Not connected to VNC server")]

            x = arguments["x"]
            y = arguments["y"]
            button = arguments.get("button", 1)

            vnc_client.mouseMove(x, y)
            vnc_client.mousePress(button)

            return [TextContent(type="text", text=f"Clicked at ({x}, {y}) with button {button}")]

        elif name == "vnc_key_type":
            if not vnc_client:
                return [TextContent(type="text", text="Error: Not connected to VNC server")]

            text = arguments["text"]
            vnc_client.type(text)

            return [TextContent(type="text", text=f"Typed: {text}")]

        elif name == "vnc_key_press":
            if not vnc_client:
                return [TextContent(type="text", text="Error: Not connected to VNC server")]

            key = arguments["key"]
            vnc_client.keyPress(key)

            return [TextContent(type="text", text=f"Pressed key: {key}")]

        elif name == "vnc_status":
            if vnc_client:
                return [TextContent(
                    type="text",
                    text=f"Connected to {vnc_host}:{vnc_port}"
                )]
            else:
                return [TextContent(type="text", text="Not connected")]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {type(e).__name__}: {str(e)}")]


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
