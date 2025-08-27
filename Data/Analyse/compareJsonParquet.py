import os
import json
import pandas as pd

def compare_file_counts():
    """
    Compares the number of records in a JSON file and a Parquet file
    located one directory above the script.
    """
    print("--- Starting File Comparison ---")

    # --- SETUP ---
    # Get the directory where the script is running
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go one level up to the parent directory
    parent_dir = os.path.dirname(script_dir)

    # Define the full paths to the files
    json_filename = "btcusd_5min_all_PolygonIO.json"
    parquet_filename = "btcusd_5min_all_PolygonIO.parquet"
    json_filepath = os.path.join(parent_dir, json_filename)
    parquet_filepath = os.path.join(parent_dir, parquet_filename)

    json_count = 0
    parquet_count = 0
    
    # --- PROCESS JSON FILE ---
    print(f"\nAttempting to read JSON file: {json_filepath}")
    try:
        with open(json_filepath, 'r') as f:
            # Load the entire JSON structure from the file
            data = json.load(f)
            # Get the list associated with the "results" key. If key doesn't exist, return empty list.
            results_list = data.get("results", [])
            # Count the number of items in that list
            json_count = len(results_list)
        print(f" -> Success: Found {json_count} items in '{json_filename}'.")
    except FileNotFoundError:
        print(f" -> ERROR: JSON file not found at the expected location.")
    except json.JSONDecodeError:
        print(f" -> ERROR: The file '{json_filename}' is not a valid JSON file.")
    except KeyError:
        print(" -> ERROR: The JSON file does not contain a 'results' key.")
    except Exception as e:
        print(f" -> An unexpected error occurred: {e}")

    # --- PROCESS PARQUET FILE ---
    print(f"\nAttempting to read Parquet file: {parquet_filepath}")
    try:
        # Read the Parquet file into a pandas DataFrame
        df = pd.read_parquet(parquet_filepath)
        # The number of items is the number of rows in the DataFrame
        parquet_count = len(df)
        print(f" -> Success: Found {parquet_count} items in '{parquet_filename}'.")
    except FileNotFoundError:
        print(f" -> ERROR: Parquet file not found at the expected location.")
    except Exception as e:
        # This can catch errors from the pyarrow engine if the file is corrupt
        print(f" -> An unexpected error occurred while reading the Parquet file: {e}")


    # --- FINAL COMPARISON AND REPORT ---
    print("\n--- Final Report ---")
    print(f"Total items counted in JSON:   {json_count}")
    print(f"Total items counted in Parquet: {parquet_count}")

    # Only declare a match if both counts are greater than zero
    if json_count > 0 and parquet_count > 0:
        if json_count == parquet_count:
            print("\n✅ Result: The files contain the same number of items.")
        else:
            print(f"\n❌ Result: The files DO NOT contain the same number of items. Difference: {abs(json_count - parquet_count)}")
    else:
        print("\n⚠️ Result: Could not perform a valid comparison because one or both files could not be read or were empty.")

if __name__ == "__main__":
    # Add a check for required libraries
    try:
        import pandas
    except ImportError:
        print("ERROR: The 'pandas' library is required but not installed.")
        print("Please install it by running: pip install pandas pyarrow")
    else:
        compare_file_counts()

