import pandas as pd
import glob
import os

# 1. Define the folder path containing your 10 CSV files
folder_path = '.' 

# 2. Use glob to find all CSV files in that folder
file_pattern = os.path.join(folder_path, '*.csv')
csv_files = glob.glob(file_pattern)

print(f"Found {len(csv_files)} CSV files. Merging...")

# 3. Read each CSV file into a dataframe and store them in a list
dataframes = []
for file in csv_files:
    try:
        # Read the file
        df = pd.read_csv(file)
        
        # --- NEW CODE ADDED HERE ---
        # Add a new column with the base name of the file
        df['Source_File'] = os.path.basename(file)
        
        dataframes.append(df)
        print(f"Successfully read: {os.path.basename(file)}")
    except Exception as e:
        print(f"Error reading {file}: {e}")

# 4. Concatenate all dataframes into a single one
if dataframes:
    merged_dataframe = pd.concat(dataframes, ignore_index=True)

    # 5. Save the merged dataframe to a new CSV file
    output_filename = "merged_output_with_source.csv"
    merged_dataframe.to_csv(output_filename, index=False)
    print(f"\nAll files successfully merged into '{output_filename}'!")
else:
    print("No dataframes to merge.")
