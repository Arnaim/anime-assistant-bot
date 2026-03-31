import os
import subprocess
import pyautogui
import webbrowser
import time
import webbrowser
import pyautogui
from datetime import datetime

def open_website(url: str):
    """Opens any specific URL in the default browser."""
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return f"I've opened {url} for you. Don't get distracted, Senpai."

def google_search(query: str):
    """Searches Google for the given query."""
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Here are the search results for '{query}'. I hope it's what you were looking for."

def facebook_search(query: str):
    """Searches Facebook for the given query."""
    try:
        # Create a direct Facebook search URL
        url = f"https://www.facebook.com/search/top/?q={query.replace(' ', '%20')}"
        webbrowser.open(url)
        return f"I've searched Facebook for '{query}'. Take a look at the results, Arnab."
    except Exception as e:
        return f"Logic error while searching Facebook: {e}"
    
def type_in_notepad(text: str):
    """Opens Notepad and types the provided text into it."""
    try:
        # 1. Open Notepad
        subprocess.Popen(['notepad.exe'])
        time.sleep(1) # Give it a second to wake up
        
        # 2. Type the message
        pyautogui.write(text, interval=0.05) 
        return f"I've written your notes in Notepad, Senpai. Don't lose them."
    except Exception as e:
        return f"Logic error while typing: {e}"

def search_youtube(query: str):
    """Opens the browser and searches for a video on YouTube."""
    try:
        # Create a direct search URL
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"I've found some videos about '{query}' on YouTube. Go watch them."
    except Exception as e:
        return f"Browser error: {e}"

def open_app(app_name: str):
    """
    Opens a specific application on the PC. 
    Examples: 'notepad', 'calc', 'chrome'
    """
    try:
        # Simple start command for Windows
        subprocess.Popen(['start', app_name], shell=True)
        return f"Successfully opened {app_name}, Senpai!"
    except Exception as e:
        return f"I couldn't open it because: {str(e)}"

def take_screenshot():
    """Takes a screenshot with a unique timestamp and saves it to the Screenshots folder."""
    try:
        # Define the directory
        folder_path = r"C:\Users\naimu\Pictures\Screenshots"
        
        # Ensure the directory exists
        os.makedirs(folder_path, exist_ok=True)
        
        # Create a unique filename using the current date and time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"herta_snap_{timestamp}.png"
        save_path = os.path.join(folder_path, filename)
        
        # Take and save the screenshot
        pyautogui.screenshot(save_path)
        
        return f"Snapshot captured as {filename}, Arnab. I've archived it in your Pictures folder."
    except Exception as e:
        return f"Logic error while capturing screen: {e}"

def press_key(key: str):
    """Presses a keyboard key (e.g., 'space', 'enter', 'volumeup')."""
    pyautogui.press(key)
    return f"Pressed the {key} key for you!"