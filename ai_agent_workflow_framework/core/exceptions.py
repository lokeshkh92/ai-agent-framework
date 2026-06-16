class WorkflowValidationError(Exception):
    """Raised when a workflow definition is invalid."""


class WorkflowExecutionError(Exception):
    """Raised when a workflow or node execution fails."""


class NodeExecutionError(Exception):
    """Raised when a node fails."""
