from typing import Generator

import secrets
import string
import streamlit as st
import openai
import yaml
import orjson

from chatbot import initialize_messages, get_next_ai_message

CONFIG = yaml.safe_load(open("config.yaml", "r"))

def end_conversation() -> None:
    del st.session_state["messages"]


def reset_conversation() -> None:
    end_conversation()
    st.session_state.is_finished = False


def display_headers() -> None:
    headers = ["What this chatbot can do", "Usage guidelines"]
    paths = [
        "src/what_chatbot_can_do.txt",
        "src/usage_guidelines.txt",
    ]
    for header, path in zip(headers, paths):
        with open(path, "r", encoding="utf-8") as fin:
            content = fin.read()
        st.header(header)
        st.markdown(content)


def finish_interaction() -> None:
    st.session_state.is_finished = True
    # Generate a random order ID
    # using uppercase letters and digits
    # The order ID is 6 characters long
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
        "Quit",
        icon="🔚",
        on_click=end_conversation,
        use_container_width=True,
    )
    right.button(
        "Place a new order",
        icon="🔄",
        on_click=reset_conversation,
        use_container_width=True,
    )


def output_ai_reply(ai_reply: openai.Stream) -> str:
    with st.chat_message("assistant"):
        response = st.write_stream(ai_reply)
    return str(response)


def update_order() -> None:
    st.session_state.messages.append(
        {"role": "user", "content": CONFIG["update_order_user_msg"]}
    )
    st.session_state.messages.append({"role": "assistant", "content": CONFIG["update_order_ai_msg"]})
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

azure_client = openai.AzureOpenAI(
    api_key=chatbot_model_dict["api_key"],
    azure_endpoint=chatbot_model_dict["api_base"],
    api_version="2025-04-01-preview",
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
        if isinstance(message, dict) and message["role"] in ["user", "assistant"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if human_message := st.chat_input(
        placeholder=CONFIG["input_placeholder"],
        max_chars=CONFIG["max_input_length"],
    ):
        with st.chat_message("user"):
            st.markdown(human_message)
        st.session_state.messages.append({"role": "user", "content": human_message})

        if not CONFIG["use_tools"]:
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
                    CONFIG["confirmation_agree_msg"],
                    icon="✅",
                    on_click=finish_interaction,
                    use_container_width=True,
                )
                right.button(
                    CONFIG["confirmation_disagree_msg"],
                    icon="❌",
                    on_click=update_order,
                    use_container_width=True,
                )

        else:
            response = azure_client.chat.completions.create(
                model=chatbot_model,
                messages=st.session_state.messages,
                temperature=CONFIG["temperature"],
                tools=tools_list,
                tool_choice="auto",
                stream=True,
            )
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            print(response_message)
            if tool_calls:
                st.session_state.messages.append(response_message)
                for i in range(len(tool_calls)):
                    tool_call_id = tool_calls[i].id
                    tool_function_name = tool_calls[i].function.name
                    print(tool_function_name)

                    print(
                        "TOOL ARGUMENTS:",
                        orjson.loads(tool_calls[i].function.arguments),
                    )
                    tool_arguments = orjson.loads(tool_calls[i].function.arguments)

                    results = functions_by_name[tool_function_name](**tool_arguments)

                    st.session_state.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "name": tool_function_name,
                            "content": results,
                        }
                    )

                    if tool_function_name == "ask_for_order_confirmation":
                        # Move this to the tool function
                        left, right = st.columns(2)
                        left.button(
                            CONFIG["confirmation_agree_msg"],
                            icon="✅",
                            on_click=finish_interaction,
                            use_container_width=True,
                        )
                        right.button(
                            CONFIG["confirmation_disagree_msg"],
                            icon="❌",
                            on_click=update_order,
                            use_container_width=True,
                        )

                print(st.session_state.messages)

                model_response_with_function_call = (
                    azure_client.chat.completions.create(
                        model=chatbot_model,
                        messages=st.session_state.messages,
                        temperature=CONFIG["temperature"],
                        stream=True,
                    )
                )
                ai_reply = model_response_with_function_call.choices[0].message.content
            else:
                ai_reply = response_message.content

            response = output_ai_reply(ai_reply)
            st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.markdown("You can safely navigate away. See you next time!")
