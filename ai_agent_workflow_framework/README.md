# Workflow-Based AI Framework (Phase 1)

This bundle contains a phase-1 implementation skeleton for a workflow-based AI framework.

## Included
- Workflow models, validator, DAG engine, runtime
- Generic node registry and node specs
- Core nodes: postgres_read, python_script, llm_infer, send_email, ui_render
- Service wrappers for Postgres, Ollama, email, and a script runner
- Repository skeletons for workflow definitions and execution audit
- FastAPI API skeleton
- Example SQL DDL

## Important
The `PythonScriptNode` uses a placeholder script runner. In production, replace it with a sandboxed runner.
