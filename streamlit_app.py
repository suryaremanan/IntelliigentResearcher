import streamlit as st
import requests
import os

# Get backend URL from environment variable or use default
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

st.title("Research Paper Section Generator (Chat Mode)")

st.markdown("Upload your PDF research papers and specify the research topic. Then type the section you want (e.g., 'intro', 'methodology', etc.) in the chatbox.")

with st.form("chat_form"):
    topic = st.text_input("Enter the research topic", "Deep Learning for Medical Imaging")
    uploaded_files = st.file_uploader("Upload PDF(s) of research papers", type=["pdf"], accept_multiple_files=True)
    message = st.text_input("What section do you want to generate? (e.g., intro, literature review)")
    submitted = st.form_submit_button("Send")

if submitted:
    data = {"topic": topic, "message": message}
    files = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            files.append(
                ("pdf_files", (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type))
            )
    
    try:
        response = requests.post(f"{BACKEND_URL}/chat", data=data, files=files)
        if response.status_code == 200:
            result = response.json()
            if "generated_text" in result:
                st.subheader(f"Generated '{message}' Section:")
                st.write(result["generated_text"])
            else:
                st.error(result.get("error", "Unknown error occurred."))
        else:
            st.error(f"Error: Status code {response.status_code}")
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")

