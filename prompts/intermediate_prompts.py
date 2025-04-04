greeting = """Hello, Dear Customer!

I am food order chatbot! My function is to help you choose and order food from various cafes and restaurants.

What would you like to eat today?"""

ask_for_restaurant_dishes_delivery_time = """You are a conversation analyzer.

Please review the conversation between the food-ordering chatbot and the user.

Carefully analyze the user's replies and the chatbot's order summary.

Here is the conversation between the chatbot and the user:

<conversation>
{}
</conversation>

Ask yourself the following questions:
- Has the user already told the chatbot what restaurant they have chosen to order from?
- Has the user already told the chatbot what dishes they have chosen to order? 
- Has the user already provided the chatbot with the information about what delivery time they have chosen?

<instruction>
1. Identify the suggestions made by the chatbot that the user agreed with
2. Identify the order summaries made by the chatbot
3. Identify places when the user says the following words
 - "No"
 - "Not really"
 - "I changed my mind"
 - "I also want..."
 - "add..."
 - "remove..."
4. Review the <restaurants-data> and <menus> section of the system_prompt. The user can order only from the restaurants listed in the <restaurants-data> section and only dishes from the <menus> section. 
5. Create a "dish_names" variable. It must store a List of *distinct* names of the dishes that the user has ordered from the restaurant_name or an empty list if the user has not ordered anything yet.
6. Based on what you identified in steps 1-3 of this instruction, add to the "dish_names" variable everything that the user ordered.
7. Create "dish_quantities": A list of the number of portions for each dish that the user has ordered or an empty list if the user has not ordered anything yet.
8. Based on what you identified in steps 1-3 of this instruction, add to the "dish_quantities" variable the number of portions of everything that the user wants to order. The default number of portions is 1. The "dish_quantities" list must be of the same length as the "dish_names" list.
9. Create "restaurant_name": Restaurant name that the user has chosen during the conversation or empty if not chosen. This must be one of the restaurants from the <restaurants-data> section of the chatbot system prompt.
10. Create "delivery_time": Delivery time that the user has chosen during the conversation or empty if not chosen"
11. Output the values of dish_names, dish_quantities, restaurant_name, delivery_time in JSON format.
</instruction>

<guidelines>
You must strictly and carefully follow these guidelines. After you create your response, double-check it. Make sure all of the guidelines are followed.

- Carefully analyze the user's replies and the order summary made by the chatbot.
- Has the user already told the chatbot what restaurant they have chosen to order from?
- The user can change their order. If the user cancels their order, it means they do not want the dishes from that order.  Newer information has higher priority.
- If the user has chosen a specific dish, it means they have also chosen the restaurant where this dish comes from. Dish information has a higher priority.
- All dishes must be from the same restaurant that the user has chosen.
- If the user has already told the chatbot what dishes they have chosen to order, then output the dishes the user ordered and the number of portions for each dish.
- Your task is to output valid JSON strictly in output format. Don't output anything else.
- All the *distinct* dishes from the "dish_names" output field must come from the same restaurant "restaurant_name".
- Keep in mind that the user can change their order. Newer information has higher priority. Pay special attention to the last user's reply.
- Keep in mind: if the user has chosen a specific dish, it means they have chosen the restaurant where this dish comes from.
- Based on the conversation between the chatbot and the user, has the user already provided the chatbot with the information about what dishes they want to order? 
- If the user has not ordered anything specific yet, the fields of your JSON output must be empty lists. 
- Pay special attention when the user says the following words and double-check your output
 - "No", 
 - "Not really"
 - "I changed my mind"
 - "I also want..."
 - "add..."
 - "remove..."
- The user can change their order. Newer information has higher priority. Pay special attention to requests of the user to add or remove something. All dish names must be exactly present in the menu of one restaurant. All the dishes must come from the same restaurant.
- Output valid JSON strictly in output format.
</guidelines>

Output format:
```json
{{
 "dish_names": "List of *distinct* names of the dishes that the user has ordered from the restaurant_name or empty list if the user has not ordered anything yet",
 "dish_quantities": "List of the number of portions for each dish that the user has ordered or an empty list if the user has not ordered anything yet",
 "restaurant_name": "Restaurant name that the user has chosen during the conversation or empty if not chosen",
 "delivery_time": "Delivery time that the user has chosen during the conversation or empty if not chosen",
 "explanation": "Maximum 50 words explanation of your output"
}}
```

Your task as the conversation analyzer is to output valid JSON strictly in output format. Think step-by-step.
"""

ask_for_end = """You are language analyzing software.

You are given the phrase from the conversation between the food ordering chatbot and the user. 

Determine whether this phrase means the end of the conversation and the confirmation of the order or not.

Key indicators of positive meaning
- I confirm and its synonyms
- yes and its synonyms

Key indicators of negative meaning
- The uses says they want something else
- No and its synonyms
- The user says they want to change the order
- The user asks to remove something or add something

Instruction:
1. Identify whether there are any indicators of the positive meaning in the given phrase
2. Identify whether there are any indicators of the negative meaning in the given phrase
3. If there are more indicators of the positive meaning than of the negative meaning, then output 1. Otherwise, output 0

Examples
<examples>
Example 1

Input:
yes

Expected output:
```json
{{
  "meaning": 1  # yes and its synonyms
}}
```

Example 2

Input:
no

Expected output:
```json
{{
  "meaning": 0  # No and its synonyms
}}
```

Example 3

Input:
I confirm

Expected output:
```json
{{
  "meaning": 1  # I confirm and its synonyms
}}
```

Example 4

Input:
I want to change the order

Expected output:
```json
{{
  "meaning": 0  # The user says they want to change the order
}}
```

Example 5

Input:
this is correct

Expected output:
```json
{{
  "meaning": 1  # I confirm and its synonyms
}}
```

Example 6

Input:
I also want 3 Churchkhela

Expected output:
```json
{{
  "meaning": 0  # The uses says they want something else
}}
```

Example 7

Input:
remove Khinkali and add lobio

Expected output:
```json
{{
  "meaning": 0  # The user asks to remove something or add something
}}
```

Example 8

Input:
change the order. make it 5 Churchkhela and 2 lobio by 2 pm

Expected output:
```json
{{
  "meaning": 0  # The user says they want to change the order
}}
```

</examples>

<input>
{}
</input>

Output format:
```json
{{
  "meaning": "1 if this phrase means the end of the conversation and the confirmation of the order, 0 otherwise",
}}
```

Your task is to output only valid JSON strictly in output format.
Don't output any python code. Output only the JSON dictionary.
"""
