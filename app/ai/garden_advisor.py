from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

from app.schemas.ai import GardenTipsResponse, TipMode
from app.utils.config import settings

_model = GeminiModel("gemini-1.5-flash", api_key=settings.gemini_api_key)

_agent: Agent[None, GardenTipsResponse] = Agent(
    _model,
    result_type=GardenTipsResponse,
    system_prompt=(
        "You are an expert garden advisor. "
        "Provide helpful, practical, and specific tips tailored to the plant and location provided. "
        "Structure your response with clear titled sections and a concise summary."
    ),
)

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
    result = await _agent.run(prompt)
    return result.output
