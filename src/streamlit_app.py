import streamlit as st
import openai
import random
import time

from chatbot import initialize_messages, get_next_ai_message

chatbot_model_dict = {
    "model": "neuralmagic/Llama-3.1-Nemotron-70B-Instruct-HF-FP8-dynamic",
    "api_base": "***REMOVED***",
    "api_key": "***REMOVED***",
}
analyzer_model_dict = {
    "model": "neuralmagic/Llama-3.1-Nemotron-70B-Instruct-HF-FP8-dynamic",
    "api_base": "***REMOVED***",
    "api_key": "***REMOVED***",
}

chatbot_client = openai.OpenAI(
    api_key=chatbot_model_dict["api_key"], base_url=chatbot_model_dict["api_base"]
)
analyzer_client = openai.OpenAI(
    api_key=analyzer_model_dict["api_key"], base_url=analyzer_model_dict["api_base"]
)

st.title("Food order chatbot")

st.subheader("What this chatbot can do")
with open("what_chatbot_can_do.txt", "r", encoding="utf-8") as fin:
    what_chatbot_can_do = fin.read()
st.markdown(what_chatbot_can_do)

st.subheader("Usage guidelines")
with open("usage_guidelines.txt", "r", encoding="utf-8") as fin:
    usage_guidelines = fin.read()
st.markdown(usage_guidelines)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = initialize_messages()
st.session_state.confirmation_requested = False
st.session_state.is_finished = False

# Display chat messages from history on app rerun
for message in st.session_state.messages[2:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not st.session_state.is_finished:
    # Accept user input
    if human_message := st.chat_input("Enter your gastronomical ideas"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(human_message)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": human_message})
        with st.chat_message("assistant"):
            st.write("Analyzing your message...")
        ai_reply, confirmation_requested, is_finished = get_next_ai_message(
            st.session_state.messages,
            st.session_state.confirmation_requested,
            chatbot_model_dict["model"],
            chatbot_client,
            analyzer_model_dict["model"],
            analyzer_client,
            stream=True,
        )
        print(is_finished)
        st.session_state.is_finished = is_finished
        if isinstance(ai_reply, str):
            st.write(ai_reply)
            response = ai_reply
        else:
            with st.chat_message("assistant"):
                response = st.write_stream(ai_reply)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
