from typing import Any
import json
import pandas as pd


def get_restaurant_descriptions() -> str:
    """Retrieves descriptions of all available restaurants.

    Returns:
        str: Markdown table with restaurant descriptions.
    """
    with open("../data/restaurants.jsonl", "r") as f:
    restaurants: list[dict[str, Any]] = [json.loads(line) for line in f.readlines()]

    RESTAURANT_DESCRIPTIONS: str = pd.DataFrame(restaurants).to_markdown()
    return RESTAURANT_DESCRIPTIONS

    
def get_restaurant_menu(restaurant_name: str) -> str:
    """Retrieves the menu for a given restaurant.

    Args:
        restaurant_name (str): The name of the restaurant for which to get the menu.

    Returns:
        str: Markdown table with the restaurant's menu, or an error message if not found.
    """
    try:
        with open(f"../data/{restaurant_name}.jsonl", "r") as f:
            menu: list[dict[str, Any]] = [json.loads(line) for line in f.readlines()]
    except FileNotFoundError:
        return f"Menu for {restaurant_name} not found."
    menu_df = pd.DataFrame(menu)
    return menu_df.to_markdown()


def generate_dishes_string(dish_names: list[str], dish_quantities: list[int]) -> str:
    """Generates a string describing the chosen dishes and their quantities.

    Args:
        dish_names (list[str]): Names of the dishes.
        dish_quantities (list[int]): Quantities for each dish.

    Returns:
        str: Human-readable string describing the order.
    """
    current_chosen_dishes_list: list[str] = []
    for (num_portions, dish_name) in zip(dish_quantities, dish_names):
        num_portions = int(num_portions)
        portions_word = "portions" if num_portions > 1 else "portion"
        current_chosen_dishes_list.append(
            f"{num_portions} {portions_word} of {dish_name}"
        )
    current_chosen_dishes_string = ", ".join(current_chosen_dishes_list)
    return current_chosen_dishes_string


def ask_for_order_confirmation(
    restaurant_name: str,
    dish_names: list[str],
    dish_quantities: list[int],
    delivery_time: str
) -> str:
    """Asks the user for confirmation of their order.

    Args:
        restaurant_name (str): The name of the restaurant chosen by the user.
        dish_names (list[str]): The names of the dishes chosen by the user.
        dish_quantities (list[int]): The quantities of each dish chosen by the user.
        delivery_time (str): The time when the user wants the food to be delivered.

    Returns:
        str: Confirmation message for the user.
    """
    chosen_dishes_string = generate_dishes_string(dish_names, dish_quantities)
    if not delivery_time.startswith("within") and not delivery_time.startswith("by"):
        add_by = " by"
    else:
        add_by = ""
    ai_reply_template = (
        "You have chosen to order {} from {}{} {}. Is that accurate?"
    )
    ai_reply = ai_reply_template.format(
        chosen_dishes_string,
        restaurant_name,
        add_by,
        delivery_time,
    )
    return ai_reply


rest_descriptions_tool: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "get_restaurant_descriptions",
        "description": "Get descriptions of all available restaurants.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        },
        "strict": True
    }
}

rest_menu_tool: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "get_restaurant_menu",
        "description": "Get menu for a given restaurant.",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_name": {
                    "type": "string",
                    "description": "The name of the restaurant for which to get the menu."
                }
            },
            "required": [
                "restaurant_name"
            ],
            "additionalProperties": False
        },
        "strict": True
    }
}

ask_for_order_confirmation_tool: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "ask_for_order_confirmation",
        "description": "Ask the user for confirmation of their order.",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_name": {
                    "type": "string",
                    "description": "The name of the restaurant chosen by the user."
                },
                "dish_names": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "The names of the dishes chosen by the user. Must be of the same length as dish_quantities."
                },
                "dish_quantities": {
                    "type": "array",
                    "items": {
                        "enum":[1, 2, 3, 4, 5]
                    },
                    "description": "The quantities of each dish chosen by the user. Must be of the same length as dish_names."
                },
                "delivery_time": {
                    "type": "string",
                    "description": "The time when the user wants the food to be delivered."
                },
            },
            "required": [
                "restaurant_name",
                "dish_names",
                "dish_quantities",
                "delivery_time"
            ],
            "additionalProperties": False
        },
        "strict": True
    }
}


tools_list: list[dict[str, Any]] = [
    rest_descriptions_tool,
    rest_menu_tool,
    ask_for_order_confirmation_tool,
]

functions_by_name: dict[str, Any] = {
    "get_restaurant_descriptions": get_restaurant_descriptions,
    "get_restaurant_menu": get_restaurant_menu,
    "ask_for_order_confirmation": ask_for_order_confirmation
}
