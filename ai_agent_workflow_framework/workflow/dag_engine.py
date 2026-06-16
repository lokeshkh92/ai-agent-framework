from typing import List
from workflow.models import WorkflowDefinition


class DAGEngine:
    def build_execution_order(self, workflow: WorkflowDefinition) -> List[str]:
        in_degree = {node.id: 0 for node in workflow.nodes}
        graph = {node.id: [] for node in workflow.nodes}

        for edge in workflow.edges:
            graph[edge.source].append(edge.target)
            in_degree[edge.target] += 1

        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        order = []

        while queue:
            node_id = queue.pop(0)
            order.append(node_id)
            for nxt in graph[node_id]:
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)

        if len(order) != len(workflow.nodes):
            raise ValueError("Workflow contains cycles or unresolved dependencies")

        return order
