
import json
import pandas as pd

# Load data from 'grocery_store_a.json' with specified encoding
with open('grocery_store_a.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Initialize a list to hold product information
product_list = []

# Iterate through all items in the JSON data
for item in data:
    # Access the 'data' part
    element = item.get("data", {})
    product_info = element.get('product', {})
    
    # Extract relevant information with default values
    name = product_info.get('name', 'N/A')

    # Extract price information with nested key checks
    price_info = product_info.get('priceInfo', {})
    
    # Check if priceInfo exists before checking deeper
    if isinstance(price_info, dict):
        
        # Check if currentPrice exists within 'priceInfo'
        if isinstance(price_info.get('currentPrice', {}), dict):
            current_price = price_info['currentPrice'].get('price', 0) 
        else:
            current_price = 0  
        
    else:
        # If priceInfo itself is missing or not a dict, set current price value to 0
        current_price = 0
        
    
    # Append product info to the list
    product_list.append({
        'Name': name,
        'Current Price': current_price,
    })

# Convert the list of products to a DataFrame
df = pd.DataFrame(product_list)

# Remove duplicate rows based on the 'Name' column
df = df.drop_duplicates(subset='Name')

# Define the Excel filename
excel_filename = 'grocery_store_products.xlsx'

# Save the DataFrame to an Excel file
df.to_excel(excel_filename, index=False)

print(f"Data has been saved to {excel_filename}")

