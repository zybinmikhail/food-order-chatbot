import json


def load_configs() -> tuple[dict[str, str]]:
    with open("../config_models.json", "r", encoding="utf-8") as fin:
        config_models = json.load(fin)

    with open("../config_launch.json", "r", encoding="utf-8") as fin:
        config_launch = json.load(fin)

    with open("../secrets_models.json", "r", encoding="utf-8") as fin:
        secrets_models = json.load(fin)
    return config_launch, config_models, secrets_models


def init_model_dicts() -> list[dict[str, str]]:
    config_launch, config_models, secrets_models = load_configs()
    chatbot_model_dict = {
        "model": config_launch["chatbot_model"],
        "api_base": config_models[config_launch["chatbot_model"]],
        "api_key": secrets_models[config_launch["chatbot_model"]],
    }
    analyzer_model_dict = {
        "model": config_launch["analyzer_model"],
        "api_base": config_models[config_launch["analyzer_model"]],
        "api_key": secrets_models[config_launch["analyzer_model"]],
    }
    model_dicts = [chatbot_model_dict, analyzer_model_dict]
    use_provocator = config_launch["use_provocator"]
    use_evaluator = config_launch["use_evaluator"]
    if use_evaluator:
        evaluator_model_dict = {
            "model": config_launch["evaluator_model"],
            "api_base": config_models[config_launch["evaluator_model"]],
            "api_key": secrets_models[config_launch["evaluator_model"]],
        }
        model_dicts.append(evaluator_model_dict)
    if use_provocator:
        provocator_model_dict = {
            "model": config_launch["provocator_model"],
            "api_base": config_models[config_launch["provocator_model"]],
            "api_key": secrets_models[config_launch["provocator_model"]],
        }
        model_dicts.append(provocator_model_dict)
    return model_dicts
