import requests
import json
import time

# Define the category and base URL
category_id = 24306
base_url = "https://tiki.vn/api/personalish/v1/blocks/listings"

# Parameters for pagination and API request
params = {
    "limit": 40,
    "include": "advertisement",
    "aggregations": 2,
    "version": "home-persionalized",
    "trackity_id": "7a06d2b7-bbf3-0fa6-31f1-b26251aa2d80",
    "category": category_id,
    "page": 1,
    "urlKey": "nha-sach-tiki"
}

# Custom headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://tiki.vn/",  # Adding the referer may also help
}

# Store all filtered products
all_products = []

# Fetch all pages
while True:
    print(f"Fetching page {params['page']}...")
    response = requests.get(base_url, headers=headers, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"Failed to parse JSON response on page {params['page']}. Response text:\n{response.text}")
            break
        
        # Check if there are products in the response
        if "data" in data and data["data"]:
            products = data["data"]
            
            # Filter and keep only necessary fields
            for product in products:
                filtered_product = {
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
                all_products.append(filtered_product)

            print(f"Found {len(products)} products on page {params['page']}.")
            params["page"] += 1  # Move to the next page
            time.sleep(1)  # Pause to avoid overwhelming the server
        else:
            print(f"No more products found on page {params['page']}.")
            break
    else:
        print(f"Request failed with status code {response.status_code} on page {params['page']}.")
        print("Response text:", response.text)
        break

# Save the filtered data to a JSON file
output_file = f"tiki_{category_id}_products.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump({"total_products": len(all_products), "products": all_products}, f, ensure_ascii=False, indent=2)

print(f"Data saved to {output_file}")
