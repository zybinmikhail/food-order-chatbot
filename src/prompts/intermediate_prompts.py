greeting = """Hello, Dear Customer!

I am food order chatbot! My function is to help you choose and order food from various cafes and restaurants.

What would you like to eat today?"""

ask_for_restaurant = """You are conversation analyzer.

Please review the conversation between the food ordering chatbot and the user.

Carefully analyze the user's replies and the order summary made by the chatbot.

Has the user already told the chatbot what restaurant they have chosen to have order from?

Keep in mind that the user can change their order.

Keep in mind: if the user has chosen a specific dish, it means they have chosen the restaurant where this dish comes from.

Here is the conversation of the chatbot and the user:

<conversation>
{}
</conversation>

Output format:
```json
{{
  "restaurant_name": "Restaurant name that the user has chosen during the conversation or empty if not chosen"
}}
```

Guidelines:
- Carefully analyze the user's replies and the order summary made by the chatbot.
- Has the user already told the chatbot what restaurant they have chosen to have order from?
- The user can change their order. If the user canceled their order, it means they do not want the dishes from that order.  Newer information has higher priority.
- If the user has chosen a specific dish, it means they have also chosen the restaurant where this dish comes from.
- All dishes must be from the same restaurant that the user has chosen.
- Your task is to output valid json strictly in output format. Don't output anything else.
"""

ask_for_dishes = """Please review the conversation between the food ordering chatbot and the user.

Carefully analyze the user's replies and the order summary made by the chatbot.

Has the user already told the chatbot what dishes they have chosen to order? 

If the user has already told the chatbot what dishes they have chosen to order, then output the dishes the user ordered and the number of portions for each dish.

Here is the conversation of the chatbot and the user:

<conversation>
{}
</conversation>

You must answer only based on the information from this conversation. 

Guidelines:
- All the dishes must come from the same restaurant.
- Keep in mind that the user can change their order. Newer information has higher priority.
- Carefully analyze the user's replies and the order summary made by the chatbot.
- Based on the conversation of the chatbot and the user, has the user already provided chatbot with the information about what dishes they want to order? 
- if the user has not ordered anything specific yet, the fields of your json output must be empty lists. 
- The user can change their order. Newer information has higher priority. All dish names must be exactly present in the menu of one restaurant. All the dishes must come from the same restaurant.
- Output valid json strictly in output format.


Output format:
```json
{{
  "dish_names": "List of distinct names of the dishes that the user has ordered or empty list if the user has not ordered anything yet",
  "dish_quantities": "List of the number of portions for each dish that the user has ordered or empty list if the user has not ordered anything yet"
}}
```

"""

ask_for_delivery_time = """You are conversation analyzer.

Please review the conversation between the food ordering chatbot and the user.

Carefully analyze the user's replies and the order summary made by the chatbot.

Has the user already provided chatbot with the information about what delivery time they have chosen?

Keep in mind that the user can change their order. Newer information has higher priority.

Here is the conversation of the chatbot and the user:

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

ask_for_end = """
You are conversation analyzer.

Please review the conversation between the food ordering chatbot and the user.

Carefully analyze the user's replies and the order summary made by the chatbot.

Has the user already fully provided chatbot with all the necessary information about their order and confirmed the order?

Here is the conversation of the chatbot and the user:

<conversation>
{}
</conversation>

Examples
<examples>
Example 1

...beginning of the conversation...
Chatbot: You have chosen to order 1 portion of Chicken Parmigiana from Roman Holiday by right away. Is that correct?
User: Yes! Totally correct

Expected output:
```json
{{
  "order_made": 1,
  "order explanation": "User's replica indicates the confirmation of the order"
}}

Example 2

...beginning of the conversation...
Chatbot: You have chosen to order 6 portions of Lobio, 6 portions of Chakapuli, 3 portions of Mtsvadi, 12 portions of Pkhali from Gagimarjos by 19:00. Is that correct? If so, please exactly type 'I confirm the order' (without quotation marks) and our conversation will be over. If, otherwise, you would like to change or add something, please let me know.
User: Remove lobio please

Expected output:
```json
{{
  "order_made": 0,
  "order explanation": "user decided to change their order"
}}

```

Example 3

...beginning of the conversation...
Chatbot: You have chosen to order Sushi (Assorted) from Nippon by 12:00. Is that correct? If so, please type 'I confirm' and our conversation will be over.
User: confirm

Expected output:
```json
{{
  "order_made": 1,
  "order explanation": "User's replica indicates the confirmation of the order"
}}

```

</examples>

Output format:
```json
{{
  "order_made": "1 if all the order information was received by the chatbot from the user, and the order is created and confirmed by the user, 0 otherwise",
  "order_explanation": "Maximum 50 words explanation of the chosen order_made value"
}}
```

Please review the conversation between the food ordering chatbot and the user.

Carefully analyze the user's replies and the order summary made by the chatbot. It is prohibited to suggest what the chatbot needs to do next.

Has the user already fully provided chatbot with all the necessary information about their order and confirmed the order?

Your task is to output only valid json strictly in output format.
"""
