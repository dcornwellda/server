"""
Keithley 2015 Multimeter Driver

Supports DC/AC voltage, DC/AC current, 2-wire and 4-wire resistance measurements.
Communicates via GPIB through PyVISA.
"""

import pyvisa
from typing import Optional, Dict, Any
import time


class Keithley2015:
    """Driver for Keithley 2015 THD Multimeter"""
    
    def __init__(self, resource_address: str = "GPIB0::23::INSTR"):
        """
        Initialize connection to Keithley 2015

        Args:
            resource_address: VISA resource string (e.g., "GPIB0::23::INSTR")
        """
        self.resource_address = resource_address
        self.instrument: Optional[pyvisa.Resource] = None
        self.rm: Optional[pyvisa.ResourceManager] = None
        
    def connect(self) -> Dict[str, Any]:
        """
        Connect to the instrument
        
        Returns:
            Dictionary with connection status and instrument info
        """
        try:
            self.rm = pyvisa.ResourceManager()
            self.instrument = self.rm.open_resource(self.resource_address)
            self.instrument.timeout = 5000  # 5 second timeout
            
            # Get instrument identification
            idn = self.instrument.query("*IDN?").strip()
            
            # Reset to known state
            self.instrument.write("*RST")
            time.sleep(0.5)
            
            return {
                "status": "connected",
                "address": self.resource_address,
                "identification": idn
            }
        except Exception as e:
            return {
                "status": "error",
                "address": self.resource_address,
                "error": str(e)
            }
    
    def disconnect(self):
        """Close connection to instrument"""
        if self.instrument:
            self.instrument.close()
        if self.rm:
            self.rm.close()
    
    def get_identification(self) -> str:
        """Get instrument identification string"""
        if not self.instrument:
            raise ConnectionError("Not connected to instrument")
        return self.instrument.query("*IDN?").strip()
    
    def reset(self):
        """Reset instrument to default state"""
        if not self.instrument:
            raise ConnectionError("Not connected to instrument")
        self.instrument.write("*RST")
        time.sleep(0.5)
    
    def measure_dc_voltage(self, range_value: Optional[float] = None) -> float:
        """
        Measure DC voltage
        
        Args:
            range_value: Voltage range in volts (None for auto-range)
                        Valid ranges: 0.2, 2, 20, 200, 1000
        
        Returns:
            Measured voltage in volts
        """
        if not self.instrument:
            raise ConnectionError("Not connected to instrument")
        
        # Configure for DC voltage measurement
        self.instrument.write("FUNC 'VOLT:DC'")
        
        if range_value:
            self.instrument.write(f"VOLT:DC:RANG {range_value}")
        else:
            self.instrument.write("VOLT:DC:RANG:AUTO ON")
        
        # Trigger measurement and read
        result = self.instrument.query("READ?")
        return float(result)
    
    def measure_ac_voltage(self, range_value: Optional[float] = None) -> float:
        """
        Measure AC voltage
        
        Args:
            range_value: Voltage range in volts (None for auto-range)
                        Valid ranges: 0.2, 2, 20, 200, 750
        
        Returns:
            Measured voltage in volts RMS
        """
        if not self.instrument:
            raise ConnectionError("Not connected to instrument")
        
        self.instrument.write("FUNC 'VOLT:AC'")
        
        if range_value:
            self.instrument.write(f"VOLT:AC:RANG {range_value}")
        else:
            self.instrument.write("VOLT:AC:RANG:AUTO ON")
        
        result = self.instrument.query("READ?")
        return float(result)
    
    def measure_dc_current(self, range_value: Optional[float] = None) -> float:
        """
        Measure DC current
        
        Args:
            range_value: Current range in amps (None for auto-range)
                        Valid ranges: 0.02, 0.2, 2
        
        Returns:
            Measured current in amps
        """
        if not self.instrument:
            raise ConnectionError("Not connected to instrument")
        
        self.instrument.write("FUNC 'CURR:DC'")
        
        if range_value:
            self.instrument.write(f"CURR:DC:RANG {range_value}")
        else:
            self.instrument.write("CURR:DC:RANG:AUTO ON")
        
        result = self.instrument.query("READ?")
        return float(result)
    
    def measure_ac_current(self, range_value: Optional[float] = None) -> float:
        """
        Measure AC current
        
        Args:
            range_value: Current range in amps (None for auto-range)
                        Valid ranges: 0.02, 0.2, 2
        
        Returns:
            Measured current in amps RMS
        """
        if not self.instrument:
            raise ConnectionError("Not connected to instrument")
        
        self.instrument.write("FUNC 'CURR:AC'")
        
        if range_value:
            self.instrument.write(f"CURR:AC:RANG {range_value}")
        else:
            self.instrument.write("CURR:AC:RANG:AUTO ON")
        
        result = self.instrument.query("READ?")
        return float(result)
    
    def measure_resistance_2wire(self, range_value: Optional[float] = None) -> float:
        """
        Measure resistance using 2-wire method
        
        Args:
            range_value: Resistance range in ohms (None for auto-range)
                        Valid ranges: 200, 2000, 20000, 200000, 2000000, 20000000
        
        Returns:
            Measured resistance in ohms
        """
        if not self.instrument:
            raise ConnectionError("Not connected to instrument")
        
        self.instrument.write("FUNC 'RES'")
        
        if range_value:
            self.instrument.write(f"RES:RANG {range_value}")
        else:
            self.instrument.write("RES:RANG:AUTO ON")
        
        result = self.instrument.query("READ?")
        return float(result)
    
    def measure_resistance_4wire(self, range_value: Optional[float] = None) -> float:
        """
        Measure resistance using 4-wire method (more accurate for low resistances)
        
        Args:
            range_value: Resistance range in ohms (None for auto-range)
                        Valid ranges: 200, 2000, 20000, 200000, 2000000, 20000000
        
        Returns:
            Measured resistance in ohms
        """
        if not self.instrument:
            raise ConnectionError("Not connected to instrument")
        
        self.instrument.write("FUNC 'FRES'")
        
        if range_value:
            self.instrument.write(f"FRES:RANG {range_value}")
        else:
            self.instrument.write("FRES:RANG:AUTO ON")
        
        result = self.instrument.query("READ?")
        return float(result)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get instrument status
        
        Returns:
            Dictionary with current instrument settings
        """
        if not self.instrument:
            raise ConnectionError("Not connected to instrument")
        
        try:
            func = self.instrument.query("FUNC?").strip().strip('"')
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
