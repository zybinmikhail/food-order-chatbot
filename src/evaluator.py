import openai
from loguru import logger

import chatbot


def read_scenario(scenario_id: int) -> list[dict[str, str]]:
    with open(f"../evaluator_scenarios/scenario{scenario_id}.txt", "r") as fin:
        scenario = fin.readlines()

    # This is to remove the commentaries
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
    predicted_message,
    ground_truth,
    chatbot_data,
    model: str,
    client: openai.OpenAI,
    temperature: float = 0.0,
) -> str:
    evaluator_prompt = template.format(
        chatbot_data, str(messages), predicted_message, ground_truth
    )
    evaluator = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": evaluator_prompt}],
        temperature=temperature,
    )
    return evaluator.choices[0].message.content


def evaluate_scenario(
    scenario_id: int,
    evaluator_model_dict,
    chatbot_model_dict,
    analyzer_model_dict,
) -> tuple[float, float]:
    with open("prompts/evaluator_prompt.txt") as fin:
        evaluator_prompt = fin.read()
    descriptions, menus_string = chatbot.initialize_menus_string()

    chatbot_data = descriptions + "\n" + menus_string
    logger.info(f"Evaluating scenario {scenario_id}")
    system_prompt = chatbot.initialize_system_prompt()
    messages = [{"role": "system", "content": system_prompt}] + read_scenario(
        scenario_id
    )
    # logger.disable("chatbot")
    factual_correctness_list = []
    appropriateness_list = []
    confirmation_requested = False
    evaluator_client = openai.OpenAI(
        api_key="***REMOVED***", base_url=evaluator_model_dict["api_base"]
    )
    chatbot_client = openai.OpenAI(
        api_key="***REMOVED***", base_url=chatbot_model_dict["api_base"]
    )
    analyzer_client = openai.OpenAI(
        api_key="***REMOVED***", base_url=analyzer_model_dict["api_base"]
    )
    for i in range(4, len(messages), 2):
        predicted_message, confirmation_requested, _ = chatbot.get_next_ai_message(
            messages[:i],
            confirmation_requested,
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
                ground_truth,
                chatbot_data,
                evaluator_model_dict["model"],
                evaluator_client,
            )
            evaluation = chatbot.parse_llm_json(evaluation)
            success = ("factual_correctness" in evaluation) and (
                "appropriateness" in evaluation
            )

        factual_correctness_list.append(evaluation["factual_correctness"])
        appropriateness_list.append(evaluation["appropriateness"])
        logger.info(str(evaluation))
    factual_correctness = sum(factual_correctness_list) / len(factual_correctness_list)
    appropriateness = sum(appropriateness_list) / len(appropriateness_list)
    return factual_correctness, appropriateness
