"""
Remote Instrument Control Server
FastAPI server for Keithley 2015 and QA402 Audio Analyzer
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from keithley_routes import router as keithley_router
from qa402_routes import router as qa402_router
from vnc_routes import router as vnc_router
import uvicorn

# Create FastAPI application
app = FastAPI(
    title="Remote Instrument Control Server",
    description="REST API for Keithley 2015 Multimeter and QA402 Audio Analyzer",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for remote access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(keithley_router)
app.include_router(qa402_router)
app.include_router(vnc_router)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Remote Instrument Control Server",
        "version": "1.0.0",
        "status": "running",
        "instruments": {
            "keithley_2015": {
                "status": "available",
                "endpoints": "/keithley/*"
            },
            "qa402": {
                "status": "available",
                "endpoints": "/qa402/*"
            },
            "vnc": {
                "status": "available",
                "endpoints": "/vnc/*"
            }
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Server is running"
    }


if __name__ == "__main__":
    print("=" * 60)
    print("Remote Instrument Control Server")
    print("=" * 60)
    print("\nStarting server...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("\nInstruments:")
    print("  - Keithley 2015 Multimeter")
    print("  - QA402 Audio Analyzer")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,
        log_level="info"
    )
