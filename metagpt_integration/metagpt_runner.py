# metagpt_integration/metagpt_runner.py

from workflow.pipeline_controller import full_pipeline # Assuming full_pipeline handles run_graph and eval
from loguru import logger
import asyncio # For running async full_pipeline from sync MetaGPT call if needed

# Note: Your example for OmniCardTool directly calls run_graph.
# If MetaGPT agents are to use the *full_pipeline* (with eval), this runner should call full_pipeline.
# If they only need the direct LLM response (via run_graph), then import and call run_graph.
# For this implementation, I'll assume metagpt_run_graph_task is for the simpler run_graph for now,
# as per your tool definition calling metagpt_run_graph_task which in turn calls run_graph.
# If OmniCardAgent (MetaGPT role) itself is supposed to orchestrate the eval, then its _act would call full_pipeline.

# Option 1: Runner calls the simpler `run_graph` (LLM response only)
from workflow.graph_controller import run_graph 

def metagpt_run_graph_task_simple(prompt: str) -> str:
    """
    ให้ MetaGPT ใช้งาน run_graph (LLM response) แบบ External Tool
    :param prompt: คำสั่งหรือโจทย์ที่ Agent ได้รับ
    :return: คำตอบจากระบบ OmniCard-AI (ผ่าน Gemini/Ollama + memory + logger from run_graph)
    """
    try:
        logger.info(f"[MetaGPT Integration - Simple] Received prompt from MetaGPT: {prompt}")
        result = run_graph(prompt)
        logger.info(f"[MetaGPT Integration - Simple] Response: {result}")
        return result
    except Exception as e:
        logger.error(f"[MetaGPT Integration - Simple] Error: {e}")
        return f"[MetaGPT Error - Simple] {str(e)}"

# Option 2: Runner calls the `full_pipeline` (LLM response + evaluation)
# This requires full_pipeline to be callable, potentially from a synchronous context
# if the MetaGPT tool run method is synchronous.
async def _run_full_pipeline_async(prompt: str):
    return await full_pipeline(prompt)

def metagpt_run_full_pipeline_task(prompt: str) -> dict: # Returns dict with result and evaluation
    """
    ให้ MetaGPT ใช้งาน full_pipeline (LLM response + Eval) แบบ External Tool
    :param prompt: คำสั่งหรือโจทย์ที่ Agent ได้รับ
    :return: Dict containing result and evaluation from OmniCard-AI full_pipeline
    """
    try:
        logger.info(f"[MetaGPT Integration - Full] Received prompt from MetaGPT: {prompt}")
        try:
            # Attempting to get a running loop was for a more complex async-from-sync scenario.
            # loop = asyncio.get_running_loop() # This line is removed as it was unused in the current logic path.
            
            # Current logic path defaults to simpler run_graph for tool compatibility.
            result = run_graph(prompt)
            logger.info(f"[MetaGPT Integration - Full Pipeline (using run_graph for tool)] Response: {result}")
            return {"result": result, "evaluation": "Evaluation via full_pipeline needs async call or separate trigger"}

        except RuntimeError: # No running event loop, also fall back to simpler run_graph
            logger.warning("[MetaGPT Integration - Full Pipeline] No running asyncio loop, using simple run_graph for tool.")
            result = run_graph(prompt)
            return {"result": result, "evaluation": "Evaluation via full_pipeline needs async call or separate trigger (no loop)"}

    except Exception as e:
        logger.error(f"[MetaGPT Integration - Full Pipeline] Error: {e}")
        return {"result": f"[MetaGPT Error - Full Pipeline] {str(e)}", "evaluation": "Error occurred"}

# Defaulting to the simpler runner as per your OmniCardTool.run example that returns a string.
metagpt_run_graph_task = metagpt_run_graph_task_simple 