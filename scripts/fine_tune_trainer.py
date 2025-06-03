# fine_tune_trainer.py
import json
from datasets import load_dataset, Dataset # type: ignore 
# Using type: ignore for datasets and transformers as they might not be immediately available to the linter
# but will be in the execution environment after pip install.
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer # type: ignore
import os

def load_jsonl(file_path):
    """Loads a .jsonl file into a list of dictionaries."""
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Skipping line due to JSONDecodeError: {e} in line: {line.strip()}")
    # Ensure a consistent structure, expecting 'prompt' and 'response' keys
    # This part might need adjustment based on the actual structure logged by dataset_logger.py
    # The dataset_logger logs a dict like: {"timestamp": ..., "agent_name": ..., "prompt": ..., "response": ..., "feedback": ...}
    # For fine-tuning, we typically need a prompt-response pair or instruction-output pair.
    # Adapting to use the logged 'prompt' and 'response' keys directly if they exist.
    processed_data = []
    for item in data:
        if "prompt" in item and "response" in item:
            processed_data.append({"prompt": item["prompt"], "response": item["response"]})
        else:
            print(f"Skipping item due to missing 'prompt' or 'response' key: {item}")
    return processed_data

def train(dataset_path="datasets/omnicard_evaluated_log.jsonl", # Updated to match potential logger output
          base_model="TheBloke/Nous-Hermes-2-Yi-34B-GGUF", 
          output_dir="fine_tuned_model"):
    
    print(f"[FineTune] Starting fine-tuning process...")
    print(f"[FineTune] Loading dataset from: {dataset_path}")
    if not os.path.exists(dataset_path):
        print(f"[FineTune Error] Dataset file not found: {dataset_path}")
        return

    data = load_jsonl(dataset_path)
    if not data:
        print(f"[FineTune Error] No data loaded from dataset: {dataset_path}. Check file content and format.")
        return
        
    ds = Dataset.from_list(data)
    print(f"[FineTune] Loaded {len(ds)} records into Dataset.")

    print(f"[FineTune] Loading tokenizer for base model: {base_model}")
    try:
        tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
        # Add padding token if missing (common for some models)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            print("[FineTune] Tokenizer pad_token set to eos_token.")
    except Exception as e:
        print(f"[FineTune Error] Could not load tokenizer for {base_model}: {e}")
        return

    print(f"[FineTune] Loading base model: {base_model}")
    try:
        # For GGUF models, AutoModelForCausalLM might not be the direct way if you intend to fine-tune GGUF.
        # Fine-tuning GGUF usually involves converting to a full model format (like PyTorch), fine-tuning, then converting back.
        # Or using tools specifically designed for GGUF fine-tuning (e.g., llama.cpp training features).
        # The transformers library primarily works with PyTorch/TensorFlow models.
        # If base_model is a GGUF path, this from_pretrained will likely fail or not load it for training.
        # Assuming base_model here refers to a Hugging Face model identifier for a full model (e.g., a non-quantized version).
        # If you intend to fine-tune a GGUF directly, this script would need significant changes
        # and different libraries (like llama-cpp-python with training support if available, or external tools).
        # For now, proceeding as if base_model is a standard Hugging Face model ID for a full precision model.
        model = AutoModelForCausalLM.from_pretrained(base_model, trust_remote_code=True)
        print(f"[FineTune] Model loaded. Type: {type(model)}")
    except Exception as e:
        print(f"[FineTune Error] Could not load base model {base_model}: {e}")
        print("[FineTune Info] Note: If using a GGUF model path directly, ensure it's a full model format compatible with Hugging Face Trainer for fine-tuning.")
        return

    def tokenize_function(example):
        # Create a prompt format suitable for instruction fine-tuning
        # This example uses a simple instruction-response format.
        # Adjust the format based on how the base model was trained or expects inputs.
        text = f"### Instruction:\n{example['prompt']}\n\n### Response:\n{example['response']}{tokenizer.eos_token}"
        # Max length should be chosen based on model and data characteristics
        tokenized_output = tokenizer(text, truncation=True, padding="max_length", max_length=512) 
        return tokenized_output

    print("[FineTune] Tokenizing dataset...")
    try:
        tokenized_ds = ds.map(tokenize_function, remove_columns=["prompt", "response"])
        print(f"[FineTune] Dataset tokenized. Example record: {tokenized_ds[0] if len(tokenized_ds) > 0 else 'N/A'}")
    except Exception as e:
        print(f"[FineTune Error] Failed to tokenize dataset: {e}")
        return

    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=1, # Adjusted for potentially large models
        num_train_epochs=1, # Start with 1 epoch for testing
        logging_steps=10,
        save_steps=50, # Save more frequently for long runs
        save_total_limit=2,
        logging_dir=f"{output_dir}/logs",
        fp16=True, # Requires NVIDIA GPU with Apex, or set to False if issues/no GPU
        # gradient_accumulation_steps=4, # Useful for larger effective batch sizes
        remove_unused_columns=False, # Important if dataset still has other columns
        # report_to="tensorboard", # Or wandb, etc.
    )
    print(f"[FineTune] TrainingArguments prepared: {training_args}")

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_ds,
        tokenizer=tokenizer,
        # data_collator can be added for dynamic padding if padding="longest" in tokenizer
    )

    print("[FineTune] Starting training...")
    try:
        trainer.train()
        print("[FineTune] Training completed.")
    except Exception as e:
        print(f"[FineTune Error] Training failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print(f"[FineTune] Saving fine-tuned model to: {output_dir}")
    try:
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        print(f"[✅] Fine-Tune สำเร็จ → Model อยู่ที่: {output_dir}")
    except Exception as e:
        print(f"[FineTune Error] Failed to save model/tokenizer: {e}")

if __name__ == "__main__":
    # Example: Fetch parameters from a config file or command line arguments
    # For now, using defaults set in the train function signature.
    # config_path = "train_config.json"
    # if os.path.exists(config_path):
    #     with open(config_path, "r") as f:
    #         config = json.load(f)
    #     train(
    #         dataset_path=config.get("dataset_path", "datasets/omnicard_evaluated_log.jsonl"),
    #         base_model=config.get("base_model", "TheBloke/Nous-Hermes-2-Yi-34B-GGUF"),
    #         output_dir=config.get("output_dir", "fine_tuned_model")
    #     )
    # else:
    #     print(f"[FineTune] Config file {config_path} not found. Running with default parameters.")
    train() 