from typing import Generator

import secrets
import string
import streamlit as st
import openai

from chatbot import initialize_messages, get_next_ai_message


def end_conversation() -> None:
    del st.session_state["messages"]


def reset_conversation() -> None:
    end_conversation()
    st.session_state.is_finished = False


def display_headers() -> None:
    st.header("What this chatbot can do")
    with open("src/what_chatbot_can_do.txt", "r", encoding="utf-8") as fin:
        what_chatbot_can_do = fin.read()
    st.markdown(what_chatbot_can_do)

    st.header("Usage guidelines")
    with open("src/usage_guidelines.txt", "r", encoding="utf-8") as fin:
        usage_guidelines = fin.read()
    st.markdown(usage_guidelines)


def finish_interaction() -> None:
    st.session_state.is_finished = True
    order_id = "".join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6)
    )
    response = (
        f"Your order has been received. Order ID is {order_id}. Remember to write it down! "
        "Have a nice meal! Concact me again anytime you need to order food. "
        "I hope I was helpful to you as an AI assistant."
    )
    with st.chat_message("assistant"):
        st.success(response)
    
    sentiment_mapping = ["one", "two", "three", "four", "five"]
    selected = st.feedback("stars")
    st.markdown("Before you go, please, rate your experience!")
    if selected is not None:
        st.markdown(f"You selected {sentiment_mapping[selected]} star(s).")
    left, right = st.columns(2)
    left.button(
        "Quit", icon="🔚", on_click=end_conversation, use_container_width=True
    )
    right.button(
        "Place a new order",
        icon="🔄",
        on_click=reset_conversation,
        use_container_width=True,
    )


def output_ai_reply(ai_reply: Generator) -> str:
    with st.chat_message("assistant"):
        response = st.write_stream(ai_reply)
    return response


def update_order() -> None:
    st.session_state.messages.append({"role": "user", "content": "No, I would like to change or update my order"})
    ai_reply = "Sure! What would you like to modify?"
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    with st.chat_message("assistant"):
        st.markdown(ai_reply)


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

chatbot_client = openai.OpenAI(
    api_key=chatbot_model_dict["api_key"], base_url=chatbot_model_dict["api_base"]
)
analyzer_client = openai.OpenAI(
    api_key=analyzer_model_dict["api_key"], base_url=analyzer_model_dict["api_base"]
)


if "is_finished" not in st.session_state or not st.session_state.is_finished:
    st.title("Food order chatbot")
    display_headers()
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = initialize_messages()
        st.session_state.confirmation_requested = False
        st.session_state.is_finished = False

    # Display chat messages from history on app rerun
    for message in st.session_state.messages[2:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if human_message := st.chat_input("Enter your gastronomical ideas", max_chars=256, key="user_input_field"):
        with st.chat_message("user"):
            st.markdown(human_message)
        st.session_state.messages.append({"role": "user", "content": human_message})

        with st.spinner("Analyzing your response...", show_time=True):
            ai_reply, confirmation_requested = get_next_ai_message(
                st.session_state.messages,
                chatbot_model_dict["model"],
                chatbot_client,
                analyzer_model_dict["model"],
                analyzer_client,
                stream=True,
            )
        response = output_ai_reply(ai_reply)
        st.session_state.messages.append({"role": "assistant", "content": response})
        if confirmation_requested:
            left, right = st.columns(2)
            left.button(
                "Yes, I confirm",
                icon="✅",
                on_click=finish_interaction,
                use_container_width=True,
            )
            right.button(
                "No, I would like to change or update my order",
                icon="❌",
                on_click=update_order,
                use_container_width=True,
            )
else:
    st.markdown("You can safely navigate away. See you next time!")
