import pandas as pd
import numpy as np
import os

matches    = pd.read_csv("matches.csv")
deliveries = pd.read_csv("deliveries.csv")

print(f"Matches shape    : {matches.shape}")
print(f"Deliveries shape : {deliveries.shape}")

# TEAM NAME STANDARDIZATION MAP

TEAM_MAP = {
    # Kolkata Knight Riders
    "Kolkata Knight Riders"         : "Kolkata Knight Riders",

    # Royal Challengers (renamed 2023)
    "Royal Challengers Bangalore"   : "Royal Challengers Bengaluru",
    "Royal Challengers Bengaluru"   : "Royal Challengers Bengaluru",

    # Chennai Super Kings
    "Chennai Super Kings"           : "Chennai Super Kings",

    # Mumbai Indians
    "Mumbai Indians"                : "Mumbai Indians",

    # Kings XI Punjab (renamed 2021)
    "Kings XI Punjab"               : "Punjab Kings",
    "Punjab Kings"                  : "Punjab Kings",

    # Delhi franchise (renamed twice)
    "Delhi Daredevils"              : "Delhi Capitals",
    "Delhi Capitals"                : "Delhi Capitals",

    # Rajasthan Royals
    "Rajasthan Royals"              : "Rajasthan Royals",

    # Sunrisers Hyderabad / Deccan Chargers
    "Deccan Chargers"               : "Sunrisers Hyderabad",
    "Sunrisers Hyderabad"           : "Sunrisers Hyderabad",

    # Pune & Hyderabad franchises (defunct)
    "Pune Warriors"                 : "Pune Warriors",
    "Rising Pune Supergiant"        : "Rising Pune Supergiant",
    "Rising Pune Supergiants"       : "Rising Pune Supergiant",

    # Kochi (defunct)
    "Kochi Tuskers Kerala"          : "Kochi Tuskers Kerala",

    # Gujarat Titans & Lucknow (from 2022)
    "Gujarat Titans"                : "Gujarat Titans",
    "Lucknow Super Giants"          : "Lucknow Super Giants",
}

def standardize_teams(df, columns):
    """Replace team names in specified columns using TEAM_MAP."""
    for col in columns:
        if col in df.columns:
            df[col] = df[col].map(TEAM_MAP).fillna(df[col])  # keep unmapped as-is
    return df


# CLEAN MATCHES

m = matches.copy()

# Parse date
m["date"] = pd.to_datetime(m["date"], errors="coerce")
m["year"]  = m["date"].dt.year
m["month"] = m["date"].dt.month

# Standardize team columns
team_cols_m = ["team1", "team2", "toss_winner", "winner"]
m = standardize_teams(m, team_cols_m)

# Normalize season to 4-digit year  (e.g. "2007/08" → 2008)
def parse_season(s):
    s = str(s).strip()
    if "/" in s:
        return int(s.split("/")[0]) + 1   # "2007/08" → 2008
    return int(s)

m["season_year"] = m["season"].apply(parse_season)

# Fill missing/NA string values
m["city"]          = m["city"].replace("NA", np.nan).fillna("Unknown")
m["method"]        = m["method"].replace("NA", np.nan).fillna("Normal")
m["player_of_match"] = m["player_of_match"].replace("NA", np.nan).fillna("Unknown")

# result_margin: coerce to numeric
m["result_margin"] = pd.to_numeric(m["result_margin"], errors="coerce")

# super_over flag → bool
m["super_over"] = m["super_over"].map({"Y": True, "N": False})

# Drop fully-duplicate rows
m.drop_duplicates(inplace=True)

print(f"\n✅ Matches cleaned  : {m.shape}")



# CLEAN DELIVERIES

d = deliveries.copy()

# Standardize team columns
team_cols_d = ["batting_team", "bowling_team"]
d = standardize_teams(d, team_cols_d)

# Fill NA strings
for col in ["extras_type", "player_dismissed", "dismissal_kind", "fielder"]:
    if col in d.columns:
        d[col] = d[col].replace("NA", np.nan)

# Coerce numeric columns
for col in ["batsman_runs", "extra_runs", "total_runs", "is_wicket"]:
    d[col] = pd.to_numeric(d[col], errors="coerce").fillna(0).astype(int)

# Legal delivery flag (not wide or no-ball)
d["is_legal"] = ~d["extras_type"].isin(["wides", "noballs"])

# Boundary flag
d["is_four"] = (d["batsman_runs"] == 4).astype(int)
d["is_six"]  = (d["batsman_runs"] == 6).astype(int)

# Merge season info from matches
d = d.merge(m[["id", "season_year", "date"]], left_on="match_id", right_on="id", how="left")
d.drop(columns=["id"], inplace=True)

# Drop duplicates
d.drop_duplicates(inplace=True)

print(f"✅ Deliveries cleaned: {d.shape}")



# ANALYSIS  →  Power BI tables


os.makedirs("powerbi_tables", exist_ok=True)

# ── Match Summary (dim_matches) ──────
m.to_csv("powerbi_tables/dim_matches.csv", index=False)
print("  → dim_matches.csv")


# ── Season-level stats ───────────────
season_stats = (
    m.groupby("season_year")
     .agg(
         total_matches   = ("id",            "count"),
         unique_venues   = ("venue",         "nunique"),
         unique_cities   = ("city",          "nunique"),
         super_overs     = ("super_over",    "sum"),
     )
     .reset_index()
)
season_stats.to_csv("powerbi_tables/season_stats.csv", index=False)
print("  → season_stats.csv")


# ── Team performance per season ──────
team_wins = (
    m[m["winner"].notna()]
     .groupby(["season_year", "winner"])
     .size()
     .reset_index(name="wins")
     .rename(columns={"winner": "team"})
)

# matches played (each team appears as team1 or team2)
t1 = m[["season_year", "team1"]].rename(columns={"team1": "team"})
t2 = m[["season_year", "team2"]].rename(columns={"team2": "team"})
team_played = (
    pd.concat([t1, t2])
      .groupby(["season_year", "team"])
      .size()
      .reset_index(name="matches_played")
)

team_perf = team_played.merge(team_wins, on=["season_year", "team"], how="left")
team_perf["wins"]   = team_perf["wins"].fillna(0).astype(int)
team_perf["losses"] = team_perf["matches_played"] - team_perf["wins"]
team_perf["win_pct"] = (team_perf["wins"] / team_perf["matches_played"] * 100).round(2)
team_perf.to_csv("powerbi_tables/team_performance.csv", index=False)
print("  → team_performance.csv")


# ── Toss analysis ────────────────────
toss = m.copy()
toss["toss_won_match"] = (toss["toss_winner"] == toss["winner"]).astype(int)
toss_stats = (
    toss.groupby(["season_year", "toss_decision"])
        .agg(
            matches          = ("id",              "count"),
            toss_wins_match  = ("toss_won_match",  "sum"),
        )
        .reset_index()
)
toss_stats["toss_win_match_pct"] = (
    toss_stats["toss_wins_match"] / toss_stats["matches"] * 100
).round(2)
toss_stats.to_csv("powerbi_tables/toss_analysis.csv", index=False)
print("  → toss_analysis.csv")


# ── Batting scorecard (per batter per match) ──
batting = (
    d.groupby(["match_id", "season_year", "batting_team", "batter"])
     .agg(
         runs    = ("batsman_runs", "sum"),
         balls   = ("is_legal",     "sum"),
         fours   = ("is_four",      "sum"),
         sixes   = ("is_six",       "sum"),
     )
     .reset_index()
)
batting["strike_rate"] = (batting["runs"] / batting["balls"] * 100).replace([np.inf, -np.inf], 0).round(2)
batting.to_csv("powerbi_tables/batting_scorecard.csv", index=False)
print("  → batting_scorecard.csv")


# ── Batting aggregates (career) ──────
bat_career = (
    batting.groupby("batter")
           .agg(
               innings      = ("match_id",     "nunique"),
               total_runs   = ("runs",         "sum"),
               total_balls  = ("balls",        "sum"),
               total_fours  = ("fours",        "sum"),
               total_sixes  = ("sixes",        "sum"),
               highest_score= ("runs",         "max"),
               fifties      = ("runs",         lambda x: (x >= 50).sum()),
               hundreds     = ("runs",         lambda x: (x >= 100).sum()),
           )
           .reset_index()
)
bat_career["career_sr"] = (bat_career["total_runs"] / bat_career["total_balls"] * 100).round(2)
bat_career["avg"]       = (bat_career["total_runs"] / bat_career["innings"]).round(2)
bat_career.to_csv("powerbi_tables/batting_career.csv", index=False)
print("  → batting_career.csv")


# ── Bowling scorecard (per bowler per match) ──
bowling = (
    d.groupby(["match_id", "season_year", "bowling_team", "bowler"])
     .agg(
         legal_balls = ("is_legal",     "sum"),
         runs_given  = ("total_runs",   "sum"),
         wickets     = ("is_wicket",    "sum"),
         wides       = ("extras_type",  lambda x: (x == "wides").sum()),
         noballs     = ("extras_type",  lambda x: (x == "noballs").sum()),
     )
     .reset_index()
)
bowling["overs"]   = (bowling["legal_balls"] // 6) + (bowling["legal_balls"] % 6) / 10
bowling["economy"] = (bowling["runs_given"] / (bowling["legal_balls"] / 6)).round(2)
bowling.to_csv("powerbi_tables/bowling_scorecard.csv", index=False)
print("  → bowling_scorecard.csv")


# ── Bowling career aggregates ────────
bowl_career = (
    bowling.groupby("bowler")
           .agg(
               matches      = ("match_id",    "nunique"),
               total_balls  = ("legal_balls", "sum"),
               total_runs   = ("runs_given",  "sum"),
               total_wickets= ("wickets",     "sum"),
               best_wickets = ("wickets",     "max"),
           )
           .reset_index()
)
bowl_career["overs"]   = (bowl_career["total_balls"] // 6 + bowl_career["total_balls"] % 6 / 10).round(1)
bowl_career["economy"] = (bowl_career["total_runs"] / (bowl_career["total_balls"] / 6)).round(2)
bowl_career["avg"]     = (bowl_career["total_runs"] / bowl_career["total_wickets"].replace(0, np.nan)).round(2)
bowl_career["sr"]      = (bowl_career["total_balls"] / bowl_career["total_wickets"].replace(0, np.nan)).round(2)
bowl_career.to_csv("powerbi_tables/bowling_career.csv", index=False)
print("  → bowling_career.csv")


# ── Over-by-over run rate ─────────────
over_rr = (
    d.groupby(["season_year", "over"])
     .agg(
         total_runs   = ("total_runs",  "sum"),
         total_balls  = ("is_legal",    "sum"),
         total_wickets= ("is_wicket",   "sum"),
     )
     .reset_index()
)
over_rr["run_rate"] = (over_rr["total_runs"] / (over_rr["total_balls"] / 6)).round(2)
over_rr.to_csv("powerbi_tables/over_runrate.csv", index=False)
print("  → over_runrate.csv")


# ── Venue stats ───────────────────────
venue_stats = (
    m.groupby("venue")
     .agg(
         matches        = ("id",             "count"),
         avg_margin_runs= ("result_margin",  "mean"),
         city           = ("city",           "first"),
     )
     .reset_index()
)
venue_stats["avg_margin_runs"] = venue_stats["avg_margin_runs"].round(1)
venue_stats.to_csv("powerbi_tables/venue_stats.csv", index=False)
print("  → venue_stats.csv")


# ── Player of the Match frequency ─────
potm = (
    m[m["player_of_match"] != "Unknown"]
     .groupby("player_of_match")
     .size()
     .reset_index(name="potm_awards")
     .sort_values("potm_awards", ascending=False)
)
potm.to_csv("powerbi_tables/player_of_match.csv", index=False)
print("  → player_of_match.csv")


# ── Dismissal types distribution ──────
dismissals = (
    d[d["dismissal_kind"].notna()]
     .groupby(["season_year", "dismissal_kind"])
     .size()
     .reset_index(name="count")
)
dismissals.to_csv("powerbi_tables/dismissal_types.csv", index=False)
print("  → dismissal_types.csv")


print("\n✅ All Power BI tables exported to /powerbi_tables/")
print("\nFiles created:")
for f in sorted(os.listdir("powerbi_tables")):
    path = f"powerbi_tables/{f}"
    rows = pd.read_csv(path).shape[0]
    print(f"  {f:40s}  {rows:>7,} rows")
