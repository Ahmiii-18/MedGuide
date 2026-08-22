"""
src/chains.py
-------------
LLM builder and LCEL chain definitions (LangChain v0.3+ / 1.x compatible).
"""
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


def build_llm(model_name: str, temperature: float = 0.2, streaming: bool = False) -> ChatOpenAI:
    """Instantiate ChatOpenAI model using environment API key."""
    api_key = os.getenv("OPENAI_API_KEY")
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        streaming=streaming,
        openai_api_key=api_key,
    )


def build_assessment_chain(llm, prompt=None):
    """
    Builds assessment chain using LCEL (RunnablePipe) syntax: prompt | llm.
    Replaces deprecated LLMChain.
    """
    if prompt is None:
        from src.prompts import ASSESSMENT_PROMPT
        prompt = ASSESSMENT_PROMPT

    return prompt | llm


def run_assessment(chain, inputs: dict) -> str:
    """Executes the LCEL chain and returns the text response content."""
    response = chain.invoke(inputs)
    return response.content if hasattr(response, "content") else str(response)


def stream_narrative(llm, inputs: dict):
    """Stream narrative patient explanation token-by-token via LCEL stream."""
    from src.prompts import NARRATIVE_PROMPT
    chain = NARRATIVE_PROMPT | llm
    for chunk in chain.stream(inputs):
        content = chunk.content if hasattr(chunk, "content") else str(chunk)
        if content:
            yield content