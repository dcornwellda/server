"""Read-only VNC connection test using vncdotool internals"""

from vncdotool.client import VNCDoToolClient
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from twisted.internet.defer import Deferred
import time

class ReadOnlyVNCFactory(ClientFactory):
    protocol = VNCDoToolClient

    def __init__(self):
        self.deferred = Deferred()
        self.client = None

    def buildProtocol(self, addr):
        print(f"Building protocol for {addr}")
        self.client = ClientFactory.buildProtocol(self, addr)
        self.client.factory = self
        return self.client

    def clientConnectionMade(self, client):
        print("Connection made!")
        # Don't request screen updates
        # Just get basic info after handshake
        reactor.callLater(2, self.check_client_state)

    def check_client_state(self):
        if self.client:
            try:
                print(f"Client state: {self.client.state}")
                if hasattr(self.client, 'width'):
                    print(f"Screen: {self.client.width}x{self.client.height}")
                if hasattr(self.client, 'name'):
                    print(f"Desktop: {self.client.name}")
                if hasattr(self.client, 'pixel_format'):
                    print(f"Format: {self.client.pixel_format}")
            except Exception as e:
                print(f"Error accessing client state: {e}")

        # Disconnect after checking
        reactor.callLater(1, reactor.stop)

    def clientConnectionLost(self, connector, reason):
        print(f"Connection lost: {reason.value}")

    def clientConnectionFailed(self, connector, reason):
        print(f"Connection failed: {reason.value}")
        reactor.stop()


def test_readonly():
    host = "192.168.4.82"
    port = 5900

    print(f"Connecting to {host}:{port} in read-only mode...")

    factory = ReadOnlyVNCFactory()
    reactor.connectTCP(host, port, factory, timeout=10)

    # Run reactor for max 10 seconds
    reactor.callLater(10, reactor.stop)
    reactor.run()

    print("\nTest completed")


if __name__ == "__main__":
    test_readonly()