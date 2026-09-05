"""
NSE Instruments Catalog and Sector Classifications for Indian Equities.
Includes Nifty 50 constituents, Upstox instrument key mapping, and sector categories.
"""

from typing import Dict, List, Any

NSE_INSTRUMENTS: List[Dict[str, Any]] = [
    {
        "symbol": "RELIANCE.NS",
        "name": "Reliance Industries Ltd",
        "sector": "Energy & Oil",
        "upstox_key": "NSE_EQ|INE002A01018",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "TCS.NS",
        "name": "Tata Consultancy Services Ltd",
        "sector": "Information Technology",
        "upstox_key": "NSE_EQ|INE467B01029",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "HDFCBANK.NS",
        "name": "HDFC Bank Ltd",
        "sector": "Financial Services",
        "upstox_key": "NSE_EQ|INE040A01034",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "INFY.NS",
        "name": "Infosys Ltd",
        "sector": "Information Technology",
        "upstox_key": "NSE_EQ|INE009A01021",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "ICICIBANK.NS",
        "name": "ICICI Bank Ltd",
        "sector": "Financial Services",
        "upstox_key": "NSE_EQ|INE090A01021",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "HINDUNILVR.NS",
        "name": "Hindustan Unilever Ltd",
        "sector": "Consumer Goods",
        "upstox_key": "NSE_EQ|INE030A01027",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "ITC.NS",
        "name": "ITC Ltd",
        "sector": "Consumer Goods",
        "upstox_key": "NSE_EQ|INE154A01025",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "SBIN.NS",
        "name": "State Bank of India",
        "sector": "Financial Services",
        "upstox_key": "NSE_EQ|INE062A01020",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "BHARTIARTL.NS",
        "name": "Bharti Airtel Ltd",
        "sector": "Telecommunication",
        "upstox_key": "NSE_EQ|INE397D01024",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "LT.NS",
        "name": "Larsen & Toubro Ltd",
        "sector": "Construction",
        "upstox_key": "NSE_EQ|INE018A01030",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "KOTAKBANK.NS",
        "name": "Kotak Mahindra Bank Ltd",
        "sector": "Financial Services",
        "upstox_key": "NSE_EQ|INE237A01028",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "AXISBANK.NS",
        "name": "Axis Bank Ltd",
        "sector": "Financial Services",
        "upstox_key": "NSE_EQ|INE238A01034",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "ASIANPAINT.NS",
        "name": "Asian Paints Ltd",
        "sector": "Consumer Goods",
        "upstox_key": "NSE_EQ|INE021A01026",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "MARUTI.NS",
        "name": "Maruti Suzuki India Ltd",
        "sector": "Automobile",
        "upstox_key": "NSE_EQ|INE585B01010",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "SUNPHARMA.NS",
        "name": "Sun Pharmaceutical Industries Ltd",
        "sector": "Healthcare",
        "upstox_key": "NSE_EQ|INE044A01036",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "TITAN.NS",
        "name": "Titan Company Ltd",
        "sector": "Consumer Goods",
        "upstox_key": "NSE_EQ|INE280A01028",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "BAJFINANCE.NS",
        "name": "Bajaj Finance Ltd",
        "sector": "Financial Services",
        "upstox_key": "NSE_EQ|INE296A01024",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "TATAMOTORS.NS",
        "name": "Tata Motors Ltd",
        "sector": "Automobile",
        "upstox_key": "NSE_EQ|INE155A01022",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "ULTRACEMCO.NS",
        "name": "UltraTech Cement Ltd",
        "sector": "Construction",
        "upstox_key": "NSE_EQ|INE481G01011",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "WIPRO.NS",
        "name": "Wipro Ltd",
        "sector": "Information Technology",
        "upstox_key": "NSE_EQ|INE075A01022",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "NTPC.NS",
        "name": "NTPC Ltd",
        "sector": "Power",
        "upstox_key": "NSE_EQ|INE733E01010",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "POWERGRID.NS",
        "name": "Power Grid Corporation of India Ltd",
        "sector": "Power",
        "upstox_key": "NSE_EQ|INE752E01010",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "M&M.NS",
        "name": "Mahindra & Mahindra Ltd",
        "sector": "Automobile",
        "upstox_key": "NSE_EQ|INE101A01026",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "TATASTEEL.NS",
        "name": "Tata Steel Ltd",
        "sector": "Metals",
        "upstox_key": "NSE_EQ|INE081A01020",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "HCLTECH.NS",
        "name": "HCL Technologies Ltd",
        "sector": "Information Technology",
        "upstox_key": "NSE_EQ|INE860A01027",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "COALINDIA.NS",
        "name": "Coal India Ltd",
        "sector": "Energy & Oil",
        "upstox_key": "NSE_EQ|INE522F01014",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "ONGC.NS",
        "name": "Oil & Natural Gas Corp Ltd",
        "sector": "Energy & Oil",
        "upstox_key": "NSE_EQ|INE213A01029",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "ADANIENT.NS",
        "name": "Adani Enterprises Ltd",
        "sector": "Metals",
        "upstox_key": "NSE_EQ|INE423A01024",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "ADANIPORTS.NS",
        "name": "Adani Ports and SEZ Ltd",
        "sector": "Services",
        "upstox_key": "NSE_EQ|INE742F01042",
        "lot_size": 1,
        "market_cap": "Large"
    },
    {
        "symbol": "BAJAJFINSV.NS",
        "name": "Bajaj Finserv Ltd",
        "sector": "Financial Services",
        "upstox_key": "NSE_EQ|INE918I01026",
        "lot_size": 1,
        "market_cap": "Large"
    }
]

INSTRUMENT_LOOKUP: Dict[str, Dict[str, Any]] = {
    inst["symbol"]: inst for inst in NSE_INSTRUMENTS
}

SECTOR_MAP: Dict[str, str] = {
    inst["symbol"]: inst["sector"] for inst in NSE_INSTRUMENTS
}

PRESETS = {
    "NIFTY_TOP_10": [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
        "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "LT.NS"
    ],
    "TECH_AND_FINANCE": [
        "TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS",
        "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "BAJFINANCE.NS"
    ],
    "BALANCED_DEFENSIVE": [
        "HINDUNILVR.NS", "ITC.NS", "SUNPHARMA.NS", "NTPC.NS", "POWERGRID.NS",
        "TCS.NS", "HDFCBANK.NS", "RELIANCE.NS"
    ],
    "GROWTH_MOMENTUM": [
        "TATAMOTORS.NS", "M&M.NS", "BAJFINANCE.NS", "TITAN.NS",
        "BHARTIARTL.NS", "LT.NS", "RELIANCE.NS", "ICICIBANK.NS"
    ]
}

def get_instrument(symbol: str) -> Dict[str, Any]:
    return INSTRUMENT_LOOKUP.get(symbol, {
        "symbol": symbol,
        "name": symbol.replace(".NS", ""),
        "sector": "General",
        "upstox_key": f"NSE_EQ|{symbol.replace('.NS', '')}",
        "lot_size": 1,
        "market_cap": "Mid"
    })

def get_all_symbols() -> List[str]:
    return [inst["symbol"] for inst in NSE_INSTRUMENTS]

def get_sector_for_symbol(symbol: str) -> str:
    return SECTOR_MAP.get(symbol, "Other")
