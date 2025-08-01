import streamlit as st
import time

from api_call import get_response, generate_vector_database

st.title("Chat with your Document")
uploaded_file = st.file_uploader("Upload an article", type=("pdf"))

if uploaded_file:
    filename = "uploaded_file_" + str(time.time()) + ".pdf"
    with open(filename, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if 'conversational_id' not in st.session_state:
        st.session_state.conversational_id = None
    
    vbd_resp = generate_vector_database(st.session_state.conversational_id, filename)
    st.session_state.conversational_id = vbd_resp['conversational_id']

    if 'history' not in st.session_state:
        st.session_state.history = []

    if 'user_query' not in st.session_state:
        st.session_state.user_query = ""

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input(f"What is up? (Conversation ID: {st.session_state.conversational_id})"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        response_data = get_response(conversational_id=st.session_state.conversational_id, query=prompt)
        st.session_state.conversational_id = response_data['conversational_id']
        response = response_data['response']
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})