from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import time

driver = webdriver.Chrome()
driver.get("https://index.ros.org/?search_packages=true#kilted")

time.sleep(5)

container = driver.find_element(
    By.CSS_SELECTOR,
    "#packages-table .tabulator-tableholder"
)

seen_rows = set()
all_rows = []

while True:
    rows = driver.find_elements(
        By.CSS_SELECTOR,
        "#packages-table .tabulator-row"
    )

    for row in rows:
        cells = row.find_elements(By.CSS_SELECTOR, ".tabulator-cell")
        row_data = [cell.text.strip() for cell in cells]

        # Use the row contents themselves as unique identifier
        row_key = tuple(row_data)

        if row_data and row_key not in seen_rows:
            seen_rows.add(row_key)
            all_rows.append(row_data)
            print(row_data)

    previous_scroll = driver.execute_script(
        "return arguments[0].scrollTop",
        container
    )

    driver.execute_script(
        "arguments[0].scrollTop = arguments[0].scrollTop + 300",
        container
    )

    time.sleep(1)

    new_scroll = driver.execute_script(
        "return arguments[0].scrollTop",
        container
    )

    # Stop when scroll no longer changes
    if new_scroll == previous_scroll:
        break

driver.quit()

csv_file = "ros_packages.csv"

with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    for row in all_rows:
        writer.writerow(row)

print(f"Saved {len(all_rows)} rows to {csv_file}")