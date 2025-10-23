from flask import Flask, request, jsonify
from flask_cors import CORS  # To allow cross-origin requests from React
import main as gruu_core  # Import your modified main.py
import os
import datetime
import subprocess
import webbrowser  # Missing import - needed for opening websites
import sqlite3     # Missing import - needed for database operations

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the database when the Flask app starts
gruu_core.init_db()
gruu_core.say("Hello I'm Gruu, ready for commands!")  # Initial greeting on backend start

# Global state for chat mode (can be improved for multi-user sessions)
in_chat_mode = False

@app.route('/')
def home():
    return "Gruu Backend is running!"

@app.route('/api/command', methods=['POST'])
def handle_command():
    global in_chat_mode
    data = request.get_json()
    query = data.get('command', '').lower()
    response_message = ""
    command_executed = False

    print(f"Received command: {query}")

    # Handle chat mode first
    if in_chat_mode:
        if "stop chat" in query:
            in_chat_mode = False
            response_message = "Okay, exiting chat mode."
            gruu_core.save_to_db(query, response_message)
            return jsonify({"response": response_message, "chat_mode": in_chat_mode})
        else:
            response_message = gruu_core.chat(query)
            gruu_core.save_to_db(query, response_message)
            return jsonify({"response": response_message, "chat_mode": in_chat_mode})

    # --- Normal Command Processing ---
    sites = [["youtube", "https://youtube.com"], ["google", "https://www.google.com/"], ["instagram", "https://instagram.com"]]
    apps = [
        ["excel", r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Excel.lnk"],
        ["words", r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Word.lnk"],
        ["powerpoint", r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PowerPoint.lnk"]
    ]

    for site in sites:
        if f"open {site[0]}".lower() in query:
            response_message = f"Opening {site[0]} sir...."
            webbrowser.open(site[1])
            gruu_core.save_to_db(query, response_message)
            command_executed = True
            break

    if not command_executed and "open music".lower() in query:
        path = r"C:\Users\hp\OneDrive\Desktop\chat\chat\gorila-315977.mp3"  # Ensure this path is correct on your server
        try:
            # This will open the music file on the server, not stream to client.
            # For client-side audio, you'd need to serve the file or stream it.
            subprocess.Popen(['start', '', path], shell=True)
            response_message = f"Playing music: {os.path.basename(path)}"
            gruu_core.save_to_db(query, response_message)
            command_executed = True
        except Exception as e:
            response_message = f"Error playing music: {e}"
            print(response_message)
            gruu_core.save_to_db(query, response_message)
            command_executed = True

    if not command_executed and any(phrase in query for phrase in ["what is the time", "what's the time", "tell me the time"]):
        strfTime = datetime.datetime.now().strftime("%H:%M:%S")
        response_message = f"Sir the time is {strfTime}"
        gruu_core.save_to_db(query, response_message)
        command_executed = True

    if not command_executed:
        for app_item in apps:
            if f"open {app_item[0]}".lower() in query:
                try:
                    os.startfile(app_item[1])
                    response_message = f"Launched {app_item[0]}"
                    gruu_core.save_to_db(query, response_message)
                    command_executed = True
                    break
                except Exception as e:
                    response_message = f"Could not launch {app_item[0]}: {e}"
                    print(response_message)
                    gruu_core.save_to_db(query, response_message)
                    command_executed = True
                    break

    if not command_executed and "use ai" in query:
        # Extract the actual prompt for AI_features
        ai_prompt = query.replace("use ai", "").strip()
        if not ai_prompt:
            response_message = "Please provide a prompt for the AI."
        else:
            response_message = gruu_core.AI_features(ai_prompt)
        gruu_core.save_to_db(query, response_message)
        command_executed = True

    if not command_executed and "chat" in query:
        in_chat_mode = True
        response_message = "Sure, let's chat! Say 'stop chat' to exit chat mode."
        gruu_core.save_to_db(query, response_message)
        command_executed = True

    if not command_executed and "weather" in query:
        # Assuming the location is part of the query, e.g., "weather in London"
        location_keywords = ["weather in ", "weather of ", "weather for "]
        location = ""
        for kw in location_keywords:
            if kw in query:
                location = query.split(kw, 1)[1].strip()
                break
        if not location:
            response_message = "Please specify a location for the weather, e.g., 'weather in London'."
        else:
            response_message = gruu_core.get_weather_info(location)
        gruu_core.save_to_db(query, response_message)
        command_executed = True

    if not command_executed and "play song" in query:
        song_name = query.replace("play song", "").strip()
        if not song_name:
            response_message = "Please tell me which song to play."
        else:
            response_message = gruu_core.play_song(song_name)
        gruu_core.save_to_db(query, response_message)
        command_executed = True

    if not command_executed and any(cmd in query for cmd in ["quit", "exit", "stop", "shutdown"]):
        response_message = "Goodbye! Shutting down the backend."
        gruu_core.save_to_db(query, response_message)
        # sys.exit(0) # Do not exit the server directly from a request in production
        # For development, you might want to stop it, but for a deployed app,
        # you'd handle shutdown differently (e.g., via a separate admin interface).
        return jsonify({"response": response_message, "shutdown": True})

    if not command_executed:
        response_message = "I didn't understand that command. Can you please rephrase?"
        gruu_core.save_to_db(query, response_message)

    return jsonify({"response": response_message, "chat_mode": in_chat_mode})

@app.route('/api/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect("History.db")
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, command, response FROM command_history ORDER BY id DESC")
    history_data = cursor.fetchall()
    conn.close()

    # Convert to a list of dictionaries for easier JSON serialization
    history_list = []
    for item in history_data:
        history_list.append({
            "timestamp": item[0],
            "command": item[1],
            "response": item[2]
        })
    return jsonify({"history": history_list})

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Run on port 5000