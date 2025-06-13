from datetime import datetime
from pathlib import Path
from typing import Any

import orjson
import pandas as pd
from mcp.server.fastmcp import FastMCP

CURRENT_DIR = Path(__file__).parent

mcp = FastMCP("restaurants")


@mcp.tool()
def get_restaurant_descriptions() -> str:
    """Retrieves descriptions of all available restaurants.

    Returns:
        str: Markdown table with restaurant descriptions.
    """

    with open(CURRENT_DIR.parent / "data/restaurants.jsonl") as f:
        restaurants: list[dict[str, Any]] = [
            orjson.loads(line) for line in f.readlines()
        ]

    RESTAURANT_DESCRIPTIONS: str = pd.DataFrame(restaurants).to_markdown()
    return RESTAURANT_DESCRIPTIONS


@mcp.tool()
def get_restaurant_menu(restaurant_name: str) -> str:
    """Retrieves the menu for a given restaurant.

    Args:
        restaurant_name (str): The name of the restaurant for which to get the menu.

    Returns:
        str: Markdown table with the menu, or an error message if not found.
    """
    try:
        with open(CURRENT_DIR.parent / f"data/{restaurant_name}.jsonl") as f:
            menu: list[dict[str, Any]] = [orjson.loads(line) for line in f.readlines()]
    except FileNotFoundError:
        return f"Menu for {restaurant_name} not found."
    menu_df = pd.DataFrame(menu)
    return menu_df.to_markdown()


@mcp.tool()
def generate_dishes_string(dish_names: list[str], dish_quantities: list[int]) -> str:
    """Generates a string describing the chosen dishes and their quantities.

    Args:
        dish_names (list[str]): Names of the dishes.
        dish_quantities (list[int]): Quantities for each dish.

    Returns:
        str: Human-readable string describing the order.
    """
    current_chosen_dishes_list: list[str] = []
    for num_portions, dish_name in zip(dish_quantities, dish_names):
        num_portions = int(num_portions)
        portions_word = "portions" if num_portions > 1 else "portion"
        current_chosen_dishes_list.append(
            f"{num_portions} {portions_word} of {dish_name}"
        )
    current_chosen_dishes_string = ", ".join(current_chosen_dishes_list)
    return current_chosen_dishes_string


@mcp.tool()
def ask_for_order_confirmation(
    restaurant_name: str,
    dish_names: list[str],
    dish_quantities: list[int],
    delivery_time: str,
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
    ai_reply_template = "You have chosen to order {} from {}{} {}. Is that accurate?"
    ai_reply = ai_reply_template.format(
        chosen_dishes_string,
        restaurant_name,
        add_by,
        delivery_time,
    )
    return ai_reply


@mcp.tool()
def get_current_datetime() -> str:
    """Retrieves the current date, time, day of the week.

    Returns:
        str: Current date, time, day of the week in ISO format.
    """
    return datetime.now().strftime("%Y-%m-%dT%H:%M (%A)")


if __name__ == "__main__":
    mcp.run(transport="stdio")
