import speech_recognition as sr
import pyaudio
import os 
import webbrowser
import pyttsx3
import openai
import subprocess , sys
import datetime
import requests
import json
import time
import random
from config import openrouter_api as api_key , weather_api as api
import sqlite3
import vlc

def init_db():
    conn = sqlite3.connect("History.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS command_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            command TEXT,
            response TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(command, response):
    conn = sqlite3.connect("History.db")
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO command_history (timestamp, command, response)
        VALUES (?, ?, ?)
    ''', (timestamp, command, response))
    conn.commit()
    conn.close()

chat_history = [
    {"role": "system", "content": "You are a helpful assistant."}
]

def chat(query):
    global chat_history
    print("📢 Chat function called with query:", query)
    
    chat_history.append({"role": "user", "content": query})
    
    try:
        OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "YOUR_WEBSITE_URL",  # Optional: add your URL
            "X-Title": "Your-Chat-App"           # Optional: app title
        }

        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": chat_history,  # Pass all messages properly
            "temperature": 1,
            "max_tokens": 256,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            error_msg = response_data["error"].get("message", "Unknown error")
            print(f"❌ OpenRouter Error: {error_msg}")
            return f"Error: {error_msg}"

        if not response_data.get("choices"):
            print("❌ No response from AI.")
            return "No response from AI."

        ai_response = response_data["choices"][0]["message"]["content"].strip()
        chat_history.append({"role": "assistant", "content": ai_response})
        
        return ai_response

    except Exception as e:
        print(f"❌ Exception in chat(): {e}")
        return "Sorry, I encountered an error."

def AI_features(prompt):
    print("📢 Processing AI request...")  # Status update only
    try:
        OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "YOUR_WEBSITE_URL",
            "X-Title": "Your-App-Name"
        }

        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 256,
        }

        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        response_data = response.json()

        if "error" in response_data:
            error_msg = response_data["error"].get("message", "Unknown API error")
            print(f"❌ Error: {error_msg}")
            say(f"API error occurred")
            return

        if not response_data.get("choices"):
            print("❌ No response from AI")
            say("AI didn't respond")
            return

        result = response_data["choices"][0]["message"]["content"].strip()

        # Save response to file without printing content
        folder_path = os.path.join(os.getcwd(), "AI_Responses")
        os.makedirs(folder_path, exist_ok=True)
        filename = f"response_{random.randint(1000, 9999999)}.txt"
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Prompt: {prompt}\n---\n{result}")

        print(f"✅ Response saved to {filename}")
        say("I've saved the response to a file")

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        say("Failed to process your request")

def say(text):
    eng = pyttsx3.init()
    eng.say(text)
    eng.runAndWait()

def take_cmd():
    r = sr.Recognizer()
    
    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        print("Listening...")
        
        # Adjust for ambient noise
        r.adjust_for_ambient_noise(source, duration=1)
        r.pause_threshold = 1  # seconds of non-speaking audio before a phrase is considered complete
        
        try:
            audio = r.listen(source, timeout=5)  # Listen for up to 5 seconds
            print("Processing...")
            
            # Recognize speech using Google Speech Recognition
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query.lower()  # Return lowercase for easier comparison
            
        except sr.WaitTimeoutError:
            print("Listening timed out. Please try again.")
            return ""
        except sr.UnknownValueError:
            print("Sorry, I didn't understand that.")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return ""
        except Exception as e:
            print(f"Error: {e}")
            return ""

def get_weather_info(location):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    api_key=api
    
    params = {
        'q': location,
        'appid': api_key,
        'units': 'metric'
    }
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if data['cod'] != 200:
            error_msg = f"Error: {data.get('message', 'Unknown error')}"
            print(f"❌ {error_msg}")  
            return error_msg
        
        city = data['name']
        country = data['sys']['country']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        description = data['weather'][0]['description']
        
        weather_str = (f"\n=== Weather Information ===\n"
                      f"Location: {city}, {country}\n"
                      f"Temperature: {temp}°C (Feels like {feels_like}°C)\n"
                      f"Humidity: {humidity}%\n"
                      f"Wind Speed: {wind_speed} m/s\n"
                      f"Conditions: {description.capitalize()}\n"
                      f"==========================")
        
        print(weather_str)  
        return f"Weather in {city}: {temp}°C with {description}"  
        
    except Exception as e:
        error_msg = f"Sorry, I couldn't fetch weather data. Error: {str(e)}"
        print(f"❌ {error_msg}")  
        return error_msg  

def play_song(song_name):
    try:
        print(f"Searching for '{song_name}' on JioSaavn...")

        # Search song via saavn.dev
        res = requests.get(f"https://saavn.dev/api/search/songs?query={song_name}")
        data = res.json()

        if not data['data']['results']:
            print("No results found.")
            return

        song = data['data']['results'][0]
        media_url = song['downloadUrl'][-1]['link']  # Best quality link

        print(f"Now streaming: {song['name']}")

        # Play using VLC
        player = vlc.MediaPlayer(media_url)
        player.play()

        # Let it buffer and play (avoid quitting too fast)
        time.sleep(1)
        duration = player.get_length() / 1000  # in seconds
        time.sleep(duration if duration > 0 else 180)  # fallback to 3 mins

    except Exception as e:
        print("Error:", e)
# if __name__== "__main__":
#     init_db()
#     print("hello")
#     say("Hello I'm Gruu")
#     while True:
#         say("What do you command me ?? ")
#         query=take_cmd()
#         sites=[["Youtube","https://youtube.com"],["google","https://www.google.com/"],["Instagram","https://instagram.com"]]
#         # apps onening will be determined by the location of the file in the system
#         apps=[["Excel",r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Excel.lnk"],["Words",r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Word.lnk"],["PowerPoint", r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PowerPoint.lnk"]]
#         # to be filled music list when download more than one music or has more music exist
#         music=[] 

#         for site in sites:
#             if f"Open {site[0]}".lower() in query.lower():
#                 say(f"Opening {site[0]} sir....")
#                 webbrowser.open(site[1])
#                 save_to_db(query, f"Opened {site[0]}")

#         # only Downloaded music will be played
#         if "open music".lower() in query.lower():
#             path=r"C:\Users\hp\OneDrive\Desktop\chat\chat\gorila-315977.mp3"
#             try:
#                 subprocess.Popen(['start', '', path], shell=True)
#                 save_to_db(query, f"Playing music: {os.path.basename(path)}")
#             except Exception as e:
#                 print("Error:", e)
        
#         if any(phrase in query.lower() for phrase in ["what is the time", "what's the time", "tell me the time"]):
#             strfTime=datetime.datetime.now().strftime("%H:%M:%S")
#             # print(strfTime)
#             say(f"Sir the time is {strfTime}")
#             save_to_db(query, f"The time is {strfTime}")

#         for app in apps:
#             if f"open {app[0]}".lower() in query.lower():
#                 os.startfile(app[1])
#                 save_to_db(query, f"Launched {app[0]}")

#         # This will not work as API call limit is over and need to purchase it 
#         if "use AI".lower() in query.lower():
#             AI_features(prompt=query)
#             save_to_db(query, "AI feature called and saved response to file.")
        
#         if "chat" in query.lower():
#             say("Sure, let's chat ! Say ' Stop Chat ' to disable chatting mode.")
#             print("🟢 Entered chat mode.")
#             while True:
#                 query = take_cmd()
#                 if "stop chat" in query.lower():
#                     say("Okay, exiting chat mode.")
#                     print("🔴 Exiting chat mode.")
#                     break
#                 response = chat(query)
#                 print("AI:", response)
#                 say(response)
#                 save_to_db(query, response)

#         if "weather" in query.lower():
#             say("Which location's weather would you like to know?")
#             print("\n[Listening for location...]")  # Visual feedback
#             location = take_cmd()
#             if location:
#                 weather_report = get_weather_info(location)  
#                 say(weather_report)  
#                 save_to_db(f"Weather request for {location}", weather_report)
#             continue

#         if "play song" in query.lower():
#             say("Which song would you like to hear?")
#             song_name = take_cmd()
#             if song_name:
#                 play_song(song_name)
#                 save_to_db(f"Play {song_name}", song_name)

#         if any(cmd in query.lower() for cmd in ["quit", "exit", "stop", "shutdown"]):
#             say("Goodbye! Shutting down.")
#             print("🛑 Shutting down Gruu...")
#             save_to_db(query, "Gruu shut down")
#             sys.exit(0)