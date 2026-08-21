# AI-Agent-Hub

A safe, extensible personal AI agent foundation.

## V1

The first version provides:

- AI reasoning through the OpenAI Responses API
- A tool loop for multi-step tasks
- Workspace file listing and reading
- File writing with explicit terminal approval
- Basic arithmetic
- Environment-based configuration
- Guardrails against paths outside the workspace

## Run locally

1. Install Python 3.10+.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.
4. Start the agent:

```bash
python agent.py
```

The agent will ask for approval before writing files.

## Roadmap

- Web research tool
- GitHub tool integration
- Persistent memory
- Task planning and progress tracking
- More approval-gated actions
- Freelancing workflow support
