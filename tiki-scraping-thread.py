import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Custom headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://tiki.vn/",  # Adding the referer may also help
}

base_url = "https://tiki.vn/api/personalish/v1/blocks/listings"
product_detail_url = "https://tiki.vn/api/v2/products"

# List of category IDs to scrape (update to include electronics or other categories)
category_ids = [18328,4624,6225,6541,18330,8264,18332,18334,6246,6226,18346,6215,8265,6212,6213,18342,18344,25706,68202,68205,68208]  

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
    }

    all_products = []
    while True:
        print(f"Fetching page {params['page']} for category {category_id}...")
        try:
            response = requests.get(base_url, headers=headers, params=params)
            time.sleep(0.8)  # Pause between category requests to avoid being blocked

            if response.status_code == 200:
                data = response.json()
                if "data" in data and data["data"]:
                    products = data["data"]
                    all_products.extend(products)
                    print(f"Found {len(products)} products on page {params['page']}.")
                    params["page"] += 1
                else:
                    print(f"No more products found for category {category_id} on page {params['page']}.")
                    break
            else:
                print(f"Request failed with status code {response.status_code} for category {category_id} on page {params['page']}.")
                break
        except Exception as e:
            print(f"Error fetching products for category {category_id}: {e}")
            break

    return all_products

# Function to fetch detailed data for a product
def fetch_product_details(product_id):
    print(f"Fetching details for product ID: {product_id}...")
    try:
        response = requests.get(f"{product_detail_url}/{product_id}", headers=headers)
        time.sleep(0.8)  # Pause between product detail requests to avoid being blocked

        if response.status_code == 200:
            data = response.json()
            return {
                "short_description": data.get("short_description", ""),
                "description": data.get("description", ""),
                "specifications": data.get("specifications", []),
                "seller_name": data.get("current_seller", {}).get("name", ""),
                "stock_status": data.get("inventory_status", ""),
            }
        else:
            print(f"Failed to fetch details for product ID {product_id}. Status code: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error fetching details for product ID {product_id}: {e}")
        return {}

# Main function to fetch data for multiple categories with multithreading
def scrape_categories(category_ids):
    for category_id in category_ids:
        print(f"Scraping category ID: {category_id}...")
        products = fetch_products_for_category(category_id)

        # Using ThreadPoolExecutor to fetch product details concurrently
        detailed_products = []
        with ThreadPoolExecutor(max_workers=8) as executor:  # Adjust `max_workers` as needed
            future_to_product = {executor.submit(fetch_product_details, product["id"]): product for product in products}

            for future in as_completed(future_to_product):
                product = future_to_product[future]
                try:
                    details = future.result()
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
                    product_data.update(details)
                    detailed_products.append(product_data)
                except Exception as e:
                    print(f"Error processing product: {e}")

        # Save data for the category with the product count
        output_data = {
            "total_products": len(detailed_products),
            "products": detailed_products
        }
        output_file = f"tiki_category_{category_id}_products_thread.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"Data for category {category_id} saved to {output_file} with {output_data['total_products']} products.")

# Run the scraper
scrape_categories(category_ids)
