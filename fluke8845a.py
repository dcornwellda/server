"""
Fluke 8845A Digital Multimeter Driver

Supports DC/AC voltage, DC/AC current, 2-wire and 4-wire resistance,
frequency, and capacitance measurements.
Communicates via RS-232 (serial) using pyserial directly.
"""

import serial
from typing import Optional, Dict, Any
import time


class Fluke8845A:
    """Driver for Fluke 8845A 6.5-Digit Precision Multimeter"""

    def __init__(self, com_port: str = "COM5"):
        """
        Initialize connection to Fluke 8845A

        Args:
            com_port: COM port name (e.g., "COM5")
        """
        self.com_port = com_port
        self.serial: Optional[serial.Serial] = None

    def connect(self) -> Dict[str, Any]:
        """
        Connect to the instrument

        Returns:
            Dictionary with connection status and instrument info
        """
        try:
            # Open serial connection
            self.serial = serial.Serial(
                port=self.com_port,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=10,  # 10 second timeout for measurements
                write_timeout=2
            )

            # Wait for port to stabilize
            time.sleep(0.2)

            # Clear any existing data in buffers
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()

            # Enable remote mode (required for RS-232 measurements)
            self._write("SYST:REM")
            time.sleep(0.2)

            # Clear any errors
            self._write("*CLS")
            time.sleep(0.1)

            # Get instrument identification
            idn = self._query("*IDN?")

            return {
                "status": "connected",
                "address": self.com_port,
                "identification": idn
            }
        except Exception as e:
            return {
                "status": "error",
                "address": self.com_port,
                "error": str(e)
            }

    def disconnect(self):
        """Close connection to instrument"""
        if self.serial and self.serial.is_open:
            self.serial.close()

    def _write(self, command: str):
        """Write command to instrument"""
        if not self.serial or not self.serial.is_open:
            raise ConnectionError("Not connected to instrument")
        self.serial.write(f"{command}\r".encode('ascii'))
        self.serial.flush()

    def _read(self) -> str:
        """Read response from instrument"""
        if not self.serial or not self.serial.is_open:
            raise ConnectionError("Not connected to instrument")
        response = self.serial.read_until(b'\r').decode('ascii').strip()
        return response

    def _query(self, command: str) -> str:
        """Write command and read response"""
        self._write(command)
        time.sleep(0.1)  # Small delay for instrument to process
        return self._read()

    def get_identification(self) -> str:
        """Get instrument identification string"""
        if not self.serial or not self.serial.is_open:
            raise ConnectionError("Not connected to instrument")
        return self._query("*IDN?")

    def reset(self):
        """Reset instrument to default state"""
        if not self.serial or not self.serial.is_open:
            raise ConnectionError("Not connected to instrument")
        self._write("*RST")
        time.sleep(0.5)

    def measure_dc_voltage(self, range_value: Optional[float] = None, resolution: Optional[float] = None) -> float:
        """
        Measure DC voltage

        Args:
            range_value: Voltage range in volts (None for auto-range)
                        Valid ranges: 0.1, 1, 10, 100, 1000
            resolution: Resolution in volts (None for default)

        Returns:
            Measured voltage in volts
        """
        if not self.serial or not self.serial.is_open:
            raise ConnectionError("Not connected to instrument")

        if range_value and resolution:
            cmd = f"MEAS:VOLT:DC? {range_value},{resolution}"
        elif range_value:
            cmd = f"MEAS:VOLT:DC? {range_value}"
        else:
            cmd = "MEAS:VOLT:DC?"

        result = self._query(cmd)
        return float(result)

    def measure_ac_voltage(self, range_value: Optional[float] = None, resolution: Optional[float] = None) -> float:
        """
        Measure AC voltage

        Args:
            range_value: Voltage range in volts (None for auto-range)
                        Valid ranges: 0.1, 1, 10, 100, 750
            resolution: Resolution in volts (None for default)

        Returns:
            Measured voltage in volts RMS
        """
        if not self.serial or not self.serial.is_open:
            raise ConnectionError("Not connected to instrument")

        if range_value and resolution:
            cmd = f"MEAS:VOLT:AC? {range_value},{resolution}"
        elif range_value:
            cmd = f"MEAS:VOLT:AC? {range_value}"
        else:
            cmd = "MEAS:VOLT:AC?"

        result = self._query(cmd)
        return float(result)

    def measure_dc_current(self, range_value: Optional[float] = None, resolution: Optional[float] = None) -> float:
        """
        Measure DC current

        Args:
            range_value: Current range in amps (None for auto-range)
                        Valid ranges: 0.0001, 0.001, 0.01, 0.1, 1, 3 (8845A) or 10 (8846A)
            resolution: Resolution in amps (None for default)

        Returns:
            Measured current in amps
        """
        if not self.serial or not self.serial.is_open:
            raise ConnectionError("Not connected to instrument")

        if range_value and resolution:
            cmd = f"MEAS:CURR:DC? {range_value},{resolution}"
        elif range_value:
            cmd = f"MEAS:CURR:DC? {range_value}"
        else:
            cmd = "MEAS:CURR:DC?"

        result = self._query(cmd)
        return float(result)

    def measure_ac_current(self, range_value: Optional[float] = None, resolution: Optional[float] = None) -> float:
        """
        Measure AC current

        Args:
            range_value: Current range in amps (None for auto-range)
                        Valid ranges: 0.001, 0.01, 0.1, 1, 3
            resolution: Resolution in amps (None for default)

        Returns:
            Measured current in amps RMS
        """
        if not self.serial or not self.serial.is_open:
            raise ConnectionError("Not connected to instrument")

        if range_value and resolution:
            cmd = f"MEAS:CURR:AC? {range_value},{resolution}"
        elif range_value:
            cmd = f"MEAS:CURR:AC? {range_value}"
        else:
            cmd = "MEAS:CURR:AC?"

        result = self._query(cmd)
        return float(result)

    def measure_resistance_2wire(self, range_value: Optional[float] = None, resolution: Optional[float] = None) -> float:
        """
        Measure resistance using 2-wire method

        Args:
            range_value: Resistance range in ohms (None for auto-range)
                        Valid ranges: 100, 1000, 10000, 100000, 1000000, 10000000, 100000000
            resolution: Resolution in ohms (None for default)

        Returns:
            Measured resistance in ohms
        """
        if not self.serial or not self.serial.is_open:
            raise ConnectionError("Not connected to instrument")

        if range_value and resolution:
            cmd = f"MEAS:RES? {range_value},{resolution}"
        elif range_value:
            cmd = f"MEAS:RES? {range_value}"
        else:
            cmd = "MEAS:RES?"

        result = self._query(cmd)
        return float(result)

    def measure_resistance_4wire(self, range_value: Optional[float] = None, resolution: Optional[float] = None) -> float:
        """
        Measure resistance using 4-wire method (more accurate for low resistances)

        Args:
            range_value: Resistance range in ohms (None for auto-range)
                        Valid ranges: 100, 1000, 10000, 100000, 1000000, 10000000, 100000000
            resolution: Resolution in ohms (None for default)

        Returns:
            Measured resistance in ohms
        """
        if not self.serial or not self.serial.is_open:
            raise ConnectionError("Not connected to instrument")

        if range_value and resolution:
            cmd = f"MEAS:FRES? {range_value},{resolution}"
        elif range_value:
            cmd = f"MEAS:FRES? {range_value}"
        else:
            cmd = "MEAS:FRES?"

        result = self._query(cmd)
        return float(result)

    def measure_frequency(self, range_value: Optional[float] = None, resolution: Optional[float] = None) -> float:
        """
        Measure frequency

        Args:
            range_value: Expected voltage range for signal (None for auto)
            resolution: Resolution in Hz (None for default)

        Returns:
            Measured frequency in Hz
        """
        if not self.serial or not self.serial.is_open:
            raise ConnectionError("Not connected to instrument")

        if range_value and resolution:
            cmd = f"MEAS:FREQ? {range_value},{resolution}"
        elif range_value:
            cmd = f"MEAS:FREQ? {range_value}"
        else:
            cmd = "MEAS:FREQ?"

        result = self._query(cmd)
        return float(result)

    def measure_capacitance(self, range_value: Optional[float] = None, resolution: Optional[float] = None) -> float:
        """
        Measure capacitance

        Args:
            range_value: Capacitance range in farads (None for auto-range)
                        Valid ranges: 1e-9, 10e-9, 100e-9, 1e-6, 10e-6, 100e-6
            resolution: Resolution in farads (None for default)

        Returns:
            Measured capacitance in farads
        """
        if not self.serial or not self.serial.is_open:
            raise ConnectionError("Not connected to instrument")

        if range_value and resolution:
            cmd = f"MEAS:CAP? {range_value},{resolution}"
        elif range_value:
            cmd = f"MEAS:CAP? {range_value}"
        else:
            cmd = "MEAS:CAP?"

        result = self._query(cmd)
        return float(result)

    def measure_continuity(self) -> float:
        """
        Measure continuity (resistance with beeper)

        Returns:
            Measured resistance in ohms
        """
        if not self.serial or not self.serial.is_open:
            raise ConnectionError("Not connected to instrument")

        result = self._query("MEAS:CONT?")
        return float(result)

    def measure_diode(self) -> float:
        """
        Measure diode forward voltage

        Returns:
            Forward voltage in volts
        """
        if not self.serial or not self.serial.is_open:
            raise ConnectionError("Not connected to instrument")

        result = self._query("MEAS:DIOD?")
        return float(result)

    def get_status(self) -> Dict[str, Any]:
        """
        Get instrument status

        Returns:
            Dictionary with current instrument settings
        """
        if not self.serial or not self.serial.is_open:
            raise ConnectionError("Not connected to instrument")

        try:
            func = self._query("FUNC?").strip().strip('"')
            return {
                "connected": True,
                "current_function": func,
                "identification": self.get_identification()
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }
