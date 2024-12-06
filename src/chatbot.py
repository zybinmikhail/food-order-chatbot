import openai
import pandas as pd

from loguru import logger


from prompts.intermediate_prompts import (
    ask_for_restaurant,
    ask_for_dishes,
    ask_for_delivery_time,
    ask_for_end,
    greeting,
)


def analyze_conversation(
    template: str,
    messages: list[dict[str, str]],
    model: str,
    client: openai.OpenAI,
    temperature: float = 0.1,
) -> str:
    generator = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": template.format(str(messages))}],
        temperature=temperature,
    )
    return generator.choices[0].message.content


def parse_llm_json(llm_response: str) -> str:
    logger.debug(llm_response)
    if "{" not in llm_response:
        llm_response = "{" + llm_response
    if "}" not in llm_response:
        llm_response = "}" + llm_response
    llm_response = llm_response[llm_response.find("{") : llm_response.find("}") + 1]
    llm_response = eval(llm_response)
    return llm_response


def order(restaurant_name: str, dishes_list: list[str], delivery_time: str) -> None:
    current_chosen_dishes_string = generate_dishes_string(dishes_list)
    order_template = "Your order of {} from {} was successfully received and will be delivered to you by {}"
    print(
        order_template.format(
            current_chosen_dishes_string, restaurant_name, delivery_time
        )
    )


def initialize_menus_string() -> tuple[str, str]:
    with open("../data/restaurants.jsonl") as fin:
        descriptions = fin.readlines()
    restaurant_names = [eval(description)["name"] for description in descriptions]
    menus = []
    for name in restaurant_names:
        with open(f"../data/{name}.jsonl") as fin:
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
    with open("prompts/system_prompt.txt") as fin:
        system_prompt = fin.read()
    descriptions, menus_string = initialize_menus_string()
    system_prompt = system_prompt.format(descriptions, menus_string)
    return system_prompt


def initialize_messages() -> list[dict[str, str]]:
    system_prompt = initialize_system_prompt()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Please help me to order food"},
        {"role": "assistant", "content": greeting},
    ]
    return messages


def generate_dishes_string(current_chosen_dishes):
    current_chosen_dishes_string = []
    for i in range(len(current_chosen_dishes["dish_names"])):
        num_portions = current_chosen_dishes["dish_quantities"][i]
        dish_name = current_chosen_dishes["dish_names"][i]
        portions_word = "portions" if num_portions > 1 else "portion"
        current_chosen_dishes_string.append(
            f"{num_portions} {portions_word} of {dish_name}"
        )
    current_chosen_dishes_string = ", ".join(current_chosen_dishes_string)
    return current_chosen_dishes_string


def get_next_ai_message(
    messages: list[dict[str, str]],
    confirmation_requested: bool,
    model: str,
    client: openai.OpenAI,
    temperature: float = 0.1,
) -> tuple[str, list[dict[str, str]]]:

    logger.debug("Determining the chosen restaurant...")
    current_chosen_restaurant_json = analyze_conversation(
        ask_for_restaurant, messages, model, client
    )
    current_chosen_restaurant = parse_llm_json(current_chosen_restaurant_json)[
        "restaurant_name"
    ]
    logger.debug("Here is the determined chosen restaurant:", current_chosen_restaurant)

    logger.debug("Determining the chosen dishes...")
    current_chosen_dishes_json = analyze_conversation(
        ask_for_dishes, messages, model, client
    )
    current_chosen_dishes = parse_llm_json(current_chosen_dishes_json)
    logger.debug("Here are the determined dishes:", current_chosen_dishes)

    logger.debug("Determining the delivery time...")
    current_delivery_time_json = analyze_conversation(
        ask_for_delivery_time, messages, model, client
    )
    current_delivery_time = parse_llm_json(current_delivery_time_json)["delivery_time"]
    logger.debug("Here is the delivery time:", current_delivery_time)

    is_finished = False
    if confirmation_requested:
        logger.debug("Determining if the order is made and confirmed")
        is_finished_json = analyze_conversation(
            ask_for_end, messages[-1]["content"], model, client
        )
        is_finished = int(parse_llm_json(is_finished_json)["meaning"])
        logger.debug("Is the conversation finished", is_finished)
        if is_finished:
            order(
                current_chosen_restaurant, current_chosen_dishes, current_delivery_time
            )

    if current_chosen_restaurant and current_chosen_dishes and current_delivery_time:
        current_chosen_dishes_string = generate_dishes_string(current_chosen_dishes)
        ai_reply = "You have chosen to order {} from {} by {}. Is that correct?"
        ai_reply = ai_reply.format(
            current_chosen_dishes_string,
            current_chosen_restaurant,
            current_delivery_time,
        )
        confirmation_requested = True
    else:
        ai_reply_generator = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=None,
            temperature=temperature,
        )
        ai_reply = ai_reply_generator.choices[0].message.content
    return ai_reply, confirmation_requested, is_finished


def make_conversation(messages: list[dict[str, str]], model: str, client) -> None:
    confirmation_requested = False
    print("Chatbot: ", end="")
    print(greeting)
    while True:
        print("You: ", end="")
        human_message = input()
        messages.append({"role": "user", "content": human_message})
        ai_reply, confirmation_requested, is_finished = get_next_ai_message(
            messages, confirmation_requested, model, client
        )
        if is_finished:
            break
        print("Chatbot: ", end="")
        print(ai_reply)
        messages.append({"role": "assistant", "content": ai_reply})
