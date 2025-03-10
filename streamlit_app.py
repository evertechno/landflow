import streamlit as st
import requests
import json
from typing import Optional

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "edc89198-05a9-4dd1-a754-7c2ccbcc2c55"
FLOW_ID = "bdb15b27-ac48-4581-9a9c-bb9eb3299e08"
APPLICATION_TOKEN = "<YOUR_APPLICATION_TOKEN>"  # Replace with your token
ENDPOINT = ""
TWEAKS = {
    "ChatInput-kwypw": {},
    "ChatOutput-7Nz31": {},
    "ParseData-XdRVt": {},
    "File-SPYcb": {},
    "Prompt-GkhTo": {},
    "GoogleGenerativeAIModel-PXfJR": {},
}


def run_flow(
    message: str,
    endpoint: str,
    output_type: str = "chat",
    input_type: str = "chat",
    tweaks: Optional[dict] = None,
    application_token: Optional[str] = None,
) -> dict:
    """Run a flow with a given message and optional tweaks."""
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
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "response_text": response.text if response else None}

def main():
    st.title("Langflow API Web App")

    message = st.text_area("Enter your message:")
    endpoint = st.text_input("Endpoint (leave blank for default):", ENDPOINT or FLOW_ID)
    application_token = st.text_input("Application Token:", APPLICATION_TOKEN)
    output_type = st.selectbox("Output Type:", ["chat", "json", "text"])
    input_type = st.selectbox("Input Type:", ["chat", "json", "text"])

    tweaks_json = st.text_area("Tweaks (JSON format):", json.dumps(TWEAKS, indent=2))

    if st.button("Run Flow"):
        try:
            tweaks = json.loads(tweaks_json)
        except json.JSONDecodeError:
            st.error("Invalid tweaks JSON.")
            return

        with st.spinner("Running flow..."):
            response = run_flow(
                message=message,
                endpoint=endpoint,
                output_type=output_type,
                input_type=input_type,
                tweaks=tweaks,
                application_token=application_token,
            )

        st.subheader("Response:")
        st.json(response)


if __name__ == "__main__":
    main()
