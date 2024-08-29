import json
from bs4 import BeautifulSoup
import pandas as pd
import time  # Import the time module

# Function to extract product information from HTML
def extract_product_info(html_data):
    soup = BeautifulSoup(html_data, 'html.parser')
    products = []

    for product_div in soup.find_all('div', class_='product-grid-item'):
        product_info = {}

        # Extract product name
        name_tag = product_div.find('h3')
        product_info['Name'] = name_tag.get_text(strip=True) if name_tag else 'N/A'
        
        # Extract product price
        price_tag = product_div.find('p', class_='precio')
        product_info['Current Price'] = price_tag.get_text(strip=True).replace('$', '') if price_tag else '0'

        # Append the product info to the list
        products.append(product_info)
    
    return products

def main():
    # Start timing
    start_time = time.time()

    # Load data from JSON
    with open('grocery_store_b.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Initialize a list to hold product information
    product_list = []

    # Process each item in the data
    for item in data:
        html_data = item.get('data', {}).get('html_data', '')
        product_list.extend(extract_product_info(html_data))
    
    # Convert the list of products to a DataFrame
    df = pd.DataFrame(product_list)

    # Remove duplicate rows based on the Name column
    df = df.drop_duplicates(subset='Name')

    # Define the Excel filename
    excel_filename = 'grocery_storeB_products.xlsx'

    # Save the DataFrame to an Excel file
    df.to_excel(excel_filename, index=False)

    # End timing
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Data has been saved to {excel_filename}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")

if __name__ == '__main__':
    main()
