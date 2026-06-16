class NodeRegistry:
    def __init__(self):
        self._registry = {}

    def register(self, node_type: str, node_instance):
        self._registry[node_type] = node_instance

    def get(self, node_type: str):
        if node_type not in self._registry:
            raise KeyError(f"Node type '{node_type}' is not registered")
        return self._registry[node_type]

    def list_node_types(self):
        return list(self._registry.keys())
