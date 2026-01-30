import time
import json
import os
import sys
import random  # Added this - you need it for the fireworks!
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 1. SETTINGS ---
options = Options()
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
driver_path = r"C:\Users\2011484-MTS\OneDrive - Church of Jesus Christ\Attachments\MissionAI\scraper\chromedriver.exe"
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Color codes for PowerShell
GREEN = "\033[32m"
WHITE = "\033[37m"
RESET = "\033[0m"
YELLOW = "\033[33m"

# --- 2. FUNCTIONS ---

def get_data_and_save(target_url, api_keyword, filename):
    """Navigates to a page, finds the hidden ID, and saves the JSON file."""
    driver.get_log("performance") 
    print(f"Opening: {target_url}")
    driver.get(target_url)
    
    time.sleep(12) 
    
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
        api_url = f"https://imos.churchofjesuschrist.org/ws/auth-controller/api-v1/dynamic-reports/{api_keyword}{found_id}"
        data = driver.execute_script(f"return fetch('{api_url}').then(r => r.json())")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"Done! {filename} is ready.")
    else:
        print(f"Could not find data for {filename}")

def random_pos(low, high):
    return random.randint(low, high)

def philly_mega_animation():
    skyline = [
        r"    |          |          ",
        r"   / \        [ ]      _   ",
        r"  /   \      [   ]    | |  ",
        r" |     | ||  |   | __| |__",
        r" |_____|_||__|___||_______|"
    ]
    stadium = [
        r"  _______________________  ",
        r" /  [  E A G L E S  ]   \ ",
        r"|_________________________|",
        r"  |  [|||||||||||||]   |  "
    ]

    try:
        # STAGE 1: THE DRIVE
        for i in range(40):
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"\n{GREEN}   💚🦅 GO BIRDS 🦅💚{RESET}\n")
            for line in skyline: print(" " * 15 + line)
            for line in stadium: print(" " * 15 + line)
            road_padding = " " * (i % 50)
            print(f"{WHITE}{'-'*60}{RESET}")
            print(f"{road_padding}  __{YELLOW}o{WHITE}_{YELLOW}o{WHITE}>")
            print(f"{WHITE}{'-'*60}{RESET}")
            time.sleep(0.05)

        # STAGE 2: THE FIREWORKS
        for i in range(60):
            os.system('cls' if os.name == 'nt' else 'clear')
            if i % 3 == 0:
                print("\n" + " " * random_pos(20, 50) + f"{YELLOW}* . *{RESET}")
                print(" " * random_pos(20, 50) + f"{GREEN}  FLY  {RESET}")
            else:
                print("\n" + " " * 30 + f"{GREEN}FLY EAGLES FLY!{RESET}")
            for line in skyline: print(" " * 15 + line)
            stadium_color = GREEN if i % 2 == 0 else WHITE
            for line in stadium: print(stadium_color + " " * 15 + line + RESET)
            print(f"\n{GREEN}" + " " * 20 + "E - A - G - L - E - S  EAGLES!" + RESET)
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

# --- 3. THE ACTUAL RUN ---
if __name__ == "__main__":
    os.system('') # Enable ANSI colors in PowerShell
    
    try:
        # A. Login
        driver.get("https://missionary.churchofjesuschrist.org")
        print("Please log in manually in the browser...")
        WebDriverWait(driver, 6969).until(EC.url_contains("/portal/home"))

        # B. Get Areas
        get_data_and_save(
            "https://imos.churchofjesuschrist.org/dynamic-areas/#/list/default", 
            "areas/data/", 
            r"C:\Users\2011484-MTS\OneDrive - Church of Jesus Christ\Attachments\MissionAI\data\areas.json"
        )

        # C. Get Roster
        get_data_and_save(
            "https://imos.churchofjesuschrist.org/dynamic-roster/#/list/default", 
            "roster/data/", 
            r"C:\Users\2011484-MTS\OneDrive - Church of Jesus Christ\Attachments\MissionAI\data\missionaries.json"
        )
        
        # --- NEW ORDER: CLOSE FIRST, THEN CELEBRATE ---
        print("\nScraping complete! Closing browser...")
        driver.quit() # The Chrome window disappears here

        print("💚🦅 GO BIRDS 🦅💚")
        philly_mega_animation() # Animation starts in the clean terminal
        
        print("😎THE AUTOMATION IS COMPLETE😎")
        print("🏁YOU MAY NOW CLOSE THIS WINDOW🏁")
        print("HAPPY PLANNING :)")

    except Exception as e:
        print(f"An error occurred during the run: {e}")
        # Ensure driver closes even if there's an error
        try:
            driver.quit()
        except:
            pass

    finally:
        # Keep the terminal open for a few seconds so you can see the "Done" message
        time.sleep(5)