from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from app.schemas.ai import GardenTipsResponse, TipMode
from app.utils.config import settings

provider = GoogleProvider(api_key=settings.gemini_api_key)
model = GoogleModel("gemini-2.5-flash", provider=provider)

_PROMPTS: dict[TipMode, str] = {
    TipMode.PLANTING: "Provide planting tips for {plant_desc}{location_desc}.",
    TipMode.CARE: "Provide care and troubleshooting tips for {plant_desc}{location_desc}.",
    TipMode.HARVEST: "Provide harvesting tips for {plant_desc}{location_desc}.",
}


async def get_plant_tips(
    plant_type: str,
    mode: TipMode,
    variety: str | None = None,
    location: str | None = None,
) -> GardenTipsResponse:
    plant_desc = f"{variety} {plant_type}" if variety else plant_type
    location_desc = f" in {location}" if location else ""
    prompt = _PROMPTS[mode].format(plant_desc=plant_desc, location_desc=location_desc)

    agent: Agent = Agent(
        model=model,
        output_type=GardenTipsResponse,
        instructions=(
            "You are an expert garden advisor. "
            "Provide helpful, practical, and specific tips tailored to the plant and location provided. "
            "Structure your response with clear titled sections and a concise summary."
        ),
        retries=3,
    )
    result = await agent.run(user_prompt=prompt)
    return result.output
