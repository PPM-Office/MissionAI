import json
import os
import logging
import requests

# --- CONFIG ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("IMOS_MagicSync")

# 🟢 YOUR DEPLOYED GOOGLE SCRIPT URL:
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbw90WyhwAwTSDafNtBu5_u22Vx5j2EWYH53tY90rpwVZNtXakrcsbqSv7ePJxTMdBLf/exec"

def push_data_to_sheet():
    """ 
    Sends the local data to Google Sheets via the 'Magic Link' (Web App).
    No credentials.json required.
    """
    try:
        logger.info("🚀 Preparing Payload for Google Sheets...")
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, 'data')
        
        payload = {
            "missionaries": [],
            "areas": []
        }

        # Load Missionaries
        m_path = os.path.join(data_dir, 'missionaries.json')
        if os.path.exists(m_path):
            with open(m_path, 'r', encoding='utf-8') as f:
                raw = json.load(f)
                payload["missionaries"] = raw if isinstance(raw, list) else raw.get("missionaries", [])

        # Load Areas
        a_path = os.path.join(data_dir, 'areas.json')
        if os.path.exists(a_path):
            with open(a_path, 'r', encoding='utf-8') as f:
                raw = json.load(f)
                payload["areas"] = raw if isinstance(raw, list) else raw.get("areas", [])

        # SEND TO GOOGLE
        logger.info("📡 Sending data to Google Sheets...")
        
        # We use a POST request to send the JSON data to your script
        response = requests.post(WEB_APP_URL, json=payload)

        if response.status_code == 200 or response.status_code == 302:
            # Google often returns 302 redirects for scripts, which requests handles automatically
            logger.info("✅ SUCCESS! Data uploaded to Google Sheets.")
            return "Success"
        else:
            raise Exception(f"Google Error: {response.status_code} - {response.text}")

    except Exception as e:
        logger.error(f"❌ Sync Failed: {e}")
        # If requests is missing, remind the user
        if "No module named 'requests'" in str(e):
            logger.error("💡 HINT: Run 'pip install requests' in your terminal!")
        raise e

if __name__ == "__main__":
    push_data_to_sheet()