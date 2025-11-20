"""Low-level VNC protocol test using Twisted"""
from twisted.internet import reactor, protocol
from twisted.internet.endpoints import TCP4ClientEndpoint
import struct

class VNCProtocol(protocol.Protocol):
    def __init__(self):
        self.state = "INIT"
        self.buffer = b""

    def connectionMade(self):
        print(f"Connected to {self.transport.getPeer()}")

    def dataReceived(self, data):
        self.buffer += data
        print(f"Received {len(data)} bytes in state {self.state}")

        if self.state == "INIT":
            # Expect RFB version string
            if len(self.buffer) >= 12:
                version = self.buffer[:12].decode('ascii', errors='ignore')
                print(f"Server version: {version}")
                self.buffer = self.buffer[12:]

                # Send our version back (RFB 003.003 for simplicity)
                self.transport.write(b"RFB 003.003\n")
                self.state = "AUTH"
                print("Sent client version")

        elif self.state == "AUTH":
            # Check authentication type
            if len(self.buffer) >= 4:
                auth_type = struct.unpack('>I', self.buffer[:4])[0]
                print(f"Authentication type: {auth_type}")

                if auth_type == 0:
                    print("[FAIL] Connection failed (auth type 0)")
                    self.transport.loseConnection()
                elif auth_type == 1:
                    print("[OK] No authentication required")
                    self.state = "INIT_CLIENT"
                    # Send ClientInit (shared flag = 1)
                    self.transport.write(b'\x01')
                    print("Sent ClientInit")
                elif auth_type == 2:
                    print("VNC authentication required (need password)")
                    self.transport.loseConnection()
                else:
                    print(f"Unknown auth type: {auth_type}")
                    self.transport.loseConnection()

                self.buffer = self.buffer[4:]

        elif self.state == "INIT_CLIENT":
            # Expect ServerInit message
            if len(self.buffer) >= 24:  # Minimum ServerInit size
                # Parse framebuffer dimensions
                width = struct.unpack('>H', self.buffer[0:2])[0]
                height = struct.unpack('>H', self.buffer[2:4])[0]
                print(f"[OK] Framebuffer size: {width}x{height}")

                # Parse pixel format
                bits_per_pixel = self.buffer[4]
                depth = self.buffer[5]
                big_endian = self.buffer[6]
                true_color = self.buffer[7]

                if true_color:
                    r_max = struct.unpack('>H', self.buffer[8:10])[0]
                    g_max = struct.unpack('>H', self.buffer[10:12])[0]
                    b_max = struct.unpack('>H', self.buffer[12:14])[0]
                    r_shift = self.buffer[14]
                    g_shift = self.buffer[15]
                    b_shift = self.buffer[16]
                    print(f"[OK] Pixel format: {bits_per_pixel}bpp, depth={depth}, RGB max=({r_max},{g_max},{b_max})")
                else:
                    print(f"[OK] Pixel format: {bits_per_pixel}bpp, depth={depth}, color-mapped")

                # Get desktop name length
                name_length = struct.unpack('>I', self.buffer[20:24])[0]

                if len(self.buffer) >= 24 + name_length:
                    desktop_name = self.buffer[24:24+name_length].decode('ascii', errors='ignore')
                    print(f"[OK] Desktop name: '{desktop_name}'")

                    print("\n[SUCCESS] Successfully connected and received framebuffer info!")
                    print("\nNow requesting a screen update...")

                    # Send FramebufferUpdateRequest
                    # Type=3, incremental=0, x=0, y=0, width, height
                    update_req = struct.pack('>BBHHHH', 3, 0, 0, 0, width, height)
                    self.transport.write(update_req)
                    print("Sent FramebufferUpdateRequest")

                    self.state = "CONNECTED"
                    self.buffer = self.buffer[24+name_length:]

        elif self.state == "CONNECTED":
            print(f"Received {len(self.buffer)} bytes of framebuffer data")
            # In a real implementation, we'd parse framebuffer updates here

    def connectionLost(self, reason):
        print(f"Connection lost: {reason.value}")
        reactor.stop()

class VNCFactory(protocol.ClientFactory):
    def buildProtocol(self, addr):
        return VNCProtocol()

    def clientConnectionFailed(self, connector, reason):
        print(f"Connection failed: {reason.value}")
        reactor.stop()

if __name__ == "__main__":
    import sys

    host = "192.168.4.82"
    port = 5900

    print(f"Connecting to VNC server at {host}:{port}...")

    endpoint = TCP4ClientEndpoint(reactor, host, port, timeout=10)
    d = endpoint.connect(VNCFactory())

    # Run for 15 seconds max
    reactor.callLater(15, reactor.stop)

    reactor.run()
    print("\nTest completed")