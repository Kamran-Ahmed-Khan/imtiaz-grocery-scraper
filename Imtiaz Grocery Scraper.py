# file: imtiaz_category_subcategory_products_final.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import json
import re

BASE_URL = "https://shop.imtiaz.com.pk"
OUT_FILE = "imtiaz_category_subcategory_products_final.xlsx"

opts = Options()
# opts.add_argument("--headless=new")  # Uncomment to run invisible
opts.add_argument("--disable-gpu")
opts.add_argument("--window-size=1920,1080")
opts.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 40)

print(f"🌐 Opening main site: {BASE_URL}")
driver.get(BASE_URL)
time.sleep(4)

# --- Unlock popup ---
try:
    wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'modal') or contains(text(),'Delivery')]")))
    print("✅ Popup detected")
except:
    print("⚠️ Popup not detected, maybe already unlocked")

try:
    express_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'EXPRESS') or contains(text(),'Delivery')]")))
    driver.execute_script("arguments[0].click();", express_btn)
    print("✅ Clicked EXPRESS/Delivery")
    time.sleep(1)
except:
    print("⚠️ Express button not clickable")

try:
    city_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'select__control')]")))
    driver.execute_script("arguments[0].click();", city_dropdown)
    karachi_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Karachi')]")))
    driver.execute_script("arguments[0].click();", karachi_option)
    print("✅ Selected Karachi city")
except:
    print("⚠️ City dropdown not clickable")

try:
    select_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Select') or contains(text(),'Continue')]")))
    driver.execute_script("arguments[0].click();", select_btn)
    print("✅ Clicked Continue - site unlocked!")
    time.sleep(5)
except:
    print("⚠️ Continue/Select button not found")

# --- Extract categories ---
print("🔎 Extracting main categories...")
categories = []
try:
    js = """
    const data = [];
    document.querySelectorAll("a[href*='/catalog/']").forEach(link => {
        const name = link.innerText.trim();
        const href = link.href;
        if (name && href && !data.some(d => d.href === href)) {
            data.push({category_name: name, category_url: href});
        }
    });
    return JSON.stringify(data);
    """
    categories = json.loads(driver.execute_script(js))
    print(f"✅ Found {len(categories)} categories")
except Exception as e:
    print("❌ Error extracting categories:", e)

# --- Visit each category & subcategory ---
rows = []

for cat in categories:
    category_name = cat["category_name"]
    category_url = cat["category_url"]
    print(f"\n➡️ Category: {category_name}")
    driver.get(category_url)
    time.sleep(4)

    # Sub-categories
    try:
        js_subs = """
        const subs = [];
        document.querySelectorAll("a[href*='/catalog/']").forEach(link => {
            const sub = link.innerText.trim();
            const href = link.href;
            if (sub && href && !subs.some(s => s.href === href)) {
                subs.push({sub_category: sub, sub_url: href});
            }
        });
        return JSON.stringify(subs);
        """
        subcats = json.loads(driver.execute_script(js_subs))
        subcats = [s for s in subcats if s["sub_category"].lower() != category_name.lower()]
        if not subcats:
            subcats = [{"sub_category": "", "sub_url": category_url}]
    except:
        subcats = [{"sub_category": "", "sub_url": category_url}]

    # Visit subcategories
    for sub in subcats:
        sub_name = sub["sub_category"]
        sub_url = sub["sub_url"]
        print(f"   🔹 Sub-category: {sub_name}")
        driver.get(sub_url)
        time.sleep(5)

        # Scroll to load products
        last_height = 0
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # --- Extract products ---
        try:
            js_products = """
            const data = [];
            document.querySelectorAll("div[data-testid='product-card'], div[class*='ProductCard'], div[class*='product']").forEach(card => {
                const title = card.querySelector("h3, [class*='name'], [class*='title']")?.innerText?.trim() || "";
                const price = card.querySelector("[class*='price'], .price, [data-testid*='price']")?.innerText?.trim() || "";
                if (title || price) data.push({title, price});
            });
            return JSON.stringify(data);
            """
            products = json.loads(driver.execute_script(js_products))

            for p in products:
                title = p["title"]
                price = p["price"]

                # Extract brand and size from title using regex
                size_match = re.search(r"(\d+\s?(g|ml|kg|l|L|pcs|Pack))", title)
                size = size_match.group(1) if size_match else ""

                # Brand = everything before size or first 2 words
                if size:
                    brand = title.split(size)[0].strip()
                else:
                    brand = " ".join(title.split()[:2]).strip()

                rows.append({
                    "category_name": category_name,
                    "sub_category": sub_name,
                    "brand_name": brand,
                    "size": size,
                    "price": price
                })

            print(f"      ✅ Copied {len(products)} products")
        except Exception as e:
            print("      ❌ JS Error:", e)
            rows.append({
                "category_name": category_name,
                "sub_category": sub_name,
                "brand_name": "",
                "size": "",
                "price": ""
            })

# --- Save to Excel ---
driver.quit()
if rows:
    df = pd.DataFrame(rows)
    df.to_excel(OUT_FILE, index=False)
    print(f"\n💾 Saved {len(df)} rows to {OUT_FILE}")
else:
    print("❌ No data extracted")

print("🏁 Done!")