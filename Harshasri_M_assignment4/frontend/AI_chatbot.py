import streamlit as st
from api_call import get_response

st.title("AI Chatbot")
 

#intializing the session state
if("conversational_id" not in st.session_state):
    st.session_state.conversational_id = None
if("history" not in st.session_state):
    st.session_state.history = []
if("user_query" not in st.session_state):
    st.session_state.user_query = ""
if("messages" not in st.session_state):
    st.session_state.messages = []

#getting all messages stored in messages session_state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#taking user input
if prompt := st.chat_input(f"what's up ? (Conversational ID : {st.session_state.conversational_id})"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.user_query = prompt
    st.session_state.messages.append({"role":"user","content":st.session_state.user_query})
    response_data = get_response(conversational_id=st.session_state.conversational_id, query=st.session_state.user_query)
    st.session_state.conversational_id = response_data["conversational_id"]
    response = response_data["response"]
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role":"assistant","content":response})


