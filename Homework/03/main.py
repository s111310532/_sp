import argparse
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from src.core.agent import ReActAgent
from src.core.config import Config
from src.core.memory import Memory
from src.core.planner import Planner
from src.plugins import PluginManager
from src.scheduler.scheduler import Scheduler
from src.tools import ToolRegistry
from src.tools.code_exec import PythonExecTool
from src.tools.file_ops import FileListTool, FileReadTool, FileWriteTool
from src.tools.web_fetch import WebFetchTool
from src.tools.web_search import WebSearchTool

load_dotenv()


def bootstrap():
    config = Config.from_env()
    client = OpenAI(api_key=config.openai_api_key)
    memory = Memory(config.memory_path)
    registry = ToolRegistry()

    registry.register(WebSearchTool())
    registry.register(WebFetchTool())
    registry.register(FileReadTool())
    registry.register(FileWriteTool())
    registry.register(FileListTool())
    registry.register(PythonExecTool())

    scheduler = Scheduler()

    if config.plugins_enabled:
        plugin_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "src", "plugins"
        )
        pm = PluginManager(plugin_dir)
        pm.discover_and_load(registry, scheduler)

    agent = ReActAgent(client, registry, memory, config)
    planner = Planner(client, config)

    return config, client, memory, registry, scheduler, agent, planner


def main():
    config, client, memory, registry, scheduler, agent, planner = bootstrap()

    parser = argparse.ArgumentParser(
        description="AI Agent - 自動化與智能化深化系統"
    )
    parser.add_argument("prompt", nargs="*", help="Prompt to process")
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Interactive chat mode"
    )
    parser.add_argument(
        "--plan", type=str, help="Use task planner for a complex goal"
    )
    parser.add_argument(
        "--scheduler", action="store_true", help="Run the scheduler daemon"
    )
    parser.add_argument(
        "--list-convs", action="store_true", help="List all conversations"
    )
    parser.add_argument(
        "--conv", type=str, help="Continue a specific conversation by ID"
    )
    parser.add_argument(
        "--conv-clear", type=str, help="Clear a specific conversation by ID"
    )
    args = parser.parse_args()

    if args.scheduler:
        scheduler.start()
        print("[Scheduler] Running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            scheduler.stop()
        return

    if args.list_convs:
        convs = memory.list_conversations()
        if not convs:
            print("No conversations found.")
        else:
            for cid, preview in convs.items():
                print(f"[{cid}] {preview}...")
        return

    if args.conv_clear:
        memory.clear(args.conv_clear)
        print(f"Cleared conversation: {args.conv_clear}")
        return

    if args.plan:
        print(f"\n[Planner] Planning goal: {args.plan}\n")
        results = planner.execute_plan(args.plan, agent, args.conv)
        print("\n" + "=" * 60)
        print("PLAN EXECUTION RESULTS")
        print("=" * 60)
        for r in results:
            print(f"\n--- Task {r['task']['id']}: {r['task']['description']} ---")
            print(r["result"])
        return

    if args.interactive:
        conv_id = args.conv or f"conv_{int(time.time())}"
        print("Interactive mode. Commands: /exit, /new, /conv <id>")
        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ("/exit", "/quit"):
                break
            if user_input.lower() == "/new":
                conv_id = f"conv_{int(time.time())}"
                print(f"New conversation: {conv_id}")
                continue
            if user_input.lower().startswith("/conv "):
                conv_id = user_input.split(maxsplit=1)[1]
                print(f"Switched to conversation: {conv_id}")
                continue
            result = agent.run(user_input, conversation_id=conv_id)
            print(f"\nAgent: {result}")
        return

    prompt = " ".join(args.prompt) if args.prompt else input("You: ")
    if prompt:
        result = agent.run(prompt, conversation_id=args.conv)
        print(f"\n{result}")


if __name__ == "__main__":
    main()
