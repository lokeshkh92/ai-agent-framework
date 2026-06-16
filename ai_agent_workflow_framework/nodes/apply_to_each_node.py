from typing import Any, Dict, List

from nodes.base_node import BaseNode


class ApplyToEachNode(BaseNode):
    """
    Row-wise lookup iterator.

    Inputs/config:
      - items: list from preceding node
      - key: field name inside each row
      - map: dict/object where map[key_value] => mapped_value

    Behavior:
      For each row in items:
        lookup_key = row[key]
        mapped_value = map[lookup_key]
      Emit mapped_value list for loop propagation.

    Example:
      items = [{"country": "KE"}, {"country": "UG"}]
      key = "country"
      map = {"KE": "Kenya", "UG": "Uganda"}

      output.items = ["Kenya", "Uganda"]
    """

    node_type = "apply_to_each"

    def __init__(self, template_resolver):
        self.template_resolver = template_resolver

    def validate_config(self, config: Dict[str, Any]) -> None:
        if "items" not in config:
            raise ValueError("apply_to_each requires 'items'")
        if "key" not in config:
            raise ValueError("apply_to_each requires 'key'")
        if "map" not in config:
            raise ValueError("apply_to_each requires 'map'")

    def execute(
        self,
        inputs: Dict[str, Any],
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        resolved_config = self.template_resolver.resolve(config, context)

        items = resolved_config.get("items")
        key = resolved_config.get("key")
        key_value_map = resolved_config.get("map")

        item_alias = resolved_config.get("item_alias", "current_item")
        index_alias = resolved_config.get("index_alias", "current_index")
        key_alias = resolved_config.get("key_alias", "current_key")

        strict = resolved_config.get("strict", True)
        default_value = resolved_config.get("default_value")

        if items is None:
            raise ValueError("apply_to_each could not resolve 'items'")

        if not isinstance(items, list):
            raise ValueError("apply_to_each expects 'items' to be a list")

        if not isinstance(key_value_map, dict):
            raise ValueError("apply_to_each expects 'map' to be a dictionary/object")

        mapped_items: List[Any] = []
        keys_used: List[Any] = []

        for idx, row in enumerate(items):
            lookup_key = self._resolve_lookup_key(row=row, key=key)

            if lookup_key is None:
                if strict:
                    raise ValueError(
                        f"apply_to_each could not find key '{key}' in row at index {idx}: {row}"
                    )
                mapped_value = default_value
            else:
                # Exact lookup first, then stringified lookup fallback
                if lookup_key in key_value_map:
                    mapped_value = key_value_map[lookup_key]
                elif str(lookup_key) in key_value_map:
                    mapped_value = key_value_map[str(lookup_key)]
                else:
                    if strict:
                        raise ValueError(
                            f"apply_to_each could not find lookup value for key '{lookup_key}' in map"
                        )
                    mapped_value = default_value

            mapped_items.append(mapped_value)
            keys_used.append(lookup_key)

        return {
            "status": "SUCCESS",
            "output": {
                "__apply_to_each__": True,
                "items": mapped_items,
                "keys": keys_used,
                "item_alias": item_alias,
                "index_alias": index_alias,
                "key_alias": key_alias,
                "total_items": len(mapped_items)
            }
        }

    def _resolve_lookup_key(self, row: Any, key: Any) -> Any:
        """
        If row is a dict and key is a string, return row[key].
        If row is not a dict, treat row itself as the lookup key.
        """
        if isinstance(row, dict) and isinstance(key, str):
            return row.get(key)

        # For scalar lists, allow direct item lookup
        if not isinstance(row, dict):
            return row

        return None
