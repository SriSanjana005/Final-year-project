from enum import IntEnum
from typing import Dict

class ActionType(IntEnum):
    REVIEW_PREVIOUS_TOPIC = 0
    EASIER_CONTENT = 1
    SAME_DIFFICULTY = 2
    HARDER_CONTENT = 3
    PRACTICE_CONTENT = 4

ACTION_DESCRIPTIONS: Dict[ActionType, str] = {
    ActionType.REVIEW_PREVIOUS_TOPIC: "Recommend review/practice content for previous completed topic.",
    ActionType.EASIER_CONTENT: "Recommend lower difficulty content in current learning topic.",
    ActionType.SAME_DIFFICULTY: "Recommend same difficulty content in current learning topic.",
    ActionType.HARDER_CONTENT: "Recommend higher difficulty content in current learning topic.",
    ActionType.PRACTICE_CONTENT: "Recommend interactive practice/activity content."
}

def get_action_description(action: int) -> str:
    try:
        act = ActionType(action)
        return ACTION_DESCRIPTIONS.get(act, "Custom educational action.")
    except ValueError:
        return "Unknown learning action."
