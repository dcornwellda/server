"""
API endpoints for Fluke 8845A Digital Multimeter
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from fluke8845a_service import fluke_service

router = APIRouter(prefix="/fluke", tags=["Fluke 8845A"])


class ConnectionRequest(BaseModel):
    """Request model for connection"""
    address: str = Field(
        default="COM5",
        description="COM port address (e.g., 'COM5', 'COM3', etc.)"
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
    Connect to Fluke 8845A multimeter

    - **address**: COM port address (e.g., "COM5", "COM3", etc.)
    """
    result = fluke_service.connect(request.address)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


@router.post("/disconnect")
async def disconnect():
    """Disconnect from Fluke 8845A"""
    return fluke_service.disconnect()


@router.get("/status")
async def get_status():
    """Get current status and connection state"""
    return fluke_service.get_status()


@router.post("/reset")
async def reset():
    """Reset instrument to default state"""
    result = fluke_service.reset()
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/measure/voltage/dc")
async def measure_voltage_dc(request: MeasurementRequest = MeasurementRequest()):
    """
    Measure DC voltage

    - **range_value**: Voltage range in volts (None for auto-range)
    - Valid ranges: 0.1, 1, 10, 100, 1000
    """
    result = fluke_service.measure_voltage_dc(request.range_value)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/measure/voltage/ac")
async def measure_voltage_ac(request: MeasurementRequest = MeasurementRequest()):
    """
    Measure AC voltage (RMS)

    - **range_value**: Voltage range in volts (None for auto-range)
    - Valid ranges: 0.1, 1, 10, 100, 750
    """
    result = fluke_service.measure_voltage_ac(request.range_value)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/measure/current/dc")
async def measure_current_dc(request: MeasurementRequest = MeasurementRequest()):
    """
    Measure DC current

    - **range_value**: Current range in amps (None for auto-range)
    - Valid ranges: 0.0001, 0.001, 0.01, 0.1, 1, 3
    """
    result = fluke_service.measure_current_dc(request.range_value)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/measure/current/ac")
async def measure_current_ac(request: MeasurementRequest = MeasurementRequest()):
    """
    Measure AC current (RMS)

    - **range_value**: Current range in amps (None for auto-range)
    - Valid ranges: 0.001, 0.01, 0.1, 1, 3
    """
    result = fluke_service.measure_current_ac(request.range_value)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/measure/resistance/2wire")
async def measure_resistance_2wire(request: MeasurementRequest = MeasurementRequest()):
    """
    Measure resistance using 2-wire method

    - **range_value**: Resistance range in ohms (None for auto-range)
    - Valid ranges: 100, 1000, 10000, 100000, 1000000, 10000000, 100000000
    """
    result = fluke_service.measure_resistance_2wire(request.range_value)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/measure/resistance/4wire")
async def measure_resistance_4wire(request: MeasurementRequest = MeasurementRequest()):
    """
    Measure resistance using 4-wire method (more accurate for low resistances)

    - **range_value**: Resistance range in ohms (None for auto-range)
    - Valid ranges: 100, 1000, 10000, 100000, 1000000, 10000000, 100000000
    """
    result = fluke_service.measure_resistance_4wire(request.range_value)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/measure/frequency")
async def measure_frequency(request: MeasurementRequest = MeasurementRequest()):
    """
    Measure frequency

    - **range_value**: Expected voltage range for signal (None for auto)
    """
    result = fluke_service.measure_frequency(request.range_value)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/measure/capacitance")
async def measure_capacitance(request: MeasurementRequest = MeasurementRequest()):
    """
    Measure capacitance

    - **range_value**: Capacitance range in farads (None for auto-range)
    - Valid ranges: 1e-9, 10e-9, 100e-9, 1e-6, 10e-6, 100e-6
    """
    result = fluke_service.measure_capacitance(request.range_value)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/measure/continuity")
async def measure_continuity():
    """
    Measure continuity (resistance with beeper)

    Returns resistance value in ohms
    """
    result = fluke_service.measure_continuity()
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/measure/diode")
async def measure_diode():
    """
    Measure diode forward voltage

    Returns forward voltage in volts
    """
    result = fluke_service.measure_diode()
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result
