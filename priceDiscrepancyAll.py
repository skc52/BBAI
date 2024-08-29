import pandas as pd
from fuzzywuzzy import process
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from multiprocessing import Manager

# Preprocess names by cleaning and standardizing them
def preprocess_name(name):
    return name.lower().strip()

def find_best_match(name, choices):
    result = process.extractOne(name, choices)
    if result:
        match, score, _ = result
        return match if score > 90 else None
    return None

def find_best_match_chunk(chunk, name_mapping, df_b_names):
    for a_name in chunk:
        best_match = find_best_match(a_name, df_b_names)
        if best_match:
            print(best_match)
            name_mapping[a_name] = best_match

def main():
    file_a = 'grocery_store_products.xlsx'
    file_b = 'grocery_storeB_products.xlsx'

    df_a = pd.read_excel(file_a, sheet_name='Sheet1')
    df_b = pd.read_excel(file_b, sheet_name='Sheet1')

    df_a.rename(columns={'Current Price': 'Price_A'}, inplace=True)
    df_b.rename(columns={'Current Price': 'Price_B'}, inplace=True)

    df_a['Name'] = df_a['Name'].apply(preprocess_name)
    df_b['Name'] = df_b['Name'].apply(preprocess_name)

    df_a['Price_A'] = pd.to_numeric(df_a['Price_A'], errors='coerce')
    df_b['Price_B'] = pd.to_numeric(df_b['Price_B'], errors='coerce')

    chunks = np.array_split(df_a['Name'], 10)

    # Create a manager to handle shared data
    with Manager() as manager:
        name_mapping = manager.dict()

        with ProcessPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(find_best_match_chunk, chunk, name_mapping, df_b['Name']) for chunk in chunks]
            for future in futures:
                future.result()

        # Convert managed dictionary to a regular dictionary
        name_mapping = dict(name_mapping)

    df_a['Normalized Name'] = df_a['Name'].map(name_mapping)
    df_b['Normalized Name'] = df_b['Name']

    merged_df = pd.merge(df_a, df_b, left_on='Normalized Name', right_on='Normalized Name', how='left')

   

    # Calculate the price discrepancy where both prices are available
    merged_df['Price Discrepancy'] = merged_df.apply(
        lambda row: row['Price_B'] - row['Price_A'] if pd.notnull(row['Price_B']) and pd.notnull(row['Price_A']) else np.nan,
        axis=1
    )
    # Modify it to have abs value of discrepancies
    merged_df['Price Discrepancy'] = pd.to_numeric(merged_df['Price Discrepancy'], errors='coerce').abs()
    # Sort by descending order based on Price Discrepancy
    merged_df.sort_values(by='Price Discrepancy', ascending=False, inplace=True)

    # Filter out rows where Price Discrepancy is NaN
    final_df = merged_df[merged_df['Price Discrepancy'].notna()]

  

    # Save to Excel
    excel_filename = 'pricing_discrepancies.xlsx'
    final_df.to_excel(excel_filename, index=False)

    print(f"Pricing discrepancies have been saved to {excel_filename}")
    print(final_df[['Normalized Name', 'Price_A', 'Price_B', 'Price Discrepancy']])

if __name__ == '__main__':
    main()
