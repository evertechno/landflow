import streamlit as st
import requests
import json
import os

# Define Langflow API Details
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "edc89198-05a9-4dd1-a754-7c2ccbcc2c55"
APPLICATION_TOKEN = os.getenv("APPLICATION_TOKEN")  # Use an environment variable for security
FLOW_ID = "bdb15b27-ac48-4581-9a9c-bb9eb3299e08"  # Flow ID (can be changed as needed)

# Set up your tweaks dictionary (modify as needed)
TWEAKS = {
  "ChatInput-kwypw": {},
  "ChatOutput-7Nz31": {},
  "ParseData-XdRVt": {},
  "File-SPYcb": {},
  "Prompt-GkhTo": {},
  "GoogleGenerativeAIModel-PXfJR": {}
}

# Function to run the Langflow API call
def run_flow(message: str, endpoint: str, tweaks: dict = None, application_token: str = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :param application_token: Application token for authentication
    :return: The JSON response from the flow
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": "chat",  # or change to whatever type you prefer
        "input_type": "chat",
    }

    if tweaks:
        payload["tweaks"] = tweaks

    headers = None
    if application_token:
        headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"}

    response = requests.post(api_url, json=payload, headers=headers)

    # Debug: Print the full response to check its structure
    print(f"Response from Langflow: {response.json()}")

    return response.json()


# Streamlit Web App Interface
def main():
    st.title("Langflow Chatbot")
    st.subheader("Ask me anything and I'll try to assist you.")

    # Chat history management in the session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Text Input for the User's Message
    user_message = st.text_input("Your message:")

    if user_message:
        # Show the user's input message
        st.session_state.chat_history.append({"role": "user", "message": user_message})

        # Run the Langflow agent with the user's message
        response = run_flow(
            message=user_message,
            endpoint=FLOW_ID,
            tweaks=TWEAKS,
            application_token=APPLICATION_TOKEN
        )

        # Debug: Print the response to understand its structure
        print("Response from Langflow:", response)

        # Extract bot's response and add it to the chat history
        bot_message = response.get('output_value', "Sorry, I couldn't process your request.")
        st.session_state.chat_history.append({"role": "bot", "message": bot_message})

    # Display chat history
    for chat in st.session_state.chat_history:
        if chat['role'] == 'user':
            st.markdown(f"**You:** {chat['message']}")
        else:
            st.markdown(f"**Bot:** {chat['message']}")

# Run the Streamlit app
if __name__ == "__main__":
    main()
