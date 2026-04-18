from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

from app.utils.config import settings

provider = AnthropicProvider(api_key=settings.anthropic_api_key)
model = AnthropicModel("claude-haiku-4-5", provider=provider)


class LatinNameOutput(BaseModel):
    latin_name: str | None = None


class PlantCareOutput(BaseModel):
    planting: str | None = None
    care: str | None = None
    harvesting: str | None = None
    summary: str | None = None
    latin_name: str | None = None


async def get_latin_name(
    plant_type: str,
    species: str,
    variety: str | None = None,
) -> str | None:
    plant_desc = f"{variety} {species}" if variety else species
    agent: Agent = Agent(
        model=model,
        output_type=LatinNameOutput,
        instructions="You are a botanist. Return only the scientific Latin name for the given plant.",
        retries=3,
    )
    result = await agent.run(user_prompt=f"What is the scientific Latin name for {plant_desc} ({plant_type})?")
    return result.output.latin_name


def get_prompt(plant: str, location: str) -> str:
    return f"""
Provide specific care instructions for {plant}{location}.
All information must be specific to {plant} — do not substitute generic advice.

Include the Latin name for {plant}.

Planting: soil preparation, pH, planting depth, spacing, timing and companion plants specific to {plant}.
Care: watering, sunlight, fertilising, and common pests or diseases that affect {plant}.
Harvesting: how to tell when {plant} is ready to harvest and how to harvest it correctly.
"""

async def get_plant_tips(
    plant_type: str,
    species: str,
    variety: str | None = None,
    location: str | None = None,
) -> PlantCareOutput:
    plant_desc = f"{variety} {species} ({plant_type})" if variety else f"{species} ({plant_type})"
    location_desc = f" in {location}" if location else ""
    prompt = get_prompt(plant=plant_desc, location=location_desc)

    agent: Agent = Agent(
        model=model,
        output_type=PlantCareOutput,
        instructions=(
            "You are an expert garden advisor. "
            f"You are providing advice specifically for {plant_desc} — not generic {plant_type} advice. "
            "Every detail (planting depth, spacing, timing, pests, harvest cues) must be specific to this exact plant. "
            "Do not give general or vague guidance that would apply to any plant."
        ),
        retries=3,
    )
    result = await agent.run(user_prompt=prompt)
    return result.output
