from pathlib import Path

CURRENT_DIR = Path(__file__).parent
TEMPLATE_NAMES = [
    "evaluator_prompt_with_reference",
    "evaluator_prompt",
    "provocation_prompt",
    "system_prompt",
    "system_prompt_with_tools",
]

# Read all templates at once using a dictionary comprehension
PROMPTS = {
    name.upper(): (CURRENT_DIR / f"{name}.template").read_text()
    for name in TEMPLATE_NAMES
}

# Unpack the prompts into individual variables
EVALUATOR_PROMPT_WITH_REFERENCE = PROMPTS["EVALUATOR_PROMPT_WITH_REFERENCE"]
EVALUATOR_PROMPT = PROMPTS["EVALUATOR_PROMPT"]
PROVOCATION_PROMPT = PROMPTS["PROVOCATION_PROMPT"]
SYSTEM_PROMPT = PROMPTS["SYSTEM_PROMPT"]
SYSTEM_PROMPT_WITH_TOOLS = PROMPTS["SYSTEM_PROMPT_WITH_TOOLS"]

__all__ = list(PROMPTS.values())
