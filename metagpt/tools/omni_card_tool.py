# metagpt/tools/omni_card_tool.py

from metagpt_integration.metagpt_runner import metagpt_run_graph_task # Ensure this path is correct relative to MetaGPT's execution context

class OmniCardTool:
    name: str = "OmniCardTool"
    description: str = "ใช้ OmniCard-AI วิเคราะห์ธุรกรรม, จำลองความเสี่ยง, ตรวจสอบ prompt"

    def run(self, prompt: str) -> str:
        """Runs the OmniCard AI task with the given prompt."""
        # This assumes metagpt_run_graph_task is a synchronous function
        # or that MetaGPT handles async tools appropriately if it were async.
        # The current metagpt_run_graph_task (defaulting to _simple) is synchronous.
        return metagpt_run_graph_task(prompt)

# Example usage (not part of the class, for testing only)
# if __name__ == '__main__':
#     # This test requires the main project root to be in PYTHONPATH
#     # to find metagpt_integration and then workflow, clients, etc.
#     import sys
#     import os
#     SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
#     PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..")) # up one level from metagpt/tools to metagpt/
#     PROJECT_ROOT_TOP = os.path.abspath(os.path.join(PROJECT_ROOT, "..")) # up one level from metagpt/ to D:/MEEMEE

#     if PROJECT_ROOT_TOP not in sys.path:
#         sys.path.insert(0, PROJECT_ROOT_TOP)
#     print(f"Sys.path for OmniCardTool test: {sys.path}")

#     tool = OmniCardTool()
#     test_prompt = "วิเคราะห์ความเสี่ยงของธุรกรรมนี้หน่อย"
#     print(f"Testing OmniCardTool with prompt: '{test_prompt}'")
#     result = tool.run(test_prompt)
#     print(f"Result from OmniCardTool: {result}") 