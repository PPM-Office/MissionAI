import time
import logging
import subprocess
import sys
import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- CONFIG ---
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("MissionBrain_Commander")

# 🟢 CONFIGURATION
# If you are using Ngrok for Chat, keep the server running.
# If you are using Mailbox for Sync, we check that too.

def summon_soldier():
    """ 
    Launches the Iron Curtain (imos_scraper.py) as a completely separate process.
    This ensures the Server/Chatbot NEVER freezes.
    """
    logger.info("⚔️ Commander: Summoning the Iron Curtain...")
    
    # Calculate path to the soldier file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, 'imos_scraper.py')
    
    # Launch it!
    # 'python' might need to be 'py' depending on your system, but sys.executable finds the right one.
    subprocess.Popen([sys.executable, script_path])
    
    return "Soldier Deployed."

# --- CHATBOT ENDPOINT ---
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_msg = data.get("message", "")
    logger.info(f"💬 Chat: {user_msg}")
    
    # [AI LOGIC GOES HERE LATER]
    return jsonify({"reply": f"I heard: {user_msg}"})

# --- SYNC ENDPOINT (Triggered via Sidebar Button) ---
@app.route('/run_auto_sync', methods=['POST'])
def run_sync():
    summon_soldier()
    return jsonify({"reply": "✅ Sync Initiated in Background."})

if __name__ == '__main__':
    logger.info("🫡 Commander is Online. Listening for orders...")
    app.run(port=5000)