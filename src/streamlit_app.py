import secrets
import string
import streamlit as st
import openai

from chatbot import initialize_messages, get_next_ai_message, order


def end_conversation():
    del st.session_state["messages"]


def reset_conversation():
    end_conversation()
    st.session_state.is_finished = False


chatbot_model = st.secrets["launch_parameters"]["chatbot_model"]
chatbot_model_dict = {
    "model": chatbot_model,
    "api_base": st.secrets["api_bases"][chatbot_model],
    "api_key": st.secrets["api_keys"][chatbot_model],
}
analyzer_model = st.secrets["launch_parameters"]["analyzer_model"]
analyzer_model_dict = {
    "model": analyzer_model,
    "api_base": st.secrets["api_bases"][analyzer_model],
    "api_key": st.secrets["api_keys"][analyzer_model],
}

print(chatbot_model_dict, analyzer_model_dict)

chatbot_client = openai.OpenAI(
    api_key=chatbot_model_dict["api_key"], base_url=chatbot_model_dict["api_base"]
)
analyzer_client = openai.OpenAI(
    api_key=analyzer_model_dict["api_key"], base_url=analyzer_model_dict["api_base"]
)

st.title("Food order chatbot")

if "is_finished" not in st.session_state or not st.session_state.is_finished:
    st.header("What this chatbot can do")
    with open("src/what_chatbot_can_do.txt", "r", encoding="utf-8") as fin:
        what_chatbot_can_do = fin.read()
    st.markdown(what_chatbot_can_do)

    st.header("Usage guidelines")
    with open("src/usage_guidelines.txt", "r", encoding="utf-8") as fin:
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
        st.session_state.is_finished = is_finished
        st.session_state.confirmation_requested = confirmation_requested
        
        if is_finished:
            order_id = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            response = (
                f"Your order has been received. Order ID is {order_id}. Remember to write it down! "
                "Have a nice meal! Concact me again anytime you need to order food. "
                "I hope I was helpful to you as an AI assistant."
            )
            with st.chat_message("assistant"):
                st.write(response)
            left, right = st.columns(2)
            left.button("Quit", icon="🔚", on_click=end_conversation, use_container_width=True)
            right.button("Place a new order", icon="🔄", on_click=reset_conversation, use_container_width=True)
        else:
            if isinstance(ai_reply, str):
                with st.chat_message("assistant"):
                    st.write(ai_reply)
                response = ai_reply
            else:
                with st.chat_message("assistant"):
                    response = st.write_stream(ai_reply)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.markdown("You can safely navigate away. See you next time!")
