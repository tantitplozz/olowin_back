from metagpt.actions import Action # Assuming Action is importable from metagpt.actions
from metagpt.tools.omni_card_tool import OmniCardTool # Assuming this path is correct

class OmniCardAction(Action):
    name: str = "OmniCardAnalysis"
    # No explicit __init__ needed if just inheriting and setting name

    async def run(self, context: str) -> str:
        """Runs the OmniCardTool with the given context (prompt)."""
        # If OmniCardTool().run() is synchronous, and MetaGPT Action's run can be async,
        # it's fine to call it directly. If tool.run() itself became async, you'd await it.
        tool = OmniCardTool()
        response = tool.run(context) # This is a sync call
        return response

# Example usage (for understanding, not part of the class)
# async def main_test():
#     action = OmniCardAction()
#     test_context = "วิเคราะห์ความเสี่ยงของธุรกรรมบัตรเครดิตนี้"
#     print(f"Testing OmniCardAction with context: '{test_context}'")
#     # To run this test, similar sys.path adjustments as in omni_card_tool.py would be needed
#     # and the MetaGPT library (for metagpt.actions.Action) must be installed.
#     # Also, the underlying OmniCard stack (run_graph, etc.) must be operational.
#     result = await action.run(test_context)
#     print(f"Result from OmniCardAction: {result}")

# if __name__ == '__main__':
#     import asyncio
#     asyncio.run(main_test()) 