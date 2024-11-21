import requests
import json
import time
import random
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logging
logging.basicConfig(level=logging.INFO, filename="scraper.log", filemode="w", format="%(asctime)s - %(message)s")

# Custom headers to mimic a browser request
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

base_url = "https://tiki.vn/api/personalish/v1/blocks/listings"
product_detail_url = "https://tiki.vn/api/v2/products"

# List of category IDs to scrape
category_ids = [1975,8411,1977, 8438,4227,8443,2980,2981,8444,23120,67442,24002,8445,24052,24074,69617,24294,6826,6827,24306,8413,24306, 10803,10806, 10804, 67485,8428,24258,67647,67703,67648,69498, 24128,24142,3323,24164,69627,67651,67700,24064,24092,24098,24102]

# Function to fetch all products for a specific category
def fetch_products_for_category(category_id):
    params = {
        "limit": 60,
        "include": "advertisement",
        "aggregations": 2,
        "version": "home-persionalized",
        "trackity_id": "7a06d2b7-bbf3-0fa6-31f1-b26251aa2d80",
        "category": category_id,
        "page": 1,
    }

    all_products = []
    MAX_PAGES = 100  # Maximum number of pages to fetch

    while params["page"] <= MAX_PAGES:
        logging.info(f"Fetching page {params['page']} for category {category_id}...")
        try:
            headers = {"User-Agent": random.choice(user_agents)}
            response = requests.get(base_url, headers=headers, params=params, timeout=10)
            time.sleep(random.uniform(1, 3))  # Random delay to mimic human behavior

            if response.status_code == 200:
                data = response.json()
                if "data" in data and data["data"]:
                    products = data["data"]
                    all_products.extend(products)
                    logging.info(f"Found {len(products)} products on page {params['page']}.")
                    params["page"] += 1
                else:
                    logging.info(f"No more products found for category {category_id} on page {params['page']}.")
                    break
            else:
                logging.warning(f"Request failed with status code {response.status_code} for category {category_id} on page {params['page']}.")
                break
        except Exception as e:
            logging.error(f"Error fetching products for category {category_id}: {e}")
            break

    return all_products

# Function to fetch detailed data for a product
def fetch_product_details(product_id):
    logging.info(f"Fetching details for product ID: {product_id}...")
    try:
        headers = {"User-Agent": random.choice(user_agents)}
        response = requests.get(f"{product_detail_url}/{product_id}", headers=headers, timeout=10)
        time.sleep(random.uniform(1, 2))  # Random delay between product detail requests

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
            logging.warning(f"Failed to fetch details for product ID {product_id}. Status code: {response.status_code}")
            return {}
    except Exception as e:
        logging.error(f"Error fetching details for product ID {product_id}: {e}")
        return {}

# Main function to fetch data for multiple categories with multithreading
def scrape_categories(category_ids):
    for category_id in category_ids:
        logging.info(f"Scraping category ID: {category_id}...")
        products = fetch_products_for_category(category_id)

        # Using ThreadPoolExecutor to fetch product details concurrently
        detailed_products = []
        with ThreadPoolExecutor(max_workers=4) as executor:  # Adjust `max_workers` as needed
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
                    logging.error(f"Error processing product: {e}")

        # Save data for the category with the product count
        output_data = {
            "total_products": len(detailed_products),
            "products": detailed_products
        }
        output_file = f"tiki_category_{category_id}_products_thread.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        logging.info(f"Data for category {category_id} saved to {output_file} with {output_data['total_products']} products.")

# Run the scraper
if __name__ == "__main__":
    scrape_categories(category_ids)
