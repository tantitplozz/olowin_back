import time
import random
import json
import os
import logging

logger = logging.getLogger(__name__)


def random_delay(min_seconds, max_seconds):
    """Generates a random delay between min_seconds and max_seconds."""
    delay = random.uniform(min_seconds, max_seconds)
    logger.debug("Delaying for %.2f seconds.", delay)
    time.sleep(delay)


def save_json(data, filepath, filename):
    """Saves data to a JSON file."""
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    full_path = os.path.join(filepath, filename)
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info("Successfully saved JSON to %s", full_path)
        return True
    except IOError as e:
        logger.error("Error saving JSON to %s: %s", full_path, e)
        return False


def load_json(filepath, filename):
    """Loads data from a JSON file."""
    full_path = os.path.join(filepath, filename)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info("Successfully loaded JSON from %s", full_path)
        return data
    except FileNotFoundError:
        logger.warning("JSON file not found: %s", full_path)
        return None
    except json.JSONDecodeError as e:
        logger.error("Error decoding JSON from %s: %s", full_path, e)
        return None
    except IOError as e:
        logger.error("Error loading JSON from %s: %s", full_path, e)
        return None


# Add any other utility functions that might be needed across the project.
# For example, functions for specific data parsing, string manipulation, etc.

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger.info("Testing utility functions.")

    # Test random_delay
    print("Testing random_delay...")
    random_delay(0.1, 0.5)
    print("Delay finished.")

    # Test save_json and load_json
    test_data_dir = "test_output"
    test_file = "test_data.json"
    sample_data = {"name": "Test User", "id": 123, "preferences": ["books", "travel"]}

    if save_json(sample_data, test_data_dir, test_file):
        loaded_data = load_json(test_data_dir, test_file)
        if loaded_data:
            print(f"Loaded data: {loaded_data}")
            assert loaded_data == sample_data
            print("JSON save/load test successful.")
            # Clean up test file and directory
            try:
                os.remove(os.path.join(test_data_dir, test_file))
                os.rmdir(test_data_dir)
                print(f"Cleaned up {test_data_dir}")
            except OSError as e:
                print(f"Error cleaning up test files: {e}")
        else:
            print("JSON load test failed.")
    else:
        print("JSON save test failed.") 