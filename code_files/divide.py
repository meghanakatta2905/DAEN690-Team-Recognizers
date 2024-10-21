import pandas as pd

# Load the product data from the full CSV file
# Update 'full_product_data.csv' with your actual file path
df = pd.read_csv('C:/Users/cheth/OneDrive/Desktop/capstone/class_api_result_data.csv')

# Group the product data by 'INDID'
grouped = df.groupby("INDID")

# Loop through each group and save it as a separate CSV file
for indid, group in grouped:
    # Create a file name using the Industry ID
    file_name = f"class_data_industry_{indid}.csv"

    # Save each group's data to a CSV file
    group.to_csv(file_name, index=False)

    # Output the file name to keep track of what's saved
    print(f"Saved file: {file_name}")
