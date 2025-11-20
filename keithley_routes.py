"""
API endpoints for Keithley 2015 Multimeter
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from keithley_service import keithley_service

router = APIRouter(prefix="/keithley", tags=["Keithley 2015"])


class ConnectionRequest(BaseModel):
    """Request model for connection"""
    address: str = Field(
        default="GPIB0::23::INSTR",
        description="VISA resource address (e.g., 'GPIB0::23::INSTR')"
    )


class MeasurementRequest(BaseModel):
    """Request model for measurements"""
    range_value: Optional[float] = Field(
        default=None,
        description="Measurement range (None for auto-range)"
    )


@router.post("/connect")
async def connect(request: ConnectionRequest):
    """
    Connect to Keithley 2015 multimeter

    - **address**: VISA resource address (e.g., "GPIB0::23::INSTR")
    """
    result = keithley_service.connect(request.address)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


@router.post("/disconnect")
async def disconnect():
    """Disconnect from Keithley 2015"""
    return keithley_service.disconnect()


@router.get("/status")
async def get_status():
    """Get current status and connection state"""
    return keithley_service.get_status()


@router.post("/reset")
async def reset():
    """Reset instrument to default state"""
    result = keithley_service.reset()
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/measure/voltage/dc")
async def measure_voltage_dc(request: MeasurementRequest = MeasurementRequest()):
    """
    Measure DC voltage
    
    - **range_value**: Voltage range in volts (None for auto-range)
    - Valid ranges: 0.2, 2, 20, 200, 1000
    """
    result = keithley_service.measure_voltage_dc(request.range_value)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/measure/voltage/ac")
async def measure_voltage_ac(request: MeasurementRequest = MeasurementRequest()):
    """
    Measure AC voltage (RMS)
    
    - **range_value**: Voltage range in volts (None for auto-range)
    - Valid ranges: 0.2, 2, 20, 200, 750
    """
    result = keithley_service.measure_voltage_ac(request.range_value)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/measure/current/dc")
async def measure_current_dc(request: MeasurementRequest = MeasurementRequest()):
    """
    Measure DC current
    
    - **range_value**: Current range in amps (None for auto-range)
    - Valid ranges: 0.02, 0.2, 2
    """
    result = keithley_service.measure_current_dc(request.range_value)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/measure/current/ac")
async def measure_current_ac(request: MeasurementRequest = MeasurementRequest()):
    """
    Measure AC current (RMS)
    
    - **range_value**: Current range in amps (None for auto-range)
    - Valid ranges: 0.02, 0.2, 2
    """
    result = keithley_service.measure_current_ac(request.range_value)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/measure/resistance/2wire")
async def measure_resistance_2wire(request: MeasurementRequest = MeasurementRequest()):
    """
    Measure resistance using 2-wire method
    
    - **range_value**: Resistance range in ohms (None for auto-range)
    - Valid ranges: 200, 2000, 20000, 200000, 2000000, 20000000
    """
    result = keithley_service.measure_resistance_2wire(request.range_value)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/measure/resistance/4wire")
async def measure_resistance_4wire(request: MeasurementRequest = MeasurementRequest()):
    """
    Measure resistance using 4-wire method (more accurate for low resistances)
    
    - **range_value**: Resistance range in ohms (None for auto-range)
    - Valid ranges: 200, 2000, 20000, 200000, 2000000, 20000000
    """
    result = keithley_service.measure_resistance_4wire(request.range_value)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result
