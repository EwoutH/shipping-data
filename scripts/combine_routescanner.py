import pandas as pd

# Define date range to merge (currently only works for October)
dates = [f"2022-10-{day}" for day in range(14,26)]

# Read first DataFrame from Pickle
comb_df = pd.read_pickle(f"../pickles/routescanner_daily/connections_{dates[0]}.pickle")
print(f"Starting with dataframe {dates[0]} with {len(comb_df.index)} rows")

# For each other date, load the pickle, merge the dataframes and drop duplicates
for date in dates[1:]:
    # Save the current number of rows
    entries = len(comb_df.index)
    # Load the new dataframe from pickle
    new_df = pd.read_pickle(f"../pickles/routescanner_daily/connections_{date}.pickle")
    # Combine the two dataframes
    comb_df = pd.concat([comb_df, new_df], ignore_index=True)
    # Drop duplicate entries
    # Note that dataframes with lists can be converted, so check after converting to strings
    comb_df = comb_df.loc[comb_df.astype(str).drop_duplicates(comb_df.columns.tolist()).index]
    # Print some stats
    print(f"Merging dataframe {date}: {(n := len(comb_df.index)) - entries} rows added, {n} total")
# Display a few rows of the sorted dataframe
comb_df.astype(str).sort_values(by=comb_df.columns.tolist()[::-1]).head(15)
comb_df.head()

# Save as Pickle and CSV
comb_df.to_pickle(f"../pickles/routescanner_connections_combined.pickle")
comb_df.to_csv(f"../data/routescanner_connections_combined.csv")
