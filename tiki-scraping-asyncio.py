import aiohttp
import asyncio
import json
import time
import sys
from aiohttp import ClientSession

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# Custom headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://tiki.vn/",
}

base_url = "https://tiki.vn/api/personalish/v1/blocks/listings"
product_detail_url = "https://tiki.vn/api/v2/products"
category_ids = [1836, 18358, 625, 626, 126]  # Replace with your actual category IDs

# Semaphore to limit concurrent requests
semaphore = asyncio.Semaphore(10)  # Limit the number of concurrent requests


async def fetch_products_for_category(session: ClientSession, category_id):
    """Fetch all products for a given category."""
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
        async with semaphore:
            print(f"Fetching page {params['page']} for category {category_id}...")
            async with session.get(base_url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if "data" in data and data["data"]:
                        products = data["data"]
                        all_products.extend(products)
                        print(f"Found {len(products)} products on page {params['page']}.")
                        params["page"] += 1
                        await asyncio.sleep(0.8)  # Prevent overwhelming the server
                    else:
                        print(f"No more products found for category {category_id} on page {params['page']}.")
                        break
                else:
                    print(f"Request failed with status {response.status} for category {category_id} on page {params['page']}.")
                    break
    return all_products


async def fetch_product_details(session: ClientSession, product):
    """Fetch detailed information for a single product."""
    product_id = product.get("id")
    print(f"Fetching details for product ID: {product_id}...")
    async with semaphore:
        try:
            async with session.get(f"{product_detail_url}/{product_id}", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    detailed_info = {
                        "short_description": data.get("short_description", ""),
                        "description": data.get("description", ""),
                        "specifications": data.get("specifications", []),
                        "seller_name": data.get("current_seller", {}).get("name", ""),
                        "stock_status": data.get("inventory_status", ""),
                    }
                    product.update(detailed_info)
                else:
                    print(f"Failed to fetch details for product ID {product_id}. Status: {response.status}")
        except Exception as e:
            print(f"Error fetching details for product ID {product_id}: {e}")
    return product


async def scrape_category(session: ClientSession, category_id):
    """Scrape all products for a specific category."""
    products = await fetch_products_for_category(session, category_id)
    print(f"Found {len(products)} products for category {category_id}. Fetching details...")

    detailed_products = await asyncio.gather(*[fetch_product_details(session, product) for product in products])

    # Save the results to a file
    output_file = f"tiki_category_{category_id}_products.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"length": len(detailed_products), "products": detailed_products}, f, ensure_ascii=False, indent=2)
    print(f"Data for category {category_id} saved to {output_file} with {len(detailed_products)} products.")


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_category(session, category_id) for category_id in category_ids]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
