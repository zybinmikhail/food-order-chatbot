import openai
from loguru import logger

from prompts.intermediate_prompts import (
    ask_for_end,
    ask_for_restaurant_dishes_delivery_time,
    greeting,
)


def analyze_conversation(
    template: str,
    messages: list[dict[str, str]],
    model: str,
    client: openai.OpenAI,
) -> str:
    generator = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": template.format(str(messages))}],
        temperature=0.0,
        stop=["}\n```", "python", "I will suggest"],
    )
    return generator.choices[0].message.content


def parse_llm_json(llm_response: str) -> dict[str, str]:
    logger.debug(llm_response)
    if "{" not in llm_response:
        llm_response = "{" + llm_response
    if "}" not in llm_response:
        llm_response = llm_response + "}"
    llm_response = llm_response[llm_response.find("{") : llm_response.find("}") + 1]
    llm_response = eval(llm_response)
    return llm_response


def postprocess_conversation_analysis(current_chosen_info_json):
    try:
        current_chosen_info_json_parsed = parse_llm_json(current_chosen_info_json)
    except SyntaxError:
        return "", "", "", False

    # If not all necessary fields are present, the generation is unsuccessful
    restaurant_in = "restaurant_name" in current_chosen_info_json_parsed
    names_in = "dish_names" in current_chosen_info_json_parsed
    quantities_in = "dish_quantities" in current_chosen_info_json_parsed
    time_in = "delivery_time" in current_chosen_info_json_parsed
    if not (restaurant_in and names_in and quantities_in and time_in):
        return "", "", "", False

    current_chosen_restaurant = current_chosen_info_json_parsed["restaurant_name"]
    current_chosen_dishes = {
        "dish_names": current_chosen_info_json_parsed["dish_names"],
        "dish_quantities": current_chosen_info_json_parsed["dish_quantities"],
    }

    # If the number of dishes is not the same as the number of portions, the generation is unsuccessful
    if len(current_chosen_dishes["dish_names"]) != len(
        current_chosen_dishes["dish_quantities"]
    ):
        return "", "", "", False

    current_delivery_time = current_chosen_info_json_parsed["delivery_time"]
    return current_chosen_restaurant, current_chosen_dishes, current_delivery_time, True


def order(restaurant_name: str, dishes_list: list[str], delivery_time: str) -> None:
    current_chosen_dishes_string = generate_dishes_string(dishes_list)
    order_template = "Chatbot: Your order of {} from {} was successfully received and will be delivered to you by {}"
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
    analyzer_model: str,
    analyzer_client: openai.OpenAI,
    temperature: float = 0.0,
) -> tuple[str, list[dict[str, str]]]:
    current_chosen_info_json = analyze_conversation(
        ask_for_restaurant_dishes_delivery_time,
        messages,
        analyzer_model,
        analyzer_client,
    )

    # In case of wrong json format, just repeat
    success = False
    while not success:
        (
            current_chosen_restaurant,
            current_chosen_dishes,
            current_delivery_time,
            success,
        ) = postprocess_conversation_analysis(current_chosen_info_json)

    is_finished = False
    if confirmation_requested:
        logger.debug("Determining if the order is made and confirmed")
        is_finished_json = analyze_conversation(
            ask_for_end, messages[-1]["content"], model, client
        )
        is_finished = int(parse_llm_json(is_finished_json)["meaning"])
        logger.debug("Is the conversation finished" + str(is_finished))
        if is_finished:
            order(
                current_chosen_restaurant, current_chosen_dishes, current_delivery_time
            )

    if (
        current_chosen_restaurant
        and current_chosen_dishes["dish_names"]
        and current_delivery_time
    ):
        current_chosen_dishes_string = generate_dishes_string(current_chosen_dishes)
        add_by = "" if current_delivery_time.startswith("within") else " by"
        ai_reply = "You have chosen to order {} from {}{} {}. Is that accurate?"
        ai_reply = ai_reply.format(
            current_chosen_dishes_string,
            current_chosen_restaurant,
            add_by,
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


def make_conversation(
    messages: list[dict[str, str]],
    model: str,
    client: openai.OpenAI,
    analyzer_model: str,
    analyzer_client: openai.OpenAI,
) -> None:
    confirmation_requested = False
    print("Chatbot: ", end="")
    print(greeting)
    while True:
        print("You: ", end="")
        human_message = input()
        messages.append({"role": "user", "content": human_message})
        ai_reply, confirmation_requested, is_finished = get_next_ai_message(
            messages,
            confirmation_requested,
            model,
            client,
            analyzer_model,
            analyzer_client,
        )
        if is_finished:
            break
        print("Chatbot: ", end="")
        print(ai_reply)
        messages.append({"role": "assistant", "content": ai_reply})
