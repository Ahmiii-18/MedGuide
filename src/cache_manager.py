"""
src/cache_manager.py
---------------------
Switches LangChain's global LLM cache between None / InMemoryCache /
SQLiteCache based on the sidebar selection.
"""

try:
    from langchain.globals import set_llm_cache
except ImportError:
    from langchain_core.globals import set_llm_cache
from langchain_community.cache import InMemoryCache, SQLiteCache

CACHE_EXPLANATIONS = {
    "None": "Caching disabled - every submission calls the API.",
    "In-Memory": "Cached in RAM for this session only (fastest, lost on restart).",
    "SQLite": "Cached to mediguide_cache.db on disk (survives restarts).",
}


def configure_cache(mode: str) -> str:
    if mode == "In-Memory":
        set_llm_cache(InMemoryCache())
    elif mode == "SQLite":
        set_llm_cache(SQLiteCache(database_path="mediguide_cache.db"))
    else:
        set_llm_cache(None)
    return CACHE_EXPLANATIONS.get(mode, "")
