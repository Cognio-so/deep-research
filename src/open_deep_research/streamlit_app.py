import streamlit as st
import asyncio
from typing import Dict, Any
import uuid
import os
from langchain_core.messages import SystemMessage, HumanMessage

from open_deep_research.graph import graph
from open_deep_research.configuration import Configuration, SearchAPI, PlannerProvider, WriterProvider

def load_api_keys():
    """Load and validate required API keys"""
    # Check for API keys in environment variables
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    # If not in environment, check session state
    if not openai_key and 'OPENAI_API_KEY' in st.session_state:
        openai_key = st.session_state.OPENAI_API_KEY
    if not anthropic_key and 'ANTHROPIC_API_KEY' in st.session_state:
        anthropic_key = st.session_state.ANTHROPIC_API_KEY
    if not tavily_key and 'TAVILY_API_KEY' in st.session_state:
        tavily_key = st.session_state.TAVILY_API_KEY
    
    return openai_key, anthropic_key, tavily_key

def api_keys_interface():
    """Display interface for API key input"""
    st.sidebar.subheader("API Keys")
    
    openai_key = st.sidebar.text_input(
        "OpenAI API Key",
        type="password",
        value=st.session_state.get('OPENAI_API_KEY', ''),
        key="openai_key_input"
    )
    
    anthropic_key = st.sidebar.text_input(
        "Anthropic API Key",
        type="password",
        value=st.session_state.get('ANTHROPIC_API_KEY', ''),
        key="anthropic_key_input"
    )
    
    tavily_key = st.sidebar.text_input(
        "Tavily API Key",
        type="password",
        value=st.session_state.get('TAVILY_API_KEY', ''),
        key="tavily_key_input"
    )
    
    if st.sidebar.button("Save API Keys"):
        if openai_key:
            st.session_state.OPENAI_API_KEY = openai_key
            os.environ["OPENAI_API_KEY"] = openai_key
        if anthropic_key:
            st.session_state.ANTHROPIC_API_KEY = anthropic_key
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key
        if tavily_key:
            st.session_state.TAVILY_API_KEY = tavily_key
            os.environ["TAVILY_API_KEY"] = tavily_key
        st.sidebar.success("API keys saved!")
        st.rerun()

async def process_graph_events(topic: str, config: Dict[str, Any]):
    """Process graph events asynchronously"""
    thread = {"configurable": config}
    
    try:
        # Initial run with topic
        if not st.session_state.get('feedback_submitted'):
            async for event in graph.astream({"topic": topic}, thread, stream_mode="updates"):
                if '__interrupt__' in event:
                    interrupt_value = event['__interrupt__'][0]
                    yield "interrupt", interrupt_value
                else:
                    yield "plan", event
        
        # If feedback is submitted, continue with feedback
        else:
            feedback_text = st.session_state.feedback_text
            # Resume with the feedback - use Command for proper graph continuation
            async for event in graph.astream(Command(resume=feedback_text), thread, stream_mode="updates"):
                if "final_report" in event:
                    yield "report", event
                else:
                    yield "progress", event

    except Exception as e:
        st.error(f"Error processing events: {str(e)}")
        raise

async def run_graph_with_topic(topic: str, config: Dict[str, Any]):
    """Run the graph and collect all events"""
    events = []
    try:
        async for event_type, event in process_graph_events(topic, config):
            events.append((event_type, event))
            # Debug output
            st.write(f"Collected event - Type: {event_type}, Content: {event}")
    except Exception as e:
        st.error(f"Error running graph: {str(e)}")
        raise
    return events

def init_session_state():
    """Initialize session state variables"""
    if 'topic' not in st.session_state:
        st.session_state.topic = ""
    if 'config' not in st.session_state:
        st.session_state.config = None
    if 'events' not in st.session_state:
        st.session_state.events = []
    if 'feedback_submitted' not in st.session_state:
        st.session_state.feedback_submitted = False
    if 'feedback_text' not in st.session_state:
        st.session_state.feedback_text = ""
    if 'report_generated' not in st.session_state:
        st.session_state.report_generated = False
    if 'current_sections' not in st.session_state:
        st.session_state.current_sections = None
    if 'error' not in st.session_state:
        st.session_state.error = None
    if 'interrupt_handled' not in st.session_state:
        st.session_state.interrupt_handled = False

def main():
    st.title("Deep Research Assistant")
    
    # Initialize session state
    init_session_state()
    
    # Load API keys
    openai_key, anthropic_key, tavily_key = load_api_keys()
    
    # Show API keys interface
    api_keys_interface()
    
    # Check if required API keys are available
    if not openai_key:
        st.warning("Please enter your OpenAI API key in the sidebar to continue.")
        return
    
    if not tavily_key and search_api == "tavily":
        st.warning("Please enter your Tavily API key to use Tavily search.")
        return
    
    # Display any errors from previous runs
    if st.session_state.error:
        st.error(st.session_state.error)
        st.session_state.error = None
    
    # Sidebar for configuration
    st.sidebar.title("Configuration")
    
    search_api = st.sidebar.selectbox(
        "Search API",
        options=[api.value for api in SearchAPI],
        index=0
    )
    
    planner_provider = st.sidebar.selectbox(
        "Planner Provider",
        options=[provider.value for provider in PlannerProvider],
        index=0
    )
    
    writer_provider = st.sidebar.selectbox(
        "Writer Provider",
        options=[provider.value for provider in WriterProvider],
        index=0
    )
    
    max_search_depth = st.sidebar.slider(
        "Max Search Depth",
        min_value=1,
        max_value=5,
        value=2
    )
    
    number_of_queries = st.sidebar.slider(
        "Number of Queries per Section",
        min_value=1,
        max_value=5,
        value=2
    )

    # Main interface
    topic = st.text_input("Enter your research topic:", value=st.session_state.topic)
    
    start_button = st.button("Generate Report Plan")
    
    if (start_button and topic) or st.session_state.feedback_submitted:
        try:
            # Save topic
            st.session_state.topic = topic
            
            # Configure the graph if not already configured
            if start_button or not st.session_state.config:
                st.session_state.config = {
                    "thread_id": str(uuid.uuid4()),
                    "search_api": search_api,
                    "planner_provider": planner_provider,
                    "writer_provider": writer_provider,
                    "max_search_depth": max_search_depth,
                    "number_of_queries": number_of_queries,
                    "planner_model": "o3-mini",
                    "writer_model": "gpt-4o"
                }
            
            # Create progress container
            progress_container = st.empty()
            
            with progress_container.container():
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Process events
                with st.spinner("Processing..."):
                    events = asyncio.run(run_graph_with_topic(topic, st.session_state.config))
                    
                    for event_type, event in events:
                        if event_type == "interrupt" and not st.session_state.interrupt_handled:
                            # Display the report plan and get feedback
                            st.session_state.interrupt_handled = True
                            progress_bar.progress(50)
                            status_text.text("Report plan generated. Awaiting feedback...")
                            
                            # Extract sections from interrupt value
                            sections_text = event.value.split("Please provide feedback")[0]
                            
                            # Display sections in a structured way
                            st.subheader("Generated Report Plan")
                            sections = sections_text.strip().split("\n\n")
                            for section in sections:
                                if section.startswith("Section:"):
                                    with st.expander(section.split("\n")[0]):
                                        st.text("\n".join(section.split("\n")[1:]))
                            
                            # Feedback interface
                            st.subheader("Provide Feedback")
                            feedback_col1, feedback_col2 = st.columns([3, 1])
                            
                            with feedback_col1:
                                feedback_text = st.text_area(
                                    "Enter your feedback or suggestions for the report plan:",
                                    help="Enter feedback to modify the plan, or leave empty to approve as-is",
                                    key="feedback_input"
                                )
                            
                            with feedback_col2:
                                if st.button("Submit Feedback", key="submit_feedback"):
                                    if feedback_text.strip():
                                        st.session_state.feedback_text = feedback_text
                                    else:
                                        st.session_state.feedback_text = "true"
                                    
                                    st.session_state.feedback_submitted = True
                                    st.rerun()
                                
                        elif event_type == "progress":
                            if "completed_sections" in event:
                                status_text.text(f"Completed sections: {len(event['completed_sections'])}")
                                progress_bar.progress(75 + len(event['completed_sections']) * 2)
                            
                        elif event_type == "report" and "final_report" in event:
                            progress_bar.progress(100)
                            status_text.text("Report generated successfully!")
                            st.session_state.report_generated = True
                            
                            # Clear progress container and display final report
                            progress_container.empty()
                            st.subheader("Final Report")
                            st.markdown(event["final_report"])
                            
                            # Reset state for next run
                            st.session_state.feedback_submitted = False
                            st.session_state.interrupt_handled = False
                            st.session_state.config = None

        except Exception as e:
            st.session_state.error = f"An error occurred: {str(e)}"
            st.error(st.session_state.error)

    # Display current status
    if st.session_state.events:
        st.sidebar.subheader("Process Status")
        status = st.sidebar.empty()
        
        if st.session_state.report_generated:
            status.success("Report Generated")
        elif st.session_state.feedback_submitted:
            status.info("Processing Feedback")
        elif st.session_state.interrupt_handled:
            status.info("Awaiting Feedback")
        else:
            status.info("Generating Plan")

if __name__ == "__main__":
    main() 