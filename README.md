# Deep Research Assistant by Cognio Labs

A sophisticated AI research assistant built by Cognio Labs that automates the process of conducting deep research and generating comprehensive reports. Created by Ashutosh Upadhyay and Shivam Upadhyay.

## 🌟 Overview

Deep Research Assistant is an advanced LLM-powered agent that follows a workflow similar to OpenAI and Gemini Deep Research, but with extensive customization options. You can:

- Provide custom report structures and outlines
- Choose the planner model (e.g., DeepSeek, OpenAI reasoning model)
- Give feedback on report sections and iterate until approval
- Configure search APIs (Tavily, Perplexity) and search parameters
- Set research depth per section
- Select writer models (OpenAI, Anthropic, Groq)


## 🔄 How It Works

1. **Plan and Execute**
   - Uses a plan-and-execute workflow separating planning from research
   - Enables human-in-the-loop approval of report plans
   - Uses reasoning models for section planning
   - Incorporates web search for initial topic understanding
   - Accepts custom report structures and human feedback

2. **Research and Write**
   - Parallel processing of report sections
   - Web research via Tavily API or Perplexity
   - Iterative reflection and follow-up questions
   - Configurable research depth
   - Final sections (intro, conclusion) written after main body
   
3. **Managing Different Types**
   - Built on LangGraph with native configuration management
   - Supports different assistant types for various report styles
   - Flexible structure field in graph configuration

## �� Quickstart

Ensure you have API keys set for your desired tools.

Select a web search tool (by default Open Deep Research uses Tavily):

* [Tavily API](https://tavily.com/)
* [Perplexity API](https://www.perplexity.ai/hub/blog/introducing-the-sonar-pro-api)

Select a writer model (by default Open Deep Research uses Anthropic):

* [Anthropic](https://www.anthropic.com/)

Select a planner model (by default Open Deep Research uses OpenAI o3-mini):

* [OpenAI](https://openai.com/)
* [Groq](https://groq.com/)

### Using the package

Import and compile the graph:
```python
from langgraph.checkpoint.memory import MemorySaver
from open_deep_research.graph import builder
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
```

View the graph:
```python
from IPython.display import Image, display
display(Image(graph.get_graph(xray=1).draw_mermaid_png()))
```

Run the graph with a desired topic and configuration:
```python
import uuid 
thread = {"configurable": {"thread_id": str(uuid.uuid4()),
                           "search_api": "tavily",
                           "planner_provider": "openai",
                           "max_search_depth": 1,
                           "planner_model": "o3-mini"}}

topic = "Overview of the AI inference market with focus on Fireworks, Together.ai, Groq"
async for event in graph.astream({"topic":topic,}, thread, stream_mode="updates"):
    print(event)
    print("\n")
```

The graph will stop when the report plan is generated, and you can pass feedback to update the report plan:
```python
from langgraph.types import Command
async for event in graph.astream(Command(resume="Include a revenue estimate (ARR) in the sections"), thread, stream_mode="updates"):
    print(event)
    print("\n")
```

When you are satisfied with the report plan, you can pass `True` to proceed to report generation:
```
# Pass True to approve the report plan and proceed to report generation
async for event in graph.astream(Command(resume=True), thread, stream_mode="updates"):
    print(event)
    print("\n")
```

### Running LangGraph Studio UI locally

Clone the repository:
```bash
git clone https://github.com/langchain-ai/open_deep_research.git
cd open_deep_research
```

Edit the `.env` file with your API keys (e.g., the API keys for default selections are shown below):

```bash
cp .env.example .env
```

Set:
```bash
export TAVILY_API_KEY=<your_tavily_api_key>
export ANTHROPIC_API_KEY=<your_anthropic_api_key>
export OPENAI_API_KEY=<your_openai_api_key>
```

## 📖 Customizing the report

You can customize the research assistant's behavior through several parameters:

- `report_structure`: Define a custom structure for your report (defaults to a standard research report format)
- `number_of_queries`: Number of search queries to generate per section (default: 2)
- `max_search_depth`: Maximum number of reflection and search iterations (default: 2)
- `planner_provider`: Model provider for planning phase (default: "openai", but can be "groq")
- `planner_model`: Specific model for planning (default: "o3-mini", but can be any Groq hosted model such as "deepseek-r1-distill-llama-70b")
- `writer_model`: Model for writing the report (default: "claude-3-5-sonnet-latest")
- `search_api`: API to use for web searches (default: Tavily)

These configurations allow you to fine-tune the research process based on your needs, from adjusting the depth of research to selecting specific AI models for different phases of report generation.

## 🛠️ Technical Architecture

### State Management
- `ReportState`: Manages overall report progress
- `SectionState`: Handles individual section research
- `SectionOutputState`: Controls section completion

### Key Components
- **Graph Structure**:
  - Outer graph for overall report flow
  - Inner graph for section-specific research
  - Human-in-the-loop feedback integration

- **Node Types**:
  - `generate_report_plan`: Creates initial structure
  - `human_feedback`: Handles user interaction
  - `build_section_with_web_research`: Manages research flow
  - `write_final_sections`: Generates non-research sections
  - `compile_final_report`: Assembles final output

## 🔍 Research Process

1. **Query Generation**
   - Analyzes section requirements
   - Generates targeted search queries
   - Adapts queries based on missing information

2. **Web Research**
   - Performs parallel searches
   - Deduplicates and formats sources
   - Maintains source attribution

3. **Content Generation**
   - Synthesizes research findings
   - Ensures factual accuracy
   - Maintains consistent style

4. **Quality Control**
   - Evaluates section completeness
   - Identifies information gaps
   - Triggers additional research if needed

## 📊 Use Cases

- Market Research Reports
- Technical Documentation
- Academic Literature Reviews
- Industry Analysis
- Competitive Intelligence
- Technology Assessments

## 🏢 About Cognio Labs

Cognio Labs specializes in building advanced AI agents and automation solutions. Our mission is to enhance human capabilities through intelligent software systems.

For more information, contact:
- Ashutosh Upadhyay
- Shivam Upadhyay

---

Built with ❤️ by Cognio Labs


