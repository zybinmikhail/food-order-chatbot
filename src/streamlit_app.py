import secrets
import string

import nest_asyncio
import openai
import orjson
import streamlit as st
import yaml

from chatbot import initialize_messages

nest_asyncio.apply()
import asyncio
import logging
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


with open("config.yaml") as fin:
    CONFIG = yaml.safe_load(fin)


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
        with open(path, encoding="utf-8") as fin:
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
        f"Your order has been received. Order ID is {order_id}. "
        "Remember to write it down! "
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


def output_ai_reply(ai_reply: openai.Stream | str) -> str:
    if isinstance(ai_reply, str):
        ai_reply = (c for c in ai_reply)

    with st.chat_message("assistant"):
        response = st.write_stream(ai_reply)
    return str(response)


def update_order() -> None:
    update_msg = CONFIG["update_order_ai_msg"]
    st.session_state.messages.append(
        {"role": "user", "content": CONFIG["update_order_user_msg"]}
    )
    st.session_state.messages.append({"role": "assistant", "content": update_msg})
    with st.chat_message("assistant"):
        st.markdown(update_msg)


def remove_titles_from_input_schema(schema: dict) -> dict:
    # Remove 'title' from the root if present
    schema = dict(schema)  # Make a shallow copy
    schema.pop("title", None)
    # Remove 'title' from all properties if present
    if "properties" in schema:
        for value in schema["properties"].values():
            if isinstance(value, dict):
                value.pop("title", None)
    return schema


async def run_mcp_tool(tool_name, tool_args):
    exit_stack = AsyncExitStack()
    server_params = StdioServerParameters(
        command="python",
        args=["src/mcp_server.py"],
        env=None,
    )
    stdio_gen = stdio_client(server_params)
    stdio_transport = await exit_stack.enter_async_context(stdio_gen)
    mcp_session = await exit_stack.enter_async_context(
        ClientSession(stdio_transport[0], stdio_transport[1])
    )
    await mcp_session.initialize()
    result = await mcp_session.call_tool(tool_name, tool_args)
    await exit_stack.aclose()
    return result


async def get_tools_list():
    exit_stack = AsyncExitStack()
    server_params = StdioServerParameters(
        command="python",
        args=["src/mcp_server.py"],
        env=None,
    )
    stdio_gen = stdio_client(server_params)
    stdio_transport = await exit_stack.enter_async_context(stdio_gen)
    mcp_session = await exit_stack.enter_async_context(
        ClientSession(stdio_transport[0], stdio_transport[1])
    )
    await mcp_session.initialize()
    response = await mcp_session.list_tools()
    tools_list = [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": dict(
                    remove_titles_from_input_schema(tool.inputSchema),
                    **{"additionalProperties": False},
                ),
                "strict": True,
            },
        }
        for tool in response.tools
    ]
    await exit_stack.aclose()
    return tools_list


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
azure_client = openai.AzureOpenAI(
    api_key=chatbot_model_dict["api_key"],
    azure_endpoint=chatbot_model_dict["api_base"],
    api_version="2024-02-01",
)
logger.info(chatbot_model_dict["api_base"])
logger.info(chatbot_model)

# Setup a persistent event loop for all async operations
try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

if "tools_list" not in st.session_state:
    st.session_state.tools_list = loop.run_until_complete(get_tools_list())

if "is_finished" not in st.session_state or not st.session_state.is_finished:
    st.title("Food order chatbot")
    display_headers()
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = initialize_messages()
        st.session_state.confirmation_requested = False
        st.session_state.is_finished = False

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
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
        confirmation_requested = False

        logger.info(f"Tools list: {st.session_state.tools_list}")
        logger.info(f"Chatbot model: {chatbot_model}")

        with st.spinner("Analyzing your response...", show_time=True):
            response = azure_client.chat.completions.create(
                model=chatbot_model,
                messages=st.session_state.messages,
                tools=st.session_state.tools_list,
                max_tokens=CONFIG["max_tokens"],
                temperature=CONFIG["temperature"],
            )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        logger.info(f"LLM reply token count: {response.usage.completion_tokens}")

        if tool_calls:
            st.session_state.messages.append(response_message)

            for i in range(len(tool_calls)):
                tool_call_id = tool_calls[i].id
                tool_name = tool_calls[i].function.name
                tool_args = orjson.loads(tool_calls[i].function.arguments)

                logger.info(f"Tool call {i}: {tool_name} with args {tool_args}")

                result_response = loop.run_until_complete(
                    run_mcp_tool(tool_name, tool_args)
                )

                result = result_response.content[0].text
                logger.info(f"Result from tool {tool_name}: {result}")

                st.session_state.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": tool_name,
                        "content": result,
                    }
                )

                if tool_name == "ask_for_order_confirmation":
                    confirmation_requested = True

            with st.spinner("Preparing final reply...", show_time=True):
                model_response_with_function_call = (
                    azure_client.chat.completions.create(
                        model=chatbot_model,
                        messages=st.session_state.messages,
                        temperature=CONFIG["temperature"],
                        max_tokens=CONFIG["max_tokens"],
                    )
                )
            response = model_response_with_function_call.choices[0].message.content
        else:
            response = response_message.content

        with st.chat_message("assistant"):
            st.markdown(response)
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
    st.markdown("You can safely navigate away. See you next time!")
