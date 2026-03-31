import os
import subprocess
import pyautogui
import webbrowser
import time
import webbrowser
import pyautogui

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
    """Takes a screenshot of the current screen."""
    pyautogui.screenshot("screenshot.png")
    return "Snapshot taken! I've saved it to our folder."

def press_key(key: str):
    """Presses a keyboard key (e.g., 'space', 'enter', 'volumeup')."""
    pyautogui.press(key)
    return f"Pressed the {key} key for you!"