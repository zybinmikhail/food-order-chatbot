greeting = """Hello, dear Customer!

I am food order chat bot! My function is to help you choose and order food from various cafes and restaurants.

What would you like to eat today?"""

ask_for_restaurant = """Please review the conversation between the food ordering chat bot and the user.

Carefully analyze the user's replies.

Has the user already told the chatbot what restaurant they have chosen to have order from?

Keep in mind that the user can change their opinion.

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

Carefully analyze the user's replies.

Has the user already told the chatbot what restaurant they have chosen to have order from?

Keep in mind that the user can change their opinion.

Your task is to output valid json strictly in output format. Don't output anything else.
"""

ask_for_dishes = """Please review the conversation between the food ordering chat bot and the user.

Carefully analyze the user's replies.

Based on our conversation so far, has the user already provided chatbot with the exact information about what dishes they want to order?

Keep in mind that the user can change their opinion.

Here is the conversation in the form of Python dictionary:

<conversation>
{}
</conversation>

Output format:
```json
{{
  "dishes": "List of dishes that the user has chosen during the conversation or empty if not chosen"
}}
```

Carefully analyze the user's replies.

Based on our conversation so far, has the user already provided chatbot with the exact information about what dishes they want to order?

Keep in mind that the user can change their opinion.

Your task is to output valid json strictly in output format. Don't output anything else.
"""

ask_for_delivery_time = """Please review the conversation between the food ordering chat bot and the user.

Carefully analyze the user's replies.

Has the user already provided chatbot with the information about what delivery time they have chosen?

Keep in mind that the user can change their opinion.

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

Carefully analyze the user's replies.

Has the user already provided chatbot with the information about what delivery time they have chosen?

Keep in mind that the user can change their opinion.

Your task is to output valid json strictly in output format. Don't output anything else.
"""


ask_is_finished = """Please review the conversation between the food ordering chat bot and the user.

Based on our conversation so far, please determine whether the conversation is finished.

Here is the conversation in the form of Python dictionary:
<conversation>
{}
</conversation>

if it is finished, output the string "yes"
if it is not finished, output the string "no"
"""
