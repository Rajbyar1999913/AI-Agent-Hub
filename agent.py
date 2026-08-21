import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("AGENT_MODEL", "gpt-5.6-luna")
MAX_STEPS = int(os.getenv("AGENT_MAX_STEPS", "8"))
WORKSPACE = Path(os.getenv("AGENT_WORKSPACE", ".")).resolve()

SYSTEM_PROMPT = """
You are AI-Agent-Hub, a practical personal AI agent.
Your job is to understand the user's goal, make a short plan, use available tools when useful,
and report the result clearly. Do not claim that an action happened unless a tool actually completed it.

Safety rules:
- Never ask for or expose API keys, passwords, cookies, or private tokens.
- Reading files is allowed only inside the configured workspace.
- Writing or modifying a file always requires explicit user approval in the terminal.
- Do not execute shell commands, install software, send messages, submit applications, make purchases,
or perform external account actions in V1.
- When an action is outside the available tools, explain what is missing instead of pretending.
""".strip()


def safe_path(raw_path: str) -> Path:
    candidate = (WORKSPACE / raw_path).resolve()
    if candidate != WORKSPACE and WORKSPACE not in candidate.parents:
        raise ValueError("Path is outside the agent workspace.")
    return candidate


def calculator(expression: str) -> str:
    """Evaluate simple arithmetic without exposing Python builtins."""
    allowed = set("0123456789+-*/(). %")
    if not expression or any(ch not in allowed for ch in expression):
        raise ValueError("Only basic arithmetic characters are allowed.")
    # eval is restricted to an empty builtins dictionary and a character allow-list.
    result = eval(expression, {"__builtins__": {}}, {})
    return str(result)


def list_files(path: str = ".") -> str:
    folder = safe_path(path)
    if not folder.is_dir():
        raise ValueError("Not a directory.")
    items = []
    for item in sorted(folder.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        items.append((item.relative_to(WORKSPACE).as_posix() + ("/" if item.is_dir() else "")))
    return "\n".join(items[:200]) or "(empty directory)"


def read_file(path: str, max_chars: int = 20000) -> str:
    file_path = safe_path(path)
    if not file_path.is_file():
        raise ValueError("File not found.")
    if file_path.stat().st_size > 2_000_000:
        raise ValueError("File is too large for V1.")
    text = file_path.read_text(encoding="utf-8", errors="replace")
    return text[:max_chars]


def write_file(path: str, content: str) -> str:
    file_path = safe_path(path)
    relative = file_path.relative_to(WORKSPACE).as_posix()
    print(f"\n[APPROVAL REQUIRED] Agent wants to write: {relative}")
    answer = input("Allow this write? [y/N]: ").strip().lower()
    if answer not in {"y", "yes"}:
        return "Write cancelled by user."
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"Wrote {relative} successfully."


TOOLS = [
    {
        "type": "function",
        "name": "calculator",
        "description": "Calculate a basic arithmetic expression.",
        "parameters": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "list_files",
        "description": "List files and directories inside the agent workspace.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "read_file",
        "description": "Read a text file inside the agent workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "max_chars": {"type": "integer", "minimum": 1, "maximum": 20000},
            },
            "required": ["path", "max_chars"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "write_file",
        "description": "Create or replace a text file after explicit terminal approval.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


FUNCTIONS = {
    "calculator": calculator,
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
}


def run_agent(client: OpenAI, user_text: str) -> str:
    response = client.responses.create(
        model=MODEL,
        instructions=SYSTEM_PROMPT,
        input=user_text,
        tools=TOOLS,
    )

    for _ in range(MAX_STEPS):
        calls = [item for item in response.output if getattr(item, "type", None) == "function_call"]
        if not calls:
            return response.output_text or "No text response returned."

        tool_outputs: list[dict[str, Any]] = []
        for call in calls:
            try:
                args = json.loads(call.arguments)
                result = FUNCTIONS[call.name](**args)
            except Exception as exc:
                result = f"Tool error: {type(exc).__name__}: {exc}"
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": str(result),
                }
            )

        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM_PROMPT,
            previous_response_id=response.id,
            input=tool_outputs,
            tools=TOOLS,
        )

    return "Stopped: maximum agent steps reached."


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is missing. Copy .env.example to .env and add your API key.")

    client = OpenAI()
    print("\nAI-Agent-Hub V1 is ready.")
    print(f"Model: {MODEL}")
    print(f"Workspace: {WORKSPACE}")
    print("Type 'exit' to stop.\n")

    while True:
        try:
            user_text = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if not user_text:
            continue
        if user_text.lower() in {"exit", "quit"}:
            break
        try:
            print(f"\nAgent > {run_agent(client, user_text)}\n")
        except Exception as exc:
            print(f"\nAgent error: {type(exc).__name__}: {exc}\n")


if __name__ == "__main__":
    main()
