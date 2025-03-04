import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionLlamaResponse(Action):
    def name(self):
        return "action_llama_response"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        user_message = tracker.latest_message.get("text")

        # Send "Thinking..." only once per conversation
        if tracker.get_slot("waiting_message_sent") is None:
            dispatcher.utter_message(text="Thinking... ⏳ Please wait.")
            return [SlotSet("waiting_message_sent", True)]  # Set slot and stop further responses

        try:
            response = requests.post(
                "http://localhost:8000/generate",
                json={"prompt": user_message},
                timeout=10
            )
            if response.status_code == 200:
                response_data = response.json()

                # Extract only the assistant's response
                if "response" in response_data and isinstance(response_data["response"], list):
                    # Find the assistant's message
                    assistant_message = next(
                        (msg["content"] for msg in response_data["response"] if msg["role"] == "assistant"),
                        "Sorry, I couldn't generate a response."
                    )
                    llama_response = assistant_message
                else:
                    llama_response = "Sorry, I couldn't generate a response."

                dispatcher.utter_message(text=llama_response)

        except requests.exceptions.RequestException:
            dispatcher.utter_message(text="Sorry, I couldn't reach the AI server.")

        return [SlotSet("waiting_message_sent", False)]  # Reset slot after one response
