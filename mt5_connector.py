import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict
import json


class MT5Connector:
    def __init__(self, config_path: str = "config.json"):
        """Initialize MT5 connector with config"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.mt5_config = self.config['mt5']
        self.connected = False
    
    def connect(self, login: Optional[int] = None, 
                password: Optional[str] = None, 
                server: Optional[str] = None,
                path: Optional[str] = None) -> Dict:
        """Connect to MT5 terminal"""
        try:
            # Use provided credentials or fall back to config
            _login = login or self.mt5_config['login']
            _password = password or self.mt5_config['password']
            _server = server or self.mt5_config['server']
            _path = path or self.mt5_config.get('path')
            
            # Initialize MT5
            if _path:
                if not mt5.initialize(path=_path):
                    return {
                        "success": False,
                        "error": f"MT5 initialize failed: {mt5.last_error()}"
                    }
            else:
                if not mt5.initialize():
                    return {
                        "success": False,
                        "error": f"MT5 initialize failed: {mt5.last_error()}"
                    }
            
            # Login
            if not mt5.login(_login, password=_password, server=_server):
                return {
                    "success": False,
                    "error": f"MT5 login failed: {mt5.last_error()}"
                }
            
            self.connected = True
            account_info = mt5.account_info()
            
            return {
                "success": True,
                "account": {
                    "login": account_info.login,
                    "server": account_info.server,
                    "name": account_info.name,
                    "balance": account_info.balance,
                    "currency": account_info.currency
                }
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def disconnect(self):
        """Disconnect from MT5"""
        mt5.shutdown()
        self.connected = False
    
    def get_symbols(self) -> list:
        """Get all available symbols"""
        if not self.connected:
            return []
        
        symbols = mt5.symbols_get()
        return [s.name for s in symbols] if symbols else []
    
    def get_rates(self, symbol: str, timeframe: str = "M15", bars: int = 1000) -> Optional[pd.DataFrame]:
        """Get historical rates from MT5"""
        if not self.connected:
            return None
        
        # Map timeframe string to MT5 constant
        timeframe_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
            "MN1": mt5.TIMEFRAME_MN1
        }
        
        tf = timeframe_map.get(timeframe, mt5.TIMEFRAME_M15)
        
        try:
            rates = mt5.copy_rates_from_pos(symbol, tf, 0, bars)
            
            if rates is None or len(rates) == 0:
                return None
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            return df[['time', 'open', 'high', 'low', 'close', 'tick_volume']]
        
        except Exception as e:
            print(f"Error getting rates: {e}")
            return None
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol information"""
        if not self.connected:
            return None
        
        info = mt5.symbol_info(symbol)
        if info is None:
            return None
        
        return {
            "name": info.name,
            "description": info.description,
            "point": info.point,
            "digits": info.digits,
            "spread": info.spread,
            "bid": info.bid,
            "ask": info.ask
        }
