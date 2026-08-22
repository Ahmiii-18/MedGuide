"""
src/cache_manager.py
--------------------
Manages dynamic cache switching between In-Memory, SQLite, and Disabled states.
"""
try:
    from langchain_core.globals import set_llm_cache
except ImportError:
    from langchain.globals import set_llm_cache

from langchain_community.cache import InMemoryCache, SQLiteCache

CACHE_EXPLANATIONS = {
    "None": "LLM responses are fetched live from OpenAI without caching.",
    "In-Memory": "Responses are cached in RAM for the duration of the active session.",
    "SQLite": "Responses are cached persistently in a local SQLite file (mediguide_cache.db).",
}


def configure_cache(cache_mode: str) -> str:
    """Configures global LangChain LLM cache based on UI choice."""
    if cache_mode == "In-Memory":
        set_llm_cache(InMemoryCache())
        return "In-Memory cache active (RAM)."
    elif cache_mode == "SQLite":
        set_llm_cache(SQLiteCache(database_path="mediguide_cache.db"))
        return "SQLite persistent cache active (mediguide_cache.db)."
    else:
        set_llm_cache(None)
        return "Caching disabled."