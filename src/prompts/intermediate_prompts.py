greeting = """Hello, Dear Customer!

I am food order chatbot! My function is to help you choose and order food from various cafes and restaurants.

What would you like to eat today?"""

ask_for_restaurant = """You are conversation analyzer.

Please review the conversation between the food ordering chatbot and the user.

Carefully analyze the user's replies and the order summary made by the chatbot.

Has the user already told the chatbot what restaurant they have chosen to have order from?

Keep in mind that the user can change their order.

Keep in mind: if the user has chosen a specific dish, it means they have chosen the restaurant where this dish comes from.

Here is the conversation in the form of Python dictionary:
<conversation>
{}
</conversation>

Output format:
```json
{{
  "restaurant_name": "Restaurant name that the user has chosen during the conversation or empty if not chosen"
}}
```

Carefully analyze the user's replies and the order summary made by the chatbot.

Has the user already told the chatbot what restaurant they have chosen to have order from?

Keep in mind that the user can change their order. If the user canceled their order, it means they do not want the dishes from that order.  Newer information has higher priority.

Keep in mind: if the user has chosen a specific dish, it means they have also chosen the restaurant where this dish comes from.

Keep in mind: all dishes must be from the same restaurant that the user has chosen.

Your task is to output valid json strictly in output format. Don't output anything else.
"""

ask_for_dishes = """You are conversation analyzer.

Please review the conversation between the food ordering chatbot and the user.

Carefully analyze the user's replies and the order summary made by the chatbot.

Has the user already told the chatbot what dishes they have chosen to order? All the dishes must come from the same restaurant.

Keep in mind that the user can change their order. Newer information has higher priority.

Here is the conversation in the form of Python dictionary:

<conversation>
{}
</conversation>

If the user has already told the chatbot what dishes they have chosen to order, then output the dishes the user ordered and the number of portions for each dish. If the user has not ordered anything yet, output the empty dictionary.

Output format:
```json
{{
  "dish_name_1": "the number of portions of dish_name_1 (if applicable)",
  "dish_name_2": "the number of portions of dish_name_2 (if applicable)",
  ...
  "dish_name_n": "the number of portions of dish_name_n (if applicable, where n is the total numner of ordered dishes)",
}}
```

Carefully analyze the user's replies and the order summary made by the chatbot.

Based on our conversation so far, has the user already provided chatbot with the information about what dishes they want to order?  All the dishes must come from the same restaurant.

Keep in mind that the user can change their order. Newer information has higher priority.

Your task is to output valid json strictly in output format. Don't output anything else.
"""

ask_for_delivery_time = """You are conversation analyzer.

Please review the conversation between the food ordering chatbot and the user.

Carefully analyze the user's replies and the order summary made by the chatbot.

Has the user already provided chatbot with the information about what delivery time they have chosen?

Keep in mind that the user can change their order. Newer information has higher priority.

Here is the conversation in the form of Python dictionary:
<conversation>
{}
</conversation>

Output format:
```json
{{
  "delivery_time": "Delivery time that the user has chosen during the conversation or empty if not chosen"
}}
```

Carefully analyze the user's replies and the order summary made by the chatbot.

Has the user already provided chatbot with the information about what delivery time they have chosen?

Keep in mind that the user can change their order.

Your task is to output valid json strictly in output format. Don't output anything else.
"""

is_this_confirmation = """
Please examine the phrase and determine whether it means confirmation.

Example confirmation phrases are:
- I confirm
- I confirm.
- confirm

Here is the phrase itself:
<given phrase>
{}
</given phrase>

Output format:
```json
{{
  "is_confirmation": True if the meaning of the given phrase is confirmation, False otherwise
}}
Your task is to output valid json strictly in output format. Don't output anything else.
"""
