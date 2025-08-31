from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from time import sleep
import re
import os
import json
from utils import convert_to_filename

# -----------------------------
# Helpers
# -----------------------------
def split_cell_list(text: str):
    """Split merged ward names into list, remove parentheses content."""
    return [s.strip() for s in re.split(r"\s*và\s*|,\s*", re.sub(r"\s*\([^)]*\)", "", text)) if s.strip()]

def extract_cell(text: str):
    """Extract ward level (phường/xã/thị trấn) + name."""
    level_of_ward = re.findall(r"\(([^)]*)\)", text)[0].strip()
    name = re.sub(r"\s*\([^)]*\)", "", text).strip()
    return f"{level_of_ward} {name}"

def collect_all_province(container : WebElement, driver : webdriver.Chrome) -> WebElement:
    """Scroll through a Tabulator container and return unique rows (elements)."""
    seen = set()
    collected = []
    last_height = -1

    while True:
        rows = container.find_elements(By.CLASS_NAME, "tabulator-row")
        for row in rows:
            try:
                row_text = row.text.strip()
            except:
                row_text = False
            if row_text and row_text not in seen:
                seen.add(row_text)
                try:
                    cells = row.find_elements(By.CLASS_NAME, "tabulator-cell")
                except:
                    cells = []
                province_name = cells[1].text.strip()
                province_list = split_cell_list(cells[2].text.strip())
                collected.append((province_name, province_list))

        # scroll down a bit
        driver.execute_script("arguments[0].scrollTop += 150;", container)
        sleep(0.4)

        # check scroll position
        new_height = driver.execute_script("return arguments[0].scrollTop;", container)
        max_height = driver.execute_script("return arguments[0].scrollHeight;", container)
        if new_height == last_height or new_height >= max_height:
            driver.execute_script("arguments[0].scrollTop = 0;", container)
            break
        last_height = new_height

    return collected

def collect_all_ward(container : WebElement, driver : webdriver.Chrome) -> list:
    seen = set()
    ward_dict = {}
    last_height = -1
    while True:
        rows = container.find_elements(By.CLASS_NAME, "tabulator-row")
        for row in rows:
            try:
                row_text = row.text.strip()
            except:
                row_text = False
            if row_text and row_text not in seen:
                seen.add(row_text)
                try:
                    cells = row.find_elements(By.CLASS_NAME, "tabulator-cell")
                except:
                    cells = []
                ward_name = cells[1].text.strip()
                real_name = extract_cell(ward_name)
                before_merger = cells[2].text.strip()
                list_of_old_ward = split_cell_list(before_merger)
                ward_dict[real_name] = list_of_old_ward

        # scroll down a bit
        driver.execute_script("arguments[0].scrollTop += 250;", container)
        sleep(0.4)

        # check scroll position
        new_height = driver.execute_script("return arguments[0].scrollTop;", container)
        max_height = driver.execute_script("return arguments[0].scrollHeight;", container)
        if new_height == last_height or new_height >= max_height:
            driver.execute_script("arguments[0].scrollTop = 0;", container)
            break
        last_height = new_height

    return ward_dict
# -----------------------------
# Main
# -----------------------------
def run():
    driver = webdriver.Chrome()
    driver.get("https://sapnhap.bando.com.vn/")
    sleep(5)

    # Collect all provinces
    province_container = driver.find_element(By.CSS_SELECTOR, "#bangtinh .tabulator-tableholder")
    list_of_province = collect_all_province(province_container, driver)

    # Prepare output folder
    output_base = "data/map_2025"
    os.makedirs(output_base, exist_ok=True)

    # Loop through each province
    for province_name in list_of_province:
        print(f"Processing {province_name[0]} ...")

        # Click the province row
        province_container = driver.find_element(By.ID, "bangtinh")
        rows = province_container.find_elements(By.CLASS_NAME, "tabulator-row")
        for row in rows:
            if province_name[0] in row.text:
                row.click()
                break

        sleep(3)

        # Collect wards for this province
        ward_container = driver.find_element(By.CSS_SELECTOR, "#bangxa .tabulator-tableholder")
        ward_dict = collect_all_ward(ward_container, driver)

        # Save to JSON
        filename = convert_to_filename(province_name[0])
        filepath = os.path.join(output_base, f"{filename}.json")

        province_data = {
            "name": province_name[0],
            "old_province": province_name[1],
            "ward": ward_dict
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(province_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Saved {province_name} to {filepath}")

    driver.quit()
