import argparse
import json
import requests
import streamlit as st
from typing import Optional
import warnings

try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "edc89198-05a9-4dd1-a754-7c2ccbcc2c55"
FLOW_ID = "bdb15b27-ac48-4581-9a9c-bb9eb3299e08"
APPLICATION_TOKEN = "<YOUR_APPLICATION_TOKEN>"
ENDPOINT = "" # You can set a specific endpoint name in the flow settings

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
    # Streamlit UI elements
    st.title("Langflow Flow Runner")
    
    message = st.text_area("Enter your message:")
    endpoint = st.text_input("Endpoint", value=FLOW_ID)
    tweaks_input = st.text_area("Enter tweaks (JSON format):", value=json.dumps(TWEAKS))
    application_token = st.text_input("Application Token", value=APPLICATION_TOKEN)
    output_type = st.selectbox("Output Type", options=["chat", "json", "text"], index=0)
    input_type = st.selectbox("Input Type", options=["chat", "json", "text"], index=0)

    # File upload
    uploaded_file = st.file_uploader("Upload a file (Optional)", type=["txt", "pdf", "docx"])
    components = st.text_input("Components to upload the file to (Optional)")

    # Button to trigger flow execution
    if st.button("Run Flow"):
        try:
            tweaks = json.loads(tweaks_input)
        except json.JSONDecodeError:
            st.error("Invalid tweaks JSON string.")
            return

        if uploaded_file:
            if not upload_file:
                raise ImportError("Langflow is not installed. Please install it to use the upload_file function.")
            if not components:
                st.error("You need to provide the components to upload the file to.")
                return
            # Upload the file
            tweaks = upload_file(file_path=uploaded_file, host=BASE_API_URL, flow_id=endpoint, components=components, tweaks=tweaks)

        # Run the flow
        try:
            response = run_flow(
                message=message,
                endpoint=endpoint,
                output_type=output_type,
                input_type=input_type,
                tweaks=tweaks,
                application_token=application_token
            )

            # Display the response in a readable format
            st.subheader("Response:")
            st.json(response)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    streamlit_app()
