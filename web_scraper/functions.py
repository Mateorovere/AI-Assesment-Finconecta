import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict

def get_page_content(url: str) -> str:
    """
    Retrieves the HTML content of a given URL.

    Args:
        url (str): URL of the page to scrape.

    Returns:
        str: HTML content of the page.

    Raises:
        Exception: If the HTTP request fails.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses.
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching URL {url}: {e}")
        raise

def parse_product_page(html: str) -> Dict:
    """
    Parses the HTML content of a Mercado Libre product page to extract key details.

    Args:
        html (str): HTML content of the product page.

    Returns:
        dict: Dictionary containing 'name', 'price', and 'description'.
    """
    soup = BeautifulSoup(html, 'html.parser')
    product = {}

    # Extract product name.
    try:
        title_tag = soup.find('h1', class_='ui-pdp-title')
        product['name'] = title_tag.get_text(strip=True) if title_tag else None
        if product['name'] is None:
            logging.warning("Product name not found.")
    except Exception as e:
        logging.error("Error parsing product name: %s", e)
        product['name'] = None

    # Extract product price.
    try:
        # Note: The price may be split into multiple parts or change class names.
        price_tag = soup.find('span', class_='andes-money-amount__fraction')
        price_text = price_tag.get_text(strip=True).replace('.', '') if price_tag else None
        product['price'] = price_text
        if product['price'] is None:
            logging.warning("Product price not found.")
    except Exception as e:
        logging.error("Error parsing product price: %s", e)
        product['price'] = None

    # Extract product description.
    try:
        desc_tag = soup.find('p', class_='ui-pdp-description__content')
        product['description'] = desc_tag.get_text(strip=True) if desc_tag else None
        if product['description'] is None:
            logging.warning("Product description not found.")
    except Exception as e:
        logging.error("Error parsing product description: %s", e)
        product['description'] = None

    return product

def scrape_product(url: str) -> Dict:
    """
    Scrapes a single product page from Mercado Libre.

    Args:
        url (str): URL of the product page.

    Returns:
        dict: A dictionary containing the product details.
    """
    logging.info(f"Scraping product page: {url}")
    html = get_page_content(url)
    return parse_product_page(html)

def scrape_category(url: str) -> List[Dict]:
    """
    Scrapes a Mercado Libre category page to gather data for each listed product.

    Args:
        url (str): URL of the category page.

    Returns:
        list: A list of dictionaries, each containing details of a product.
    """
    logging.info(f"Scraping category page: {url}")
    html = get_page_content(url)
    soup = BeautifulSoup(html, 'html.parser')
    products = []

    # Locate product links on the category page.
    # The CSS selectors might change if Mercado Libre updates their site.
    product_link_tags = soup.find_all('a', class_='poly-component__title')
    if not product_link_tags:
        logging.warning("No product links found on category page.")

    for tag in product_link_tags:
        product_url = tag.get('href')
        if product_url:
            try:
                product_data = scrape_product(product_url)
                products.append(product_data)
            except Exception as e:
                logging.error(f"Error scraping product at {product_url}: {e}")

    return products
    #[TODO] Add pagination to catch all the data