"""
NBA Player Efficiency Analysis — Interactive Dashboard

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

EXPORTS = Path(__file__).parent / "data" / "exports"

st.set_page_config(
    page_title="NBA Player Efficiency Analysis",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Data loading (cached)
# ---------------------------------------------------------------------------

@st.cache_data
def load_shots():
    return pd.read_csv(EXPORTS / "master_shot_chart.csv")

@st.cache_data
def load_game_logs():
    df = pd.read_csv(EXPORTS / "player_game_logs.csv")
    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"], errors="coerce")
    return df

@st.cache_data
def load_zone_stats():
    return pd.read_csv(EXPORTS / "all_players_zone_stats.csv")

@st.cache_data
def load_grid():
    return pd.read_csv(EXPORTS / "all_players_grid_heatmap.csv")

@st.cache_data
def load_yoy():
    return pd.read_csv(EXPORTS / "player_year_over_year.csv")

@st.cache_data
def load_era_trends():
    return pd.read_csv(EXPORTS / "era_shooting_trends.csv")

@st.cache_data
def load_player_era():
    return pd.read_csv(EXPORTS / "player_era_breakdown.csv")

@st.cache_data
def load_league_stats():
    return pd.read_csv(EXPORTS / "league_player_stats.csv")

@st.cache_data
def load_team_stats():
    return pd.read_csv(EXPORTS / "team_stats_by_season.csv")

@st.cache_data
def load_career_stats():
    return pd.read_csv(EXPORTS / "career_stats.csv")


# ---------------------------------------------------------------------------
# Court drawing helper
# ---------------------------------------------------------------------------

def draw_court(fig, line_color="gray", line_width=1):
    """Add NBA half-court lines to a plotly figure."""
    shapes = []

    # Hoop
    shapes.append(dict(type="circle", x0=-7.5, y0=-7.5, x1=7.5, y1=7.5,
                       line=dict(color=line_color, width=line_width)))
    # Backboard
    shapes.append(dict(type="line", x0=-30, y0=-7.5, x1=30, y1=-7.5,
                       line=dict(color=line_color, width=line_width)))
    # Outer paint
    shapes.append(dict(type="rect", x0=-80, y0=-47.5, x1=80, y1=142.5,
                       line=dict(color=line_color, width=line_width)))
    # Inner paint
    shapes.append(dict(type="rect", x0=-60, y0=-47.5, x1=60, y1=142.5,
                       line=dict(color=line_color, width=line_width)))
    # Free throw circle
    shapes.append(dict(type="circle", x0=-60, y0=77.5, x1=60, y1=197.5,
                       line=dict(color=line_color, width=line_width)))
    # Restricted area
    shapes.append(dict(type="circle", x0=-40, y0=-40, x1=40, y1=40,
                       line=dict(color=line_color, width=line_width)))
    # Three-point line (arc portion)
    three_pts = []
    for angle in np.linspace(np.radians(22), np.radians(158), 100):
        x = 237.5 * np.cos(angle)
        y = 237.5 * np.sin(angle) - 47.5 + 47.5
        three_pts.append((x, y))
    x3 = [p[0] for p in three_pts]
    y3 = [p[1] for p in three_pts]
    fig.add_trace(go.Scatter(x=x3, y=y3, mode="lines",
                             line=dict(color=line_color, width=line_width),
                             showlegend=False, hoverinfo="skip"))
    # Three-point corners
    shapes.append(dict(type="line", x0=-220, y0=-47.5, x1=-220, y1=92.5 - 47.5,
                       line=dict(color=line_color, width=line_width)))
    shapes.append(dict(type="line", x0=220, y0=-47.5, x1=220, y1=92.5 - 47.5,
                       line=dict(color=line_color, width=line_width)))
    # Baseline
    shapes.append(dict(type="line", x0=-250, y0=-47.5, x1=250, y1=-47.5,
                       line=dict(color=line_color, width=line_width)))

    fig.update_layout(shapes=shapes)
    return fig


# ---------------------------------------------------------------------------
# Page: Shot Chart
# ---------------------------------------------------------------------------

def page_shot_chart():
    st.header("Shot Chart Explorer")

    shots = load_shots()
    players = sorted(shots["PLAYER_NAME_LABEL"].unique())

    col1, col2 = st.columns([1, 1])
    with col1:
        player = st.selectbox("Select Player", players, key="sc_player")
    with col2:
        shot_result = st.selectbox("Filter", ["All Shots", "Made Only", "Missed Only"], key="sc_filter")

    df = shots[shots["PLAYER_NAME_LABEL"] == player].copy()

    if shot_result == "Made Only":
        df = df[df["SHOT_MADE_FLAG"] == 1]
    elif shot_result == "Missed Only":
        df = df[df["SHOT_MADE_FLAG"] == 0]

    # Stats summary
    total = len(df) if shot_result == "All Shots" else len(shots[shots["PLAYER_NAME_LABEL"] == player])
    made = df["SHOT_MADE_FLAG"].sum() if shot_result == "All Shots" else len(df)
    fg_pct = (shots[shots["PLAYER_NAME_LABEL"] == player]["SHOT_MADE_FLAG"].mean() * 100)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Shots", f"{len(shots[shots['PLAYER_NAME_LABEL'] == player]):,}")
    c2.metric("FG%", f"{fg_pct:.1f}%")
    c3.metric("Avg Distance", f"{shots[shots['PLAYER_NAME_LABEL'] == player]['CALC_DISTANCE_FT'].mean():.1f} ft")
    c4.metric("Showing", f"{len(df):,} shots")

    # Shot chart scatter
    fig = go.Figure()

    color_map = df["RESULT"].map({"Made": "#2ecc71", "Missed": "#e74c3c"}).fillna("#95a5a6")

    fig.add_trace(go.Scatter(
        x=df["LOC_X"], y=df["LOC_Y"],
        mode="markers",
        marker=dict(size=4, color=color_map, opacity=0.5),
        text=df.apply(lambda r: f"{r.get('ACTION_TYPE', '')}<br>{r.get('SHOT_ZONE_BASIC', '')}<br>{r.get('RESULT', '')}", axis=1),
        hoverinfo="text",
        showlegend=False,
    ))

    fig = draw_court(fig)
    fig.update_layout(
        xaxis=dict(range=[-250, 250], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[-50, 420], showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x"),
        plot_bgcolor="white",
        height=550,
        margin=dict(l=20, r=20, t=40, b=20),
        title=f"{player} — Shot Chart",
    )
    st.plotly_chart(fig, width="stretch")

    # Zone breakdown
    st.subheader("Shooting by Zone")
    zone_stats = load_zone_stats()
    pz = zone_stats[zone_stats["PLAYER"] == player].sort_values("FGA", ascending=False)
    if not pz.empty:
        fig_zone = px.bar(
            pz, x="SHOT_ZONE_BASIC", y="FGA", color="FG_PCT",
            color_continuous_scale="RdYlGn", range_color=[0.2, 0.7],
            text="FG_PCT", hover_data=["FGM", "FGA"],
        )
        fig_zone.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        fig_zone.update_layout(height=350, xaxis_title="", yaxis_title="Field Goal Attempts")
        st.plotly_chart(fig_zone, width="stretch")


# ---------------------------------------------------------------------------
# Page: Heatmap
# ---------------------------------------------------------------------------

def page_heatmap():
    st.header("Shooting Efficiency Heatmap")

    grid = load_grid()
    players = sorted(grid["PLAYER"].unique())
    player = st.selectbox("Select Player", players, key="hm_player")

    df = grid[grid["PLAYER"] == player].copy()
    df = df[df["FGA"] >= 3]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["grid_x"], y=df["grid_y"],
        mode="markers",
        marker=dict(
            size=df["FGA"].clip(upper=50) * 0.8 + 4,
            color=df["FG_PCT"],
            colorscale="RdYlGn",
            cmin=0.2, cmax=0.7,
            colorbar=dict(title="FG%"),
            opacity=0.75,
            line=dict(width=0.5, color="gray"),
        ),
        text=df.apply(lambda r: f"FG%: {r['FG_PCT']:.1%}<br>FGA: {int(r['FGA'])}<br>FGM: {int(r['FGM'])}", axis=1),
        hoverinfo="text",
        showlegend=False,
    ))

    fig = draw_court(fig)
    fig.update_layout(
        xaxis=dict(range=[-250, 250], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[-50, 420], showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x"),
        plot_bgcolor="white",
        height=600,
        margin=dict(l=20, r=20, t=40, b=20),
        title=f"{player} — Efficiency Heatmap (bubble size = volume)",
    )
    st.plotly_chart(fig, width="stretch")

    st.caption("Green = high efficiency, Red = low efficiency. Bubble size represents shot volume. Zones with fewer than 3 attempts are hidden.")


# ---------------------------------------------------------------------------
# Page: Player Comparison
# ---------------------------------------------------------------------------

def page_comparison():
    st.header("Player Comparison")

    shots = load_shots()
    players = sorted(shots["PLAYER_NAME_LABEL"].unique())

    col1, col2 = st.columns(2)
    with col1:
        p1 = st.selectbox("Player 1", players, index=players.index("Stephen Curry") if "Stephen Curry" in players else 0, key="cmp_p1")
    with col2:
        p2 = st.selectbox("Player 2", players, index=players.index("LeBron James") if "LeBron James" in players else 1, key="cmp_p2")

    df1 = shots[shots["PLAYER_NAME_LABEL"] == p1]
    df2 = shots[shots["PLAYER_NAME_LABEL"] == p2]

    # Side-by-side shot charts
    fig = make_subplots(rows=1, cols=2, subplot_titles=[p1, p2],
                        horizontal_spacing=0.05)

    for i, (df, name) in enumerate([(df1, p1), (df2, p2)], 1):
        colors = df["RESULT"].map({"Made": "#2ecc71", "Missed": "#e74c3c"}).fillna("#95a5a6")
        fig.add_trace(go.Scatter(
            x=df["LOC_X"], y=df["LOC_Y"], mode="markers",
            marker=dict(size=3, color=colors, opacity=0.5),
            showlegend=False, hoverinfo="skip",
        ), row=1, col=i)

    fig.update_xaxes(range=[-250, 250], showgrid=False, zeroline=False, showticklabels=False)
    fig.update_yaxes(range=[-50, 420], showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x")
    fig.update_layout(height=500, plot_bgcolor="white", margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig, width="stretch")

    # Stats comparison table
    st.subheader("Stats Comparison")

    def player_stats(df, name):
        return {
            "Player": name,
            "Total Shots": len(df),
            "FG%": f"{df['SHOT_MADE_FLAG'].mean():.1%}" if len(df) > 0 else "N/A",
            "Avg Distance (ft)": f"{df['CALC_DISTANCE_FT'].mean():.1f}" if len(df) > 0 else "N/A",
            "3PT Shots": len(df[df["SHOT_TYPE"] == "3PT Field Goal"]) if "SHOT_TYPE" in df.columns else "N/A",
            "2PT Shots": len(df[df["SHOT_TYPE"] == "2PT Field Goal"]) if "SHOT_TYPE" in df.columns else "N/A",
        }

    stats_df = pd.DataFrame([player_stats(df1, p1), player_stats(df2, p2)])
    st.dataframe(stats_df.set_index("Player"), width="stretch")

    # Zone comparison
    st.subheader("Zone Efficiency Comparison")
    zones = load_zone_stats()
    z1 = zones[zones["PLAYER"] == p1].copy()
    z2 = zones[zones["PLAYER"] == p2].copy()

    if not z1.empty and not z2.empty:
        z1["Player"] = p1
        z2["Player"] = p2
        zc = pd.concat([z1, z2])
        fig_z = px.bar(
            zc, x="SHOT_ZONE_BASIC", y="FG_PCT", color="Player",
            barmode="group", text="FG_PCT",
            color_discrete_sequence=["#3498db", "#e74c3c"],
        )
        fig_z.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        fig_z.update_layout(height=400, yaxis_title="FG%", xaxis_title="")
        st.plotly_chart(fig_z, width="stretch")


# ---------------------------------------------------------------------------
# Page: Game Log Trends
# ---------------------------------------------------------------------------

def page_game_logs():
    st.header("Game Log Trends")

    logs = load_game_logs()
    players = sorted(logs["PLAYER_NAME_LABEL"].unique())
    player = st.selectbox("Select Player", players, key="gl_player")

    df = logs[logs["PLAYER_NAME_LABEL"] == player].sort_values("GAME_DATE")

    if df.empty:
        st.warning("No game log data for this player.")
        return

    # Stat selector
    stat = st.selectbox("Stat", ["PTS", "AST", "REB", "GAME_SCORE", "FG_PCT", "PLUS_MINUS", "FG3M"], key="gl_stat")

    # Summary metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Games", f"{len(df):,}")
    c2.metric(f"Avg {stat}", f"{df[stat].mean():.1f}" if stat in df.columns else "N/A")
    c3.metric(f"Max {stat}", f"{df[stat].max():.0f}" if stat in df.columns else "N/A")
    c4.metric("Win%", f"{(df['WL'] == 'W').mean():.1%}" if "WL" in df.columns else "N/A")

    if stat not in df.columns:
        st.warning(f"Column {stat} not available.")
        return

    # Game-by-game line chart with rolling average
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["GAME_DATE"], y=df[stat],
        mode="markers", name=stat,
        marker=dict(size=3, opacity=0.3, color="#3498db"),
    ))

    roll_col = f"{stat}_ROLL10"
    if roll_col in df.columns:
        fig.add_trace(go.Scatter(
            x=df["GAME_DATE"], y=df[roll_col],
            mode="lines", name="10-Game Avg",
            line=dict(width=2.5, color="#e74c3c"),
        ))

    fig.update_layout(
        height=400, xaxis_title="Date", yaxis_title=stat,
        title=f"{player} — {stat} Over Time",
        hovermode="x unified",
    )
    st.plotly_chart(fig, width="stretch")

    # Season averages
    st.subheader("Season Averages")
    if "SEASON" in df.columns:
        season_avg = df.groupby("SEASON").agg(
            GP=("PTS", "count"),
            PPG=("PTS", "mean"),
            APG=("AST", "mean"),
            RPG=("REB", "mean"),
            FG_PCT=("FG_PCT", "mean"),
            PLUS_MINUS=("PLUS_MINUS", "mean"),
        ).round(1).reset_index()
        season_avg.columns = ["Season", "GP", "PPG", "APG", "RPG", "FG%", "+/-"]
        st.dataframe(season_avg, width="stretch", hide_index=True)


# ---------------------------------------------------------------------------
# Page: Era Analysis
# ---------------------------------------------------------------------------

def page_era_analysis():
    st.header("Era Analysis — How Shooting Has Evolved")

    era_trends = load_era_trends()
    player_era = load_player_era()

    # Overall era trends
    st.subheader("League-Wide Shooting Trends by Era")

    era_order = [
        "Pre-Three-Point", "Early 2000s", "Mid 2000s",
        "Early 2010s", "Three-Point Revolution", "Modern Era",
    ]
    era_trends["ERA"] = pd.Categorical(era_trends["ERA"], categories=era_order, ordered=True)
    era_trends = era_trends.sort_values("ERA")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            era_trends, x="ERA", y="FG_PCT", text="FG_PCT",
            color="FG_PCT", color_continuous_scale="Blues",
        )
        fig.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        fig.update_layout(height=400, xaxis_title="", yaxis_title="FG%", title="Field Goal % by Era",
                          showlegend=False)
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.bar(
            era_trends, x="ERA", y="AVG_DISTANCE", text="AVG_DISTANCE",
            color="AVG_DISTANCE", color_continuous_scale="Oranges",
        )
        fig.update_traces(texttemplate="%{text:.1f} ft", textposition="outside")
        fig.update_layout(height=400, xaxis_title="", yaxis_title="Avg Shot Distance (ft)",
                          title="Average Shot Distance by Era", showlegend=False)
        st.plotly_chart(fig, width="stretch")

    # Per-player era breakdown
    st.subheader("Player Efficiency Across Eras")

    players = sorted(player_era["PLAYER_NAME_LABEL"].unique())
    selected = st.multiselect("Select Players", players, default=players[:4], key="era_players")

    if selected:
        filtered = player_era[player_era["PLAYER_NAME_LABEL"].isin(selected)]
        fig = px.bar(
            filtered, x="ERA", y="FG_PCT", color="PLAYER_NAME_LABEL",
            barmode="group", text="FG_PCT",
            category_orders={"ERA": era_order},
        )
        fig.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        fig.update_layout(height=450, xaxis_title="", yaxis_title="FG%",
                          legend_title="Player")
        st.plotly_chart(fig, width="stretch")

        # Volume table
        st.subheader("Shot Volume by Era")
        pivot = filtered.pivot_table(index="PLAYER_NAME_LABEL", columns="ERA",
                                     values="FGA", aggfunc="sum").fillna(0).astype(int)
        pivot = pivot.reindex(columns=[e for e in era_order if e in pivot.columns])
        st.dataframe(pivot, width="stretch")


# ---------------------------------------------------------------------------
# Page: Career Stats
# ---------------------------------------------------------------------------

def page_career_stats():
    st.header("Career Season Stats")

    yoy = load_yoy()
    players = sorted(yoy["PLAYER_NAME_LABEL"].unique())
    player = st.selectbox("Select Player", players, key="cs_player")

    df = yoy[yoy["PLAYER_NAME_LABEL"] == player].copy()

    if df.empty:
        st.warning("No year-over-year data for this player.")
        return

    # Key stats over career
    stat_cols = ["GP", "PTS", "AST", "REB", "FG_PCT", "FG3_PCT", "FT_PCT", "STL", "BLK", "TOV"]
    available = [c for c in stat_cols if c in df.columns]

    if "GROUP_VALUE" in df.columns:
        display = df[["GROUP_VALUE"] + available].copy()
        display = display.rename(columns={"GROUP_VALUE": "Season"})
        display = display.round(1)
        st.dataframe(display, width="stretch", hide_index=True)

    # Career trajectory chart
    st.subheader("Career Trajectory")
    stat = st.selectbox("Stat to Plot", ["PTS", "AST", "REB", "FG_PCT", "FG3_PCT", "TS_PCT", "EFG_PCT"], key="cs_stat")

    if stat in df.columns and "GROUP_VALUE" in df.columns:
        fig = px.line(
            df, x="GROUP_VALUE", y=stat,
            markers=True, text=stat,
        )
        fig.update_traces(texttemplate="%{text:.1f}", textposition="top center")
        fig.update_layout(
            height=400, xaxis_title="Season", yaxis_title=stat,
            title=f"{player} — {stat} by Season",
        )
        st.plotly_chart(fig, width="stretch")

    # Advanced metrics
    if any(c in df.columns for c in ["TS_PCT", "EFG_PCT", "THREE_RATE"]):
        st.subheader("Advanced Efficiency Metrics")
        adv_cols = [c for c in ["TS_PCT", "EFG_PCT", "THREE_RATE", "AST_TOV"] if c in df.columns]
        if "GROUP_VALUE" in df.columns and adv_cols:
            adv = df[["GROUP_VALUE"] + adv_cols].melt(id_vars="GROUP_VALUE", var_name="Metric", value_name="Value")
            fig = px.line(adv, x="GROUP_VALUE", y="Value", color="Metric", markers=True)
            fig.update_layout(height=400, xaxis_title="Season", yaxis_title="Value")
            st.plotly_chart(fig, width="stretch")


# ---------------------------------------------------------------------------
# Page: League Overview
# ---------------------------------------------------------------------------

def page_league():
    st.header("League Overview")

    league = load_league_stats()
    team_stats = load_team_stats()

    if "SEASON" in league.columns:
        seasons = sorted(league["SEASON"].unique(), reverse=True)
        season = st.selectbox("Season", seasons, key="lg_season")
        df = league[league["SEASON"] == season].copy()
    else:
        df = league.copy()
        season = "All"

    if df.empty:
        st.warning("No league data for this season.")
        return

    # Top scorers
    st.subheader(f"Top 15 Scorers — {season}")
    if "PTS" in df.columns:
        top = df.nlargest(15, "PTS")[["PLAYER_NAME", "TEAM_ABBREVIATION", "GP", "PTS", "AST", "REB", "FG_PCT", "FG3_PCT"]].copy()
        top = top.round(1)
        st.dataframe(top, width="stretch", hide_index=True)

    # Scoring distribution
    if "PTS" in df.columns:
        st.subheader("Scoring Distribution")
        fig = px.histogram(df[df["GP"] >= 20], x="PTS", nbins=30,
                           labels={"PTS": "Points Per Game"},
                           title=f"PPG Distribution (min 20 GP) — {season}")
        fig.update_layout(height=350)
        st.plotly_chart(fig, width="stretch")

    # Team stats
    st.subheader(f"Team Stats — {season}")
    if "SEASON" in team_stats.columns:
        ts = team_stats[team_stats["SEASON"] == season].copy()
    else:
        ts = team_stats.copy()

    if not ts.empty:
        display_cols = ["TEAM_NAME", "W", "L", "W_PCT", "PTS", "FG_PCT", "FG3_PCT", "REB", "AST"]
        available = [c for c in display_cols if c in ts.columns]
        st.dataframe(ts[available].sort_values("W_PCT", ascending=False).round(3),
                     width="stretch", hide_index=True)

    # 3PT evolution across seasons
    if "SEASON" in team_stats.columns and "FG3A" in team_stats.columns and "FGA" in team_stats.columns:
        st.subheader("3-Point Revolution: Team 3PA Trend")
        team_avg = team_stats.groupby("SEASON").agg(
            AVG_FG3A=("FG3A", "mean"),
            AVG_FGA=("FGA", "mean"),
        ).reset_index()
        team_avg["THREE_RATE"] = (team_avg["AVG_FG3A"] / team_avg["AVG_FGA"] * 100).round(1)

        fig = px.line(team_avg, x="SEASON", y="THREE_RATE", markers=True,
                      text="THREE_RATE", title="Average Team 3-Point Attempt Rate by Season")
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="top center")
        fig.update_layout(height=400, xaxis_title="Season", yaxis_title="3PA as % of FGA")
        st.plotly_chart(fig, width="stretch")


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

PAGES = {
    "🏀 Shot Chart": page_shot_chart,
    "🔥 Heatmap": page_heatmap,
    "⚔️ Player Comparison": page_comparison,
    "📈 Game Log Trends": page_game_logs,
    "📊 Career Stats": page_career_stats,
    "🕰️ Era Analysis": page_era_analysis,
    "🏆 League Overview": page_league,
}

st.sidebar.title("NBA Player Efficiency")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", list(PAGES.keys()))
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Data**: nba_api (1996–2025)  \n"
    "**Players**: 10 across eras  \n"
    "**Shots**: 79,763 records  \n"
    "**Games**: 8,076 game logs"
)

PAGES[page]()
