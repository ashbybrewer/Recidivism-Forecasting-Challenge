#!/usr/bin/env python3
"""
Concentration of re-offending in the NIJ Recidivism Challenge cohort.
Reads the full dataset and reproduces every figure cited in the README's
Revised Findings, plus the two charts.

Usage:  python analysis/concentration_analysis.py
Data:   Data/NIJ_s_Recidivism_Challenge_Full_Dataset.csv
        (25,835 Georgia parolees released 2013-2015; NIJ/BJS, data.ojp.usdoj.gov ynf5-u8nk)

Method notes (read before quoting):
- "Prior arrest episodes" = Prior_Arrest_Episodes_Felony + Prior_Arrest_Episodes_Misd.
  Both fields are TOP-CODED ("6 or more", "10 or more" parsed as 6/10), so every
  concentration figure here is a conservative UNDERestimate.
- Outcome = Recidivism_Within_3years (new felony/misd arrest within 3 years).
  An arrest is not a conviction; parolees are also under heavier surveillance
  than the general public. Both caveats cut against over-reading any single row.
"""
import re
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAVY, RED, BRASS, INK = "#0b0f1a", "#d64541", "#f1d9a0", "#e8e3d8"

df = pd.read_csv("Data/NIJ_s_Recidivism_Challenge_Full_Dataset.csv")
df.columns = [c.strip("﻿") for c in df.columns]
rec = df["Recidivism_Within_3years"].astype(str).str.upper().eq("TRUE")

band_n = lambda s: int(m.group(1)) if (m := re.search(r"(\d+)", str(s))) else 0
priors = (df["Prior_Arrest_Episodes_Felony"].map(band_n)
          + df["Prior_Arrest_Episodes_Misd"].map(band_n))

print(f"cohort: {len(df):,} parolees | 3-yr re-arrest rate: {100*rec.mean():.1f}%")
print(f"prior arrest episodes (median): {priors.median():.0f}  (top-coded)")

bands = pd.cut(priors, [-1, 1, 3, 6, 9, 99], labels=["0-1", "2-3", "4-6", "7-9", "10+"])
tab = pd.DataFrame({
    "n": df.groupby(bands, observed=True).size(),
    "re_arrest_%": (100 * rec.groupby(bands, observed=True).mean()).round(1),
    "share_of_pop_%": (100 * df.groupby(bands, observed=True).size() / len(df)).round(1),
    "share_of_re-arrests_%": (100 * rec.groupby(bands, observed=True).sum() / rec.sum()).round(1),
})
print("\n", tab.to_string())

y1 = df["Recidivism_Arrest_Year1"].astype(str).str.upper().eq("TRUE")
print(f"\nof those re-arrested, back within year 1: {100*y1[rec].mean():.1f}%")

gang = df["Gang_Affiliated"].astype(str).str.upper().eq("TRUE")
print(f"gang-affiliated ({100*gang.mean():.1f}% of cohort): "
      f"{100*rec[gang].mean():.1f}% re-arrest vs {100*rec[~gang].mean():.1f}% otherwise")

# ---- chart 1: the gradient -------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5), facecolor=NAVY)
ax.set_facecolor(NAVY)
bars = ax.bar(tab.index.astype(str), tab["re_arrest_%"], color=RED, width=0.62)
for b, v in zip(bars, tab["re_arrest_%"]):
    ax.text(b.get_x() + b.get_width()/2, v + 1.2, f"{v}%", ha="center",
            color=BRASS, fontsize=12, fontweight="bold")
ax.set_title("Re-arrest within 3 years climbs with prior arrest history",
             color=INK, fontsize=13, pad=14)
ax.set_xlabel("Prior arrest episodes before this prison term (felony + misd, top-coded)",
              color=INK)
ax.set_ylabel("Re-arrested within 3 years (%)", color=INK)
ax.tick_params(colors=INK); [s.set_color("#3a4156") for s in ax.spines.values()]
ax.set_ylim(0, 78)
fig.tight_layout(); fig.savefig("analysis/gradient.png", dpi=160, facecolor=NAVY)

# ---- chart 2: who the re-arrests come from ---------------------------------
fig, ax = plt.subplots(figsize=(8, 5), facecolor=NAVY)
ax.set_facecolor(NAVY)
x = range(len(tab))
ax.bar([i - 0.2 for i in x], tab["share_of_pop_%"], width=0.38,
       color=BRASS, label="share of cohort")
ax.bar([i + 0.2 for i in x], tab["share_of_re-arrests_%"], width=0.38,
       color=RED, label="share of all re-arrests")
ax.set_xticks(list(x)); ax.set_xticklabels(tab.index.astype(str))
ax.set_title("Re-arrests concentrate in the extensive-history group",
             color=INK, fontsize=13, pad=14)
ax.set_xlabel("Prior arrest episodes", color=INK); ax.set_ylabel("Percent", color=INK)
leg = ax.legend(facecolor=NAVY, edgecolor="#3a4156"); [t.set_color(INK) for t in leg.get_texts()]
ax.tick_params(colors=INK); [s.set_color("#3a4156") for s in ax.spines.values()]
fig.tight_layout(); fig.savefig("analysis/concentration.png", dpi=160, facecolor=NAVY)
print("\nwrote analysis/gradient.png, analysis/concentration.png")
