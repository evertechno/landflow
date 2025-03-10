import json
import requests
import streamlit as st
from typing import Optional
import warnings

# Langflow import for file upload
try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "edc89198-05a9-4dd1-a754-7c2ccbcc2c55"
FLOW_ID = "bdb15b27-ac48-4581-9a9c-bb9eb3299e08"
APPLICATION_TOKEN = "<YOUR_APPLICATION_TOKEN>"
ENDPOINT = ""  # You can set a specific endpoint name in the flow settings

# Default tweaks (can be modified based on needs)
TWEAKS = {
    "ChatInput-kwypw": {},
    "ChatOutput-7Nz31": {},
    "ParseData-XdRVt": {},
    "File-SPYcb": {},
    "Prompt-GkhTo": {},
    "GoogleGenerativeAIModel-PXfJR": {}
}

def run_flow(message: str,
             endpoint: str,
             output_type: str = "chat",
             input_type: str = "chat",
             tweaks: Optional[dict] = None,
             application_token: Optional[str] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The JSON response from the flow
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if application_token:
        headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

def streamlit_app():
    # Streamlit UI elements for the chat-like interface
    st.title("Langflow Chatbot")

    # Chat history will be stored in session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display messages from the conversation
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**Bot:** {message['content']}")

    # Input text for the user message
    user_message = st.text_input("Type your message here:")

    # Button to trigger the message processing
    if st.button("Send"):
        if user_message.strip() != "":
            # Add user message to session state
            st.session_state.messages.append({"role": "user", "content": user_message})

            # Process the user message
            try:
                response = run_flow(
                    message=user_message,
                    endpoint=FLOW_ID,
                    output_type="chat",
                    input_type="chat",
                    tweaks=TWEAKS,
                    application_token=APPLICATION_TOKEN
                )

                # Get the bot's response
                bot_response = response.get("output_value", "Sorry, I couldn't process your request.")

                # Add bot response to the chat
                st.session_state.messages.append({"role": "bot", "content": bot_response})

            except Exception as e:
                # Handle errors
                st.session_state.messages.append({"role": "bot", "content": f"Error: {str(e)}"})

            # Refresh the chat window after message is processed
            st.experimental_rerun()

if __name__ == "__main__":
    streamlit_app()
