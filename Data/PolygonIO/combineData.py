import os
import json
import re
from datetime import datetime

# --- CONFIGURATION ---
# The subfolder where your individual data files are stored.
DATA_FOLDER = "Data"
# The name of the final, combined output file.
OUTPUT_FILE = "combined_btcusd_data.json"

def find_and_sort_files(folder_path: str) -> list[str]:
    """
    Finds all JSON data files in the specified folder and sorts them chronologically.

    The sorting is based on the start date found in the filename. The expected
    filename format is '..._{start_date}_{end_date}_PolygonIO.json'.

    Args:
        folder_path: The path to the directory containing the data files.

    Returns:
        A list of filenames, sorted from the earliest start date to the latest.
        Returns an empty list if the folder doesn't exist or contains no valid files.
    """
    files_with_dates = []
    # Regex to extract the start date (the first YYYY-MM-DD pattern).
    date_pattern = re.compile(r"_(\d{4}-\d{2}-\d{2})_")

    if not os.path.exists(folder_path):
        print(f"Error: Data folder '{folder_path}' not found.")
        return []

    for filename in os.listdir(folder_path):
        if filename.endswith("_PolygonIO.json"):
            match = date_pattern.search(filename)
            if match:
                try:
                    start_date_str = match.group(1)
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                    files_with_dates.append((start_date, filename))
                except (ValueError, IndexError):
                    print(f"Warning: Could not parse start date from filename: {filename}")
                    continue
    
    # Sort the list of tuples based on the date (the first element)
    files_with_dates.sort()
    
    # Return just the sorted filenames
    sorted_filenames = [filename for date, filename in files_with_dates]
    
    if sorted_filenames:
        print(f"Found and sorted {len(sorted_filenames)} data files.")
    else:
        print("No valid data files found to combine.")
        
    return sorted_filenames

def combine_data_files(sorted_files: list[str], folder_path: str) -> list[dict]:
    """
    Combines results from sorted JSON files, ensuring no data overlap.

    Args:
        sorted_files: A list of filenames, pre-sorted chronologically.
        folder_path: The path to the directory containing the files.

    Returns:
        A single list containing all unique, combined results.
    """
    combined_results = []
    latest_timestamp = -1  # Use a value guaranteed to be less than any real timestamp

    for filename in sorted_files:
        filepath = os.path.join(folder_path, filename)
        print(f"Processing file: {filename}...")
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"  - Error reading or parsing {filename}: {e}")
            continue

        results = data.get("results")
        if not results or not isinstance(results, list):
            print(f"  - No 'results' list found in {filename}. Skipping.")
            continue
            
        new_records_added = 0
        for record in results:
            # Ensure the record is valid and has a timestamp 't'
            if isinstance(record, dict) and 't' in record:
                # Only add the record if its timestamp is newer than the last one we added
                if record['t'] > latest_timestamp:
                    combined_results.append(record)
                    latest_timestamp = record['t']
                    new_records_added += 1
            else:
                 print(f"  - Warning: Found an invalid record in {filename}")

        print(f"  - Added {new_records_added} new records.")

    return combined_results

def main():
    """Main function to orchestrate the file combination process."""
    # 1. Find and sort all data files chronologically
    sorted_files = find_and_sort_files(DATA_FOLDER)
    
    if not sorted_files:
        return # Exit if no files were found

    # 2. Combine the data, handling overlaps
    final_results = combine_data_files(sorted_files, DATA_FOLDER)
    
    if not final_results:
        print("\nNo data was combined. Exiting.")
        return

    # 3. Prepare the final output structure
    output_data = {"results": final_results}
    
    # 4. Save the combined data to the output file
    try:
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(output_data, f, indent=4)
        print(f"\nSuccessfully combined {len(final_results)} records into '{OUTPUT_FILE}'.")
    except IOError as e:
        print(f"\nError writing to output file '{OUTPUT_FILE}': {e}")

if __name__ == "__main__":
    main()
