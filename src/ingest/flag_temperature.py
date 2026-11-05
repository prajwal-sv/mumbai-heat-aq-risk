import pandas as pd

df = pd.read_csv("data/clean/daily_clean.csv", parse_dates=["date_ist"])
t = df["variable"] == "temperature"

# Rule A: impossible for a daily average in Mumbai (my own limits)
a = t & ((df["value"] < 10) | (df["value"] > 45))
df.loc[a, "suspect"] = True
df.loc[a, "reason"] = "impossible temperature"

# Rule B: more than 8 degrees from the same-day median of the other stations
ok = df["value"].where(t & ~a)
day_median = ok.groupby([df["variable"], df["date_ist"]]).transform("median")
b = t & ~a & ((df["value"] - day_median).abs() > 8)
df.loc[b, "suspect"] = True
df.loc[b, "reason"] = "far from other stations"

# Blank, never delete
df["keep"] = df["usable"] & ~df["suspect"]
df["clean_value"] = df["value"].where(df["keep"])
df.to_csv("data/clean/daily_clean_v2.csv", index=False)

flagged = df[t & df["suspect"]]
print("Flagged temperature rows:", len(flagged))
print(flagged.groupby(["station", "reason"]).size())

left = df[t & df["keep"]]
print(left.groupby("station")["value"].describe().round(1))



# Flagged temperature rows: 292
# station          reason                 
# bkc_mpcb         far from other stations     18
#                  impossible temperature      26
# ghatkopar        far from other stations      7
#                  impossible temperature      13
# kherwadi         impossible temperature       1
# malad_west_iitm  impossible temperature     187
# shivaji_nagar    far from other stations     29
#                  impossible temperature      11
# dtype: int64
#                count  mean  std   min   25%   50%   75%   max
# station                                                      
# bkc_mpcb       460.0  29.8  2.5  15.7  28.5  29.7  31.1  39.2
# byculla        519.0  28.4  1.8  22.9  27.2  28.4  29.6  32.3
# ghatkopar      508.0  32.6  2.5  24.6  30.9  32.6  34.4  39.2
# kherwadi       544.0  29.1  2.0  22.5  27.6  28.9  30.1  33.7
# shivaji_nagar  499.0  29.3  2.6  22.7  27.3  29.3  31.2  38.2

