import openai
import pandas as pd

from loguru import logger


from prompts.intermediate_prompts import (
    ask_for_restaurant,
    ask_for_dishes,
    ask_for_delivery_time, 
    greeting,
)

def analyze_conversation(
    template: str,
    messages: list[dict[str, str]],
    model: str,
    client: openai.OpenAI,    
    temperature: float = 0.2,
) -> str:
    generator = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": template.format(str(messages))}
        ],
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
    return list(llm_response.values())[0]


def order(restaurant_name: str, dishes_list: list[str], delivery_time: str) -> None:
    order_template = "Your order of {} from {} was successfully received and will be delivered to you by {}"
    print(order_template.format(", ".join(dishes_list), restaurant_name, delivery_time))


def get_next_ai_message(
    messages: list[dict[str, str]],
    model: str,
    client: openai.OpenAI,
    temperature: float = 0.1,
) -> tuple[str, list[dict[str, str]]]:

    logger.debug("Determining the chosen restaurant...")
    current_chosen_restaurant_json = analyze_conversation(ask_for_restaurant, messages, model, client)
    current_chosen_restaurant = parse_llm_json(current_chosen_restaurant_json)
    logger.debug("Here is the determined chosen restaurant:", current_chosen_restaurant)
    
    logger.debug("Determining the chosen dishes...")
    current_chosen_dishes_json = analyze_conversation(ask_for_dishes, messages, model, client)
    current_chosen_dishes = parse_llm_json(current_chosen_dishes_json)
    logger.debug("Here are the determined dishes:", current_chosen_dishes)
    
    logger.debug("Determining the delivery time...")
    current_delivery_time_json = analyze_conversation(ask_for_delivery_time, messages, model, client)
    current_delivery_time = parse_llm_json(current_delivery_time_json)
    logger.debug("Here is the delivery time:", current_delivery_time)

    if current_chosen_restaurant and current_chosen_dishes and current_delivery_time:
        ai_reply = "You have chosen to order {} from {} by {}. Is that correct? If so, please type 'I confirm' and our conversation will be over."
        ai_reply = ai_reply.format(current_chosen_dishes, current_chosen_restaurant, current_delivery_time)
    else:
        
        # is_finished_flag = analyze_conversation(ask_is_finished, messages)
        # if is_finished_flag == "Yes":
        #     order(current_chosen_restaurant, current_chosen_dishes, current_delivery_time)
        #     break
    
        ai_reply_generator = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=None,
            temperature=temperature,
        )
        ai_reply = ai_reply_generator.choices[0].message.content
    return ai_reply


def initialize_system_prompt() -> list[dict[str, str]]:
    with open("prompts/system_prompt.txt") as fin:
        system_prompt = fin.read()
    descriptions = pd.read_csv("../data/restaurants.csv", sep=";")
    restaurant_names = set(descriptions.name)
    system_prompt = system_prompt.format(descriptions.to_markdown())
    menus = []
    for name in restaurant_names:
        one_menu = f"""\n#### {name} menu table
        Here are the only dishes that are available at {name}
        <{name} menu table>
        {pd.read_csv(f"../data/{name}.csv", sep=";").to_markdown()}
        </{name} menu table>
        """
        menus.append(one_menu)
    menus_string = "\n".join(menus)
    system_prompt = system_prompt.format(menus_string)
    return system_prompt


def initialize_messages() -> list[dict[str, str]]:
    system_prompt = initialize_system_prompt()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Please help me to order food"},
        {"role": "assistant", "content": greeting}
    ]
    return messages


def make_conversation(messages: list[dict[str, str]], model: str, client) -> None:
    print("Chatbot: ", end="")
    print(greeting)
    while True:
        print("You: ", end="")
        human_message = input()
        if human_message == "I confirm":
            print("Chatbot: Great! Have a nice meal, our conversation is over.")
            break
        
        messages.append({"role": "user", "content": human_message})
        ai_reply = get_next_ai_message(messages, model, client)
        print("Chatbot: ", end="")
        print(ai_reply)
        messages.append({"role": "assistant", "content": ai_reply})
