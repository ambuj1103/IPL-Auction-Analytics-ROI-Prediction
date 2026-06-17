# 🏏 IPL Data Analysis & Power BI Dashboard
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Power Bi](https://img.shields.io/badge/power_bi-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Project Summary

An end-to-end Data Analytics project on the **Indian Premier League (IPL)** dataset (2008–2024), covering ball-by-ball delivery data and match-level records across 16 seasons.

This project demonstrates:

- Python-based data cleaning & feature engineering
- Team name standardization across franchise renames
- Star schema data modeling in Power BI
- DAX measures for KPI development
- Interactive 5-page dashboard storytelling

---

## 🧠 Business Problem

The goal was to answer:

- Which teams have dominated IPL across seasons?
- Does winning the toss actually help win the match?
- Who are the most impactful batters and bowlers in IPL history?
- How does run rate evolve across overs (powerplay vs death)?
- Which venues and cities host the most competitive matches?

---

## 🛠 Tech Stack

| Tool | Purpose |
|------|---------|
| Python (Pandas, NumPy) | Data cleaning, feature engineering & export |
| SQL | Data storage, querying & structured retrieval |
| Power BI | Dashboard development & visualization |
| DAX | KPI & aggregation measures |
| Data Modeling | Star schema implementation |
| Git + Git LFS | Version control for large dataset files |

---

## 🧹 Data Cleaning Highlights

- Parsed and standardized `date` and `season` columns (`"2007/08"` → `2008`)
- Replaced all `"NA"` strings with proper `NaN` values
- Coerced numeric columns (`result_margin`, `batsman_runs`, `is_wicket`, etc.)
- Engineered new features: `is_legal`, `is_four`, `is_six`, `season_year`
- Removed duplicate rows across both datasets
- Exported 12 analysis-ready CSVs for direct Power BI import

---

## 🏷️ Team Name Standardization

All historical franchise name variants were mapped to one canonical name to ensure consistent filtering across all 16 seasons:

| Old Name | Standardized Name |
|----------|-------------------|
| Delhi Daredevils | Delhi Capitals |
| Kings XI Punjab | Punjab Kings |
| Royal Challengers Bangalore | Royal Challengers Bengaluru |
| Deccan Chargers | Sunrisers Hyderabad |
| Rising Pune Supergiants | Rising Pune Supergiant |

---

## 🏗 Data Model Architecture

A star schema was implemented in Power BI for optimized cross-filtering and accurate aggregations.

**Central Fact Table:**
- `dim_matches`

**Supporting Tables:**
- `batting_scorecard`, `bowling_scorecard` — match-level player stats
- `batting_career`, `bowling_career` — career aggregates
- `season_stats`, `team_performance` — season & team level
- `toss_analysis`, `venue_stats`, `over_runrate` — contextual analysis
- `player_of_match`, `dismissal_types` — awards & dismissal breakdown

---

## 📈 Dashboard Structure (5 Pages)

### 🔹 1. Overview

- Total Matches, Teams, Players, Seasons (KPI Cards)
- Matches Per Season trend line
- All-Time Wins by Team
- Season Year slicer

📌 Purpose: High-level IPL history snapshot

---

### 🔹 2. Team Performance

- Win % by Team
- Wins vs Losses stacked bar
- Toss Decision Split (Bat vs Field)
- Toss Win → Match Win% card

📌 Key Insight:
> Teams winning the toss win the match only ~49% of the time — toss advantage is essentially a coin flip.

---

### 🔹 3. Batting Analysis

- Top 10 Run Scorers (table with avg, SR, 50s, 100s)
- Runs vs Strike Rate scatter plot
- Most Sixes in IPL history
- KPI Cards: Total Runs, Avg Strike Rate, Centuries, Fifties

📌 Key Insight:
> Mumbai Indians and CSK batters dominate both run-scoring and boundary-hitting charts.

---

### 🔹 4. Bowling Analysis

- Top Wicket Takers
- Best Economy Bowlers (min 10 matches)
- Dismissal Type Distribution donut
- KPI Cards: Total Wickets, Avg Economy

---

### 🔹 5. Match Insights

- Run Rate by Over (powerplay vs death over trend)
- Matches by Venue
- Top Player of the Match winners
- City-wise match distribution

📌 Key Insight:
> Run rate spikes sharply in overs 16–20, confirming death-over hitting as the decisive phase.

---

## 📊 Key DAX Measures

```DAX
Total Matches = COUNTROWS(dim_matches)

Total Seasons = DISTINCTCOUNT(dim_matches[season_year])

Total Teams = DISTINCTCOUNT(team_performance[team])

Total Players = DISTINCTCOUNT(batting_career[batter])

Total Wins = SUM(team_performance[wins])

Total Losses = SUM(team_performance[losses])

Avg Win% = AVERAGE(team_performance[win_pct])

Toss Win Match% = AVERAGE(toss_analysis[toss_win_match_pct])

Total Runs = SUM(batting_career[total_runs])

Avg Strike Rate = AVERAGE(batting_career[career_sr])

Total Wickets = SUM(bowling_career[total_wickets])

Avg Economy = AVERAGE(bowling_career[economy])
```

---

## ⚙️ How to Run

### 1. Clone the repo
```bash
git clone https://github.com/manas-shukla-101/End-to-End-IPL-Data-Analytics.git
cd End-to-End-IPL-Data-Analytics
```

### 2. Install dependencies
```bash
pip install pandas numpy
```

### 3. Place raw data files
Put `matches.csv` and `deliveries.csv` in the same directory as the script:
```
Python Script/
└── ipl_analysis.py
└── matches.csv       ← place here
└── deliveries.csv    ← place here
```

### 4. Run the cleaning script
```bash
cd "Python Script"
python ipl_analysis.py
```
This generates all 12 cleaned CSVs inside a `powerbi_tables/` folder.

### 5. Open Power BI
Open `IPL Dashboard/IPL_Dashboard.pbix` — all visuals load automatically from the `PowerBI Tables/` CSVs.

---

## 📌 Key Business Insights

- **Mumbai Indians** hold the most all-time wins in IPL history, followed by CSK and KKR
- Toss winning converts to match winning only **~49%** of the time
- **64%** of toss winners chose to field first across all seasons
- 2022 season had the most matches **(120)** due to expansion to 10 teams
- Death overs (16–20) show the sharpest run rate spike across all seasons
- A small set of players win the majority of Player of the Match awards (Pareto effect)

---

## 📂 Repository Structure

```
End-to-End-IPL-Data-Analytics/
│
├── Dashboard Screenshots/           # Preview images of all 5 dashboard pages
│   ├── 1_Overview.jpeg              
│   ├── 2_Team-Performance.jpeg             
│   ├── 3_Batting-Analysis.jpeg      
│   ├── 4_Bowling-Analysis.jpeg      
│   └── 5_Match-Insight.jpeg
│
├── IPL Dashboard/                   # Power BI Dashboard file
│   └── IPL_Dashboard.pbix           # 5-page interactive dashboard
│
├── PowerBI Tables/                  
│   ├── dim_matches.csv              
│   ├── season_stats.csv             
│   ├── team_performance.csv         
│   ├── toss_analysis.csv            
│   ├── batting_scorecard.csv        
│   ├── batting_career.csv           
│   ├── bowling_scorecard.csv        
│   ├── bowling_career.csv           
│   ├── over_runrate.csv             
│   ├── venue_stats.csv              
│   ├── player_of_match.csv          
│   └── dismissal_types.csv          
│
├── Python Script/                   # Data cleaning & export script
│   └── ipl_analysis.py              # Loads raw CSVs → cleans → exports PowerBI Tables
│
├── LICENSE
└── README.md
```

> ⚠️ Raw dataset (`matches.csv` & `deliveries.csv`) is not there in this repo due tp some technical reasons. You can download it by [clicking here](https://www.kaggle.com/datasets/patrickb1912/ipl-complete-dataset-20082020)

---

## 🎯 What This Project Demonstrates

✔ Python data cleaning & feature engineering at scale (260k+ rows)

✔ Team name standardization across franchise renames

✔ Star schema data modeling in Power BI

✔ DAX measure development for business KPIs

✔ Multi-page interactive dashboard design

✔ Insight storytelling from raw sports data

✔ Version control with Git LFS for large files

---

## 👥 Team

This project was built collaboratively:

| Contributor | GitHub | Role |
|-------------|--------|------|
| **Manas Shukla** | [@manas-shukla-101](https://github.com/manas-shukla-101) | Data Modeling, Power BI Dashboard, DAX Measures, Team Name Standardization, README |
| **Yashi Mishra** | [@yashimishra03](https://github.com/yashimishra03) | Python Data Cleaning, SQL Storage & Queries, Feature Engineering |

---

**Made with ❤️ by Manas Shukla & Yashi Mishra**

---

## 🌐 Socials:
[![Portfolio](https://img.shields.io/badge/Portfolio-Website-blue)](https://manas-shukla-portfolio.framer.website) [![Instagram](https://img.shields.io/badge/Instagram-%23E4405F.svg?logo=Instagram&logoColor=white)](https://instagram.com/manas_shukla_101) [![LinkedIn](https://img.shields.io/badge/LinkedIn-%230077B5.svg?logo=linkedin&logoColor=white)](https://linkedin.com/in/manas-shukla-006774370) [![email](https://img.shields.io/badge/Email-D14836?logo=gmail&logoColor=white)](mailto:shuklamanas8928@gmail.com)

---
