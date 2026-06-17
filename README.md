# AI Agent Workflow Framework

A Python-based workflow orchestration framework for building and running configurable **AI/data workflows** as a **Directed Acyclic Graph (DAG)** of reusable nodes.

This project is designed to execute workflows composed of pluggable nodes such as:

- PostgreSQL reads
- Trino reads
- HDFS listing
- LLM inference (via Ollama)
- Python/script execution
- conditional branching (`if/else`)
- iteration (`apply_to_each`)
- CSV writing
- email sending
- UI-oriented rendering

It also includes support for:

- workflow validation
- graph-based execution ordering
- runtime context propagation
- workflow/node execution audit
- repository and SQL-backed persistence
- API-driven workflow invocation

---

## 1. Project Goals

The framework aims to provide a modular foundation for:

- orchestrating AI/data workflows using a graph model
- separating workflow orchestration from integration code
- enabling reusable node implementations
- tracking workflow and node execution state
- supporting extensibility through registries, services, and repositories

---

## 2. High-Level Architecture

```text
                +----------------------+
                |      API Layer       |
                | app/api.py           |
                | app/workflow_api.py  |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |   Workflow Service   |
                | services/workflow_*  |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |   Workflow Runtime   |
                | workflow/runtime.py  |
                +----------+-----------+
                           |
              +------------+-------------+
              |                          |
              v                          v
    +-------------------+      +-------------------+
    |    DAG Engine     |      |   Node Registry   |
    | workflow/dag_*    |      | registry/*        |
    +--------+----------+      +---------+---------+
             |                           |
             v                           v
    +-------------------+      +-------------------+
    | Execution Order   |      | Resolve Node Type |
    +-------------------+      +---------+---------+
                                          |
                                          v
                               +----------------------+
                               |      Node Layer      |
                               | nodes/base_node.py   |
                               | nodes/*_node.py      |
                               +----------+-----------+
                                          |
                                          v
                               +----------------------+
                               |    Service Layer     |
                               | services/*.py        |
                               +----------+-----------+
                                          |
                                          v
                               +----------------------+
                               |  Repository Layer    |
                               | repositories/*.py    |
                               +----------+-----------+
                                          |
                                          v
                               +----------------------+
                               | Database / SQL Schema |
                               | sql/schema_phase*.sql |
                               +----------------------+
```

---

## 3. Core Concepts

### 3.1 Workflow Runtime

The runtime is the main orchestrator responsible for executing workflows, propagating runtime state, handling special control-flow cases (such as `apply_to_each`), and maintaining workflow/node execution audit trails.

Primary file:

- `workflow/runtime.py`

### 3.2 DAG Engine

The DAG engine computes the workflow execution order by analyzing node dependencies and performing a topological traversal of the graph.

Primary file:

- `workflow/dag_engine.py`

### 3.3 Base Node Contract

All executable nodes conform to a shared interface defined by `BaseNode`.

Expected responsibilities of a node:

- validate its configuration
- execute using upstream inputs, node config, and runtime context
- return structured output

Primary file:

- `nodes/base_node.py`

---

## 4. Project Structure

```text
ai_agent_workflow_framework/
├── app/                       # API layer, request schemas, dependency wiring
├── configs/                   # Application configuration (e.g. app.yaml)
├── core/                      # Shared exceptions and foundational constructs
├── example_workflows/         # Example workflow definitions (JSON)
├── nodes/                     # Built-in workflow node implementations
├── registry/                  # Node registration and node specs/metadata
├── repositories/              # Persistence layer for workflows/executions
├── services/                  # Integration/business service adapters
├── sql/                       # Database schema and sample seed SQL
├── utils/                     # Templating, serialization, safe condition eval
└── workflow/                  # Runtime, context, models, validator, DAG engine
```

### Notable files by area

#### `app/`
- `api.py`
- `workflow_api.py`
- `schemas.py`
- `dependencies.py`
- `clients.py`

#### `workflow/`
- `context.py`
- `dag_engine.py`
- `models.py`
- `runtime.py`
- `validator.py`

#### `nodes/`
- `base_node.py`
- `apply_to_each_node.py`
- `if_else_node.py`
- `postgres_read_node.py`
- `trino_read_node.py`
- `llm_infer_node.py`
- `python_script_node.py`
- `csv_writer_node.py`
- `send_email_node.py`
- `ui_render_node.py`
- `lambda_node.py`
- `hdfs_list_node.py`

#### `services/`
- `workflow_service.py`
- `postgres_service.py`
- `trino_service.py`
- `ollama_service.py`
- `script_runner_service.py`
- `email_service.py`
- `file_service.py`
- `hdfs_service.py`

#### `repositories/`
- `workflow_repository.py`
- `workflow_execution_repository.py`
- `node_execution_repository.py`
- `connection_repository.py`

#### `registry/`
- `node_registry.py`
- `node_specs.py`
- `node_specs_additional.py`

#### `sql/`
- `schema_phase1.sql`
- `schema_phase2.sql`
- `schema_phase3.sql`
- `sample_seed_phase2.sql`

---

## 5. Built-in Node Types

The framework includes several built-in node categories:

### Data access
- `postgres_read_node.py`
- `trino_read_node.py`
- `hdfs_list_node.py`

### AI / inference
- `llm_infer_node.py`

### Control flow
- `if_else_node.py`
- `apply_to_each_node.py`
- `lambda_node.py`

### Execution / automation
- `python_script_node.py`
- `send_email_node.py`
- `csv_writer_node.py`
- `ui_render_node.py`

These nodes suggest the framework supports mixed **data engineering + AI automation** workflows.

---

## 6. Execution Lifecycle

A typical workflow execution path looks like this:

1. A workflow run is triggered through the API layer or service layer.
2. The workflow definition is loaded and validated.
3. The runtime initializes execution context.
4. The DAG engine computes the execution order.
5. The node registry resolves each node type to an implementation.
6. Each node validates its config.
7. Each node executes with:
   - `inputs`
   - `config`
   - `context`
8. Services perform the external operations (DB, files, email, LLM, etc.).
9. Repositories persist workflow/node execution state.
10. Final outputs are returned to the caller.

---

## 7. Example Workflow Support

The project includes an example workflow definition:

- `example_workflows/airtel_money_pattern.json`

This file is a good starting point for understanding how workflows are represented declaratively.

A workflow definition will typically include:

- nodes
- edges/dependencies
- node configuration
- branching or loop semantics
- expected outputs

---

## 8. API and Dependency Wiring

The `app/` package appears to provide:

- HTTP/API entry points
- request/response schemas
- dependency creation / injection
- client construction
- phase-specific examples / variants

Files such as:

- `app/api.py`
- `app/workflow_api.py`
- `app/dependencies.py`
- `app/schemas.py`

indicate that workflows are expected to be created, managed, or triggered through an application/API layer.

---

## 9. Persistence Model

The presence of repository classes and SQL schemas indicates that the framework likely persists:

- workflow definitions
- workflow execution metadata
- node execution metadata
- connection configuration references

This enables:

- auditability
- traceability
- workflow status tracking
- debugging and run analysis

---

## 10. Utility Modules

The `utils/` package contains support functions for dynamic workflow behavior:

- `safe_condition_evaluator.py` — safe expression evaluation for branching logic
- `serialization.py` — converting outputs to storable/transferable forms
- `templating.py` — dynamic parameter/value interpolation

These utilities are commonly used by node execution and runtime orchestration.

---

## 11. Configuration

Application configuration appears under:

- `configs/app.yaml`

This file likely contains environment-specific settings such as:

- database configuration
- service endpoints
- runtime parameters
- feature toggles
- integration settings

---

## 12. Getting Started

> **Note:** This repository tree does not currently show the package/dependency manifest (`requirements.txt`, `pyproject.toml`, etc.). Update the commands below to match your actual setup.

### 12.1 Clone the repository

```bash
git clone <your-repo-url>
cd ai_agent_workflow_framework
```

### 12.2 Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 12.3 Install dependencies

If using a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

If using `pyproject.toml`, install according to your build tool (e.g. `pip`, `poetry`, `uv`).

### 12.4 Configure the application

Update:

- `configs/app.yaml`
- database connection settings
- service credentials/endpoints
- Ollama / Trino / PostgreSQL / HDFS / email integration settings

### 12.5 Initialize the database

Run the appropriate schema files from the `sql/` directory depending on your environment and target phase.

For example:

```bash
psql -h <host> -U <user> -d <db> -f sql/schema_phase3.sql
```

### 12.6 Start the API/application

The actual startup command depends on how `app/api.py` is implemented.

Examples might include:

```bash
python app/api.py
```

or, if an ASGI app is exposed:

```bash
uvicorn app.api:app --reload
```

Adjust this to match your implementation.

---

## 13. Adding a Custom Node

Custom nodes should implement the `BaseNode` contract.

### Minimal conceptual example

```python
from typing import Dict, Any
from nodes.base_node import BaseNode


class MyCustomNode(BaseNode):
    node_type = "my_custom_node"

    def validate_config(self, config: Dict[str, Any]) -> None:
        required = ["message"]
        for key in required:
            if key not in config:
                raise ValueError(f"Missing required config: {key}")

    def execute(
        self,
        inputs: Dict[str, Any],
        config: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "result": f"Processed: {config['message']}",
            "inputs": inputs,
        }
```

### To fully integrate the node

1. implement the node class
2. register it in `registry/node_registry.py`
3. define/update metadata in `registry/node_specs.py`
4. reference it in the workflow definition

---

## 14. Recommended Development Improvements

The current tree suggests a few cleanup opportunities:

### Repository hygiene
Add a `.gitignore` (if not already present at repo root) to exclude:

```gitignore
__pycache__/
*.py[cod]
.DS_Store
.idea/
.venv/
.env
```

### Clean up generated/editor artifacts
The tree currently includes:

- `__pycache__/`
- `.idea/`
- `.DS_Store`

These should not usually be committed.

### Remove backup files from source control
- `workflow/runtime.py.bkp`

Prefer Git history/branches over backup copies in the codebase.

### Add tests
Recommended test coverage areas:

- DAG ordering
- cycle detection
- node config validation
- runtime context propagation
- branching and loop behaviors
- repository persistence
- workflow audit logging

---

## 15. Suggested Next Files to Review

To understand the framework in depth, review these files in order:

1. `README.md`
2. `workflow/runtime.py`
3. `workflow/dag_engine.py`
4. `workflow/models.py`
5. `workflow/context.py`
6. `workflow/validator.py`
7. `nodes/base_node.py`
8. `registry/node_registry.py`
9. `services/workflow_service.py`
10. `example_workflows/airtel_money_pattern.json`

---

## 16. Summary

`ai_agent_workflow_framework` is a modular workflow orchestration framework that combines:

- graph-based workflow execution
- pluggable node architecture
- integration services
- execution persistence and audit
- utility support for safe dynamic behavior
- API-oriented workflow triggering and management

It is a strong foundation for building data/AI workflow automation systems where workflows can be defined declaratively and executed consistently through a shared runtime.

---

## 17. Contributing Notes

When extending the project:

- keep nodes thin and move integration logic into services
- use repositories for persistence concerns
- update node specs/registry when introducing new node types
- add tests for new control-flow or integration patterns
- prefer explicit runtime/context contracts over implicit shared state

---

