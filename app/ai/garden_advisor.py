from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

from app.models.plant import CareInfo
from app.utils.config import settings

provider = AnthropicProvider(api_key=settings.anthropic_api_key)
model = AnthropicModel("claude-haiku-4-5", provider=provider)


def get_prompt(plant: str, location: str) -> str:
    return f"""
Provide planting information for growing {plant}{location} including the Latin name. 
Be sure to provide information on planting, including soil preparation, planting depth, spacing, and timing.
Also include information about caring for the plant, common pests, watering and sunlight needs.
Provide information about how to recognize when a plant is ready for harvest and how to properly harvest it.
"""

async def get_plant_tips(
    plant_type: str,
    variety: str | None = None,
    location: str | None = None,
) -> CareInfo:
    plant_desc = f"{variety} {plant_type}" if variety else plant_type
    location_desc = f" in {location}" if location else ""
    prompt = get_prompt(plant=plant_desc, location=location_desc)

    agent: Agent = Agent(
        model=model,
        output_type=CareInfo,
        instructions=(
            "You are an expert garden advisor. "
            "Provide helpful, practical, and specific tips tailored to the plant and location provided. "
            "Structure your response with clear sections and a concise summary."
        ),
        retries=3,
    )
    result = await agent.run(user_prompt=prompt)
    return result.output
