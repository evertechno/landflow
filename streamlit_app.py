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
    return response.json()


# Streamlit Web App Interface
def main():
    st.title("Langflow Chatbot")

    # Text Input for the User's Message
    user_message = st.text_input("Ask me anything:")

    if user_message:
        # Show the user's input message
        st.write(f"You: {user_message}")

        # Run the Langflow agent with the user's message
        response = run_flow(
            message=user_message,
            endpoint=FLOW_ID,
            tweaks=TWEAKS,
            application_token=APPLICATION_TOKEN
        )

        # Display the response from the Langflow agent
        if "output_value" in response:
            st.write(f"Bot: {response['output_value']}")
        else:
            st.write("Bot: Sorry, I couldn't process your request.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
