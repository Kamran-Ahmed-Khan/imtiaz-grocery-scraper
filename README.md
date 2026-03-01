Imtiaz Grocery Scraper
Overview
This Python project automates data extraction from the Imtiaz Online Store
 using Selenium WebDriver.
It scrapes all product categories, subcategories, brands, sizes, and prices — then saves the data to an Excel file for further analysis.

Features
Automatically unlocks the delivery popup and selects the city (Karachi).
Extracts all main categories and subcategories.
Collects detailed product info (brand, size, and price).
Exports clean, structured data to Excel (.xlsx) format.
Handles dynamic content with scroll-based product loading.

Requirements
Make sure you have these installed before running the script:
pip install selenium pandas openpyxl

Also ensure:
Google Chrome is installed on your system
ChromeDriver is available and matches your Chrome version

How to Run
Clone this repository:
git clone https://github.com/your-username/imtiaz-grocery-scraper.git
cd imtiaz-grocery-scraper

Run the scraper:
python imtiaz_category_subcategory_products_final.py

Output will be saved as:
imtiaz_category_subcategory_products_final.xlsx
Output Example
Category	Sub-category	Brand Name	Size	Price
Edible Grocery	Oils & Ghee	Dalda Cooking Oil	5L	Rs. 3,200
Snacks	Biscuits	Oreo Original	100g	Rs. 150

Technologies Used
Python
Selenium
Pandas
Excel (via OpenPyXL)

Disclaimer
This project is for educational and research purposes only.
Please check the website’s terms of service before scraping.

This project is for educational and research purposes only.
Please check the website’s terms of service before scraping.
