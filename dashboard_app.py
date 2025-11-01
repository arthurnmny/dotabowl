import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_connection

st.set_page_config(page_title='Dotabowl 2025', layout='wide')

# Display header image
col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    st.image('assets/intl2.jpg', use_container_width=True)

st.title('Dotabowl 2025')

conn = get_connection()
df_matches = pd.read_sql_query('SELECT * FROM matches ORDER BY created_at DESC', conn)
df_players = pd.read_sql_query('SELECT * FROM players', conn)
df_stats = pd.read_sql_query('SELECT * FROM player_match_stats', conn)
conn.close()

st.header('Matches')
if df_matches.empty:
    st.info('No matches in DB yet')
else:
    # Display key match info
    for _, match in df_matches.iterrows():
        winner = "Radiant" if match['radiant_win'] else "Dire"
        st.write(f"**{match['match_id']}**: {winner} won - {match['description']}")
    
    # Show full matches table in expander
    with st.expander("Show full matches data"):
        st.dataframe(df_matches)

st.header('Player summary')
if df_stats.empty:
    st.info('No player stats yet')
else:
    df_group = df_stats.groupby('player_name').agg({
        'match_id':'count',
        'win':'sum', 
        'kills':'sum',
        'deaths':'sum',
        'assists':'sum',
        'net_worth':'sum'
    }).reset_index()
    
    # Rename columns for better display
    df_group.columns = ['Player', 'Matches', 'Wins', 'Kills', 'Deaths', 'Assists', 'Net Worth']
    
    # Sort by number of matches (descending)
    df_group = df_group.sort_values('Matches', ascending=False)
    
    # Display as table
    st.dataframe(df_group, width='stretch')

st.header('Team Performance')
if not df_stats.empty:
    team_stats = df_stats.groupby('team').agg({
        'kills': 'mean',
        'deaths': 'mean', 
        'assists': 'mean',
        'net_worth': 'mean',
        'win': 'mean'
    }).reset_index()
    team_stats['win_rate'] = team_stats['win'] * 100
    
    col1, col2 = st.columns(2)
    with col1:
        fig3 = px.bar(team_stats, x='team', y='win_rate', title='Win Rate by Team (%)')
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        fig4 = px.bar(team_stats, x='team', y='net_worth', title='Average Net Worth by Team')
        st.plotly_chart(fig4, use_container_width=True)

st.header('Player detail')
player_options = []
if not df_stats.empty:
    # Ensure df_group is defined
    df_group = df_stats.groupby('player_name').agg({
        'match_id':'count',
        'win':'sum', 
        'kills':'sum',
        'deaths':'sum',
        'assists':'sum',
        'net_worth':'sum'
    }).reset_index()
    df_group.columns = ['Player', 'Matches', 'Wins', 'Kills', 'Deaths', 'Assists', 'Net Worth']
    player_options = df_group['Player'].tolist()

player = st.selectbox('Select player', options=player_options)
if player:
    df_p = df_stats[df_stats['player_name']==player]
    st.write(f"**Player**: {player}")
    st.write(f"**Total Games**: {len(df_p)}")
    st.write(f"**Win Rate**: {df_p['win'].mean()*100:.1f}%")
    st.write(f"**Average KDA**: {df_p['kills'].mean():.1f}/{df_p['deaths'].mean():.1f}/{df_p['assists'].mean():.1f}")
    
    with st.expander("Show detailed stats"):
        st.dataframe(df_p)
    
    fig2 = px.line(df_p, x='match_id', y='kills', markers=True, title=f'Kills per Match for {player}')
    st.plotly_chart(fig2, use_container_width=True)


col1, col2 = st.columns([1, 1])
with col1:
    st.image('assets/collage/collage1.png', use_container_width=True)
with col2:
    st.image('assets/collage/collage2.png', use_container_width=True)

col1, col2 = st.columns([1, 1])
with col1:
    st.image('assets/collage/collage3.png', use_container_width=True)
with col2:
    st.image('assets/collage/collage4.png', use_container_width=True)
