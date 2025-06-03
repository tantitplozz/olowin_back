from utils.logger import broadcast_log, log_to_mongo
from loggers.dataset_logger import log_dataset
from agents.omnicard_agent import OmniCardAgent # Placeholder import
from agents.eval_agent import AutoEvalAgent     # Placeholder import

async def full_pipeline(prompt: str):
    await broadcast_log(f"📥 เริ่มต้น OmniCardAgent ด้วย Prompt: {prompt}")
    log_to_mongo("PipelineStart", {"prompt": prompt})

    omni_agent = OmniCardAgent()
    response = await omni_agent.run(prompt)
    await broadcast_log(f"🤖 OmniCardAgent ตอบกลับ: {response}")
    log_to_mongo("OmniCardResponse", {"prompt": prompt, "response": response})

    eval_agent = AutoEvalAgent()
    context_for_eval = f"Prompt:\n{prompt}\n\nResponse:\n{response}"
    feedback = await eval_agent.run(context_for_eval)
    await broadcast_log(f"📊 AutoEvalAgent ประเมินผล: {feedback}")
    log_to_mongo("AutoEval", {"prompt": prompt, "response": response, "feedback": feedback})

    if "✅" in feedback or "ผ่าน" in feedback:
        log_dataset(agent_name="omnicard_evaluated", data={"prompt": prompt, "response": response, "feedback": feedback})
        await broadcast_log("📁 บันทึกเข้า Dataset สำหรับ Fine-Tune แล้ว ✅")

    return {"result": response, "evaluation": feedback}

# Example of how to run this if needed (e.g., from an async FastAPI endpoint)
# async def main():
#     test_prompt = "ทดสอบระบบหน่อยครับ"
#     output = await full_pipeline(test_prompt)
#     print(output)

# if __name__ == "__main__":
#     asyncio.run(main()) 