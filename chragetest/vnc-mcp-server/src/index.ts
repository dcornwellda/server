#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { RfbClient } from "rfb2";
import sharp from "sharp";
import { EventEmitter } from "events";

interface VNCConfig {
  host: string;
  port: number;
  password?: string;
}

class VNCController extends EventEmitter {
  private client: any = null;
  private connected: boolean = false;
  private screenBuffer: Buffer | null = null;
  private screenWidth: number = 480;
  private screenHeight: number = 272;
  private config: VNCConfig;
  private lastFrameUpdate: number = 0;
  private connectionReady: boolean = false;

  constructor(config: VNCConfig) {
    super();
    this.config = config;
  }

  async connect(): Promise<void> {
    if (this.connected) {
      return;
    }

    return new Promise((resolve, reject) => {
      try {
        const options: any = {
          host: this.config.host,
          port: this.config.port,
        };

        if (this.config.password) {
          options.password = this.config.password;
        }

        this.client = RfbClient(options);

        this.client.on("connect", () => {
          this.connected = true;
          console.error("VNC connected");
        });

        this.client.on("rect", (rect: any) => {
          // rfb2 provides rect updates with decoded data
          if (!this.connectionReady) {
            this.connectionReady = true;
            console.error("VNC first frame received");
            resolve();
          }
          this.lastFrameUpdate = Date.now();
        });

        this.client.on("*", () => {
          // This catches the initial connection setup
          if (!this.screenWidth || !this.screenHeight) {
            if (this.client.width && this.client.height) {
              this.screenWidth = this.client.width;
              this.screenHeight = this.client.height;
              console.error(`VNC screen size: ${this.screenWidth}x${this.screenHeight}`);
            }
          }
        });

        this.client.on("error", (error: Error) => {
          console.error("VNC error:", error);
          this.connected = false;
          if (!this.connectionReady) {
            reject(error);
          }
        });

        this.client.on("close", () => {
          console.error("VNC connection closed");
          this.connected = false;
          this.connectionReady = false;
        });

        // Set a timeout for initial connection
        setTimeout(() => {
          if (!this.connectionReady) {
            reject(new Error("VNC connection timeout"));
          }
        }, 10000);
      } catch (error) {
        reject(error);
      }
    });
  }

  async ensureConnected(): Promise<void> {
    if (!this.connected) {
      await this.connect();
    }
  }

  async captureScreen(): Promise<string> {
    await this.ensureConnected();

    return new Promise((resolve, reject) => {
      try {
        // Get the current framebuffer from rfb2
        const fb = this.client.fb;
        if (!fb) {
          reject(new Error("No framebuffer available"));
          return;
        }

        // Get screen dimensions
        const width = this.client.width || this.screenWidth;
        const height = this.client.height || this.screenHeight;

        // rfb2 provides the framebuffer as a buffer with RGB data
        // The buffer is in BGRA format (Blue, Green, Red, Alpha)
        const fbBuffer = fb;
        const pixels = new Uint8Array(width * height * 4);

        // Convert from BGRA to RGBA
        for (let i = 0; i < fbBuffer.length; i += 4) {
          pixels[i] = fbBuffer[i + 2];     // R (from B position)
          pixels[i + 1] = fbBuffer[i + 1]; // G
          pixels[i + 2] = fbBuffer[i];     // B (from R position)
          pixels[i + 3] = 255;             // A (fully opaque)
        }

        // Convert to PNG
        sharp(Buffer.from(pixels), {
          raw: {
            width: width,
            height: height,
            channels: 4,
          },
        })
          .png()
          .toBuffer()
          .then((pngBuffer) => {
            const base64Image = pngBuffer.toString("base64");
            resolve(base64Image);
          })
          .catch(reject);
      } catch (error) {
        reject(error);
      }
    });
  }

  async click(x: number, y: number, button: number = 1): Promise<void> {
    await this.ensureConnected();

    // Move mouse to position
    this.client.sendPointer(x, y, 0);
    await new Promise((resolve) => setTimeout(resolve, 10));

    // Press button (button mask: 1=left, 2=middle, 4=right)
    this.client.sendPointer(x, y, button);
    await new Promise((resolve) => setTimeout(resolve, 50));

    // Release button
    this.client.sendPointer(x, y, 0);
  }

  async moveMouse(x: number, y: number): Promise<void> {
    await this.ensureConnected();
    this.client.sendPointer(x, y, 0);
  }

  async typeText(text: string): Promise<void> {
    await this.ensureConnected();

    for (const char of text) {
      const keyCode = char.charCodeAt(0);
      this.client.sendKey(keyCode, true); // Key down
      await new Promise((resolve) => setTimeout(resolve, 10));
      this.client.sendKey(keyCode, false); // Key up
      await new Promise((resolve) => setTimeout(resolve, 10));
    }
  }

  async keyPress(key: string): Promise<void> {
    await this.ensureConnected();

    // Map common key names to keycodes (X11 keysyms)
    const keyMap: Record<string, number> = {
      enter: 0xff0d,
      return: 0xff0d,
      tab: 0xff09,
      escape: 0xff1b,
      esc: 0xff1b,
      backspace: 0xff08,
      delete: 0xffff,
      up: 0xff52,
      down: 0xff54,
      left: 0xff51,
      right: 0xff53,
      home: 0xff50,
      end: 0xff57,
      pageup: 0xff55,
      pagedown: 0xff56,
    };

    const keyCode = keyMap[key.toLowerCase()] || key.charCodeAt(0);
    this.client.sendKey(keyCode, true); // Key down
    await new Promise((resolve) => setTimeout(resolve, 50));
    this.client.sendKey(keyCode, false); // Key up
  }

  disconnect(): void {
    if (this.client) {
      this.client.end();
      this.connected = false;
      this.connectionReady = false;
    }
  }
}

// Create VNC controller
const vncConfig: VNCConfig = {
  host: process.env.VNC_HOST || "localhost",
  port: parseInt(process.env.VNC_PORT || "5900"),
  password: process.env.VNC_PASSWORD,
};

const vncController = new VNCController(vncConfig);

// Create MCP server
const server = new Server(
  {
    name: "vnc-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define available tools
const tools: Tool[] = [
  {
    name: "vnc_capture_screen",
    description:
      "Captures the current screen from the VNC connection and returns it as a base64-encoded PNG image. Use this to see what's currently displayed on the remote screen.",
    inputSchema: {
      type: "object",
      properties: {},
      required: [],
    },
  },
  {
    name: "vnc_click",
    description:
      "Clicks at the specified coordinates on the remote screen. Button 1 is left click, 2 is middle, 4 is right click.",
    inputSchema: {
      type: "object",
      properties: {
        x: {
          type: "number",
          description: "X coordinate (0-479 for 480px width)",
        },
        y: {
          type: "number",
          description: "Y coordinate (0-271 for 272px height)",
        },
        button: {
          type: "number",
          description: "Mouse button (1=left, 2=middle, 4=right). Default is 1.",
          default: 1,
        },
      },
      required: ["x", "y"],
    },
  },
  {
    name: "vnc_move_mouse",
    description: "Moves the mouse cursor to the specified coordinates without clicking.",
    inputSchema: {
      type: "object",
      properties: {
        x: {
          type: "number",
          description: "X coordinate",
        },
        y: {
          type: "number",
          description: "Y coordinate",
        },
      },
      required: ["x", "y"],
    },
  },
  {
    name: "vnc_type_text",
    description: "Types the specified text on the remote system.",
    inputSchema: {
      type: "object",
      properties: {
        text: {
          type: "string",
          description: "Text to type",
        },
      },
      required: ["text"],
    },
  },
  {
    name: "vnc_key_press",
    description:
      "Presses a special key on the remote system. Supports: enter, tab, escape, backspace, delete, up, down, left, right, home, end, pageup, pagedown.",
    inputSchema: {
      type: "object",
      properties: {
        key: {
          type: "string",
          description: "Key name to press",
        },
      },
      required: ["key"],
    },
  },
];

// Handle list tools request
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const { name, arguments: args } = request.params;

    switch (name) {
      case "vnc_capture_screen": {
        const base64Image = await vncController.captureScreen();
        return {
          content: [
            {
              type: "image",
              data: base64Image,
              mimeType: "image/png",
            },
          ],
        };
      }

      case "vnc_click": {
        const x = args?.x as number;
        const y = args?.y as number;
        const button = (args?.button as number) || 1;

        if (x === undefined || y === undefined) {
          throw new Error("x and y coordinates are required");
        }

        await vncController.click(x, y, button);
        return {
          content: [
            {
              type: "text",
              text: `Clicked at (${x}, ${y}) with button ${button}`,
            },
          ],
        };
      }

      case "vnc_move_mouse": {
        const x = args?.x as number;
        const y = args?.y as number;

        if (x === undefined || y === undefined) {
          throw new Error("x and y coordinates are required");
        }

        await vncController.moveMouse(x, y);
        return {
          content: [
            {
              type: "text",
              text: `Moved mouse to (${x}, ${y})`,
            },
          ],
        };
      }

      case "vnc_type_text": {
        const text = args?.text as string;

        if (!text) {
          throw new Error("text is required");
        }

        await vncController.typeText(text);
        return {
          content: [
            {
              type: "text",
              text: `Typed: ${text}`,
            },
          ],
        };
      }

      case "vnc_key_press": {
        const key = args?.key as string;

        if (!key) {
          throw new Error("key is required");
        }

        await vncController.keyPress(key);
        return {
          content: [
            {
              type: "text",
              text: `Pressed key: ${key}`,
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return {
      content: [
        {
          type: "text",
          text: `Error: ${errorMessage}`,
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("VNC MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
