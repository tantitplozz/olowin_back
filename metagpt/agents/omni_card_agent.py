# metagpt/agents/omni_card_agent.py

from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.actions.omni_card_action import OmniCardAction

class OmniCardAgent(Role):
    name: str = "OmniCardAgent"
    profile: str = "ผู้วิเคราะห์ความเสี่ยงธุรกรรมด้วย AI"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_actions([OmniCardAction()]) # Use _init_actions to set actions
        # self._watch([Message]) # Example: Watch all messages or specific types

    async def _act(self) -> Message:
        """The core acting logic of the Role. 
        This is a simplified version. A more complete _act would typically:
        1. Get an observation/message from self.rc.memory (the RoleContext's memory).
        2. Decide which action to take based on the observation.
        3. Run the chosen action with appropriate context.
        4. Formulate a new Message with the action's result.
        The example you provided for agent.run("prompt") suggests a more direct invocation.
        This _act is a placeholder for how it might be structured if driven by observed messages.
        If agent.run() is directly passing a string, the Role.run() method handles it.
        """
        logger.info(f"{self.name}: Entering _act method...")
        # For a typical Role, you'd get the current context from memory
        # For example: obs = self.rc.memory.get_by_actions([self._actions[0].name])[-1] # Get last obs for action
        # prompt_content = obs.content
        
        # If the Role is called with a direct string via agent.run(prompt_string),
        # MetaGPT's Role.run() method often handles passing this to the default action.
        # Here, we assume the action will get its context from the last message if not directly passed.
        
        # This is a simplified _act. It assumes the context for the action is available
        # or that Role.run() will manage passing the initial prompt to the action.
        # If called without a specific message in memory to react to, it needs a default behavior.

        # Let's assume the last message in memory is the prompt, or Role.run handles it.
        # This is highly dependent on how MetaGPT's Environment and Role.run() are set up.
        # The provided example `await agent.run("prompt")` for a Role
        # usually means the Role's `run` method will orchestrate `_observe`, `_think`, `_act`.
        # `_act` itself usually retrieves what to act on from `self.rc.todo` (set by `_think`).
        
        # For simplicity to match the direct run style, let's assume the action can be called.
        # In a real MetaGPT flow, `_think` would set `self.rc.todo` to be this action.
        if not self.rc.todo: # If _think didn't set an action
            logger.warning(f"{self.name}: No action in self.rc.todo, cannot act.")
            # Attempt to use the first action with a generic or last known prompt if available
            # This is a fallback and might not be standard MetaGPT flow.
            # msg_from_memory = self.rc.memory.get() # get all messages
            # if not msg_from_memory:
            #     return Message(content="[OmniCardAgent] No prompt/context found to act on.", role=self.profile)
            # last_prompt = msg_from_memory[-1].content
            # result_str = await self._actions[0].run(context=last_prompt)
            # return Message(content=result_str, role=self.profile, cause_by=type(self._actions[0]))
            return Message(content="[OmniCardAgent] No specific task in todo. Action not performed by _act directly.", role=self.profile)


        action_to_run = self.rc.todo # Get action from todo (set by _think)
        # Assuming action_to_run is an instance of OmniCardAction
        # and its run method expects a string context from the message that triggered this action.
        # Typically, the message that _think decided to act upon is available.
        # For this example, let's assume the context is passed through the message that led to this action.
        msg_for_action = self.rc.memory.get_by_action(action_to_run)[-1] # Get last message for this action
        
        logger.info(f"{self.name}: Running action {action_to_run.name} with context: {msg_for_action.content[:100]}...")
        result_str = await action_to_run.run(context=msg_for_action.content)
        logger.info(f"{self.name}: Action {action_to_run.name} completed. Result: {result_str[:100]}...")
        
        return Message(content=result_str, role=self.profile, cause_by=type(action_to_run))

from loguru import logger # Added for logging within the agent 