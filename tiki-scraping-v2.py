# import requests
# import json
# import time

# # Custom headers to mimic a browser request
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
#     "Accept": "application/json, text/plain, */*",
#     "Accept-Language": "en-US,en;q=0.5",
#     "Referer": "https://tiki.vn/",  # Adding the referer may also help
# }

# base_url = "https://tiki.vn/api/personalish/v1/blocks/listings"
# product_detail_url = "https://tiki.vn/api/v2/products"

# # List of category IDs to scrape
# category_ids = [8322, 11222, 12345]  # Replace with your actual category IDs

# # Function to fetch all products for a specific category
# def fetch_products_for_category(category_id):
#     params = {
#         "limit": 40,
#         "include": "advertisement",
#         "aggregations": 2,
#         "version": "home-persionalized",
#         "trackity_id": "7a06d2b7-bbf3-0fa6-31f1-b26251aa2d80",
#         "category": category_id,
#         "page": 1,
#         "urlKey": "nha-sach-tiki"  # Update dynamically if required
#     }

#     all_products = []
#     while True:
#         print(f"Fetching page {params['page']} for category {category_id}...")
#         response = requests.get(base_url, headers=headers, params=params)
        
#         if response.status_code == 200:
#             data = response.json()
#             if "data" in data and data["data"]:
#                 products = data["data"]
#                 all_products.extend(products)
#                 print(f"Found {len(products)} products on page {params['page']}.")
#                 params["page"] += 1
#                 time.sleep(1)  # Pause to avoid overwhelming the server
#             else:
#                 print(f"No more products found for category {category_id} on page {params['page']}.")
#                 break
#         else:
#             print(f"Request failed with status code {response.status_code} for category {category_id} on page {params['page']}.")
#             break

#     return all_products

# # Function to fetch detailed data for a product
# def fetch_product_details(product_id):
#     print(f"Fetching details for product ID: {product_id}...")
#     try:
#         response = requests.get(f"{product_detail_url}/{product_id}", headers=headers)
#         if response.status_code == 200:
#             data = response.json()
#             # Extract additional fields you need
#             detailed_info = {
#                 "short_description": data.get("short_description", ""),
#                 "description": data.get("description", ""),
#                 "specifications": data.get("specifications", []),  # Product specifications
#                 "seller_name": data.get("current_seller", {}).get("name", ""),
#                 "stock_status": data.get("inventory_status", "")
#             }
#             return detailed_info
#         else:
#             print(f"Failed to fetch details for product ID {product_id}. Status code: {response.status_code}")
#             return {}
#     except Exception as e:
#         print(f"Error fetching details for product ID {product_id}: {e}")
#         return {}

# # Main function to fetch data for multiple categories
# def scrape_categories(category_ids):
#     all_data = {}
    
#     for category_id in category_ids:
#         print(f"Scraping category ID: {category_id}...")
#         products = fetch_products_for_category(category_id)
        
#         # Fetch additional details for each product
#         detailed_products = []
#         for product in products:
#             product_data = {
#                 "id": product.get("id"),
#                 "name": product.get("name"),
#                 "price": product.get("price"),
#                 "discount_rate": product.get("discount_rate"),
#                 "rating_average": product.get("rating_average"),
#                 "review_count": product.get("review_count"),
#                 "order_count": product.get("quantity_sold", {}).get("value", 0) if product.get("quantity_sold") else 0,
#                 "thumbnail_url": product.get("thumbnail_url"),
#                 "primary_category_path": product.get("primary_category_path"),
#                 "availability": product.get("availability"),
#             }

#             # Fetch additional details
#             details = fetch_product_details(product_data["id"])
#             product_data.update(details)
#             detailed_products.append(product_data)
#             time.sleep(1)  # Small delay to avoid being blocked

#         # Save data for the category
#         all_data[category_id] = detailed_products
#         output_file = f"tiki_category_{category_id}_products.json"
#         with open(output_file, "w", encoding="utf-8") as f:
#             json.dump(detailed_products, f, ensure_ascii=False, indent=2)
#         print(f"Data for category {category_id} saved to {output_file}")

#     # Save all data to a single file if needed
#     with open("tiki_all_categories_products.json", "w", encoding="utf-8") as f:
#         json.dump(all_data, f, ensure_ascii=False, indent=2)
#     print("All data saved to tiki_all_categories_products.json")

# # Run the scraper
# scrape_categories(category_ids)


import requests
import json
import time

# Custom headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://tiki.vn/",  # Adding the referer may also help
}

base_url = "https://tiki.vn/api/personalish/v1/blocks/listings"
product_detail_url = "https://tiki.vn/api/v2/products"

# List of category IDs to scrape
category_ids = [1836, 18358, 625, 626, 126]  # Replace with your actual category IDs

# Function to fetch all products for a specific category
def fetch_products_for_category(category_id):
    params = {
        "limit": 40,
        "include": "advertisement",
        "aggregations": 2,
        "version": "home-persionalized",
        "trackity_id": "7a06d2b7-bbf3-0fa6-31f1-b26251aa2d80",
        "category": category_id,
        "page": 1,
        "urlKey": "nha-sach-tiki"  # Update dynamically if required
    }

    all_products = []
    while True:
        print(f"Fetching page {params['page']} for category {category_id}...")
        response = requests.get(base_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]:
                products = data["data"]
                all_products.extend(products)
                print(f"Found {len(products)} products on page {params['page']}.")
                params["page"] += 1
                time.sleep(1)  # Pause to avoid overwhelming the server
            else:
                print(f"No more products found for category {category_id} on page {params['page']}.")
                break
        else:
            print(f"Request failed with status code {response.status_code} for category {category_id} on page {params['page']}.")
            break

    return all_products

# Function to fetch detailed data for a product
def fetch_product_details(product_id):
    print(f"Fetching details for product ID: {product_id}...")
    try:
        response = requests.get(f"{product_detail_url}/{product_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Extract additional fields you need
            detailed_info = {
                "short_description": data.get("short_description", ""),
                "description": data.get("description", ""),
                "specifications": data.get("specifications", []),  # Product specifications
                "seller_name": data.get("current_seller", {}).get("name", ""),
                "stock_status": data.get("inventory_status", "")
            }
            return detailed_info
        else:
            print(f"Failed to fetch details for product ID {product_id}. Status code: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error fetching details for product ID {product_id}: {e}")
        return {}

# Main function to fetch data for multiple categories
def scrape_categories(category_ids):
    for category_id in category_ids:
        print(f"Scraping category ID: {category_id}...")
        products = fetch_products_for_category(category_id)
        
        # Fetch additional details for each product
        detailed_products = []
        for product in products:
            product_data = {
                "id": product.get("id"),
                "name": product.get("name"),
                "price": product.get("price"),
                "discount_rate": product.get("discount_rate"),
                "rating_average": product.get("rating_average"),
                "review_count": product.get("review_count"),
                "order_count": product.get("quantity_sold", {}).get("value", 0) if product.get("quantity_sold") else 0,
                "thumbnail_url": product.get("thumbnail_url"),
                "primary_category_path": product.get("primary_category_path"),
                "availability": product.get("availability"),
            }

            # Fetch additional details
            details = fetch_product_details(product_data["id"])
            product_data.update(details)
            detailed_products.append(product_data)
            time.sleep(1)  # Small delay to avoid being blocked

        # Save data for the category with the product count
        output_data = {
            "length": len(detailed_products),
            "products": detailed_products
        }
        output_file = f"tiki_category_{category_id}_products.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"Data for category {category_id} saved to {output_file} with {output_data['length']} products.")

# Run the scraper
scrape_categories(category_ids)

