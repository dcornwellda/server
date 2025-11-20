"""
Example Python Client for Remote Instrument Server

This script demonstrates how to use the instrument server from a remote PC.
"""

import requests
from typing import Optional, Dict, Any
import time


class InstrumentClient:
    """Client for accessing remote instruments"""
    
    def __init__(self, base_url: str):
        """
        Initialize client
        
        Args:
            base_url: Base URL of the server (e.g., "http://192.168.1.100:8000")
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def _post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, json=data or {})
        response.raise_for_status()
        return response.json()
    
    def _get(self, endpoint: str) -> Dict[str, Any]:
        """Make GET request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    # Keithley 2015 Methods
    
    def keithley_connect(self, address: str = "GPIB0::15::INSTR") -> Dict:
        """Connect to Keithley 2015"""
        return self._post("/keithley/connect", {"address": address})
    
    def keithley_disconnect(self) -> Dict:
        """Disconnect from Keithley"""
        return self._post("/keithley/disconnect")
    
    def keithley_status(self) -> Dict:
        """Get Keithley status"""
        return self._get("/keithley/status")
    
    def keithley_measure_vdc(self, range_value: Optional[float] = None) -> Dict:
        """Measure DC voltage"""
        return self._post("/keithley/measure/voltage/dc", {"range_value": range_value})
    
    def keithley_measure_vac(self, range_value: Optional[float] = None) -> Dict:
        """Measure AC voltage"""
        return self._post("/keithley/measure/voltage/ac", {"range_value": range_value})
    
    def keithley_measure_idc(self, range_value: Optional[float] = None) -> Dict:
        """Measure DC current"""
        return self._post("/keithley/measure/current/dc", {"range_value": range_value})
    
    def keithley_measure_iac(self, range_value: Optional[float] = None) -> Dict:
        """Measure AC current"""
        return self._post("/keithley/measure/current/ac", {"range_value": range_value})
    
    def keithley_measure_resistance_2w(self, range_value: Optional[float] = None) -> Dict:
        """Measure resistance (2-wire)"""
        return self._post("/keithley/measure/resistance/2wire", {"range_value": range_value})
    
    def keithley_measure_resistance_4w(self, range_value: Optional[float] = None) -> Dict:
        """Measure resistance (4-wire)"""
        return self._post("/keithley/measure/resistance/4wire", {"range_value": range_value})
    
    # QA402 Methods
    
    def qa402_connect(self, base_url: str = "http://localhost:9402") -> Dict:
        """Connect to QA402"""
        return self._post("/qa402/connect", {"base_url": base_url})
    
    def qa402_status(self) -> Dict:
        """Get QA402 status"""
        return self._get("/qa402/status")
    
    def qa402_configure_acquisition(
        self,
        sample_rate: Optional[int] = None,
        buffer_size: Optional[int] = None,
        input_range: Optional[int] = None
    ) -> Dict:
        """Configure acquisition parameters"""
        return self._post("/qa402/configure/acquisition", {
            "sample_rate": sample_rate,
            "buffer_size": buffer_size,
            "input_range": input_range
        })
    
    def qa402_configure_generator(
        self,
        frequency_hz: Optional[float] = None,
        level_dbv: Optional[float] = None,
        enabled: Optional[bool] = None
    ) -> Dict:
        """Configure output generator"""
        return self._post("/qa402/configure/generator", {
            "frequency_hz": frequency_hz,
            "level_dbv": level_dbv,
            "enabled": enabled
        })
    
    def qa402_run_acquisition(self) -> Dict:
        """Run acquisition"""
        return self._post("/qa402/acquisition/run")
    
    def qa402_get_thd(self, channel: str = "left") -> Dict:
        """Get THD measurement"""
        return self._post("/qa402/data/thd", {"channel": channel})
    
    def qa402_get_rms(self, channel: str = "left") -> Dict:
        """Get RMS voltage"""
        return self._post("/qa402/data/rms", {"channel": channel})
    
    def qa402_get_peak_freq(self, channel: str = "left") -> Dict:
        """Get peak frequency"""
        return self._post("/qa402/data/peak", {"channel": channel})
    
    def qa402_get_frequency_response(self, channel: str = "left") -> Dict:
        """Get frequency response data"""
        return self._post("/qa402/data/frequency", {"channel": channel})


# Example Usage
def example_keithley():
    """Example: Using Keithley 2015"""
    print("=== Keithley 2015 Example ===\n")
    
    # Initialize client (replace with your server IP)
    client = InstrumentClient("http://192.168.1.100:8000")
    
    # Connect to Keithley
    print("Connecting to Keithley...")
    result = client.keithley_connect("GPIB0::15::INSTR")
    print(f"Connection: {result}\n")
    
    # Check status
    status = client.keithley_status()
    print(f"Status: {status}\n")
    
    # Measure DC voltage
    print("Measuring DC voltage...")
    voltage = client.keithley_measure_vdc()
    print(f"DC Voltage: {voltage['value']} {voltage['unit']}\n")
    
    # Measure resistance (4-wire for better accuracy)
    print("Measuring resistance (4-wire)...")
    resistance = client.keithley_measure_resistance_4w()
    print(f"Resistance: {resistance['value']} {resistance['unit']}\n")
    
    # Disconnect
    client.keithley_disconnect()
    print("Disconnected")


def example_qa402():
    """Example: Using QA402 Audio Analyzer"""
    print("=== QA402 Audio Analyzer Example ===\n")
    
    # Initialize client
    client = InstrumentClient("http://192.168.1.100:8000")
    
    # Connect to QA402
    print("Connecting to QA402...")
    result = client.qa402_connect()
    print(f"Connection: {result}\n")
    
    # Configure acquisition
    print("Configuring acquisition...")
    client.qa402_configure_acquisition(
        sample_rate=48000,
        buffer_size=8192,
        input_range=18
    )
    
    # Configure generator (1kHz test tone at -10dBV)
    print("Configuring generator...")
    client.qa402_configure_generator(
        frequency_hz=1000,
        level_dbv=-10,
        enabled=True
    )
    
    # Run acquisition
    print("Running acquisition...")
    client.qa402_run_acquisition()
    time.sleep(1)  # Wait for acquisition to complete
    
    # Get measurements
    thd = client.qa402_get_thd("left")
    print(f"THD: {thd['thd_db']} dB")
    
    rms = client.qa402_get_rms("left")
    print(f"RMS: {rms['rms_dbv']} dBV")
    
    peak = client.qa402_get_peak_freq("left")
    print(f"Peak: {peak['frequency_hz']} Hz at {peak['amplitude_db']} dB")


def example_automated_test():
    """Example: Automated test sequence"""
    print("=== Automated Test Sequence ===\n")
    
    client = InstrumentClient("http://192.168.1.100:8000")
    
    # Test setup
    print("Setting up instruments...")
    client.keithley_connect("GPIB0::15::INSTR")
    client.qa402_connect()
    
    # Configure QA402 generator
    client.qa402_configure_generator(
        frequency_hz=1000,
        level_dbv=-10,
        enabled=True
    )
    
    # Measure output voltage with Keithley
    print("\nMeasuring generator output...")
    voltage = client.keithley_measure_vac()
    print(f"Generator output: {voltage['value']} V RMS")
    
    # Run QA402 analysis
    print("\nRunning audio analysis...")
    client.qa402_run_acquisition()
    time.sleep(1)
    
    thd = client.qa402_get_thd("left")
    print(f"THD: {thd['thd_db']} dB")
    
    # Test multiple frequencies
    print("\nFrequency sweep:")
    frequencies = [100, 1000, 10000]
    for freq in frequencies:
        client.qa402_configure_generator(frequency_hz=freq)
        time.sleep(0.5)
        client.qa402_run_acquisition()
        time.sleep(1)
        
        result = client.qa402_get_peak_freq("left")
        print(f"  {freq} Hz → Peak: {result['frequency_hz']:.1f} Hz, "
              f"Amplitude: {result['amplitude_db']:.2f} dB")
    
    # Cleanup
    client.qa402_configure_generator(enabled=False)
    client.keithley_disconnect()
    print("\nTest complete!")


if __name__ == "__main__":
    print("Remote Instrument Client Examples")
    print("=" * 50)
    print("\nBefore running, update the server IP address in the code!")
    print("Replace 'http://192.168.1.100:8000' with your server's IP\n")
    
    # Uncomment the example you want to run:
    
    # example_keithley()
    # example_qa402()
    # example_automated_test()
    
    print("\nUncomment one of the example functions to run it.")
