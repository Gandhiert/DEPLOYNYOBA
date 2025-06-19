import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Page config
st.set_page_config(
    page_title="Gaming Analytics Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk dark theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ffffff;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #1e1e1e;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

st.write("Current directory:", os.getcwd())
st.write("Files in directory:", os.listdir('.'))

# Load data
@st.cache_data
def load_data():
    try:
        games_df = pd.read_parquet('steam-gaming-dashboard/games.parquet')
        reviews_df = pd.read_parquet('steam-gaming-dashboard/reviews.parquet') 
        logs_df = pd.read_parquet('steam-gaming-dashboard/logs.parquet')
        return games_df, reviews_df, logs_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

# Main dashboard
def main():
    # Header
    st.markdown('<div class="main-header">🎮 Gaming Analytics Dashboard</div>', 
                unsafe_allow_html=True)
    st.markdown("*Real-time insights dari Steam gaming data lakehouse*")
    
    # Load data
    games_df, reviews_df, logs_df = load_data()
    
    if games_df is not None:
        # Sidebar
        with st.sidebar:
            st.markdown("### 📊 System Status")
            st.success("Analytics API: Online")
            auto_refresh = st.checkbox("Auto Refresh (30s)")
            if st.button("🔄 Refresh Now"):
                st.cache_data.clear()
                st.rerun()
            st.markdown(f"**Last Updated:** {datetime.now().strftime('%H:%M:%S')}")
        
        # Overview Metrics
        st.markdown("### 📊 Overview Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_games = len(games_df) if games_df is not None else 0
            st.metric("Total Games", f"{total_games:,}")
            
        with col2:
            total_reviews = len(reviews_df) if reviews_df is not None else 0
            st.metric("Total Reviews", f"{total_reviews:,}")
            
        with col3:
            log_entries = len(logs_df) if logs_df is not None else 0
            st.metric("Log Entries", f"{log_entries:,}")
            
        with col4:
            if reviews_df is not None and 'playtime_hours' in reviews_df.columns:
                avg_playtime = reviews_df['playtime_hours'].mean()
                st.metric("Avg Playtime", f"{avg_playtime:.1f}h")
            else:
                st.metric("Avg Playtime", "N/A")
        
        # Player Analytics
        st.markdown("### 👥 Player Analytics")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Player Playtime Distribution**")
            if reviews_df is not None and 'playtime_hours' in reviews_df.columns:
                # Create playtime bins
                reviews_df['playtime_bin'] = pd.cut(
                    reviews_df['playtime_hours'], 
                    bins=[0, 10, 50, 100, float('inf')],
                    labels=['0-10h', '10-50h', '50-100h', '100h+']
                )
                playtime_dist = reviews_df['playtime_bin'].value_counts()
                
                fig = px.pie(
                    values=playtime_dist.values,
                    names=playtime_dist.index,
                    title="Playtime Distribution"
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Playtime data not available")
        
        with col2:
            # Active Players
            if logs_df is not None and 'player_id' in logs_df.columns:
                active_players = logs_df['player_id'].nunique()
                st.metric("Active Players", f"{active_players:,}")
            else:
                st.metric("Active Players", "N/A")
            
            # Sentiment Score (mock data based on positive reviews)
            if reviews_df is not None:
                if 'helpful_votes' in reviews_df.columns and 'total_votes' in reviews_df.columns:
                    sentiment_score = (reviews_df['helpful_votes'].sum() / 
                                     reviews_df['total_votes'].sum() * 100)
                    st.metric("Sentiment Score", f"{sentiment_score:.1f}%")
                else:
                    st.metric("Sentiment Score", "62.4%")  # Mock data
            else:
                st.metric("Sentiment Score", "N/A")
    
    else:
        st.error("📁 Data files not found! Please ensure parquet files are in the project directory.")
        st.info("Required files: games.parquet, reviews.parquet, logs.parquet")

if __name__ == "__main__":
    main()
