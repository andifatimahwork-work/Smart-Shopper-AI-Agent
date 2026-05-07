from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from .rag import retrieve_common_information, retrieve_product_recommendation
from .settings import get_settings

settings = get_settings()


def resolve_adk_model(model_name: str):
    if model_name.startswith(("groq/", "openai/", "anthropic/")):
        return LiteLlm(model=model_name)
    return model_name


root_agent = Agent(
    name="smartshopper_assistant",
    model=resolve_adk_model(settings["adk_model"]),
    description="Personalized SmartShopper Assistant with product and common information tools.",
    instruction="""
You are Personalized SmartShopper Assistant.

Route every user question to the right tool:
1. Use retrieve_product_recommendation for product recommendation, product search,
   product preference, price, brand, material, category, size/style, or outfit needs.
2. Use retrieve_common_information for common shopping process questions, including
   shipping, delivery, payment, how to buy, refund, return, cancellation, order tracking,
   voucher, warranty, account, and customer service.
3. If a question includes both product and policy needs, call the most relevant tool first,
   then call the second tool if the answer needs it.

After a tool returns a dictionary with an answer field, use that answer as the final
response. Do not call another model to rewrite it unless the user explicitly asks for
a different format.

Respond in Indonesian unless the user asks for another language. Be helpful and structured.
Do not make up product or policy details outside tool results.
""",
    tools=[retrieve_product_recommendation, retrieve_common_information],
)
