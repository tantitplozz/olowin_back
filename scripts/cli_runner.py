# main.py - Entry point for the application

import sys
# import os # No longer needed as pathlib is used
from pathlib import Path

# Add the project root to PYTHONPATH to allow for absolute imports
# This must be done before importing project-specific modules.
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent) # Adjusted for script being in scripts/
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Now that sys.path is updated, import the new graph runner
try:
    from workflow.graph_controller import run_graph
except ImportError as e:
    print(f"Error importing run_graph: {e}")
    print("Please ensure that workflow.graph_controller and its dependencies are correctly set up.")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

# AgentState import removed as it's no longer used directly in main.py
# from workflow.state_schema import AgentState

if __name__ == "__main__":
    print("[*] OmniCard AI Interactive Mode [*]")
    print("Type 'exit' or 'quit' to end.")
    while True:
        user_input = input("\n🧠 Prompt > ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting OmniCard AI.")
            break
        if not user_input.strip():
            print("Please enter a prompt.")
            continue

        print("🤖 Thinking...")
        try:
            reply = run_graph(user_input)
            print("\n🤖 Assistant:")
            print(reply)
        except ImportError as e: # More specific for import issues if run_graph itself tries dynamic imports
            print(f"\n[Error] An import error occurred during graph execution: {e}")
            import traceback
            traceback.print_exc()
        except RuntimeError as e: # For general runtime issues within the graph
            print(f"\n[Error] A runtime error occurred during graph execution: {e}")
            import traceback
            traceback.print_exc()
        except Exception as e: # Fallback for truly unexpected errors
            print(f"\n[Error] An unexpected error occurred during graph execution: {e}")
            import traceback
            traceback.print_exc() 