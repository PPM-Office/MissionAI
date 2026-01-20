// --- CONFIGURATION ---
// 🔴 UPDATE THIS URL EVERY TIME YOU RESTART NGROK
var NGROK_URL = "https://your-ngrok-url.ngrok-free.app"; 

// ==========================================
// 1. THE LISTENER (The Magic Link)
// ==========================================
// This receives the data from Python when the scraper finishes
function doPost(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var json = JSON.parse(e.postData.contents);
  
  if (json.missionaries) updateSheet("Missionaries", json.missionaries, 
    ["Name", "ID", "Companion ID", "Area ID", "Gender", "Position", "Arrived", "Departing"]);
    
  if (json.areas) updateSheet("Areas", json.areas, 
    ["Area Name", "Area ID", "District ID", "Zone ID", "Car VIN", "Car Model"]);

  return ContentService.createTextOutput("Success");
}

function updateSheet(name, data, headers) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(name);
  if (!sheet) sheet = ss.insertSheet(name);
  sheet.clear();
  
  var rows = [];
  if (name === "Missionaries") {
    rows = data.map(m => [m.fullName, m.missionaryId, m.companionshipId, m.areaId, m.gender, m.position, m.dateArrived, m.dateDeparting]);
  } else {
    rows = data.map(a => [a.name, a.areaId, a.districtId, a.zoneId, (a.vehicle ? a.vehicle.vin : "No Car"), (a.vehicle ? a.vehicle.model : "")]);
  }
  
  sheet.appendRow(headers);
  if (rows.length > 0) sheet.getRange(2, 1, rows.length, headers.length).setValues(rows);
}

// ==========================================
// 2. THE MENU & UI
// ==========================================
function onOpen() {
  SpreadsheetApp.getUi().createMenu('Mission AI')
    .addItem('💬 Open Assistant', 'showSidebar')
    .addSeparator()
    .addItem('🔄 Sync with IMOS (Iron Curtain)', 'triggerAutoSync')
    .addToUi();
}

function showSidebar() {
  var html = HtmlService.createHtmlOutputFromFile('Sidebar').setTitle('Mission Brain').setWidth(350);
  SpreadsheetApp.getUi().showSidebar(html);
}

// ==========================================
// 3. THE BRIDGE (Calls to Python)
// ==========================================

// CALL 1: Chatbot
function sendToPython(userMessage) {
  var payload = { "message": userMessage };
  var options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload),
    'muteHttpExceptions': true
  };
  try {
    var response = UrlFetchApp.fetch(NGROK_URL + "/chat", options);
    var json = JSON.parse(response.getContentText());
    return json.reply;
  } catch (e) { return "🔴 Connection Failed: " + e.message; }
}

// CALL 2: Auto Sync Trigger
function triggerAutoSync() {
  var options = { 'method': 'post', 'muteHttpExceptions': true };
  try {
    SpreadsheetApp.getUi().alert("🚀 Launching Iron Curtain on your computer...");
    var response = UrlFetchApp.fetch(NGROK_URL + "/run_auto_sync", options);
    var json = JSON.parse(response.getContentText());
    return json.reply;
  } catch (e) {
    return "🔴 Error: " + e.message;
  }
}