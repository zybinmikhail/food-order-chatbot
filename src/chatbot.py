
import sys

import openai
import orjson
import yaml
from loguru import logger
from pydantic import BaseModel, Field, validator

sys.path.append("../")

from prompts import SYSTEM_PROMPT, SYSTEM_PROMPT_WITH_TOOLS
from prompts.intermediate_prompts import (
    ask_for_restaurant_dishes_delivery_time,
    greeting,
)

with open("config.yaml") as fin:
    CONFIG = yaml.safe_load(fin)


class AIResponse(BaseModel):
    restaurant_name: str = Field(
        description="The name of the restaurant chosen by the user."
    )
    dish_names: list[str] = Field(
        description="The names of the dishes chosen by the user."
    )
    dish_quantities: list[str] = Field(
        description="The quantities of each dish chosen by the user."
    )
    delivery_time: str = Field(
        description="The time when the user wants the food to be delivered."
    )

    @validator("dish_quantities")
    def validate_dish_quantities(cls, v, values):
        if len(v) != len(values.get("dish_names", [])):
            raise ValueError("dish_quantities must have the same length as dish_names")
        return v


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
        stop=["\n```"],
    )
    ai_reply = str(generator.choices[0].message.content) + "\n```"
    return ai_reply


def parse_llm_json(reply: str) -> AIResponse | None:
    logger.info(f"Parsing LLM JSON: {reply}")
    try:
        json_text = reply[reply.find("```json") + 7 : reply.rfind("```")]
        return AIResponse.model_validate(orjson.loads(json_text))
    except (ValueError, AttributeError) as e:
        logger.error(f"Failed to parse JSON: {e}")
        return None


def postprocess_conversation_analysis(
    current_chosen_info_json_parsed: AIResponse,
) -> tuple[str, dict[str, list[str]], str]:
    current_chosen_restaurant = current_chosen_info_json_parsed.restaurant_name
    current_delivery_time = current_chosen_info_json_parsed.delivery_time
    current_chosen_dishes: dict[str, list[str]] = {
        "dish_names": current_chosen_info_json_parsed.dish_names,
        "dish_quantities": current_chosen_info_json_parsed.dish_quantities,
    }
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
<menu 'restaurant_name'="{name}">
{menu}
</menu>
"""
        menus.append(one_menu)
    menus_string = "\n".join(menus)
    descriptions_string = "".join(descriptions)
    return descriptions_string, menus_string


def initialize_system_prompt(use_tools: bool) -> str:
    if not use_tools:
        descriptions, menus_string = initialize_menus_string()
        return SYSTEM_PROMPT.format(descriptions, menus_string)
    return SYSTEM_PROMPT_WITH_TOOLS


def initialize_messages() -> list[dict[str, str]]:
    system_prompt = initialize_system_prompt(CONFIG["use_tools"])
    messages = [
        {"role": "system", "content": system_prompt},
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
) -> tuple[str | openai.Stream, bool]:
    success = False
    while not success:
        current_chosen_info_json = analyze_conversation(
            ask_for_restaurant_dishes_delivery_time,
            messages,
            analyzer_model,
            analyzer_client,
        )
        current_chosen_info_json_parsed = parse_llm_json(current_chosen_info_json)
        if current_chosen_info_json_parsed is not None:
            current_chosen_restaurant, current_chosen_dishes, current_delivery_time = (
                postprocess_conversation_analysis(current_chosen_info_json_parsed)
            )
            success = True

    ai_reply: str | openai.Stream
    if (
        current_chosen_restaurant
        and current_chosen_dishes["dish_names"]
        and current_delivery_time
        and (max(current_chosen_dishes["dish_quantities"]) <= 5)
        and (min(current_chosen_dishes["dish_quantities"]) >= 1)
    ):
        confirmation_requested = True
        current_chosen_dishes_string = generate_dishes_string(current_chosen_dishes)
        if not current_delivery_time.startswith(
            "within"
        ) and not current_delivery_time.startswith("by"):
            add_by = " by"
        else:
            add_by = ""
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
            temperature=CONFIG["temperature"],
            stream=stream,
        )
        if stream:
            ai_reply = ai_reply_generator
        else:
            ai_reply = str(ai_reply_generator.choices[0].message.content)
    return ai_reply, confirmation_requested
