# AI-Agent-Hub

A safe, extensible personal AI agent that runs locally on your laptop.

## Current build

The current branch contains the V2 foundation:

- AI reasoning through the OpenAI Responses API
- Multi-step function-calling loop
- Live web research through the Responses API web search tool
- Local SQLite memory for non-sensitive preferences and project facts
- Workspace file listing and reading
- File writing with explicit terminal approval
- Basic arithmetic
- Workspace path guardrails
- Environment-based configuration

## Run locally

1. Install Python 3.10+.
2. Open a terminal in this repository.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and add your OpenAI API key.
5. Start the agent:

```bash
python agent.py
```

The agent will show `You >`. Type a task and press Enter.

Examples:

```text
Find the latest AI agent news and summarize it.

Remember that my main project is AI-Agent-Hub.

List the files in the workspace.

Calculate 1250 * 18 / 100.
```

File writes require an explicit `y/yes` approval in the terminal.

## Safety

V2 does not execute arbitrary shell commands, install software, send external messages, submit applications,
make purchases, log into accounts, or perform external account actions. Web search is research-only.

Never put API keys, passwords, cookies, or other secrets into the repository.

## Roadmap

- GitHub integration with approval-gated repository actions
- Task planner with persistent progress
- Browser/computer automation with explicit approval
- Freelancing project research and proposal workflow
- Better memory management and user controls
- Tests and packaging for one-command startup
