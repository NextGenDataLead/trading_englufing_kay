import os
import requests
import json
import time
from datetime import datetime, date, timedelta
import re

# --- CONFIGURATION ---
# IMPORTANT: Replace "YOUR_API_KEY" with your actual Polygon.io API key.
API_KEY = "Kb6vPmc_7ZJLwan_yxsyyZCUHB1KxPrY" 
# The ticker you want to fetch data for.
TICKER = "X:BTCUSD"
# The timeframe for the data aggregation (e.g., 'minute', 'hour', 'day').
# Note: The 'limit' parameter might need adjustment for smaller timeframes.
TIMEFRAME_VALUE = 5
TIMEFRAME_UNIT = "minute"
# The subfolder where data files are stored.
DATA_FOLDER = "Data"
# The maximum number of results to fetch per API call. 50000 is the max.
LIMIT = 50000
# Rate limit: 5 requests per minute means 1 request every 12 seconds.
SLEEP_INTERVAL = 12

def get_latest_end_date(folder_path: str) -> date | None:
    """
    Scans a directory for data files and determines the latest end date from filenames.

    The expected filename format is 'btcusd_{timeframe}_{start_date}_{end_date}_PolygonIO.json'.
    Example: 'btcusd_1day_2023-06-11_2023-07-15_PolygonIO.json'

    Args:
        folder_path: The path to the directory containing the data files.

    Returns:
        A datetime.date object representing the latest end date found, 
        or None if no valid files are found.
    """
    latest_date = None
    # Regex to extract the end date (YYYY-MM-DD) from the filename.
    date_pattern = re.compile(r"_(\d{4}-\d{2}-\d{2})_PolygonIO\.json$")

    if not os.path.exists(folder_path):
        print(f"Data folder '{folder_path}' not found. It will be created.")
        os.makedirs(folder_path)
        return None

    for filename in os.listdir(folder_path):
        match = date_pattern.search(filename)
        if match:
            try:
                end_date_str = match.group(1)
                current_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                if latest_date is None or current_date > latest_date:
                    latest_date = current_date
            except ValueError:
                print(f"Warning: Could not parse date from filename: {filename}")
                continue
    
    if latest_date:
        print(f"Latest end date found in existing files: {latest_date}")
    else:
        print("No existing data files found.")
        
    return latest_date

def fetch_and_save_data(start_date: date, end_date: date) -> tuple[date | None, int, int | None]:
    """
    Fetches data from the Polygon.io API for a given date range and saves it to a file.

    Args:
        start_date: The start date for the data fetch.
        end_date: The end date for the data fetch.

    Returns:
        A tuple containing:
        - The actual end date of the data received from the API (or None if no data).
        - The number of results fetched.
        - The Unix millisecond timestamp of the last record fetched (or None).
    """
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    # Construct the API URL
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{TICKER}/range/{TIMEFRAME_VALUE}/"
        f"{TIMEFRAME_UNIT}/{start_date_str}/{end_date_str}"
        f"?adjusted=true&sort=asc&limit={LIMIT}&apiKey={API_KEY}"
    )

    print(f"\nFetching data from {start_date_str} to {end_date_str}...")
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None, 0, None

    data = response.json()
    results_count = data.get("resultsCount", 0)

    # Check if the API returned any results
    if results_count == 0 or "results" not in data:
        return None, 0, None

    # Determine the actual start and end dates from the returned data
    results = data["results"]
    actual_start_ts = results[0]['t']
    actual_end_ts = results[-1]['t']

    # Polygon timestamps are in milliseconds, so divide by 1000
    actual_start_date = datetime.fromtimestamp(actual_start_ts / 1000).date()
    actual_end_date = datetime.fromtimestamp(actual_end_ts / 1000).date()
    
    print(f"Successfully fetched {results_count} data points from {actual_start_date} to {actual_end_date}.")

    # Create the filename based on the content of the data
    filename_start_str = actual_start_date.strftime("%Y-%m-%d")
    filename_end_str = actual_end_date.strftime("%Y-%m-%d")
    filename = f"btcusd_{TIMEFRAME_VALUE}{TIMEFRAME_UNIT}_{filename_start_str}_{filename_end_str}_PolygonIO.json"
    filepath = os.path.join(DATA_FOLDER, filename)

    # Save the data to a JSON file
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"Data saved to: {filepath}")
    
    return actual_end_date, results_count, actual_end_ts

def main():
    """Main function to orchestrate the data fetching loop."""
    if API_KEY == "YOUR_API_KEY":
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! PLEASE REPLACE 'YOUR_API_KEY' with your actual   !!!")
        print("!!! Polygon.io API key in the script configuration.  !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return

    today = date.today()
    
    # Determine the starting date for the first API call
    start_date = get_latest_end_date(DATA_FOLDER)
    
    if start_date is None:
        # If no data exists, start from 2 years ago (Polygon's limit)
        start_date = today - timedelta(days=730)
        print(f"No start date found. Starting from two years ago: {start_date}")
    else:
        # Resume data fetch from the last known date to get any new intra-day data.
        print(f"Resuming data fetch from: {start_date}")

    latest_record_timestamp = None
    
    # Loop until we have fetched data up to today
    while start_date <= today:
        # Fetch data and get the actual end date and number of results
        new_end_date, results_count, last_ts_in_batch = fetch_and_save_data(start_date, today)

        # ---- ROBUST STOPPING CONDITIONS ----
        
        # Condition 1: API returns no results. We are fully caught up. This is the main exit point.
        if results_count == 0:
            print("API returned 0 results. Caught up to the latest available data. Exiting.")
            break
        
        # Condition 2: Stagnation. We are fetching the same last record repeatedly.
        # This prevents an infinite loop if the last page of data has exactly `LIMIT` results.
        if last_ts_in_batch is not None and last_ts_in_batch == latest_record_timestamp:
            print("Fetched the same last data point again. Assuming the dataset is complete. Exiting.")
            break

        # Update state for the next loop.
        if new_end_date is not None:
             latest_record_timestamp = last_ts_in_batch
             start_date = new_end_date
        else:
            # Should not happen if results_count > 0, but as a safeguard:
            print("Error: Received results but could not determine a new date. Exiting.")
            break

        # IMPORTANT: Wait before the next API call to respect the rate limit.
        print(f"Waiting for {SLEEP_INTERVAL} seconds before next request...")
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main()
