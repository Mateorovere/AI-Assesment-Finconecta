"""
mercado_scraper.py

A web scraper to collect product data from Mercado Libre using BeautifulSoup.
This script scrapes a category page, extracts individual product URLs, visits each,
and retrieves the product name, price, and description.

Usage:
    Run the script manually or schedule it using Cron.

Author: Mateo Rovere
Date: 2025-02-07
"""

import logging
import sys
import json
from functions import scrape_category

# Configure logging for debugging and audit purposes.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    """
    Main entry point for the scraper.

    This function can be scheduled to run automatically using a Cron job.
    It scrapes a predefined category page and saves the results to a JSON file.
    """
    # Example category URL: change as needed.
    category_url = 'https://listado.mercadolibre.com.ar/celulares'
    
    try:
        products = scrape_category(category_url)
        # Save the scraped data to a JSON file.
        with open('scraped_products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=4)
        logging.info("Scraping completed successfully. Data saved to scraped_products.json")
    except Exception as e:
        logging.error(f"An error occurred during scraping: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
