# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a cryptocurrency trading data collection and analysis system focused on Bitcoin (BTC/USD) price data from Polygon.io. The system fetches, combines, and analyzes historical price data at 5-minute intervals.

## Architecture

The codebase is organized into three main components:

1. **Data Collection** (`Data/PolygonIO/`): Fetches historical OHLCV data from Polygon.io API
2. **Data Processing** (`Data/PolygonIO/`): Combines multiple data files and handles overlaps
3. **Data Analysis** (`Data/Analyse/`): Compares and validates data formats

### Key Components

- `getData.py`: Main data fetching script with rate limiting and incremental updates
- `combineData.py`: Merges multiple JSON files chronologically while handling overlaps  
- `compareJsonParquet.py`: Validates data integrity between JSON and Parquet formats
- `btcusd_5min_all_PolygonIO.json`: Combined historical price data file

## Dependencies

Required Python packages:
- pandas (with pyarrow for Parquet support)
- requests
- Standard library: os, json, re, time, datetime

Install dependencies:
```bash
pip install pandas pyarrow requests
```

## Common Development Commands

### Data Collection
```bash
cd Data/PolygonIO/
python getData.py
```

### Data Combination
```bash
cd Data/PolygonIO/
python combineData.py
```

### Data Validation
```bash
cd Data/Analyse/
python compareJsonParquet.py
```

## Configuration

API configuration is in `getData.py`:
- `API_KEY`: Polygon.io API key (currently hardcoded - should be moved to environment variable)
- `TICKER`: "X:BTCUSD" (Bitcoin USD pair)
- `TIMEFRAME_VALUE`: 5 (minutes)
- `LIMIT`: 50000 (maximum records per API call)
- `SLEEP_INTERVAL`: 12 seconds (rate limiting)

## Data Structure

The JSON data follows Polygon.io's aggregates format:
- `v`: Volume
- `vw`: Volume weighted average price  
- `o`: Open price
- `c`: Close price
- `h`: High price
- `l`: Low price
- `t`: Timestamp (Unix milliseconds)
- `n`: Number of transactions

## Important Notes

- The system implements intelligent resumption - it finds the latest data point and continues from there
- Rate limiting is enforced (5 requests per minute)
- Data files use naming convention: `btcusd_{timeframe}_{start_date}_{end_date}_PolygonIO.json`
- The combination script handles overlapping data to prevent duplicates
- API key is currently hardcoded and should be moved to environment variables for security