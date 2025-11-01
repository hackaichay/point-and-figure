from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
from contextlib import asynccontextmanager
import json
import os

from mt5_connector import MT5Connector
from pnf_calculator import PointAndFigureCalculator

# Global MT5 connector
mt5_connector = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    global mt5_connector
    # Startup
    mt5_connector = MT5Connector()
    print("Application started. MT5 connector initialized.")
    yield
    # Shutdown
    if mt5_connector and mt5_connector.connected:
        mt5_connector.disconnect()
    print("Application shutdown. MT5 disconnected.")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Point and Figure Chart with MT5",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class MT5Config(BaseModel):
    login: int
    password: str
    server: str
    path: Optional[str] = None

class ChartRequest(BaseModel):
    symbol: str
    timeframe: str = "M15"
    bars: int = 1000
    box_size: Optional[float] = None
    reversal_amount: Optional[int] = None


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    try:
        with open("/home/claude/pnf_mt5_project/static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Index.html not found. Please check the static folder.</h1>", status_code=404)


@app.post("/api/connect")
async def connect_mt5(config: MT5Config):
    """Connect to MT5 with provided credentials"""
    global mt5_connector
    
    if mt5_connector is None:
        mt5_connector = MT5Connector()
    
    # If password is "from_config", read from config file
    password = config.password
    if password == "from_config":
        try:
            with open("config.json", "r") as f:
                file_config = json.load(f)
                password = file_config.get("mt5", {}).get("password")
                if not password:
                    raise HTTPException(
                        status_code=400,
                        detail="Password not found in config.json"
                    )
        except FileNotFoundError:
            raise HTTPException(
                status_code=400,
                detail="Config file not found"
            )
    
    result = mt5_connector.connect(
        login=config.login,
        password=password,
        server=config.server,
        path=config.path
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@app.get("/api/disconnect")
async def disconnect_mt5():
    """Disconnect from MT5"""
    global mt5_connector
    
    if mt5_connector and mt5_connector.connected:
        mt5_connector.disconnect()
        return {"success": True, "message": "Disconnected from MT5"}
    
    return {"success": False, "message": "Not connected"}


@app.get("/api/status")
async def get_status():
    """Get connection status"""
    global mt5_connector
    
    if mt5_connector and mt5_connector.connected:
        return {
            "connected": True,
            "message": "Connected to MT5"
        }
    
    return {
        "connected": False,
        "message": "Not connected to MT5"
    }


@app.get("/api/symbols")
async def get_symbols():
    """Get all available symbols"""
    global mt5_connector
    
    if not mt5_connector or not mt5_connector.connected:
        raise HTTPException(status_code=400, detail="Not connected to MT5")
    
    symbols = mt5_connector.get_symbols()
    return {"symbols": symbols}


@app.get("/api/symbol/{symbol}")
async def get_symbol_info(symbol: str):
    """Get symbol information"""
    global mt5_connector
    
    if not mt5_connector or not mt5_connector.connected:
        raise HTTPException(status_code=400, detail="Not connected to MT5")
    
    info = mt5_connector.get_symbol_info(symbol)
    
    if info is None:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    
    return info


@app.post("/api/chart")
async def get_chart(request: ChartRequest):
    """Get Point and Figure chart data"""
    global mt5_connector
    
    if not mt5_connector or not mt5_connector.connected:
        raise HTTPException(status_code=400, detail="Not connected to MT5. Please connect first.")
    
    # Get rates from MT5
    df = mt5_connector.get_rates(
        symbol=request.symbol,
        timeframe=request.timeframe,
        bars=request.bars
    )
    
    if df is None or len(df) == 0:
        raise HTTPException(status_code=404, detail=f"No data found for {request.symbol}")
    
    # Load config for default PnF settings
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            pnf_config = config.get("pnf", {})
    except:
        pnf_config = {}
    
    # Use request parameters or fall back to config
    box_size = request.box_size or pnf_config.get("box_size", 10)
    reversal_amount = request.reversal_amount or pnf_config.get("reversal_amount", 3)
    
    # Calculate Point and Figure chart
    calculator = PointAndFigureCalculator(
        box_size=box_size,
        reversal_amount=reversal_amount
    )
    
    chart_data = calculator.calculate(df)
    
    # Add symbol info
    chart_data["symbol"] = request.symbol
    chart_data["timeframe"] = request.timeframe
    chart_data["bars_analyzed"] = len(df)
    
    # Get current price
    symbol_info = mt5_connector.get_symbol_info(request.symbol)
    if symbol_info:
        chart_data["current_bid"] = symbol_info["bid"]
        chart_data["current_ask"] = symbol_info["ask"]
    
    return chart_data


@app.get("/api/config")
async def get_config():
    """Get current configuration"""
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        
        # Return config with password masked for security
        response = {
            "mt5": {
                "login": config.get("mt5", {}).get("login"),
                "server": config.get("mt5", {}).get("server"),
                "path": config.get("mt5", {}).get("path"),
                "auto_connect": config.get("mt5", {}).get("auto_connect", False)
            },
            "chart": config.get("chart", {
                "symbol": "EURUSD",
                "timeframe": "M15",
                "bars": 1000,
                "auto_load": False
            }),
            "pnf": config.get("pnf", {
                "box_size": 10,
                "reversal_amount": 3
            })
        }
        
        return response
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Config file not found")


if __name__ == "__main__":
    import uvicorn
    
    # Load config
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        api_config = config.get("api", {})
        host = api_config.get("host", "0.0.0.0")
        port = api_config.get("port", 8000)
    except:
        host = "0.0.0.0"
        port = 8000
    
    uvicorn.run(app, host=host, port=port)
