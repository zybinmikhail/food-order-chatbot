from typing import Any, Generator

import openai
from loguru import logger

import sys

sys.path.append("../")

from prompts.intermediate_prompts import (
    ask_for_restaurant_dishes_delivery_time,
    greeting,
)
from prompts import SYSTEM_PROMPT


def analyze_conversation(
    template: str,
    messages: list[dict[str, str]] | str,
    model: str,
    client: openai.OpenAI,
) -> str:
    generator = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": template.format(str(messages))}],
        temperature=0.0,
        timeout=120,
        stop=["}\n```", "python", "I will suggest"],
    )
    ai_reply = str(generator.choices[0].message.content)
    return ai_reply


def parse_llm_json(llm_response: str) -> dict[str, Any]:
    logger.debug(llm_response)
    if "{" not in llm_response:
        llm_response = "{" + llm_response
    if "}" not in llm_response:
        llm_response = llm_response + "}"
    llm_response = llm_response[llm_response.find("{") : llm_response.find("}") + 1]
    llm_response_evaluated = eval(llm_response)
    return llm_response_evaluated


def postprocess_conversation_analysis(
    current_chosen_info_json: str,
) -> tuple[str, dict[str, list[str]], str] | bool:
    try:
        current_chosen_info_json_parsed = parse_llm_json(current_chosen_info_json)
    except SyntaxError:
        return False

    # If not all necessary fields are present, the generation is unsuccessful
    restaurant_in = "restaurant_name" in current_chosen_info_json_parsed
    names_in = "dish_names" in current_chosen_info_json_parsed
    quantities_in = "dish_quantities" in current_chosen_info_json_parsed
    time_in = "delivery_time" in current_chosen_info_json_parsed
    if not (restaurant_in and names_in and quantities_in and time_in):
        return False

    current_chosen_restaurant = current_chosen_info_json_parsed["restaurant_name"]
    dish_names: list[str] = current_chosen_info_json_parsed["dish_names"]
    dish_quantities: list[str] = current_chosen_info_json_parsed["dish_quantities"]
    current_chosen_dishes: dict[str, list[str]] = {
        "dish_names": dish_names,
        "dish_quantities": dish_quantities,
    }

    # If the number of dishes is not the same as the number of portions, the generation is unsuccessful
    if len(current_chosen_dishes["dish_names"]) != len(
        current_chosen_dishes["dish_quantities"]
    ):
        return False

    current_delivery_time = current_chosen_info_json_parsed["delivery_time"]
    return current_chosen_restaurant, current_chosen_dishes, current_delivery_time


def initialize_menus_string() -> tuple[str, str]:
    with open("data/restaurants.jsonl") as fin:
        descriptions = fin.readlines()
    restaurant_names = [eval(description)["name"] for description in descriptions]
    menus = []
    for name in restaurant_names:
        with open(f"data/{name}.jsonl") as fin:
            menu = fin.read()
        one_menu = f"""\n#### {name} menu
Here are the only dishes that are available at {name}
<{name} menu>
{menu}
</{name} menu>
"""
        menus.append(one_menu)
    menus_string = "\n".join(menus)
    descriptions_string = "".join(descriptions)
    return descriptions_string, menus_string


def initialize_system_prompt() -> str:
    descriptions, menus_string = initialize_menus_string()
    system_prompt = SYSTEM_PROMPT.format(descriptions, menus_string)
    return system_prompt


def initialize_messages() -> list[dict[str, str]]:
    system_prompt = initialize_system_prompt()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Please help me to order food"},
        {"role": "assistant", "content": greeting},
    ]
    return messages


def generate_dishes_string(current_chosen_dishes: dict[str, list[str]]) -> str:
    current_chosen_dishes_list = []
    for i in range(len(current_chosen_dishes["dish_names"])):
        num_portions = int(current_chosen_dishes["dish_quantities"][i])
        dish_name = current_chosen_dishes["dish_names"][i]
        portions_word = "portions" if num_portions > 1 else "portion"
        current_chosen_dishes_list.append(
            f"{num_portions} {portions_word} of {dish_name}"
        )
    current_chosen_dishes_string = ", ".join(current_chosen_dishes_list)
    return current_chosen_dishes_string


def get_next_ai_message(
    messages: list[dict[str, str]],
    model: str,
    client: openai.OpenAI,
    analyzer_model: str,
    analyzer_client: openai.OpenAI,
    stream=False,
) -> tuple[str | Generator, bool]:
    # In case of wrong json format, just repeat
    success = False
    while not success:
        current_chosen_info_json = analyze_conversation(
            ask_for_restaurant_dishes_delivery_time,
            messages,
            analyzer_model,
            analyzer_client,
        )
        postprocess_result = postprocess_conversation_analysis(current_chosen_info_json)
        if not postprocess_result:
            success = False
        else:
            current_chosen_restaurant, current_chosen_dishes, current_delivery_time = (
                postprocess_result
            )
            success = True
    ai_reply: str | Generator
    if (
        current_chosen_restaurant
        and current_chosen_dishes["dish_names"]
        and current_delivery_time
    ):
        confirmation_requested = True
        current_chosen_dishes_string = generate_dishes_string(current_chosen_dishes)
        add_by = "" if current_delivery_time.startswith("within") else " by"
        ai_reply_template = (
            "You have chosen to order {} from {}{} {}. Is that accurate?"
        )
        ai_reply = ai_reply_template.format(
            current_chosen_dishes_string,
            current_chosen_restaurant,
            add_by,
            current_delivery_time,
        )
        if stream:
            ai_reply = (symbol for symbol in ai_reply)
    else:
        confirmation_requested = False
        ai_reply_generator = client.chat.completions.create(
            model=model,
            messages=messages,  # type: ignore
            max_tokens=None,
            timeout=120,
            temperature=0.0,
            stream=stream,
        )
        if stream:
            ai_reply = ai_reply_generator
        else:
            ai_reply = str(ai_reply_generator.choices[0].message.content)
    return ai_reply, confirmation_requested
