"""
QA402 Audio Analyzer Driver

This driver interfaces with the QA402's built-in REST API running on localhost:9402.
The QA402 application must be running for this driver to work.

API Documentation: https://github.com/QuantAsylum/QA40x/wiki/QA40x-API
"""

import requests
from typing import Optional, Dict, Any, List
import json


class QA402:
    """Driver for QA402 Audio Analyzer via REST API"""
    
    def __init__(self, base_url: str = "http://localhost:9402"):
        """
        Initialize QA402 API client
        
        Args:
            base_url: Base URL for QA402 REST API (default: http://localhost:9402)
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Make GET request to QA402 API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json() if response.text else None
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"QA402 API request failed: {str(e)}")
    
    def _put(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Make PUT request to QA402 API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.put(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json() if response.text else None
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"QA402 API request failed: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get QA402 application status
        
        Returns:
            Dictionary with status information
        """
        try:
            status = self._get("/Status")
            return {
                "connected": True,
                "status": status
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }
    
    def get_version(self) -> str:
        """Get QA402 application version"""
        return self._get("/Version")
    
    def is_running(self) -> bool:
        """Check if an acquisition is currently running"""
        return self._get("/Status/IsRunning")
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current QA402 settings"""
        return self._get("/Settings")
    
    def set_sample_rate(self, sample_rate: int) -> Dict[str, str]:
        """
        Set sample rate
        
        Args:
            sample_rate: Sample rate in Hz (48000 or 192000)
        
        Returns:
            Status message
        """
        valid_rates = [48000, 192000]
        if sample_rate not in valid_rates:
            raise ValueError(f"Sample rate must be one of {valid_rates}")
        
        self._put(f"/Settings/SampleRate/{sample_rate}")
        return {"status": "success", "sample_rate": sample_rate}
    
    def set_buffer_size(self, buffer_size: int) -> Dict[str, str]:
        """
        Set buffer size for acquisition
        
        Args:
            buffer_size: Buffer size (power of 2, typically 4096-65536)
        
        Returns:
            Status message
        """
        self._put(f"/Settings/BufferSize/{buffer_size}")
        return {"status": "success", "buffer_size": buffer_size}
    
    def set_input_range(self, input_range: int) -> Dict[str, str]:
        """
        Set input range
        
        Args:
            input_range: Input range in dBV (0, 6, 12, 18, 24, 30, 36, 42)
        
        Returns:
            Status message
        """
        valid_ranges = [0, 6, 12, 18, 24, 30, 36, 42]
        if input_range not in valid_ranges:
            raise ValueError(f"Input range must be one of {valid_ranges}")
        
        self._put(f"/Settings/Input/Max/{input_range}")
        return {"status": "success", "input_range_dbv": input_range}
    
    def set_output_level(self, level_dbv: float) -> Dict[str, str]:
        """
        Set output generator level
        
        Args:
            level_dbv: Output level in dBV (-100 to 18)
        
        Returns:
            Status message
        """
        if not -100 <= level_dbv <= 18:
            raise ValueError("Output level must be between -100 and 18 dBV")
        
        self._put(f"/Settings/Output/Gen1/Level/{level_dbv}")
        return {"status": "success", "output_level_dbv": level_dbv}
    
    def set_output_frequency(self, frequency_hz: float) -> Dict[str, str]:
        """
        Set output generator frequency
        
        Args:
            frequency_hz: Frequency in Hz (20 to 20000)
        
        Returns:
            Status message
        """
        self._put(f"/Settings/Output/Gen1/Frequency/{frequency_hz}")
        return {"status": "success", "output_frequency_hz": frequency_hz}
    
    def set_output_on(self, enabled: bool = True) -> Dict[str, str]:
        """
        Enable or disable output generator
        
        Args:
            enabled: True to enable, False to disable
        
        Returns:
            Status message
        """
        endpoint = "/Settings/Output/Gen1/On" if enabled else "/Settings/Output/Gen1/Off"
        self._put(endpoint)
        return {"status": "success", "output_enabled": enabled}
    
    def run_single_acquisition(self) -> Dict[str, Any]:
        """
        Run a single acquisition
        
        Returns:
            Acquisition data
        """
        self._put("/Acquisition/Start")
        # Wait for acquisition to complete
        import time
        max_wait = 10  # seconds
        waited = 0
        while self.is_running() and waited < max_wait:
            time.sleep(0.1)
            waited += 0.1
        
        if waited >= max_wait:
            raise TimeoutError("Acquisition timeout")
        
        return {"status": "completed", "data": "Use get_data methods to retrieve results"}
    
    def get_frequency_series_left(self) -> Dict[str, List[float]]:
        """Get frequency and amplitude data for left channel"""
        freq = self._get("/Data/Freq/Left")
        amp = self._get("/Data/Amplitude/Left")
        return {
            "frequency_hz": freq,
            "amplitude_db": amp
        }
    
    def get_frequency_series_right(self) -> Dict[str, List[float]]:
        """Get frequency and amplitude data for right channel"""
        freq = self._get("/Data/Freq/Right")
        amp = self._get("/Data/Amplitude/Right")
        return {
            "frequency_hz": freq,
            "amplitude_db": amp
        }
    
    def get_time_series_left(self) -> Dict[str, List[float]]:
        """Get time domain data for left channel"""
        time_data = self._get("/Data/Time/Left")
        return {
            "time_series": time_data
        }
    
    def get_time_series_right(self) -> Dict[str, List[float]]:
        """Get time domain data for right channel"""
        time_data = self._get("/Data/Time/Right")
        return {
            "time_series": time_data
        }
    
    def get_thd_left(self) -> float:
        """Get THD (Total Harmonic Distortion) for left channel in dB"""
        return self._get("/Data/THD/Left")
    
    def get_thd_right(self) -> float:
        """Get THD (Total Harmonic Distortion) for right channel in dB"""
        return self._get("/Data/THD/Right")
    
    def get_rms_left(self) -> float:
        """Get RMS voltage for left channel in dBV"""
        return self._get("/Data/RMS/Left")
    
    def get_rms_right(self) -> float:
        """Get RMS voltage for right channel in dBV"""
        return self._get("/Data/RMS/Right")
    
    def get_peak_frequency_left(self) -> Dict[str, float]:
        """Get peak frequency and amplitude for left channel"""
        freq = self._get("/Data/PeakFreq/Left")
        amp = self._get("/Data/PeakAmplitude/Left")
        return {
            "frequency_hz": freq,
            "amplitude_db": amp
        }
    
    def get_peak_frequency_right(self) -> Dict[str, float]:
        """Get peak frequency and amplitude for right channel"""
        freq = self._get("/Data/PeakFreq/Right")
        amp = self._get("/Data/PeakAmplitude/Right")
        return {
            "frequency_hz": freq,
            "amplitude_db": amp
        }
