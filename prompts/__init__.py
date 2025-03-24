import os


current_dir = os.path.dirname(os.path.abspath(__file__))
evaluator_prompt_with_reference_path = os.path.join(current_dir, "evaluator_prompt_with_reference.template")
evaluator_prompt_path = os.path.join(current_dir, "evaluator_prompt.template")
provocation_prompt_path = os.path.join(current_dir, "provocation_prompt.template")
system_prompt_path = os.path.join(current_dir, "system_prompt.template")

with open(evaluator_prompt_with_reference_path) as fin:
    EVALUATOR_PROMPT_WITH_REFERENCE = fin.read()

with open(evaluator_prompt_path) as fin:
    EVALUATOR_PROMPT = fin.read()

with open(provocation_prompt_path) as fin:
    PROVOCATION_PROMPT = fin.read()

with open(system_prompt_path) as fin:
    SYSTEM_PROMPT = fin.read()

__all__ = [EVALUATOR_PROMPT_WITH_REFERENCE, EVALUATOR_PROMPT, PROVOCATION_PROMPT, SYSTEM_PROMPT]
