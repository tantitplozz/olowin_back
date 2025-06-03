# workflow/graph_controller.py - Uses LangGraph to define and manage agent workflows

from agents.router_agent import route_model
from clients.gemini_client import call_gemini
from clients.ollama_client import call_ollama
from memory.chromadb_controller import add_to_memory, query_memory
from loggers.dataset_logger import log_dataset

# Placeholder for AgentState if it's used elsewhere or if graph compilation is still needed
# from typing import TypedDict, Optional, List, Dict, Any
# class AgentState(TypedDict):
#     input_prompt: str
#     recalled_memory: Optional[List[str]]
#     selected_model: str
#     llm_response: str
#     final_output: str
#     # Add other relevant state fields if this were a full LangGraph state

def run_graph(prompt: str) -> str:
    """Handles a prompt by querying memory, routing to a model, logging, and updating memory."""
    print(f"\n[Workflow] Received prompt: '{prompt[:100]}...'")
    
    # Step 1: ตรวจสอบ memory ก่อน (Query memory)
    print("[Workflow] Step 1: Querying memory...")
    recalled_docs = query_memory(prompt, top_k=3)
    if recalled_docs:
        print("[Workflow] Memory Recall Results:")
        for i, doc_content in enumerate(recalled_docs):
            print(f"  {i+1}. {doc_content[:150]}...")
    else:
        print("[Workflow] No relevant documents found in memory.")
    
    prompt_to_llm = prompt

    # Step 2: Route ไปยังโมเดล (Route to model)
    print("\n[Workflow] Step 2: Routing prompt to a model...")
    selected_model = route_model(prompt_to_llm)
    print(f"[Workflow] Model selected by router: {selected_model.upper()}")

    llm_response = ""
    if selected_model == "gemini":
        print("[Workflow] Calling Gemini...")
        llm_response = call_gemini(prompt_to_llm)
    else: # ollama
        print("[Workflow] Calling Ollama...")
        llm_response = call_ollama(prompt_to_llm)
    
    print(f"[Workflow] Model response: '{llm_response[:150]}...'")

    # Step 3: Logging + เพิ่มเข้า memory (Log and add to memory)
    print("\n[Workflow] Step 3: Logging response and updating memory...")
    log_dataset(agent_name=selected_model, data={"prompt": prompt_to_llm, "response": llm_response})
    
    add_to_memory(user_input=prompt, agent_response=llm_response)

    return llm_response

# --- LangGraph specific code (Commented out as run_graph is the new primary) ---
# from langgraph.graph import StateGraph
# from workflow.state_schema import AgentState as LangGraphAgentState # Alias to avoid conflict if used
# from agents.recon_agent import recon_agent_node_logic
# # ... other agent node imports

# def get_l10_graph():
#     """Constructs the LangGraph StateGraph for the L10 workflow."""
#     # This function would need to be significantly updated if it's to use the new clients and router logic
#     # or if it serves a different purpose now.
#     # For simplicity, if run_graph is the new primary, this might be deprecated or refactored.
#     print("[GraphController] Old get_l10_graph() called. Consider refactoring for new router logic if still needed.")
#     builder = StateGraph(LangGraphAgentState)
#     # ... (rest of the old graph building logic, if to be kept and adapted)
#     # Example: builder.add_node("router_node", router_node_logic) # Needs a router_node_logic
#     # builder.set_entry_point("router_node")
#     # ... conditional edges based on router_node_logic output to gemini_node or ollama_node ...
#     # compiled_graph = builder.compile()
#     # return compiled_graph
#     return None # Placeholder if old graph is not immediately usable

# --- Test code for old graph (Commented out as it's no longer primary) ---
# if __name__ == "__main__":
#     import sys
#     import os
#     # Add project root to sys.path for direct execution testing
#     PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
#     if PROJECT_ROOT not in sys.path:
#         sys.path.insert(0, PROJECT_ROOT)
#     # Re-import AgentState to ensure it's found after sys.path modification for the test
#     from workflow.state_schema import AgentState
#     print("Testing L10 graph compilation and direct invocation...")
#     test_graph = get_l10_graph() # This would cause an error as get_l10_graph is commented/removed
#     sample_card_info = {
#         "number": "4000111122223333",
#         "exp": "12/28",
#         "cvv": "123",
#         "name": "Test User",
#         "zip": "10001",
#     }
#     initial_state_for_test = AgentState(
#         target_site="test_finish_point_site",
#         card_info=sample_card_info,
#     )
#     print(f"Initial state for test: {initial_state_for_test.model_dump_json(indent=2)}")
#     try:
#         final_result_state = test_graph.invoke(initial_state_for_test)
#         print(
#             f"Final state after graph invocation: {final_result_state.model_dump_json(indent=2)}"
#         )
#     except Exception as e:
#         print(f"Error during graph invocation test: {e}")
#         import traceback
#         traceback.print_exc()
