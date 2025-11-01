import pandas as pd
import numpy as np
from typing import List, Dict, Tuple


class PointAndFigureCalculator:
    def __init__(self, box_size: float = 10, reversal_amount: int = 3):
        """
        Initialize Point and Figure calculator
        
        Args:
            box_size: Size of each box (in points/pips)
            reversal_amount: Number of boxes needed for reversal
        """
        self.box_size = box_size
        self.reversal_amount = reversal_amount
    
    def calculate(self, df: pd.DataFrame) -> Dict:
        """
        Calculate Point and Figure chart from price data
        
        Args:
            df: DataFrame with columns ['time', 'high', 'low', 'close']
        
        Returns:
            Dictionary with PnF chart data
        """
        if df is None or len(df) == 0:
            return {"columns": [], "error": "No data"}
        
        columns = []
        current_column = {
            "type": None,  # 'X' or 'O'
            "boxes": [],
            "start_price": None,
            "end_price": None,
            "start_time": None,
            "end_time": None
        }
        
        # Start with the first price
        first_price = df.iloc[0]['close']
        start_box = self._price_to_box(first_price)
        
        # Determine initial direction by looking at next few bars
        initial_direction = self._get_initial_direction(df)
        
        current_column["type"] = initial_direction
        current_column["boxes"] = [start_box]
        current_column["start_price"] = first_price
        current_column["start_time"] = df.iloc[0]['time']
        
        current_box = start_box
        
        for idx, row in df.iterrows():
            high = row['high']
            low = row['low']
            time = row['time']
            
            if current_column["type"] == 'X':  # Rising column
                # Check for continuation (new highs)
                high_box = self._price_to_box(high)
                if high_box > current_box:
                    # Add boxes
                    for box in range(current_box + 1, high_box + 1):
                        if box not in current_column["boxes"]:
                            current_column["boxes"].append(box)
                    current_box = high_box
                    current_column["end_price"] = high
                    current_column["end_time"] = time
                
                # Check for reversal (new lows)
                low_box = self._price_to_box(low)
                reversal_threshold = current_box - self.reversal_amount
                if low_box <= reversal_threshold:
                    # Save current column
                    columns.append(current_column.copy())
                    
                    # Start new O column
                    current_column = {
                        "type": 'O',
                        "boxes": [],
                        "start_price": low,
                        "end_price": low,
                        "start_time": time,
                        "end_time": time
                    }
                    
                    # Fill boxes downward
                    for box in range(current_box - 1, low_box - 1, -1):
                        current_column["boxes"].append(box)
                    
                    current_box = low_box
            
            else:  # 'O' - Falling column
                # Check for continuation (new lows)
                low_box = self._price_to_box(low)
                if low_box < current_box:
                    # Add boxes
                    for box in range(current_box - 1, low_box - 1, -1):
                        if box not in current_column["boxes"]:
                            current_column["boxes"].append(box)
                    current_box = low_box
                    current_column["end_price"] = low
                    current_column["end_time"] = time
                
                # Check for reversal (new highs)
                high_box = self._price_to_box(high)
                reversal_threshold = current_box + self.reversal_amount
                if high_box >= reversal_threshold:
                    # Save current column
                    columns.append(current_column.copy())
                    
                    # Start new X column
                    current_column = {
                        "type": 'X',
                        "boxes": [],
                        "start_price": high,
                        "end_price": high,
                        "start_time": time,
                        "end_time": time
                    }
                    
                    # Fill boxes upward
                    for box in range(current_box + 1, high_box + 1):
                        current_column["boxes"].append(box)
                    
                    current_box = high_box
        
        # Add the last column
        if len(current_column["boxes"]) > 0:
            columns.append(current_column)
        
        # Format output
        return self._format_chart_data(columns)
    
    def _price_to_box(self, price: float) -> int:
        """Convert price to box number"""
        return int(price / self.box_size)
    
    def _box_to_price(self, box: int) -> float:
        """Convert box number to price"""
        return box * self.box_size
    
    def _get_initial_direction(self, df: pd.DataFrame) -> str:
        """Determine initial direction from first few bars"""
        if len(df) < 2:
            return 'X'
        
        # Look at first 5 bars or available bars
        look_ahead = min(5, len(df))
        first_price = df.iloc[0]['close']
        avg_price = df.iloc[1:look_ahead]['close'].mean()
        
        return 'X' if avg_price > first_price else 'O'
    
    def _format_chart_data(self, columns: List[Dict]) -> Dict:
        """Format chart data for frontend"""
        if len(columns) == 0:
            return {"columns": [], "min_box": 0, "max_box": 0}
        
        # Find min and max box values
        all_boxes = []
        for col in columns:
            all_boxes.extend(col["boxes"])
        
        min_box = min(all_boxes) if all_boxes else 0
        max_box = max(all_boxes) if all_boxes else 0
        
        # Format columns for frontend
        formatted_columns = []
        for col in columns:
            formatted_columns.append({
                "type": col["type"],
                "boxes": sorted(col["boxes"]),
                "start_price": self._box_to_price(min(col["boxes"])),
                "end_price": self._box_to_price(max(col["boxes"])),
                "start_time": col["start_time"].isoformat() if pd.notna(col["start_time"]) else None,
                "end_time": col["end_time"].isoformat() if pd.notna(col["end_time"]) else None
            })
        
        return {
            "columns": formatted_columns,
            "min_box": min_box,
            "max_box": max_box,
            "box_size": self.box_size,
            "reversal_amount": self.reversal_amount,
            "min_price": self._box_to_price(min_box),
            "max_price": self._box_to_price(max_box)
        }
