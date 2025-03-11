import streamlit as st
import requests
import json
import os
from io import StringIO
from email.parser import BytesParser
from email.policy import default
from bs4 import BeautifulSoup

# Langflow API Details
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

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for bad HTTP responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
        return {"error": f"HTTP error occurred: {http_err}"}
    except Exception as err:
        st.error(f"An error occurred: {err}")
        return {"error": f"An error occurred: {err}"}

# Function to handle parsing of plain text email (Marketing)
def parse_plain_text_email(file):
    try:
        content = file.read().decode("utf-8")
        return content
    except Exception as e:
        return {"error": f"Error reading plain text email: {str(e)}"}

# Function to handle parsing of HTML email
def parse_html_email(file):
    try:
        html_content = file.read().decode("utf-8")
        # Extract text from HTML
        soup = BeautifulSoup(html_content, "html.parser")
        body = soup.get_text(separator=" ", strip=True)  # Improved extraction
        return body
    except Exception as e:
        return {"error": f"Error reading HTML email: {str(e)}"}

# Function to handle file upload and processing based on upload type
def handle_file_upload(upload_type):
    uploaded_file = st.file_uploader(f"Upload a {upload_type} email file", type=["txt", "html"])

    if uploaded_file is not None:
        if upload_type == "Plain Text Marketing":
            email_content = parse_plain_text_email(uploaded_file)
            if "error" in email_content:
                st.error(email_content["error"])
            else:
                st.write("### Email Content")
                st.write(f"**Content**: {email_content[:500]}...")  # Display first 500 characters of body

                # Perform Marketing email analysis (mockup example)
                st.write("Analyzing plain text marketing email...")
                response = run_flow(
                    message=f"Analyze the following plain text marketing email content:\n\n{email_content}",
                    endpoint=FLOW_ID,
                    tweaks=TWEAKS,
                    application_token=APPLICATION_TOKEN
                )
                st.write(f"Marketing Analysis Result: {response.get('output_value', 'No result found')}")

        elif upload_type == "HTML Marketing":
            email_content = parse_html_email(uploaded_file)
            if "error" in email_content:
                st.error(email_content["error"])
            else:
                st.write("### Email Content (HTML Extracted)")
                st.write(f"**Extracted Content**: {email_content[:500]}...")  # Display first 500 characters of extracted body

                # Perform HTML email analysis (mockup example)
                st.write("Analyzing HTML marketing email...")
                response = run_flow(
                    message=f"Analyze the following HTML marketing email content:\n\n{email_content}",
                    endpoint=FLOW_ID,
                    tweaks=TWEAKS,
                    application_token=APPLICATION_TOKEN
                )

                # Check if the response contains expected output
                if "output_value" in response:
                    st.write(f"HTML Marketing Analysis Result: {response['output_value']}")
                else:
                    st.error(f"Analysis failed. Response: {response}")

# Streamlit Web App Interface
def main():
    st.title("AI Chatbot & Marketing Email Analyzer")

    # Chat Section
    st.header("Chat with the AI Bot")
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

        # Check if 'output_value' exists in the response
        if "output_value" in response:
            st.write(f"Bot: {response['output_value']}")
        else:
            st.write("Bot: Sorry, I couldn't process your request.")

    # File Upload Section
    st.header("Email Uploads")
    # Plain Text Marketing Email Upload
    handle_file_upload("Plain Text Marketing")

    # HTML Marketing Email Upload
    handle_file_upload("HTML Marketing")

if __name__ == "__main__":
    main()
