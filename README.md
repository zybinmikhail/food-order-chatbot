# Food Order Chatbot

Pet Project

LLM is used in 3 different ways
1. As the chatbot itself to generate next reply
2. As a conversation analyzer to determine what exactly the user has ordered, from what restaurant and what is the desired delivery time
3. As a chatbot evaluator

In all three cases, `Meta-Llama-3.1-8B-Instruct` with `temperature=0.0` is used.

Repository structure
- `data/` - made-up descriptions of the restaurants and their menus in jsonl formats
- `evaluator_scenarios/` - scenarios of expected performance of the chatbot for the evaluator to use as ground truth
- `notebooks/` - notebooks to launch the evaulator (evaluator.ipynb) or the chatbot (chatbot.ipynb)
- `src/` - prompt and python scripts for the chatbot and the evaulator
