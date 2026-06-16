from typing import Any, Dict


class SafeConditionEvaluator:
    SUPPORTED_OPERATORS = {
        "eq", "ne", "gt", "gte", "lt", "lte",
        "in", "not_in", "exists", "is_empty", "not_empty"
    }

    def evaluate(self, condition: Dict[str, Any]) -> bool:
        operator = condition.get("operator")
        if operator not in self.SUPPORTED_OPERATORS:
            raise ValueError(f"Unsupported operator '{operator}'")

        left = condition.get("left")
        right = condition.get("right")

        if operator == "exists":
            return left is not None
        if operator == "is_empty":
            return left in (None, "", [], {}, ())
        if operator == "not_empty":
            return left not in (None, "", [], {}, ())

        if operator == "eq":
            return left == right
        if operator == "ne":
            return left != right
        if operator == "gt":
            return left > right
        if operator == "gte":
            return left >= right
        if operator == "lt":
            return left < right
        if operator == "lte":
            return left <= right
        if operator == "in":
            return left in right
        if operator == "not_in":
            return left not in right

        raise ValueError(f"Operator '{operator}' reached unexpected path")
