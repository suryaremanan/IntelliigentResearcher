import streamlit as st
import requests

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
    
    response = requests.post("http://localhost:8000/chat", data=data, files=files)
    if response.status_code == 200:
        result = response.json()
        if "generated_text" in result:
            st.subheader(f"Generated '{message}' Section:")
            st.write(result["generated_text"])
        else:
            st.error(result.get("error", "Unknown error occurred."))
    else:
        st.error("Error generating section. Please check the backend logs.")

