"""All environment variables in one place. Every value has a default."""

import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

# `or` (not just a getenv default) so an empty DATABASE_URL= line still falls back.
DATABASE_URL: str = os.getenv("DATABASE_URL") or "sqlite:///./research_agent.db"

PLANNER_MODEL: str = os.getenv("PLANNER_MODEL") or "openai:gpt-5.6-terra"
RESEARCH_MODEL: str = os.getenv("RESEARCH_MODEL") or "openai:gpt-6-luna"
WRITER_MODEL: str = os.getenv("WRITER_MODEL") or "openai:gpt-6-luna"
EDITOR_MODEL: str = os.getenv("EDITOR_MODEL") or "openai:gpt-6-luna"
