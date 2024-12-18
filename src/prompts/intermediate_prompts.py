greeting = """Hello, Dear Customer!

I am food order chatbot! My function is to help you choose and order food from various cafes and restaurants.

What would you like to eat today?"""

ask_for_restaurant_dishes_delivery_time = """You are conversation analyzer.

Please review the conversation between the food ordering chatbot and the user.

Carefully analyze the user's replies and the order summary made by the chatbot.

Ask yourself the following questions:
- Has the user already told the chatbot what restaurant they have chosen to have order from?
- Has the user already told the chatbot what dishes they have chosen to order? 
- Has the user already provided chatbot with the information about what delivery time they have chosen?

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
4. Create "dish_names" variable. it must store a List of DISTINCT names of the dishes that the user has ordered from the restaurant_name or empty list if the user has not ordered anything yet"
5. Based on what you identified on the steps 1-3 of this instruction, add to the "dish_names" variable everything that the user wants to order and remove everything that the user refused to order.
6. Create "dish_quantities": "List of the number of portions for each dish that the user has ordered or empty list if the user has not ordered anything yet",
7. Based on what you identified on the steps 1-3 of this instruction, add to the "dish_quantities" variable the number of portions of everything that the user wants to order and remove everything that the user refused to order.
9. Create "restaurant_name": "Restaurant name that the user has chosen during the conversation or empty if not chosen",
10. Create "delivery_time": "Delivery time that the user has chosen during the conversation or empty if not chosen"
</instruction>

Here is the conversation of the chatbot and the user:

<conversation>
{}
</conversation>

<guidelines>
You must strictly and carefully follow these guidelines. After you create your response, double-check it against these guidelines. Make sure all are followed.

- Carefully analyze the user's replies and the order summary made by the chatbot.
- Has the user already told the chatbot what restaurant they have chosen to have order from?
- The user can change their order. If the user canceled their order, it means they do not want the dishes from that order.  Newer information has higher priority.
- If the user has chosen a specific dish, it means they have also chosen the restaurant where this dish comes from. Dish information has higher priority.
- All dishes must be from the same restaurant that the user has chosen.
- If the user has already told the chatbot what dishes they have chosen to order, then output the dishes the user ordered and the number of portions for each dish.
- Your task is to output valid json strictly in output format. Don't output anything else.
- All the DISTINCT dishes from the "dish_names" output field must come from the same restaurant "restaurant_name".
- Keep in mind that the user can change their order. Newer information has higher priority. Pay special attention to the last user reply.
- Keep in mind: if the user has chosen a specific dish, it means they have chosen the restaurant where this dish comes from.
- Carefully analyze the user's replies and the order summary made by the chatbot.
- Based on the conversation of the chatbot and the user, has the user already provided chatbot with the information about what dishes they want to order? 
- If the user has not ordered anything specific yet, the fields of your json output must be empty lists. 
- Pay special attention when the user says the following words and double-check your output
  - "No", 
  - "Not really"
  - "I changed my mind"
  - "I also want..."
  - "add..."
  - "remove..."
- The user can change their order. Newer information has higher priority. Pay special attention to requests of the user to add or remove something. All dish names must be exactly present in the menu of one restaurant. All the dishes must come from the same restaurant.
- Output valid json strictly in output format.
</guidelines>

Output format:
```json
{{
  "dish_names": "List of DISTINCT names of the dishes that the user has ordered from the restaurant_name or empty list if the user has not ordered anything yet",
  "dish_quantities": "List of the number of portions for each dish that the user has ordered or empty list if the user has not ordered anything yet",
  "restaurant_name": "Restaurant name that the user has chosen during the conversation or empty if not chosen",
  "delivery_time": "Delivery time that the user has chosen during the conversation or empty if not chosen"
}}
```

Your task is to output valid json strictly in output format. Don't output anything else.
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

Your task is to output valid json strictly in output format. Don't output anything else.
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

ask_for_end = """You are language analyzing software.

You are given the phrase. Determine whether its meaning is positive or negative.

Examples
<examples>
Example 1

Input:
yes

Expected output:
```json
{{
  "meaning": 1
}}
```

Example 2

Input:
no

Expected output:
```json
{{
  "meaning": 0
}}
```

Example 3

Input:
I confirm

Expected output:
```json
{{
  "meaning": 1
}}
```

Example 4

Input:
I want to change the order

Expected output:
```json
{{
  "meaning": 0
}}
```

Example 5

Input:
this is correct

Expected output:
```json
{{
  "meaning": 1
}}
```

Example 6

Input:
I also want 3 Churchkhela

Expected output:
```json
{{
  "meaning": 0  # This sentence contains no confirmation
}}
```

Example 7

Input:
remove Khinkali and add lobio

Expected output:
```json
{{
  "meaning": 0  # the user asked to change their order, therefore the meaning is negative
}}
```

Example 8

Input:
change the order. make it 5 Churchkhela and 2 lobio by 2 pm

Expected output:
```json
{{
  "meaning": 0  # the user asked to change the order, so additional confirmation has to be made after updating the order
}}
```

</examples>

Output format:
```json
{{
  "meaning": "1 if the meaning of the phrase is positive, 0 otherwise",
}}
```

Your task is to output only valid json strictly in output format.
Don't output any python code. Output only the json dictionary.
"""
