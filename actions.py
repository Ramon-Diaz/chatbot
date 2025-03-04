import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionLlamaResponse(Action):
    def name(self):
        return "action_llama_response"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        user_message = tracker.latest_message.get("text")
        chat_history = tracker.get_slot("chat_history") or []

        chat_history.append({"role": "user", "content": user_message})

        print(f"🔹 Sending to LLaMA: {chat_history}")  # Debug log

        try:
            response = requests.post(
                "http://localhost:8000/generate",
                json={"prompt": chat_history},
                timeout=10
            )

            print(f"🔹 LLaMA API Raw Response: {response.status_code} {response.text}")  # Debug log

            if response.status_code == 200:
                response_data = response.json()

                # Extract only the last assistant response
                if "response" in response_data and isinstance(response_data["response"], list):
                    assistant_messages = [msg["content"] for msg in response_data["response"] if msg["role"] == "assistant"]
                    assistant_message = assistant_messages[-1] if assistant_messages else "Sorry, I couldn't generate a response."
                else:
                    assistant_message = "Sorry, I couldn't generate a response."

                chat_history.append({"role": "assistant", "content": assistant_message})

                print(f"🔹 Assistant Message Extracted: {assistant_message}")  # Debug log

                dispatcher.utter_message(text=assistant_message)
                return [SlotSet("chat_history", chat_history)]

        except requests.exceptions.ConnectionError:
            print("🔴 Connection Error: LLaMA server is down.")  # Debug log
            dispatcher.utter_message(text="🔴 Connection Error: LLaMA server is down.")
        except requests.exceptions.Timeout:
            print("⏳ Timeout: LLaMA server took too long to respond.")  # Debug log
            dispatcher.utter_message(text="⏳ Timeout: LLaMA server took too long to respond.")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error: {str(e)}")  # Debug log
            dispatcher.utter_message(text=f"⚠️ Error: {str(e)}")

        return [SlotSet("chat_history", chat_history)]
