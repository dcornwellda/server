# VNC MCP Server

An MCP (Model Context Protocol) server that enables Claude to control remote systems via VNC. This server provides tools for screen capture, mouse control, and keyboard input using the vncdotool Python library.

## Features

- **Screen Capture**: Capture and view the current remote screen as an image
- **Mouse Control**: Click and move the mouse at specific coordinates
- **Keyboard Input**: Type text and press special keys
- **Real-time Control**: Direct VNC connection for low-latency interaction

## Installation

1. Navigate to the server directory:
```bash
cd vnc-mcp-server
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

Or install with uv (recommended):
```bash
uv pip install -r requirements.txt
```

## Configuration

Configure the VNC connection using environment variables:

- `VNC_HOST`: VNC server hostname or IP (default: `localhost`)
- `VNC_PORT`: VNC server port (default: `5900`)
- `VNC_PASSWORD`: VNC password (optional)
- `VNC_PROTOCOL`: VNC/RFB protocol version for older servers (optional, e.g., `3.3`, `3.7`, `3.8`)
- `VNC_WIDTH`: Target screen width (default: `480`)
- `VNC_HEIGHT`: Target screen height (default: `272`)

## Usage with Claude Desktop

Add this to your Claude Desktop configuration file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "vnc-controller": {
      "command": "python",
      "args": ["C:\\Users\\dcorn\\Dropbox\\Matt share\\chragetest\\vnc-mcp-server\\server.py"],
      "env": {
        "VNC_HOST": "your-vnc-host",
        "VNC_PORT": "5900",
        "VNC_PASSWORD": "your-password-if-needed",
        "VNC_PROTOCOL": "3.3",
        "VNC_WIDTH": "480",
        "VNC_HEIGHT": "272"
      }
    }
  }
}
```

**Note**: The `VNC_PROTOCOL`, `VNC_WIDTH`, and `VNC_HEIGHT` variables are optional. Use `VNC_PROTOCOL` for older VNC servers that require RFB protocol 3.3 or 3.7.

Or using uv (recommended for better dependency management):

```json
{
  "mcpServers": {
    "vnc-controller": {
      "command": "uv",
      "args": ["--directory", "C:\\Users\\dcorn\\Dropbox\\Matt share\\chragetest\\vnc-mcp-server", "run", "server.py"],
      "env": {
        "VNC_HOST": "your-vnc-host",
        "VNC_PORT": "5900",
        "VNC_PASSWORD": "your-password-if-needed",
        "VNC_PROTOCOL": "3.3",
        "VNC_WIDTH": "480",
        "VNC_HEIGHT": "272"
      }
    }
  }
}
```

Replace the path and environment variables with your actual values.

## Protocol Version Notes

The `VNC_PROTOCOL` setting allows you to specify the RFB (Remote Framebuffer) protocol version for compatibility with older VNC servers:

- **RFB 3.3** - Oldest protocol, most compatible with legacy systems
- **RFB 3.7** - Adds support for more security types
- **RFB 3.8** - Modern protocol (default if not specified)

For embedded systems or older VNC servers (like those on 480x272 displays), using protocol version `3.3` often provides the best compatibility.

## Available Tools

### vnc_capture_screen
Captures the current screen and returns it as a PNG image.

**Parameters**: None

**Example**:
```
Can you show me what's on the VNC screen?
```

### vnc_click
Clicks at specific coordinates on the remote screen.

**Parameters**:
- `x` (number): X coordinate
- `y` (number): Y coordinate
- `button` (number, optional): Mouse button (1=left, 2=middle, 3=right, default=1)

**Example**:
```
Click at position (240, 136) on the VNC screen
```

### vnc_move_mouse
Moves the mouse cursor without clicking.

**Parameters**:
- `x` (number): X coordinate
- `y` (number): Y coordinate

**Example**:
```
Move the mouse to (100, 50)
```

### vnc_type_text
Types text on the remote system.

**Parameters**:
- `text` (string): Text to type

**Example**:
```
Type "Hello World" on the VNC screen
```

### vnc_key_press
Presses special keys on the remote system.

**Parameters**:
- `key` (string): Key name (enter, tab, esc, bsp, del, up, down, left, right, home, end, pgup, pgdn, f1-f12, etc.)

**Example**:
```
Press the enter key on the VNC screen
```

**Common key names**:
- `enter` - Enter/Return key
- `tab` - Tab key
- `esc` - Escape key
- `bsp` - Backspace
- `del` - Delete
- `up`, `down`, `left`, `right` - Arrow keys
- `home`, `end` - Home and End
- `pgup`, `pgdn` - Page Up and Page Down
- `f1` through `f12` - Function keys

## Screen Resolution

This server is configured by default for a 480x272 resolution screen (common for embedded displays and Raspberry Pi touchscreens). You can customize the resolution using the `VNC_WIDTH` and `VNC_HEIGHT` environment variables. The VNC client will automatically detect the actual screen resolution when connecting, but these settings help with coordinate calculations and documentation.

## Troubleshooting

### Connection Issues
- Verify the VNC server is running and accessible
- Check firewall settings allow connections to the VNC port
- Ensure the VNC password (if required) is correct

### Installation Issues
If you encounter installation errors:

**Windows**: Make sure you have Python 3.8 or later installed
```bash
python --version
```

**Linux**: Install Python development packages if needed
```bash
sudo apt-get install python3-dev python3-pip
```

For vncdotool installation issues, you may need Pillow dependencies:
```bash
pip install --upgrade Pillow
```

### Screen Capture Not Working
- The server needs at least one framebuffer update from the VNC server
- Try clicking or typing first to trigger a screen update
- Some VNC servers require specific encoding settings

## Development

To modify the server, edit `server.py`. The server will need to be restarted in Claude Desktop for changes to take effect.

For testing, you can run the server directly:
```bash
python server.py
```

## License

MIT
