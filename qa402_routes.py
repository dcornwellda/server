"""
API endpoints for QA402 Audio Analyzer
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from qa402_service import qa402_service

router = APIRouter(prefix="/qa402", tags=["QA402 Audio Analyzer"])


class ConnectionRequest(BaseModel):
    """Request model for QA402 connection"""
    base_url: str = Field(
        default="http://localhost:9402",
        description="Base URL for QA402 REST API"
    )


class AcquisitionConfig(BaseModel):
    """Configuration for acquisition"""
    sample_rate: Optional[int] = Field(
        default=None,
        description="Sample rate in Hz (48000 or 192000)"
    )
    buffer_size: Optional[int] = Field(
        default=None,
        description="Buffer size (power of 2)"
    )
    input_range: Optional[int] = Field(
        default=None,
        description="Input range in dBV (0, 6, 12, 18, 24, 30, 36, 42)"
    )


class GeneratorConfig(BaseModel):
    """Configuration for output generator"""
    frequency_hz: Optional[float] = Field(
        default=None,
        description="Frequency in Hz"
    )
    level_dbv: Optional[float] = Field(
        default=None,
        description="Output level in dBV (-100 to 18)"
    )
    enabled: Optional[bool] = Field(
        default=None,
        description="Enable/disable generator"
    )


class ChannelRequest(BaseModel):
    """Request model for channel selection"""
    channel: str = Field(
        default="left",
        description="Channel selection: 'left' or 'right'"
    )


@router.post("/connect")
async def connect(request: ConnectionRequest = ConnectionRequest()):
    """
    Connect to QA402 API
    
    - **base_url**: Base URL for QA402 REST API (default: http://localhost:9402)
    
    Note: QA402 application must be running for connection to work
    """
    result = qa402_service.connect(request.base_url)
    if not result.get("connected"):
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Failed to connect. Make sure QA402 application is running.")
        )
    return result


@router.get("/status")
async def get_status():
    """Get QA402 status"""
    result = qa402_service.get_status()
    if not result.get("connected"):
        raise HTTPException(
            status_code=503,
            detail="QA402 not connected. Make sure QA402 application is running."
        )
    return result


@router.get("/version")
async def get_version():
    """Get QA402 application version"""
    try:
        return qa402_service.get_version()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings")
async def get_settings():
    """Get current QA402 settings"""
    try:
        return qa402_service.get_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/configure/acquisition")
async def configure_acquisition(config: AcquisitionConfig):
    """
    Configure acquisition parameters
    
    - **sample_rate**: Sample rate in Hz (48000 or 192000)
    - **buffer_size**: Buffer size (power of 2, typically 4096-65536)
    - **input_range**: Input range in dBV (0, 6, 12, 18, 24, 30, 36, 42)
    """
    result = qa402_service.configure_acquisition(
        sample_rate=config.sample_rate,
        buffer_size=config.buffer_size,
        input_range=config.input_range
    )
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/configure/generator")
async def configure_generator(config: GeneratorConfig):
    """
    Configure output generator
    
    - **frequency_hz**: Frequency in Hz
    - **level_dbv**: Output level in dBV (-100 to 18)
    - **enabled**: Enable/disable generator
    """
    result = qa402_service.configure_generator(
        frequency_hz=config.frequency_hz,
        level_dbv=config.level_dbv,
        enabled=config.enabled
    )
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/acquisition/run")
async def run_acquisition():
    """Run a single acquisition"""
    result = qa402_service.run_acquisition()
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/data/frequency")
async def get_frequency_response(request: ChannelRequest = ChannelRequest()):
    """
    Get frequency response data
    
    - **channel**: "left" or "right"
    
    Returns frequency and amplitude arrays
    """
    result = qa402_service.get_frequency_response(request.channel)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/data/time")
async def get_time_response(request: ChannelRequest = ChannelRequest()):
    """
    Get time domain data
    
    - **channel**: "left" or "right"
    
    Returns time series array
    """
    result = qa402_service.get_time_response(request.channel)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/data/thd")
async def get_thd(request: ChannelRequest = ChannelRequest()):
    """
    Get Total Harmonic Distortion
    
    - **channel**: "left" or "right"
    
    Returns THD in dB
    """
    result = qa402_service.get_thd(request.channel)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/data/rms")
async def get_rms(request: ChannelRequest = ChannelRequest()):
    """
    Get RMS voltage
    
    - **channel**: "left" or "right"
    
    Returns RMS in dBV
    """
    result = qa402_service.get_rms(request.channel)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/data/peak")
async def get_peak_frequency(request: ChannelRequest = ChannelRequest()):
    """
    Get peak frequency and amplitude
    
    - **channel**: "left" or "right"
    
    Returns peak frequency (Hz) and amplitude (dB)
    """
    result = qa402_service.get_peak_frequency(request.channel)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/data/full")
async def get_full_measurement(request: ChannelRequest = ChannelRequest()):
    """
    Get comprehensive measurement data
    
    - **channel**: "left" or "right"
    
    Returns THD, RMS, and peak frequency data
    """
    result = qa402_service.get_full_measurement(request.channel)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result
