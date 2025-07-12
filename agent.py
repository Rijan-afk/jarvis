import asyncio
import websockets
import json
import os
import subprocess
import platform
import datetime
import requests
from dotenv import load_dotenv
import google.generativeai as genai

# .env फ़ाइल से API कुंजी लोड करें
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

# Gemini API कॉन्फ़िगरेशन
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    print("त्रुटि: GEMINI_API_KEY पर्यावरण वेरिएबल सेट नहीं है।")
    model = None

# --- सिस्टम कमांड और ऐप लॉन्चिंग ---
def open_application(app_name):
    """
    ऑपरेटिंग सिस्टम के आधार पर एक एप्लिकेशन खोलने का प्रयास करता है।
    यह फ़ंक्शन केवल उदाहरण के लिए है और सभी ऐप्स को कवर नहीं करेगा।
    """
    system = platform.system()
    app_name_lower = app_name.lower()

    try:
        if system == "Windows":
            # सामान्य Windows ऐप्स
            if "chrome" in app_name_lower or "browser" in app_name_lower:
                subprocess.Popen(["start", "chrome"], shell=True)
            elif "notepad" in app_name_lower:
                subprocess.Popen(["notepad.exe"])
            elif "calculator" in app_name_lower:
                subprocess.Popen(["calc.exe"])
            elif "paint" in app_name_lower:
                subprocess.Popen(["mspaint.exe"])
            elif "word" in app_name_lower or "microsoft word" in app_name_lower:
                subprocess.Popen(["start", "winword"])
            elif "excel" in app_name_lower or "microsoft excel" in app_name_lower:
                subprocess.Popen(["start", "excel"])
            elif "powerpoint" in app_name_lower or "microsoft powerpoint" in app_name_lower:
                subprocess.Popen(["start", "powerpnt"])
            elif "file explorer" in app_name_lower or "files" in app_name_lower:
                subprocess.Popen(["explorer.exe"])
            elif "settings" in app_name_lower:
                subprocess.Popen(["ms-settings:"])
            elif "cmd" in app_name_lower or "command prompt" in app_name_lower:
                subprocess.Popen(["cmd.exe"])
            elif "task manager" in app_name_lower:
                subprocess.Popen(["taskmgr.exe"])
            elif "vlc" in app_name_lower or "vlc media player" in app_name_lower:
                subprocess.Popen(["vlc.exe"]) # सुनिश्चित करें कि VLC PATH में है या पूरा पाथ दें
            elif "steam" in app_name_lower:
                subprocess.Popen(["start", "steam://open/main"]) # स्टीम URL प्रोटोकॉल
            elif "discord" in app_name_lower:
                subprocess.Popen(["start", "discord"]) # सुनिश्चित करें कि Discord PATH में है
            else:
                # यदि सीधा कमांड नहीं मिला, तो एप्लिकेशन को PATH में खोजने का प्रयास करें
                try:
                    subprocess.Popen([app_name])
                    return f"श्रीमान, '{app_name}' खोलने का प्रयास कर रहा हूँ।"
                except FileNotFoundError:
                    return f"क्षमा करें, श्रीमान, मैं विंडोज पर '{app_name}' को सीधे खोलने का कमांड नहीं जानता या यह PATH में नहीं है।"

        elif system == "Darwin":  # macOS
            # सामान्य macOS ऐप्स
            if "chrome" in app_name_lower or "browser" in app_name_lower:
                subprocess.Popen(["open", "-a", "Google Chrome"])
            elif "notes" in app_name_lower or "notepad" in app_name_lower or "textedit" in app_name_lower:
                subprocess.Popen(["open", "-a", "TextEdit"])
            elif "calculator" in app_name_lower:
                subprocess.Popen(["open", "-a", "Calculator"])
            elif "pages" in app_name_lower:
                subprocess.Popen(["open", "-a", "Pages"])
            elif "keynote" in app_name_lower:
                subprocess.Popen(["open", "-a", "Keynote"])
            elif "numbers" in app_name_lower:
                subprocess.Popen(["open", "-a", "Numbers"])
            elif "finder" in app_name_lower or "files" in app_name_lower:
                subprocess.Popen(["open", "-a", "Finder"])
            elif "terminal" in app_name_lower:
                subprocess.Popen(["open", "-a", "Terminal"])
            elif "safari" in app_name_lower:
                subprocess.Popen(["open", "-a", "Safari"])
            elif "mail" in app_name_lower:
                subprocess.Popen(["open", "-a", "Mail"])
            elif "photos" in app_name_lower:
                subprocess.Popen(["open", "-a", "Photos"])
            elif "app store" in app_name_lower:
                subprocess.Popen(["open", "-a", "App Store"])
            else:
                # यदि सीधा कमांड नहीं मिला, तो एप्लिकेशन को PATH में खोजने का प्रयास करें
                try:
                    subprocess.Popen(["open", "-a", app_name])
                    return f"श्रीमान, '{app_name}' खोलने का प्रयास कर रहा हूँ।"
                except FileNotFoundError:
                    return f"क्षमा करें, श्रीमान, मैं मैकओएस पर '{app_name}' को सीधे खोलने का कमांड नहीं जानता या यह एप्लिकेशन फोल्डर में नहीं है।"

        elif system == "Linux":
            # सामान्य Linux ऐप्स
            if "chrome" in app_name_lower or "browser" in app_name_lower:
                subprocess.Popen(["google-chrome"]) # या 'chromium-browser'
            elif "notepad" in app_name_lower or "text editor" in app_name_lower:
                subprocess.Popen(["gedit"]) # या 'nano', 'vim', 'kate'
            elif "calculator" in app_name_lower:
                subprocess.Popen(["gnome-calculator"]) # या 'kcalc'
            elif "files" in app_name_lower or "file manager" in app_name_lower:
                subprocess.Popen(["nautilus"]) # या 'dolphin', 'thunar'
            elif "terminal" in app_name_lower:
                subprocess.Popen(["gnome-terminal"]) # या 'konsole', 'xfce4-terminal'
            elif "firefox" in app_name_lower:
                subprocess.Popen(["firefox"])
            elif "vlc" in app_name_lower:
                subprocess.Popen(["vlc"])
            elif "libreoffice writer" in app_name_lower or "writer" in app_name_lower:
                subprocess.Popen(["libreoffice", "--writer"])
            else:
                # यदि सीधा कमांड नहीं मिला, तो एप्लिकेशन को PATH में खोजने का प्रयास करें
                try:
                    subprocess.Popen([app_name])
                    return f"श्रीमान, '{app_name}' खोलने का प्रयास कर रहा हूँ।"
                except FileNotFoundError:
                    return f"क्षमा करें, श्रीमान, मैं लिनक्स पर '{app_name}' को सीधे खोलने का कमांड नहीं जानता या यह PATH में नहीं है।"
        else:
            return "क्षमा करें, श्रीमान, आपका ऑपरेटिंग सिस्टम समर्थित नहीं है।"
        return f"श्रीमान, '{app_name}' खोलने का प्रयास कर रहा हूँ।"
    except FileNotFoundError:
        return f"क्षमा करें, श्रीमान, '{app_name}' एप्लिकेशन नहीं मिला। कृपया सुनिश्चित करें कि यह इंस्टॉल है और आपके PATH में है।"
    except Exception as e:
        return f"क्षमा करें, श्रीमान, '{app_name}' खोलने में एक त्रुटि हुई: {e}"

# --- Serp API के माध्यम से रियल-टाइम जानकारी प्राप्त करें ---
async def get_realtime_info(query):
    """Serp API का उपयोग करके वास्तविक समय की जानकारी प्राप्त करता है।"""
    if not SERP_API_KEY:
        return "क्षमा करें, श्रीमान, Serp API कुंजी सेट नहीं है। मैं वास्तविक समय की जानकारी प्राप्त नहीं कर सकता।"

    try:
        # Google Search API for SerpApi
        params = {
            "q": query,
            "api_key": SERP_API_KEY
        }
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status() # HTTP त्रुटियों के लिए
        data = response.json()

        # यहाँ Serp API प्रतिक्रिया से प्रासंगिक जानकारी निकालें
        # यह बहुत विशिष्ट हो सकता है, इसलिए मैं एक सामान्य उदाहरण दे रहा हूँ
        if "answer_box" in data and "answer" in data["answer_box"]:
            return data["answer_box"]["answer"]
        elif "organic_results" in data and len(data["organic_results"]) > 0:
            snippet = data["organic_results"][0].get("snippet", "कोई स्निपेट उपलब्ध नहीं।")
            link = data["organic_results"][0].get("link", "#")
            return f"{snippet} अधिक जानकारी के लिए, आप इस लिंक पर जा सकते हैं: {link}"
        elif "knowledge_graph" in data and "description" in data["knowledge_graph"]:
            return data["knowledge_graph"]["description"]
        elif "error" in data:
            return f"Serp API त्रुटि: {data['error']}"
        else:
            return "मुझे आपकी खोज के लिए कोई सीधी जानकारी नहीं मिली, श्रीमान।"

    except requests.exceptions.RequestException as e:
        return f"Serp API से संपर्क करने में त्रुटि: {e}"
    except Exception as e:
        return f"जानकारी प्राप्त करने में एक अप्रत्याशित त्रुटि हुई: {e}"

# --- कमांड प्रोसेसिंग लॉजिक ---
async def process_command(query):
    """उपयोगकर्ता की कमांड को प्रोसेस करता है और उचित कार्रवाई करता है।"""
    lower_query = query.lower()
    jarvis_response = ""

    if "समय" in lower_query or "time" in lower_query:
        str_time = datetime.datetime.now().strftime("%H:%M:%S")
        jarvis_response = f"श्रीमान, अभी ${str_time} बजे हैं।"
    elif "तारीख" in lower_query or "date" in lower_query:
        str_date = datetime.datetime.now().strftime("%d %B %Y")
        jarvis_response = f"श्रीमान, आज ${str_date} है।"
    elif "खोजो" in lower_query or "search" in lower_query or "क्या है" in lower_query or "what is" in lower_query:
        search_term = lower_query.replace("गूगल पर खोजो", "").replace("search on google", "").replace("क्या है", "").replace("what is", "").strip()
        if search_term:
            jarvis_response = await get_realtime_info(search_term)
        else:
            jarvis_response = "श्रीमान, कृपया बताएं कि आप क्या खोजना चाहते हैं?"
    elif "मौसम" in lower_query or "weather" in lower_query:
        jarvis_response = await get_realtime_info("current weather")
    elif "खोलो" in lower_query or "open" in lower_query:
        app_name = lower_query.replace("खोलो", "").replace("open", "").strip()
        if app_name:
            jarvis_response = open_application(app_name)
        else:
            jarvis_response = "श्रीमान, कृपया बताएं कि आप कौन सा एप्लिकेशन खोलना चाहते हैं?"
    elif "शटडाउन" in lower_query or "shutdown" in lower_query:
        jarvis_response = "श्रीमान, मैं सीधे सिस्टम को शटडाउन नहीं कर सकता। यह एक सुरक्षा प्रोटोकॉल है।"
    elif "तुम कौन हो" in lower_query or "who are you" in lower_query:
        jarvis_response = "मैं जार्विस हूँ, श्रीमान, आपकी सेवा के लिए डिज़ाइन किया गया एक कृत्रिम बुद्धिमत्ता सहायक।"
    else:
        # यदि कोई विशिष्ट कमांड नहीं है, तो Gemini से पूछें
        if model:
            try:
                response = model.generate_content(f"आप जार्विस हैं, एक उन्नत AI सहायक। आप संक्षिप्त, सटीक, और थोड़े फिल्मी अंदाज़ में जवाब देते हैं। आप हिंदी और अंग्रेजी दोनों में संवाद कर सकते हैं। वर्तमान समय: {datetime.datetime.now().strftime('%H:%M:%S')} तारीख: {datetime.datetime.now().strftime('%d %B %Y')}। उपयोगकर्ता का आदेश: {query}")
                jarvis_response = response.text
            except Exception as e:
                jarvis_response = f"क्षमा करें, श्रीमान, मेरे AI मस्तिष्क से प्रतिक्रिया प्राप्त करने में समस्या हुई: {e}"
        else:
            jarvis_response = "क्षमा करें, श्रीमान, AI मॉडल उपलब्ध नहीं है। कृपया अपनी Gemini API कुंजी जांचें।"
    
    return jarvis_response

# --- WebSocket सर्वर हैंडलर ---
async def jarvis_server(websocket, path):
    print(f"नया क्लाइंट कनेक्टेड: {websocket.remote_address}")
    await websocket.send(json.dumps({"type": "status", "text": "बैकएंड कनेक्टेड और तैयार है।"}))

    try:
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "command":
                user_command = data["text"]
                print(f"उपयोगकर्ता कमांड प्राप्त हुआ: {user_command}")
                response_text = await process_command(user_command)
                await websocket.send(json.dumps({"type": "response", "text": response_text}))
    except websockets.exceptions.ConnectionClosedOK:
        print(f"क्लाइंट डिस्कनेक्टेड: {websocket.remote_address}")
    except Exception as e:
        print(f"WebSocket त्रुटि: {e}")
        await websocket.send(json.dumps({"type": "error", "text": f"बैकएंड त्रुटि: {e}"}))

# --- मुख्य सर्वर स्टार्टर ---
async def main():
    print("जार्विस बैकएंड सर्वर शुरू हो रहा है...")
    print("WebSocket सर्वर ws://localhost:8765 पर सुन रहा है।")
    async with websockets.serve(jarvis_server, "localhost", 8765):
        await asyncio.Future()  # सर्वर को अनिश्चित काल तक चलाए रखें

if __name__ == "__main__":
    asyncio.run(main())

