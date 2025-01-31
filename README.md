# Food Order Chatbot

Pet Project

LLM is used in 3 different ways

1. As the chatbot itself to generate next reply
2. As a conversation analyzer to determine what exactly the user has ordered, from what restaurant and what is the desired delivery time
3. As a chatbot evaluator

In all three cases, `Llama-3.1-Nemotron-70B-Instruct-HF` with `temperature=0.0` is used.

Repository structure

- `src/` - prompts and python scripts for the chatbot and the evaluator
- `notebooks/` - notebooks to launch the evaluator (evaluator.ipynb) or the chatbot (chatbot.ipynb)
- `data/` - made-up descriptions of the restaurants and their menus in jsonl formats
- `evaluator_scenarios/` - scenarios of expected performance of the chatbot for the evaluator to use as ground truth

Current values of the quality metrics:

- factual_correctness: 0.89±0.07
- appropriateness: 0.86±0.08

TODO:

- Evaluate the chatbot using the role of hacker that wants to jailbreak the chatbot

- Evaluate the chatbot using the role of a person that types with a lot of typos and grammar mistakes

- Evaluate the chatbot using the role of "a person who wants to make fun out of the chatbot

- Make conclusions and improvements based on these evaluations

- Create a streamlit application
