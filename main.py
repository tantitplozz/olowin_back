"""
OmniCard-AI: Main entry point
"""

import os
import sys
import argparse
import asyncio  # Added for asyncio.run

# Ensure the project root is in sys.path if main.py is in a subdirectory or for consistency
# If main.py is at the root, this might be redundant but harmless.
project_root_dir = os.path.dirname(os.path.abspath(__file__))
if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)


def main():
    """Main entry point for OmniCard-AI"""
    parser = argparse.ArgumentParser(
        description="OmniCard-AI: Multi-Agent Financial Transaction Analysis System"
    )
    parser.add_argument(
        "--mode",
        choices=["api", "cli", "metagpt"],
        default="api",
        help="Run mode: api (web server), cli (command line), or metagpt (run MetaGPT)",
    )
    parser.add_argument("--task", type=str, help="Task to run in cli or metagpt mode")
    parser.add_argument("--port", type=int, default=8000, help="Port for API server")
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Host for API server"
    )

    args = parser.parse_args()

    if args.mode == "api":
        # Run API server
        try:
            from api.server import (
                app,
            )  # Adjusted import based on api/server.py location
            import uvicorn

            print(f"Starting API server on {args.host}:{args.port}")
            uvicorn.run(app, host=args.host, port=args.port)  # uvicorn.run is not async
        except ImportError as e:
            print(
                f"[ERROR] Could not import API server: {e}. Ensure api/server.py exists.",
                file=sys.stderr,
            )
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Failed to start API server: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.mode == "cli":
        # Run CLI mode
        if not args.task:
            print("Error: --task argument is required in cli mode")
            sys.exit(1)

        print(f"Running task in CLI mode: {args.task}")
        try:
            from metagpt.roles.di.data_interpreter import DataInterpreter

            async def run_cli_task():  # Renamed to avoid conflict if metagpt mode also defines run_task
                di = DataInterpreter()
                result = await di.run(args.task)  # Ensure di.run is async
                print(f"Result: {result}")

            asyncio.run(run_cli_task())
        except ImportError as e:
            print(
                f"[ERROR] Could not import MetaGPT components for CLI mode: {e}",
                file=sys.stderr,
            )
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Failed to run task in CLI mode: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.mode == "metagpt":
        # Run MetaGPT mode
        if not args.task:
            print("Error: --task argument is required in metagpt mode")
            sys.exit(1)

        print(f"Running task in MetaGPT mode: {args.task}")
        try:
            # Assuming run_metagpt_with_promptilus.py is in the 'scripts' directory
            # and contains a function run_with_task
            from scripts.run_metagpt_with_promptilus import run_with_task

            asyncio.run(run_with_task(args.task))
        except ImportError as e:
            print(
                f"[ERROR] Could not import from scripts.run_metagpt_with_promptilus: {e}",
                file=sys.stderr,
            )
            print(f"[DEBUG] sys.path: {sys.path}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Failed to run task in MetaGPT mode: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
