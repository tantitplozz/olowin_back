# metagpt/agents/auto_eval_agent.py

from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from loguru import logger

class EvalAction(Action):
    name: str = "EvaluateOmniCardResponse"
    # No explicit __init__ needed

    async def run(self, context: str) -> str:
        """ประเมินผลจาก OmniCardAgent. Context ควรมี prompt + response."""
        logger.info(f"[EvalAction] Evaluating context: {context[:150]}...")
        # Simple keyword-based evaluation
        if "✅" in context or "ผ่าน" in context or "สำเร็จ" in context or "ดี" in context:
            evaluation = "✅ ประเมิน: Agent ทำงานได้ผลดี"
        elif "error" in context.lower() or "ล้มเหลว" in context or "ปัญหา" in context or "ไม่สามารถ" in context:
            evaluation = "⚠️ ประเมิน: Agent อาจมีปัญหาหรือทำงานไม่สำเร็จ"
        else:
            evaluation = "⚪️ ประเมิน: ผลลัพธ์ไม่ชัดเจน, ต้องการการตรวจสอบเพิ่มเติม"
        logger.info(f"[EvalAction] Evaluation result: {evaluation}")
        return evaluation

class AutoEvalAgent(Role):
    name: str = "AutoEvalAgent"
    profile: str = "ผู้ประเมินผลลัพธ์ของ Agent โดยอัตโนมัติ"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_actions([EvalAction()])
        # self._watch([Message]) # Decide what messages this agent should react to

    async def _act(self) -> Message:
        """Core acting logic for AutoEvalAgent."""
        logger.info(f"{self.name}: Entering _act method...")
        if not self.rc.todo: # If _think didn't set an action
            logger.warning(f"{self.name}: No action in self.rc.todo.")
            # This agent might need a specific trigger or to observe specific message types.
            # For example, it might observe messages from OmniCardAgent.
            # For now, if no direct task, it does nothing or returns a default message.
            return Message(content="[AutoEvalAgent] No specific task in todo. Waiting for input to evaluate.", role=self.profile)

        action_to_run = self.rc.todo
        # Assuming the context for evaluation is in the message that triggered this action.
        msg_for_action = self.rc.memory.get_by_action(action_to_run)[-1]
        
        logger.info(f"{self.name}: Running action {action_to_run.name} with context: {msg_for_action.content[:100]}...")
        evaluation_result = await action_to_run.run(context=msg_for_action.content)
        logger.info(f"{self.name}: Action {action_to_run.name} completed. Evaluation: {evaluation_result}")
        
        return Message(content=evaluation_result, role=self.profile, cause_by=type(action_to_run)) 