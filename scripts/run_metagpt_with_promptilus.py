import sys
import os
import asyncio

# Add the parent directory of agent_prompts to sys.path for imports
# This assumes the script is in a subdirectory (e.g., 'scripts') 
# and the project root is one level up.
project_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)

# Attempt to import necessary MetaGPT components
try:
    # from metagpt.team import Team # Removed unused import
    from metagpt.roles.di.data_interpreter import DataInterpreter
    # Explicitly import the custom tool so it gets registered before MetaGPT starts
    from agent_prompts.promptilus_x import PromptilusXTool 
    print("[DEBUG] MetaGPT DataInterpreter and PromptilusXTool imported successfully.", file=sys.stderr)
except ImportError as e:
    print(f"[ERROR] Failed to import MetaGPT components: {e}", file=sys.stderr)
    print("[ERROR] Please ensure MetaGPT and related custom modules are installed correctly and accessible.", file=sys.stderr)
    print(f"[DEBUG] Current sys.path for run_metagpt_with_promptilus: {sys.path}", file=sys.stderr)
    sys.exit(1)

async def run_with_task(user_task: str):
    """Run MetaGPT DataInterpreter with a specific task."""
    print(f"[INFO] Running MetaGPT with task: {user_task}", file=sys.stderr)
    
    # Create a DataInterpreter instance
    # Tools are typically registered at the Role/Agent level, 
    # or globally if MetaGPT's mechanism supports it.
    # PromptilusXTool() should be available to DataInterpreter if registration is correct.
    di = DataInterpreter() # Ensure DataInterpreter is initialized to pick up registered tools
    print("[INFO] DataInterpreter instance created.", file=sys.stderr)
    
    # Run the DataInterpreter with the user task
    print("[INFO] Attempting to run DataInterpreter with the task...", file=sys.stderr)
    try:
        # The `run` method of a Role is typically async
        result = await di.run(user_task)
        print("[INFO] DataInterpreter task execution finished.", file=sys.stderr)
        return result
    except Exception as e: # Catching a more general exception during the run
        print(f"[ERROR] An error occurred during DataInterpreter execution: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        # Depending on requirements, you might want to re-raise or return an error indicator
        raise # Re-raise the exception to be handled by the caller (e.g., main.py)

async def main():
    """Main function for running the script directly for testing or tool registration check."""
    print("[INFO] Script run_metagpt_with_promptilus.py is starting (Tool Registration Mode).", file=sys.stderr)

    # Define the user task that should trigger the PromptilusXTool
    example_user_task = "วิเคราะห์ prompt ต่อไปนี้: ช่วยแนะนำร้านอาหารอร่อยๆ ในกรุงเทพฯ สำหรับมื้อเย็นหน่อยครับ ขอเป็นร้านอาหารไทย-อีสาน บรรยากาศดี เดินทางสะดวกด้วย BTS และราคาไม่แรงมาก"
    print(f"[INFO] Example user task for DataInterpreter (Tool Registration Mode):\n{example_user_task}", file=sys.stderr)

    try:
        await run_with_task(example_user_task)
    except Exception as e:
        # Error is already logged in run_with_task, an additional log here might be redundant
        # but can confirm that the script's main execution caught it.
        print(f"[ERROR] Main execution of run_metagpt_with_promptilus caught an error: {e}", file=sys.stderr)
    
    print("[INFO] Script execution for tool registration check ended.", file=sys.stderr)

if __name__ == "__main__":
    # This allows running the script directly, e.g., to check tool registration
    # or for simple tests of the run_with_task function.
    asyncio.run(main()) 