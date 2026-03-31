import os
import json
from groq import Groq
import tools 
from config import GROQ_API_KEY, PERSONALITY_PROMPT, ASSISTANT_NAME

class Assistant:
    def __init__(self):
        from voice import VoiceEngine 
        self.voice_engine = VoiceEngine()
        self.name = ASSISTANT_NAME 
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model_id = "llama-3.3-70b-versatile" 
        
        # Memory setup
        self.memory_file = "chat_history.json"
        self.memory = self._load_memory()
        
        # 1. Define the tools for Groq to see
        self.tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "type_in_notepad",
                    "description": "Opens notepad and types text",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "The text to type"}
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_youtube",
                    "description": "Searches for a video on YouTube",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The video or topic to search for"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "open_app",
                    "description": "Opens a specific application on the computer",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {"type": "string", "description": "The name of the app (e.g., 'chrome', 'notepad')"}
                        },
                        "required": ["app_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "take_screenshot",
                    "description": "Takes a screenshot of the current screen",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "press_key",
                    "description": "Presses a keyboard key like 'space', 'enter', or media keys",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "The key name (e.g., 'volumeup', 'playpause', 'enter')"}
                        },
                        "required": ["key"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "open_website",
                    "description": "Opens a specific website URL",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "The URL (e.g., 'facebook.com', 'github.com')"}
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "google_search",
                    "description": "Searches Google for a topic",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "What to search for"}
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)[-15:] # Keep a moderate history
            except:
                return []
        return []

    def save_memory(self):
        try:
            with open(self.memory_file, "w") as f:
                json.dump(self.memory, f, indent=4)
        except Exception as e:
            print(f"Failed to save history: {e}")

    def send_message(self, user_input):
        self.memory.append({"role": "user", "content": user_input})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "system", "content": PERSONALITY_PROMPT}] + self.memory,
                tools=self.tools_schema,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if tool_calls:
                self.memory.append(response_message)
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    if function_name == "type_in_notepad":
                        result = tools.type_in_notepad(arguments.get("text"))
                    elif function_name == "search_youtube":
                        result = tools.search_youtube(arguments.get("query"))
                    elif function_name == "open_app":
                        result = tools.open_app(arguments.get("app_name"))
                    elif function_name == "take_screenshot":
                        result = tools.take_screenshot()
                    elif function_name == "press_key":
                        result = tools.press_key(arguments.get("key"))
                    elif function_name == "open_website":
                        result = tools.open_website(arguments.get("url"))
                    elif function_name == "google_search":
                        result = tools.google_search(arguments.get("query"))
                    else:
                        result = "Unknown tool"

                    self.memory.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": result
                    })
                
                second_response = self.client.chat.completions.create(
                    model=self.model_id,
                    messages=[{"role": "system", "content": PERSONALITY_PROMPT}] + self.memory
                )
                final_text = second_response.choices[0].message.content
                self.memory.append({"role": "assistant", "content": final_text})
            else:
                final_text = response_message.content
                self.memory.append({"role": "assistant", "content": final_text})

            self.save_memory()
            self.voice_engine.speak(final_text)
            return final_text

        except Exception as e:
            print(f"Tool Error: {e}")
            return f"Error: {str(e)}"