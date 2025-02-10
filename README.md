# Food Order Chatbot

## Introduction

This is a pet project for learning prompt engineering and getting familiar with LLMs.

LLMs are used in 4 different ways

1. As the chatbot itself to generate next reply
2. As a conversation analyzer to determine what exactly the user has ordered, from what restaurant and what is the desired delivery time
3. As a chatbot evaluator
4. As a provocative customer for finding complex scenarios that are difficult for the chatbot to handle

For the reliability and stability, `temperature=0.0` is used in the cases 1-3. In the case 4, `temperature=1.0` is used for creativity and variability.

## Repository structure

- `src/` - prompts and python scripts for the chatbot and the evaluator
- `notebooks/` - notebooks to launch the evaluator (evaluator.ipynb) or the chatbot (chatbot.ipynb)
- `data/` - made-up descriptions of 5 restaurants and their menus in jsonl formats
- `evaluator_scenarios/` - scenarios of expected performance of the chatbot for the evaluator to use as ground truth

## Quality

Two LLM-based metrics are used for the evaulation of the quality of the chatbot answers. 19 scenarios are used. For each scenario, the chatbot's replies are compared to the ground truth expected replies, and the values of the metrics are computed.

- *Factual correctness* means correspondence of the chatbot response and the information available for the chatbot to use (restaurants descriptions and their menus)
- *Appropriateness* means how pertinent is what the chatbot replied to what the user said previously

Current values of the quality metrics:

- factual_correctness: 0.89±0.07
- appropriateness: 0.86±0.08

## Usage

### Local usage

Create a dedicated environment and install all the necessary libraries using the command

```bash
pip install -r requirements.txt
```

Create and fill `.streamlit/secrets.toml` file using the template `.streamlit/secrets.toml.template`.

If launching the application locally, you can customize what models to use for chatbot reply generation, for conversation analyzer, chatbot evaluator, and provocative customer. In order to do that, enter the name of the models in the `[launch_parameters]` section.

Make sure to add the api bases and api keys of the chosen models in the `[api_bases]` and `[api_keys]` sections of the file, respectively.

For example, you can use models that you run locally on your laptop or models provided by your organization.

```bash
streamlit run src/streamlit_app.py
```
