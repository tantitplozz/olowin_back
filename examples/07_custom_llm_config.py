"""Example of custom LLM configurations for different roles in a debate scenario."""
import asyncio
from typing import Optional, List, Any, Tuple

try:
    from metagpt.config import Config  # Changed from config2 to config
    from metagpt.roles.base_role import Role  # More specific import
    from metagpt.actions.action import Action
    from metagpt.environment import Environment
    from metagpt.team import Team
    from metagpt.schema import Message
    from metagpt.logs import logger
except ImportError as e:
    print(f"Error importing MetaGPT components: {e}")
    print("Please ensure MetaGPT is installed correctly")
    raise

# Example: US Election Debate with Different LLM Configurations

# Method 1: Create configurations programmatically
def create_custom_configs() -> Tuple[Config, Config, Config]:
    """Create different configurations for GPT-4, GPT-3.5, and Ollama."""
    # GPT-4 config
    gpt4_config = Config.default()
    gpt4_config.llm.model = "gpt-4"
    gpt4_config.llm.api_key = "$OPENAI_API_KEY"

    # GPT-3.5 config
    gpt35_config = Config.default()
    gpt35_config.llm.model = "gpt-3.5-turbo"
    gpt35_config.llm.api_key = "$OPENAI_API_KEY"

    # Ollama config
    ollama_config = Config.default()
    ollama_config.llm.api_type = "ollama"
    ollama_config.llm.base_url = "http://localhost:11434"
    ollama_config.llm.model = "llama2"

    return gpt4_config, gpt35_config, ollama_config


def create_openrouter_config(model_name: str = "anthropic/claude-3-haiku") -> Config:
    """Create a configuration for OpenRouter"""
    openrouter_cfg = Config.default()
    openrouter_cfg.llm.api_type = "open_router"
    openrouter_cfg.llm.base_url = "https://openrouter.ai/api/v1"
    openrouter_cfg.llm.api_key = "$OPENROUTER_API_KEY"
    openrouter_cfg.llm.model = model_name
    return openrouter_cfg


# Placeholder for openrouter_models_showcase if it was intended to be different
async def openrouter_models_showcase() -> None:
    """Showcase different OpenRouter models"""
    print("\n=== OpenRouter Models Showcase (Placeholder) ===")
    logger.info("This demo would iterate through various free models on OpenRouter.")
    logger.info(
        "Models like 'meta-llama/llama-3.2-3b-instruct', 'qwen/qwen2.5-vl-7b-instruct', etc."
    )
    # For a full demo, one would loop through a list of model names,
    # create a config for each, and run a sample task.


# Define custom actions with different configurations
class DebateAction(Action):
    """Action for candidates to debate"""
    name: str = "Debate"

    async def run(self, topic: str, opponent_view: str = "") -> str:
        prompt = f"""
        Topic: {topic}
        
        {f"Opponent's view: {opponent_view}" if opponent_view else ""}
        
        Present your position on this topic in under 80 words. 
        Be passionate and convincing, but respectful.
        """
        result: str = await self._aask(prompt)
        return result


class VoteAction(Action):
    """Action for voter to make decision"""
    name: str = "Vote"

    async def run(self, candidate_views: List[str]) -> str:
        prompt = f"""
        Based on the following candidate positions:
        
        {chr(10).join([f"Candidate {i+1}: {view}" for i, view in enumerate(candidate_views)])}
        
        As a voter, decide which candidate you support and explain why in under 50 words.
        """
        result: str = await self._aask(prompt)
        return result


# Define roles with different LLM configurations
class Candidate(Role):
    """Political candidate role"""
    def __init__(self, name: str, party: str, config: Optional[Config] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.name = name
        self.profile = f"{party} candidate"
        self.goal = "Win the election"
        self.config = config

        # Create debate action with role's config
        debate_action = DebateAction()
        if config:
            debate_action.config = config
        self.set_actions([debate_action])

        # Watch for other candidates
        self._watch([DebateAction])

    async def _act(self) -> Optional[Message]:
        """Custom acting logic to respond to debates"""
        logger.info(f"{self.name}: Preparing to debate")

        # Get the topic from initial message or previous debates
        memories = self.get_memories()
        topic = ""
        opponent_view = ""

        if memories:
            # Extract topic and opponent's view
            for memory in memories:
                if "Topic:" in memory.content:
                    topic = memory.content.split("Topic:")[1].split("\n")[0].strip()
                if memory.role != self.profile and memory.cause_by == DebateAction:
                    opponent_view = memory.content

        # Debate on the topic
        response = await self.rc.todo.run(topic=topic, opponent_view=opponent_view)
        return Message(content=response, role=self.profile, cause_by=type(self.rc.todo))


class Voter(Role):
    """Voter role that evaluates candidates"""
    def __init__(self, name: str = "Voter", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.name = name
        self.profile = "Independent Voter"
        self.goal = "Choose the best candidate"
        self.set_actions([VoteAction()])
        self._watch([DebateAction])

    async def _act(self) -> Optional[Message]:
        """Collect all candidate views and vote"""
        logger.info(f"{self.name}: Evaluating candidates")

        # Get all debate messages
        memories = self.get_memories()
        candidate_views: List[str] = []

        for memory in memories:
            if memory.cause_by == DebateAction:
                candidate_views.append(memory.content)

        # Vote based on all views
        if len(candidate_views) >= 2:
            decision = await self.rc.todo.run(candidate_views=candidate_views)
            return Message(content=decision, role=self.profile, cause_by=type(self.rc.todo))

        return None


class SmartCandidate(Role):
    """A candidate that can use different models for different responses"""
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.name = name
        self.profile = "Smart Candidate"
        
        # Get configs for different quality responses
        gpt4_config, _, ollama_config = create_custom_configs()
        
        # Create actions with specific configs
        debate_gpt4 = DebateAction(config=gpt4_config)
        debate_ollama = DebateAction(config=ollama_config)
        
        self.set_actions([debate_gpt4, debate_ollama])
        self._current_action_index = 0

    async def _think(self) -> Action:
        """Alternate between high-quality and quick responses"""
        self._set_state(self._current_action_index)
        self._current_action_index = (self._current_action_index + 1) % 2
        return self._actions[self._rc.state]


class OpenRouterCandidate(Role):
    """A candidate that uses OpenRouter for all responses"""
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.name = name
        self.profile = "OpenRouter Candidate"
        
        # Create OpenRouter configuration
        config = create_openrouter_config()
        self.set_actions([DebateAction(config=config)])

    async def _think(self) -> Action:
        """Use OpenRouter for thinking"""
        logger.info(f"{self.name}: Using OpenRouter for thinking")
        return self._actions[0]  # Return the DebateAction instance


# Demo functions
async def simple_debate_demo() -> None:
    """Simple debate with different LLM configs"""
    print("\n=== Simple Debate Demo ===")

    # Create configurations
    _, gpt35_config, ollama_config = create_custom_configs()

    # Create candidates with different LLMs
    democrat = Candidate(
        name="Alice", party="Democratic", config=ollama_config  # Use local Ollama model
    )

    republican = Candidate(
        name="Bob", party="Republican", config=gpt35_config  # Use GPT-3.5
    )

    # Create voter (uses default config)
    voter = Voter(name="Charlie")

    # Create environment and team
    env = Environment(desc="US Election Debate")
    team = Team(investment=10.0, env=env, roles=[democrat, republican, voter])

    # Run debate
    await team.run(idea="Topic: Climate Change Policy", send_to="Alice", n_round=3)


async def action_level_config_demo() -> None:
    """Demo showing action-level configuration override"""
    print("\n=== Action-Level Config Demo ===")

    # Create smart candidate
    candidate = SmartCandidate(name="Diana")

    # First response uses GPT-4 (high quality)
    logger.info("First response (using GPT-4):")
    response1 = await candidate.run("Topic: Healthcare Reform")
    logger.info(response1)

    # Second response uses Ollama (quick)
    logger.info("\nSecond response (using Ollama):")
    response2 = await candidate.run("Topic: Education Policy")
    logger.info(response2)


async def priority_demo() -> None:
    """Demo showing configuration priority"""
    print("\n=== Configuration Priority Demo ===")

    # Get configs
    gpt4_config, gpt35_config, _ = create_custom_configs()

    # Global config (from Config.default())
    default_config = Config.default()
    if default_config and default_config.llm:
        logger.info(f"Global config model: {default_config.llm.model}")

    # Create action with its own config
    action_with_config = DebateAction(config=gpt4_config)

    # Create role with different config
    role_with_config = Candidate(name="Eve", party="Independent", config=gpt35_config)

    # Add the action with config to the role
    role_with_config.set_actions([action_with_config])

    # The action will use its own config (GPT-4) instead of role config (GPT-3.5)
    if role_with_config.config and role_with_config.config.llm:
        logger.info(f"Role config model: {role_with_config.config.llm.model}")
    if action_with_config.config and action_with_config.config.llm:
        logger.info(f"Action config model: {action_with_config.config.llm.model}")
    logger.info("Action will use: GPT-4 (action config has priority)")


async def openrouter_demo() -> None:
    """Demo showing OpenRouter configuration"""
    print("\n=== OpenRouter Demo ===")

    # Create a candidate that uses OpenRouter
    candidate = OpenRouterCandidate(name="Frank")

    # First response uses OpenRouter
    logger.info("First response (using OpenRouter):")
    response1 = await candidate.run("Topic: Climate Change Policy")
    logger.info(response1)

    # Second response uses OpenRouter
    logger.info("\nSecond response (using OpenRouter):")
    response2 = await candidate.run("Topic: Healthcare Reform")
    logger.info(response2)


async def main() -> None:
    """Run all demos"""
    print("MetaGPT Custom LLM Configuration Demo")
    print("=====================================")

    # Show configuration priority rules
    print("\nConfiguration Priority: Action Config > Role Config > Global Config")

    # Run demos
    await priority_demo()
    await action_level_config_demo()
    await simple_debate_demo()


if __name__ == "__main__":
    asyncio.run(main())
