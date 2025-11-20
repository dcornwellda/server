"""
Service layer for QA402 operations
Handles business logic and API interaction
"""

from typing import Optional, Dict, Any, List
from qa402 import QA402


class QA402Service:
    """Service for managing QA402 operations"""
    
    def __init__(self):
        self.device: Optional[QA402] = None
        self.base_url: str = "http://localhost:9402"
    
    def connect(self, base_url: str = "http://localhost:9402") -> Dict[str, Any]:
        """Initialize connection to QA402 API"""
        try:
            self.base_url = base_url
            self.device = QA402(base_url)
            status = self.device.get_status()
            return status
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "message": "Make sure QA402 application is running"
            }
    
    def _ensure_connected(self):
        """Ensure device is connected"""
        if not self.device:
            raise ConnectionError("QA402 not connected. Please connect first.")
    
    def get_status(self) -> Dict[str, Any]:
        """Get QA402 status"""
        if not self.device:
            return {
                "connected": False,
                "message": "Not connected. Make sure QA402 application is running."
            }
        return self.device.get_status()
    
    def get_version(self) -> Dict[str, str]:
        """Get QA402 application version"""
        self._ensure_connected()
        version = self.device.get_version()
        return {"version": version}
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings"""
        self._ensure_connected()
        return self.device.get_settings()
    
    def configure_acquisition(
        self,
        sample_rate: Optional[int] = None,
        buffer_size: Optional[int] = None,
        input_range: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Configure acquisition parameters
        
        Args:
            sample_rate: Sample rate in Hz (48000 or 192000)
            buffer_size: Buffer size (power of 2)
            input_range: Input range in dBV (0, 6, 12, 18, 24, 30, 36, 42)
        """
        self._ensure_connected()
        results = {"status": "configured"}
        
        try:
            if sample_rate:
                self.device.set_sample_rate(sample_rate)
                results["sample_rate"] = sample_rate
            
            if buffer_size:
                self.device.set_buffer_size(buffer_size)
                results["buffer_size"] = buffer_size
            
            if input_range is not None:
                self.device.set_input_range(input_range)
                results["input_range_dbv"] = input_range
            
            return results
        except Exception as e:
            return {"error": str(e)}
    
    def configure_generator(
        self,
        frequency_hz: Optional[float] = None,
        level_dbv: Optional[float] = None,
        enabled: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Configure output generator
        
        Args:
            frequency_hz: Frequency in Hz
            level_dbv: Output level in dBV
            enabled: Enable/disable generator
        """
        self._ensure_connected()
        results = {"status": "configured"}
        
        try:
            if frequency_hz is not None:
                self.device.set_output_frequency(frequency_hz)
                results["frequency_hz"] = frequency_hz
            
            if level_dbv is not None:
                self.device.set_output_level(level_dbv)
                results["level_dbv"] = level_dbv
            
            if enabled is not None:
                self.device.set_output_on(enabled)
                results["enabled"] = enabled
            
            return results
        except Exception as e:
            return {"error": str(e)}
    
    def run_acquisition(self) -> Dict[str, Any]:
        """Run a single acquisition"""
        self._ensure_connected()
        try:
            return self.device.run_single_acquisition()
        except Exception as e:
            return {"error": str(e)}
    
    def get_frequency_response(self, channel: str = "left") -> Dict[str, Any]:
        """
        Get frequency response data
        
        Args:
            channel: "left" or "right"
        """
        self._ensure_connected()
        try:
            if channel.lower() == "left":
                return self.device.get_frequency_series_left()
            elif channel.lower() == "right":
                return self.device.get_frequency_series_right()
            else:
                return {"error": "Channel must be 'left' or 'right'"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_time_response(self, channel: str = "left") -> Dict[str, Any]:
        """
        Get time domain data
        
        Args:
            channel: "left" or "right"
        """
        self._ensure_connected()
        try:
            if channel.lower() == "left":
                return self.device.get_time_series_left()
            elif channel.lower() == "right":
                return self.device.get_time_series_right()
            else:
                return {"error": "Channel must be 'left' or 'right'"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_thd(self, channel: str = "left") -> Dict[str, Any]:
        """
        Get Total Harmonic Distortion
        
        Args:
            channel: "left" or "right"
        """
        self._ensure_connected()
        try:
            if channel.lower() == "left":
                thd = self.device.get_thd_left()
            elif channel.lower() == "right":
                thd = self.device.get_thd_right()
            else:
                return {"error": "Channel must be 'left' or 'right'"}
            
            return {
                "channel": channel,
                "thd_db": thd,
                "unit": "dB"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_rms(self, channel: str = "left") -> Dict[str, Any]:
        """
        Get RMS voltage
        
        Args:
            channel: "left" or "right"
        """
        self._ensure_connected()
        try:
            if channel.lower() == "left":
                rms = self.device.get_rms_left()
            elif channel.lower() == "right":
                rms = self.device.get_rms_right()
            else:
                return {"error": "Channel must be 'left' or 'right'"}
            
            return {
                "channel": channel,
                "rms_dbv": rms,
                "unit": "dBV"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_peak_frequency(self, channel: str = "left") -> Dict[str, Any]:
        """
        Get peak frequency and amplitude
        
        Args:
            channel: "left" or "right"
        """
        self._ensure_connected()
        try:
            if channel.lower() == "left":
                data = self.device.get_peak_frequency_left()
            elif channel.lower() == "right":
                data = self.device.get_peak_frequency_right()
            else:
                return {"error": "Channel must be 'left' or 'right'"}
            
            return {
                "channel": channel,
                **data
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_full_measurement(self, channel: str = "left") -> Dict[str, Any]:
        """
        Get comprehensive measurement data
        
        Args:
            channel: "left" or "right"
        """
        self._ensure_connected()
        try:
            results = {
                "channel": channel,
                "thd": self.get_thd(channel),
                "rms": self.get_rms(channel),
                "peak": self.get_peak_frequency(channel)
            }
            return results
        except Exception as e:
            return {"error": str(e)}


# Global service instance
qa402_service = QA402Service()
