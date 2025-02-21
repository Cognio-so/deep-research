import os
from enum import Enum
from dataclasses import dataclass, fields
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from dataclasses import dataclass

DEFAULT_REPORT_STRUCTURE = """
Use this structure to create a comprehensive report on the user-provided topic:

1. Executive Summary
   - Key findings and insights
   - Scope and objectives
   - Methodology overview

2. Introduction
   - Background and context
   - Problem statement or research question
   - Significance and relevance
   - Research methodology details
     * Data sources
     * Search strategies
     * Analysis methods

3. Main Research Findings
   - Historical Context and Evolution
     * Timeline of key developments
     * Major milestones and breakthroughs

   - Current State Analysis
     * Market/field overview
     * Key players and stakeholders
     * Statistical data and metrics
     * Geographic considerations

   - Technical/Detailed Analysis
     * Core components/concepts
     * Technological aspects
     * Process workflows
     * Regulatory framework

   - Challenges and Opportunities
     * Current limitations
     * Emerging trends
     * Future possibilities
     * Risk factors

4. Comparative Analysis
   - Industry benchmarks
   - Competitive landscape
   - Best practices
   - Case studies

5. Impact Assessment
   - Economic implications
   - Social implications
   - Environmental considerations
   - Ethical considerations

6. Future Outlook
   - Predicted trends
   - Growth opportunities
   - Potential challenges
   - Strategic recommendations

7. Conclusion
   - Summary of key findings
   - Critical insights
   - Research limitations
   - Recommendations for further research""" 

class SearchAPI(Enum):
    PERPLEXITY = "perplexity"
    TAVILY = "tavily"

class PlannerProvider(Enum):
    OPENAI = "openai"
    GROQ = "groq"

class WriterProvider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"

@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the chatbot."""
    report_structure: str = DEFAULT_REPORT_STRUCTURE # Defaults to the default report structure
    number_of_queries: int = 2 # Number of search queries to generate per iteration
    max_search_depth: int = 3 # Maximum number of reflection + search iterations
    planner_provider: PlannerProvider = PlannerProvider.OPENAI  # Defaults to OpenAI as provider
    planner_model: str = "o3-mini" # Defaults to OpenAI o3-mini as planner model
    writer_provider: WriterProvider = WriterProvider.OPENAI # Defaults to OPENAI as provider
    writer_model: str = "gpt-4o" # Defaults to OpenAI as provider
    search_api: SearchAPI = SearchAPI.TAVILY # Default to TAVILY

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})