"""
Service layer for Fluke 8845A operations
Handles business logic and connection management
"""

from typing import Optional, Dict, Any
from fluke8845a import Fluke8845A


class Fluke8845AService:
    """Service for managing Fluke 8845A operations"""

    def __init__(self):
        self.device: Optional[Fluke8845A] = None
        self.connected: bool = False

    def connect(self, address: str = "ASRL5::INSTR") -> Dict[str, Any]:
        """Connect to Fluke 8845A"""
        try:
            self.device = Fluke8845A(address)
            result = self.device.connect()
            self.connected = result.get("status") == "connected"
            return result
        except Exception as e:
            self.connected = False
            return {
                "status": "error",
                "error": str(e)
            }

    def disconnect(self) -> Dict[str, str]:
        """Disconnect from device"""
        if self.device:
            self.device.disconnect()
            self.device = None
            self.connected = False
        return {"status": "disconnected"}

    def _ensure_connected(self):
        """Ensure device is connected"""
        if not self.connected or not self.device:
            raise ConnectionError("Fluke 8845A not connected. Please connect first.")

    def get_status(self) -> Dict[str, Any]:
        """Get device status"""
        if not self.connected or not self.device:
            return {"connected": False, "message": "Not connected"}
        return self.device.get_status()

    def measure_voltage_dc(self, range_value: Optional[float] = None) -> Dict[str, Any]:
        """Measure DC voltage"""
        self._ensure_connected()
        try:
            value = self.device.measure_dc_voltage(range_value)
            return {
                "measurement_type": "DC Voltage",
                "value": value,
                "unit": "V",
                "range": range_value if range_value else "auto"
            }
        except Exception as e:
            return {"error": str(e)}

    def measure_voltage_ac(self, range_value: Optional[float] = None) -> Dict[str, Any]:
        """Measure AC voltage"""
        self._ensure_connected()
        try:
            value = self.device.measure_ac_voltage(range_value)
            return {
                "measurement_type": "AC Voltage (RMS)",
                "value": value,
                "unit": "V",
                "range": range_value if range_value else "auto"
            }
        except Exception as e:
            return {"error": str(e)}

    def measure_current_dc(self, range_value: Optional[float] = None) -> Dict[str, Any]:
        """Measure DC current"""
        self._ensure_connected()
        try:
            value = self.device.measure_dc_current(range_value)
            return {
                "measurement_type": "DC Current",
                "value": value,
                "unit": "A",
                "range": range_value if range_value else "auto"
            }
        except Exception as e:
            return {"error": str(e)}

    def measure_current_ac(self, range_value: Optional[float] = None) -> Dict[str, Any]:
        """Measure AC current"""
        self._ensure_connected()
        try:
            value = self.device.measure_ac_current(range_value)
            return {
                "measurement_type": "AC Current (RMS)",
                "value": value,
                "unit": "A",
                "range": range_value if range_value else "auto"
            }
        except Exception as e:
            return {"error": str(e)}

    def measure_resistance_2wire(self, range_value: Optional[float] = None) -> Dict[str, Any]:
        """Measure resistance using 2-wire method"""
        self._ensure_connected()
        try:
            value = self.device.measure_resistance_2wire(range_value)
            return {
                "measurement_type": "2-Wire Resistance",
                "value": value,
                "unit": "Ohm",
                "range": range_value if range_value else "auto"
            }
        except Exception as e:
            return {"error": str(e)}

    def measure_resistance_4wire(self, range_value: Optional[float] = None) -> Dict[str, Any]:
        """Measure resistance using 4-wire method"""
        self._ensure_connected()
        try:
            value = self.device.measure_resistance_4wire(range_value)
            return {
                "measurement_type": "4-Wire Resistance",
                "value": value,
                "unit": "Ohm",
                "range": range_value if range_value else "auto"
            }
        except Exception as e:
            return {"error": str(e)}

    def measure_frequency(self, range_value: Optional[float] = None) -> Dict[str, Any]:
        """Measure frequency"""
        self._ensure_connected()
        try:
            value = self.device.measure_frequency(range_value)
            return {
                "measurement_type": "Frequency",
                "value": value,
                "unit": "Hz",
                "range": range_value if range_value else "auto"
            }
        except Exception as e:
            return {"error": str(e)}

    def measure_capacitance(self, range_value: Optional[float] = None) -> Dict[str, Any]:
        """Measure capacitance"""
        self._ensure_connected()
        try:
            value = self.device.measure_capacitance(range_value)
            return {
                "measurement_type": "Capacitance",
                "value": value,
                "unit": "F",
                "range": range_value if range_value else "auto"
            }
        except Exception as e:
            return {"error": str(e)}

    def measure_continuity(self) -> Dict[str, Any]:
        """Measure continuity"""
        self._ensure_connected()
        try:
            value = self.device.measure_continuity()
            return {
                "measurement_type": "Continuity",
                "value": value,
                "unit": "Ohm"
            }
        except Exception as e:
            return {"error": str(e)}

    def measure_diode(self) -> Dict[str, Any]:
        """Measure diode forward voltage"""
        self._ensure_connected()
        try:
            value = self.device.measure_diode()
            return {
                "measurement_type": "Diode",
                "value": value,
                "unit": "V"
            }
        except Exception as e:
            return {"error": str(e)}

    def reset(self) -> Dict[str, str]:
        """Reset device to default state"""
        self._ensure_connected()
        try:
            self.device.reset()
            return {"status": "reset complete"}
        except Exception as e:
            return {"error": str(e)}


# Global service instance
fluke_service = Fluke8845AService()
