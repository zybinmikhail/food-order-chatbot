import openai
from loguru import logger
from typing import Optional

import chatbot

from os.path import dirname, abspath, join


from prompts import (
    EVALUATOR_PROMPT_WITH_REFERENCE,
    EVALUATOR_PROMPT,
    PROVOCATION_PROMPT,
)

CURRENT_DIR = dirname(abspath(__file__))
SCENARIOS_PATH = join(dirname(CURRENT_DIR), "evaluator_scenarios")


def read_scenario(scenario_id: int) -> list[dict[str, str]]:
    one_scenario_path = join(SCENARIOS_PATH, f"scenario{scenario_id}.txt")
    with open(one_scenario_path, "r") as fin:
        scenario = fin.readlines()

    # This is to remove the commentaries at the beginning of the file
    while not scenario[0].startswith("Chatbot"):
        scenario = scenario[1:]

    messages = []
    current_replica = "Please help me to order food"
    for line in scenario:
        line = line.lstrip()
        if line.startswith("User"):
            messages.append({"role": "assistant", "content": current_replica.strip()})
            current_replica = line[5:]
        elif line.startswith("Chatbot"):
            messages.append({"role": "user", "content": current_replica.strip()})
            current_replica = line[9:]
        else:
            current_replica += line

    return messages


def evaluate_ai_reply(
    template: str,
    messages: list[dict[str, str]],
    predicted_message: str,
    ground_truth: str,
    chatbot_data: str,
    model: str,
    client: openai.OpenAI,
) -> str:
    evaluator_prompt = template.format(
        chatbot_data, str(messages), predicted_message, ground_truth
    )
    evaluator = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": evaluator_prompt}],
        temperature=0.0,
    )
    ai_reply = str(evaluator.choices[0].message.content)
    return ai_reply


def generate_provocative_reply(
    template: str,
    provocator_role: str,
    messages: list[dict[str, str]],
    chatbot_data: str,
    model: str,
    client: openai.OpenAI,
) -> str:
    provocative_prompt = template.format(
        chatbot_data,
        provocator_role,
        str(messages),
    )
    provocator = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": provocative_prompt}],
        temperature=1.0,
    )
    ai_reply = str(provocator.choices[0].message.content)
    return ai_reply


def evaluate_scenario(
    scenario_id: int,
    models_dict: list[dict],
    provocator_role: Optional[str] = None,
) -> tuple[float, float]:
    """Compute metrics that represent the quality of model's answers for a given scenario.

    Args:
        scenario_id (int): A number from 1 to the maximal scenario number in evaluator_scenarios/ folder
        models_dict (list[dict]): A list of dictionaries that describe the models
        provocator_role (Optional[str], optional): Textual description of how exactly should the provocator generate its replies. Defaults to None.

    Returns:
        tuple[float, float]: mean factual correctness and appropriateness of the chatbot replies
    """

    descriptions, menus_string = chatbot.initialize_menus_string()

    chatbot_data = descriptions + "\n" + menus_string
    logger.info(f"Evaluating scenario {scenario_id}")
    system_prompt = chatbot.initialize_system_prompt()
    messages = [{"role": "system", "content": system_prompt}] + read_scenario(
        scenario_id
    )
    factual_correctness_list = []
    appropriateness_list = []
    chatbot_model_dict, analyzer_model_dict, evaluator_model_dict = models_dict[:3]
    evaluator_client = openai.OpenAI(
        api_key=evaluator_model_dict["api_key"],
        base_url=evaluator_model_dict["api_base"],
    )
    chatbot_client = openai.OpenAI(
        api_key=chatbot_model_dict["api_key"], base_url=chatbot_model_dict["api_base"]
    )
    analyzer_client = openai.OpenAI(
        api_key=analyzer_model_dict["api_key"], base_url=analyzer_model_dict["api_base"]
    )
    if len(models_dict) == 4:
        provocator_model_dict = models_dict[4]
        use_provocation = True
        provocator_client = openai.OpenAI(
            api_key=provocator_model_dict["api_key"],
            base_url=provocator_model_dict["api_base"],
        )
        provocator_prompt = PROVOCATION_PROMPT
        evaluator_prompt = EVALUATOR_PROMPT
    else:
        use_provocation = False
        evaluator_prompt = EVALUATOR_PROMPT_WITH_REFERENCE

    for i in range(4, len(messages), 2):
        # In case of provocation we change the last message (which is the user's message)
        last_message = messages[i - 1]["content"]
        if use_provocation:
            provocator_message = generate_provocative_reply(
                provocator_prompt,
                provocator_role,
                messages,
                chatbot_data,
                provocator_model_dict["model"],
                provocator_client,
            )
            last_message = chatbot.parse_llm_json(provocator_message)[
                "provocative_reply"
            ]

        predicted_message, _ = chatbot.get_next_ai_message(
            messages[: i - 1] + [{"role": "user", "content": last_message}],
            chatbot_model_dict["model"],
            chatbot_client,
            analyzer_model_dict["model"],
            analyzer_client,
        )
        ground_truth = messages[i]["content"]
        logger.info("-" * 20 + "predicted_message" + "-" * 20)
        logger.info(predicted_message)
        logger.info("-" * 20 + "ground_truth" + "-" * 20)
        logger.info(ground_truth)

        success = False
        while not success:
            evaluation = evaluate_ai_reply(
                evaluator_prompt,
                messages[1:i],
                predicted_message,
                ground_truth,  # This field is ignored withing the function if the provocative mode is used
                chatbot_data,
                evaluator_model_dict["model"],
                evaluator_client,
            )
            evaluation_parsed_dict = chatbot.parse_llm_json(evaluation)
            success = ("factual_correctness" in evaluation_parsed_dict) and (
                "appropriateness" in evaluation_parsed_dict
            )

        factual_correctness_list.append(
            float(evaluation_parsed_dict["factual_correctness"])
        )
        appropriateness_list.append(float(evaluation_parsed_dict["appropriateness"]))
        logger.info(str(evaluation_parsed_dict))
    factual_correctness = sum(factual_correctness_list) / len(factual_correctness_list)
    appropriateness = sum(appropriateness_list) / len(appropriateness_list)
    return factual_correctness, appropriateness
