import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 1. SETTINGS ---
options = Options()
# Removed "detach" so that the browser closes when the script finishes
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
driver = webdriver.Chrome(service=Service("chromedriver.exe"), options=options)

# --- 2. LOGIC TO GRAB DATA ---
def get_data_and_save(target_url, api_keyword, filename):
    """Navigates to a page, finds the hidden ID, and saves the JSON file."""
    driver.get_log("performance") # Clear old logs
    print(f"Opening: {target_url}")
    driver.get(target_url)
    
    time.sleep(12) # Wait for IMOS to load the data
    
    # Look through the background "noise" for the API link
    logs = driver.get_log("performance")
    found_id = None
    for entry in logs:
        log_message = json.loads(entry["message"])["message"]
        if "Network.requestWillBeSent" in log_message["method"]:
            url = log_message.get("params", {}).get("request", {}).get("url", "")
            if api_keyword in url:
                found_id = url.split("/")[-1].split("?")[0]
                break
    
    if found_id:
        # Build the secret API link and ask the browser to get the data
        api_url = f"https://imos.churchofjesuschrist.org/ws/auth-controller/api-v1/dynamic-reports/{api_keyword}{found_id}"
        data = driver.execute_script(f"return fetch('{api_url}').then(r => r.json())")
        
        # Write the data to a file in your folder
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"Done! {filename} is ready.")
    else:
        print(f"Could not find data for {filename}")

# --- 3. THE ACTUAL RUN ---
try:
    # A. Login
    driver.get("https://missionary.churchofjesuschrist.org")
    print("Please log in manually in the browser...")
    WebDriverWait(driver, 900).until(EC.url_contains("/portal/home"))

    # B. Get Areas
    get_data_and_save(
        "https://imos.churchofjesuschrist.org/dynamic-areas/#/list/default", 
        "areas/data/", 
        "areas_data.json"
    )

    # C. Get Roster
    get_data_and_save(
        "https://imos.churchofjesuschrist.org/dynamic-roster/#/list/default", 
        "roster/data/", 
        "roster_data.json"
    )

finally:
    # --- 4. CLEANUP ---
    print("Closing browser in 5 seconds...")
    time.sleep(5)
    driver.quit() # This closes the window and the icon on your taskbar