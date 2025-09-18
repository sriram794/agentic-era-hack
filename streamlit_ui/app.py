import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime
import numpy as np
from typing import Dict, List, Any
import re

class Event_Extractor:
    """
    Embedded extractor class for the dashboard
    """
    
    def __init__(self, json_file_path: str = None, json_data: dict = None):
        if json_file_path:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        elif json_data:
            self.data = json_data
        else:
            raise ValueError("Either json_file_path or json_data must be provided")
    
    def extract_all_events(self) -> List[Dict[str, Any]]:
        events = []
        for event in self.data.get('events', []):
            event_info = {
                'id': event.get('id'),
                'timestamp': event.get('timestamp'),
                'author': event.get('author'),
                'invocation_id': event.get('invocationId'),
                'role': event.get('content', {}).get('role'),
                'content_parts': [],
                'grounding_chunks': [],
                'grounding_supports': [],
                'search_queries': []
            }
            
            # Extract content parts
            content = event.get('content', {})
            parts = content.get('parts', [])
            for part in parts:
                if 'text' in part:
                    event_info['content_parts'].append(part['text'])
            
            # Extract grounding metadata
            grounding_metadata = event.get('groundingMetadata', {})
            
            # Extract grounding chunks
            grounding_chunks = grounding_metadata.get('groundingChunks', [])
            for chunk in grounding_chunks:
                if 'web' in chunk:
                    web_info = chunk['web']
                    event_info['grounding_chunks'].append({
                        'domain': web_info.get('domain'),
                        'title': web_info.get('title'),
                        'uri': web_info.get('uri')
                    })
            
            # Extract grounding supports
            grounding_supports = grounding_metadata.get('groundingSupports', [])
            for support in grounding_supports:
                support_info = {
                    'grounding_chunk_indices': support.get('groundingChunkIndices', []),
                    'segment': support.get('segment', {})
                }
                event_info['grounding_supports'].append(support_info)
            
            # Extract search queries
            web_search_queries = grounding_metadata.get('webSearchQueries', [])
            event_info['search_queries'] = web_search_queries
            
            events.append(event_info)
        
        return events
    
    def get_event_summary(self) -> pd.DataFrame:
        events = self.extract_all_events()
        summary_data = []
        for event in events:
            summary_data.append({
                'ID': event['id'],
                'Author': event['author'],
                'Role': event['role'],
                'Timestamp': event['timestamp'],
                'Content_Length': len(''.join(event['content_parts'])),
                'Grounding_Chunks_Count': len(event['grounding_chunks']),
                'Grounding_Supports_Count': len(event['grounding_supports']),
                'Search_Queries_Count': len(event['search_queries'])
            })
        
        return pd.DataFrame(summary_data)
    
    def get_grounding_sources(self) -> List[str]:
        all_events = self.extract_all_events()
        domains = set()
        for event in all_events:
            for chunk in event['grounding_chunks']:
                if chunk['domain']:
                    domains.add(chunk['domain'])
        return sorted(list(domains))

def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="PolyMind AI Analytics",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def load_custom_css():
    """Load custom CSS for professional styling"""
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
    }
    
    .agent-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .source-badge {
        background: #e3f2fd;
        color: #1565c0;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        margin: 0.1rem;
        display: inline-block;
        font-size: 0.8rem;
    }
    
    .timeline-item {
        border-left: 3px solid #1f77b4;
        padding-left: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def create_metrics_overview(summary_df):
    """Create key metrics overview"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_events = len(summary_df)
        st.metric(
            label="📈 Total Events",
            value=total_events,
            delta=f"{total_events} agents involved"
        )
    
    with col2:
        total_content = summary_df['Content_Length'].sum()
        st.metric(
            label="📝 Total Content",
            value=f"{total_content:,} chars",
            delta=f"Avg: {int(total_content/total_events):,} per event"
        )
    
    with col3:
        total_sources = summary_df['Grounding_Chunks_Count'].sum()
        st.metric(
            label="🔗 Grounding Sources",
            value=total_sources,
            delta=f"{len(summary_df[summary_df['Grounding_Chunks_Count'] > 0])} events with sources"
        )
    
    with col4:
        total_queries = summary_df['Search_Queries_Count'].sum()
        st.metric(
            label="🔍 Search Queries",
            value=total_queries,
            delta=f"{len(summary_df[summary_df['Search_Queries_Count'] > 0])} events with searches"
        )

def create_agent_workflow_chart(summary_df):
    """Create agent workflow visualization"""
    fig = go.Figure()
    
    # Create timeline
    timestamps = summary_df['Timestamp'].values
    authors = summary_df['Author'].values
    
    # Normalize timestamps for better visualization
    min_ts = min(timestamps)
    normalized_ts = [(ts - min_ts) for ts in timestamps]
    
    # Color mapping for different agents
    color_map = {
        'user': '#ff7f0e',
        'data_collector_agent': '#2ca02c',
        'role_identifier_agent': '#d62728',
        'prompt_generator_agent': '#9467bd',
        'role_thought_collector_agent': '#8c564b',
        'fact_checker_agent': '#e377c2',
        'conflict_resolution_agent': '#7f7f7f',
        'simulation_agent': '#bcbd22',
        'scoring_agent': '#17becf',
        'final_solution_agent': '#1f77b4',
        'visualization_agent': '#ff9896'
    }
    
    for i, (author, ts) in enumerate(zip(authors, normalized_ts)):
        fig.add_trace(go.Scatter(
            x=[ts], 
            y=[i],
            mode='markers+text',
            marker=dict(
                size=15,
                color=color_map.get(author, '#333333'),
                line=dict(width=2, color='white')
            ),
            text=[author.replace('_', ' ').title()],
            textposition="middle right",
            name=author.replace('_', ' ').title(),
            showlegend=False
        ))
    
    fig.update_layout(
        title="Agent Workflow Timeline",
        xaxis_title="Time Progression",
        yaxis_title="Event Sequence",
        height=500,
        showlegend=False,
        yaxis=dict(tickmode='array', tickvals=list(range(len(authors))), ticktext=[f"Event {i+1}" for i in range(len(authors))])
    )
    
    return fig

def create_content_analysis_chart(summary_df):
    """Create content analysis visualization"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Content Length by Agent', 'Grounding Sources Distribution', 
                       'Search Queries by Agent', 'Event Processing Flow'),
        specs=[[{"type": "bar"}, {"type": "pie"}],
               [{"type": "bar"}, {"type": "scatter"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # Clean author names for better display
    clean_authors = [author.replace('_', ' ').title() for author in summary_df['Author']]
    
    # Content length by agent
    fig.add_trace(
        go.Bar(
            x=clean_authors,
            y=summary_df['Content_Length'],
            name="Content Length",
            marker_color='lightblue',
            text=summary_df['Content_Length'],
            textposition='auto'
        ),
        row=1, col=1
    )
    
    # Grounding sources pie chart
    sources_data = summary_df[summary_df['Grounding_Chunks_Count'] > 0]
    if not sources_data.empty:
        clean_source_authors = [author.replace('_', ' ').title() for author in sources_data['Author']]
        fig.add_trace(
            go.Pie(
                labels=clean_source_authors,
                values=sources_data['Grounding_Chunks_Count'],
                name="Grounding Sources",
                textinfo='label+value'
            ),
            row=1, col=2
        )
    
    # Search queries by agent
    queries_data = summary_df[summary_df['Search_Queries_Count'] > 0]
    if not queries_data.empty:
        clean_query_authors = [author.replace('_', ' ').title() for author in queries_data['Author']]
        fig.add_trace(
            go.Bar(
                x=clean_query_authors,
                y=queries_data['Search_Queries_Count'],
                name="Search Queries",
                marker_color='lightcoral',
                text=queries_data['Search_Queries_Count'],
                textposition='auto'
            ),
            row=2, col=1
        )
    
    # Event processing flow
    fig.add_trace(
        go.Scatter(
            x=clean_authors,
            y=summary_df['Content_Length'],
            mode='lines+markers',
            name="Content Flow",
            line=dict(color='purple', width=3),
            marker=dict(size=10),
            text=summary_df['Content_Length'],
            textposition='top center'
        ),
        row=2, col=2
    )
    
    # Update x-axis to show rotated labels for better readability
    fig.update_xaxes(tickangle=45, row=1, col=1)
    fig.update_xaxes(tickangle=45, row=2, col=1)
    fig.update_xaxes(tickangle=45, row=2, col=2)
    
    fig.update_layout(
        height=800, 
        showlegend=False,
        title_text="Content Analysis Dashboard",
        title_x=0.5,
        font=dict(size=10),
        margin=dict(l=50, r=50, t=80, b=100)
    )
    return fig

def display_agent_details(extractor):
    """Display detailed information about each agent"""
    events = extractor.extract_all_events()
    
    st.subheader("🤖 Agent Contributions Analysis")
    
    for i, event in enumerate(events):
        agent_name = event['author'].replace('_', ' ').title()
        with st.expander(f"Agent {i+1}: {agent_name}", expanded=False):
            
            # Agent metadata
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                st.markdown(f"**Role:** {event['role']}")
                st.markdown(f"**Agent:** {agent_name}")
            with col2:
                st.markdown(f"**Event ID:** `{event['id'][:16]}...`")
                if event['timestamp']:
                    timestamp = datetime.fromtimestamp(event['timestamp'])
                    st.markdown(f"**Time:** {timestamp.strftime('%H:%M:%S')}")
            with col3:
                # Metrics in a cleaner format
                met_col1, met_col2, met_col3 = st.columns(3)
                with met_col1:
                    st.metric("Content", f"{len(''.join(event['content_parts'])):,}")
                with met_col2:
                    st.metric("Sources", len(event['grounding_chunks']))
                with met_col3:
                    st.metric("Queries", len(event['search_queries']))
            
            st.markdown("---")
            
            # Full content display with better formatting
            if event['content_parts']:
                st.markdown("### 📄 **Full Content Output**")
                full_content = '\n\n'.join(event['content_parts'])
                formatted_content = (
                full_content
                .replace('<', '&lt;')   # escape HTML brackets properly
                .replace('>', '&gt;')
                .replace("\n", "<br>")  # replace actual newlines with <br>
                )
                
                # Enhanced content display with better styling
                st.markdown(f"""
                <div style="
                    max-height: 500px; 
                    overflow-y: auto; 
                    padding: 1.5rem; 
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    border: 2px solid #dee2e6; 
                    border-radius: 12px;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    font-size: 14px;
                    line-height: 1.8;
                    color: #212529;
                    box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
                    margin: 1rem 0;
                ">
                    {formatted_content}
                </div>
                """, unsafe_allow_html=True)
                
                # Copy and expand buttons
                button_col1, button_col2 = st.columns([1, 1])
                with button_col1:
                    if st.button(f"📋 Copy to Clipboard", key=f"copy_{i}"):
                        st.text_area("Content (select all to copy):", full_content, height=200, key=f"copy_area_{i}")
                
                with button_col2:
                    if st.button(f"🔍 View in Modal", key=f"modal_{i}"):
                        st.info("Content displayed above in scrollable format")
            
            # Additional details in columns
            if event['grounding_chunks'] or event['search_queries']:
                st.markdown("### 🔗 **Research Sources & Queries**")
                detail_col1, detail_col2 = st.columns(2)
                
                with detail_col1:
                    if event['grounding_chunks']:
                        st.markdown("**📚 Grounding Sources:**")
                        for idx, chunk in enumerate(event['grounding_chunks'][:5]):
                            st.markdown(f"""
                            <div style="
                                background: #e3f2fd; 
                                padding: 0.5rem; 
                                margin: 0.3rem 0; 
                                border-radius: 8px;
                                border-left: 4px solid #1976d2;
                                font-size: 12px;
                            ">
                                <strong>{chunk['domain']}</strong><br>
                                <small>{chunk['title'][:50]}...</small>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        if len(event['grounding_chunks']) > 5:
                            st.caption(f"... and {len(event['grounding_chunks']) - 5} more sources")
                
                with detail_col2:
                    if event['search_queries']:
                        st.markdown("**🔍 Search Queries Used:**")
                        for idx, query in enumerate(event['search_queries']):
                            st.markdown(f"""
                            <div style="
                                background: #fff3e0; 
                                padding: 0.5rem; 
                                margin: 0.3rem 0; 
                                border-radius: 8px;
                                border-left: 4px solid #f57c00;
                                font-size: 12px;
                            ">
                                <strong>Query {idx+1}:</strong> {query}
                            </div>
                            """, unsafe_allow_html=True)

def display_source_analysis(extractor):
    """Display source analysis"""
    st.subheader("📚 Source Analysis")
    
    sources = extractor.get_grounding_sources()
    events = extractor.extract_all_events()
    
    # Count source usage
    source_usage = {}
    for event in events:
        for chunk in event['grounding_chunks']:
            domain = chunk['domain']
            if domain:
                source_usage[domain] = source_usage.get(domain, 0) + 1
    
    if source_usage:
        # Create source usage chart
        source_df = pd.DataFrame(list(source_usage.items()), columns=['Source', 'Usage_Count'])
        source_df = source_df.sort_values('Usage_Count', ascending=False).head(15)
        
        fig = px.bar(
            source_df, 
            x='Usage_Count', 
            y='Source', 
            orientation='h',
            title="Top 15 Most Referenced Sources",
            color='Usage_Count',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Source categories
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📈 Source Statistics:**")
            st.write(f"• Total unique sources: **{len(sources)}**")
            st.write(f"• Most referenced: **{source_df.iloc[0]['Source']}** ({source_df.iloc[0]['Usage_Count']} times)")
            st.write(f"• Average references per source: **{sum(source_usage.values()) / len(source_usage):.1f}**")
        
        with col2:
            # Categorize sources
            categories = {
                'Academic/Research': ['edu', 'org', 'ac.'],
                'Commercial': ['com'],
                'Technology': ['io', 'ai', 'tech'],
                'News/Media': ['news', 'medium', 'forbes']
            }
            
            source_categories = {'Other': 0}
            for source in sources:
                categorized = False
                for category, keywords in categories.items():
                    if any(keyword in source.lower() for keyword in keywords):
                        source_categories[category] = source_categories.get(category, 0) + 1
                        categorized = True
                        break
                if not categorized:
                    source_categories['Other'] += 1
            
            fig_pie = px.pie(
                values=list(source_categories.values()),
                names=list(source_categories.keys()),
                title="Source Categories"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

def main():
    """Main dashboard function"""
    setup_page_config()
    load_custom_css()
    
    # Header
    st.markdown('<h1 class="main-header">PolyMind AI Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### Multi-Agent Conversation Analysis of PolyMind AI")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload your JSON file", 
        type=['json'],
        help="Upload the session output of your google cloud adk agents JSON file containing event data"
    )
    
    if uploaded_file is not None:
        try:
            # Load data
            json_data = json.load(uploaded_file)
            extractor = Event_Extractor(json_data=json_data)
            summary_df = extractor.get_event_summary()
            
            # Success message
            st.success(f"✅ Successfully loaded {len(summary_df)} events from the file!")
            
            # Metrics Overview
            st.markdown("---")
            st.subheader("📊 Key Metrics")
            create_metrics_overview(summary_df)
            
            # Main visualizations
            st.markdown("---")
            col1, col2 = st.columns([1, 1])
            
            with col1:
                workflow_chart = create_agent_workflow_chart(summary_df)
                st.plotly_chart(workflow_chart, use_container_width=True)
            
            with col2:
                content_chart = create_content_analysis_chart(summary_df)
                st.plotly_chart(content_chart, use_container_width=True)
            
            # Detailed analysis tabs
            st.markdown("---")
            tab1, tab2, tab3, tab4 = st.tabs(["🤖 Agent Details", "📚 Source Analysis", "📋 Event Summary", "💾 Raw Data"])
            
            with tab1:
                display_agent_details(extractor)
            
            with tab2:
                display_source_analysis(extractor)
            
            with tab3:
                st.subheader("Event Summary Table")
                st.dataframe(
                    summary_df.style.format({
                        'Content_Length': '{:,}',
                        'Timestamp': lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')
                    }),
                    use_container_width=True
                )
                
                # Download button
                csv = summary_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Summary as CSV",
                    data=csv,
                    file_name="assessment_platform_summary.csv",
                    mime="text/csv"
                )
            
            with tab4:
                st.subheader("Raw Event Data")
                events = extractor.extract_all_events()
                st.json(events[0] if events else {}, expanded=False)
                
                if st.button("🔄 Show All Raw Data"):
                    st.json(events)
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("Please ensure your JSON file has the correct format with an 'events' array.")
    
    else:
        # Show sample data structure
        st.info("👆 Please upload your JSON file to begin analysis")
        
        

if __name__ == "__main__":
    main()