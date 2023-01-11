import pandas as pd
import os

dir_path = '..\pickles\maersk_daily\pickles_before_merge'
files = os.listdir(dir_path) # lists all file_names in the folder

# Read first DataFrame from Pickle
comb_df = pd.read_pickle(f'..\pickles\maersk_daily\pickles_before_merge\{files[0]}')
l0 = len(comb_df.index)
# Print stats
print('Starting with dataframe',files[0],'with', (len(comb_df.index)), 'rows')

# For each other date, load the pickle, merge the dataframes and drop duplicates
if len(files)>1:
    for file in files[1:]:
        # Save the current number of rows
        l1 = len(comb_df.index)
        # Load the new dataframe from pickle
        new_df = pd.read_pickle(f'..\pickles\maersk_daily\pickles_before_merge\{file}')
        l2 = len(new_df.index)
        # Combine the two dataframes
        comb_df = pd.concat([comb_df, new_df], ignore_index=True)
        # Drop duplicate entries
        # Note that dataframes with lists can be converted, so check after converting to strings
        comb_df = comb_df.loc[comb_df.astype(str).drop_duplicates(comb_df.columns.tolist()).index]
    # Display a few rows of the sorted dataframe
    comb_df.astype(str).sort_values(by=comb_df.columns.tolist()[::-1]).head(15)
    comb_df.head()

# Save as Pickle and CSV
comb_df.to_pickle(f"../pickles/maersk_daily/combined.pickle")
comb_df.to_csv(f"../data/maersk_daily/combined.csv")