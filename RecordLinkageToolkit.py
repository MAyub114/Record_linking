import pandas as pd
from time import time
import recordlinkage


def comparisons_timed(indexer):
    accuracy = 1
    start = time()
    candidates = indexer.index(hospital_accounts, hospital_reimbursement)

    # Set up the comparison logic
    compare = recordlinkage.Compare()
    # Exact match on city
    compare.exact('City', 'Provider City', label='City')
    # 85% match on name
    compare.string('Facility Name',
                   'Provider Name',
                   threshold=0.85,
                   label='Hosp_Name')
    # 85% match on address using Jaro-Winkler string distance (https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance)
    compare.string('Address',
                   'Provider Street Address',
                   method='jarowinkler',
                   threshold=0.85,
                   label='Hosp_Address')
    features = compare.compute(candidates, hospital_accounts,
                               hospital_reimbursement)

    number_comparisons = len(candidates)
    runtime = round(time() - start, accuracy)
    return number_comparisons, runtime, features


# Load hospital data
hospital_accounts = pd.read_csv(
    'hospital_account_info.csv', index_col='Account_Num')
hospital_reimbursement = pd.read_csv(
    'hospital_reimbursement.csv', index_col='Provider_Num')

# Create an indexer object for recordlinkage
indexer = recordlinkage.Index()
# Full() indexes all pairs (14M)
indexer.full()

number_comparisons, runtime, features = comparisons_timed(indexer)
print(
    f"Number of comparisons using all pairs: {number_comparisons} in {runtime} seconds")


# Limit the number of comparisons using blocking
# We only compare hospitals that are in the same state leading to far fewer comparisons
indexer = recordlinkage.Index()
indexer.block(left_on='State', right_on='Provider State')

number_comparisons, runtime, features = comparisons_timed(indexer)
print(
    f"Number of comparisons using reduced pairs: {number_comparisons} in {runtime} seconds")


# This dataset is clean. For messier datasets where the state names are misspelt i.e. "Tenessee" and "Tennessee", use sortedneighbourhood()
indexer = recordlinkage.Index()
indexer.sortedneighbourhood(left_on='State', right_on='Provider State')

number_comparisons, runtime, features = comparisons_timed(indexer)
print(
    f"Number of comparisons reduced pairs and allowing minor spelling mistakes: {number_comparisons} in {runtime} seconds")

print(features)

# 987848 rows with no matching values
print(features.sum(axis=1).value_counts().sort_index(ascending=False))

# All records with 2 or 3 matches
potential_matches = features[features.sum(axis=1) > 1].reset_index()
potential_matches['Score'] = potential_matches.loc[:,
                                                   'City':'Hosp_Address'].sum(axis=1)

# Concatenated name and address lookup for each of the source DataFrames
hospital_accounts['Acct_Name_Lookup'] = hospital_accounts[[
    'Facility Name', 'Address', 'City', 'State'
]].apply(lambda x: '_'.join(x), axis=1)

hospital_reimbursement['Reimbursement_Name_Lookup'] = hospital_reimbursement[[
    'Provider Name', 'Provider Street Address', 'Provider City',
    'Provider State'
]].apply(lambda x: '_'.join(x), axis=1)

account_lookup = hospital_accounts[['Acct_Name_Lookup']].reset_index()
reimbursement_lookup = hospital_reimbursement[[
    'Reimbursement_Name_Lookup']].reset_index()

# Merge with account data
account_merge = potential_matches.merge(account_lookup, how='left')

# Merge with reimbursement data
final_merge = account_merge.merge(reimbursement_lookup, how='left')

# Final data
cols = ['Account_Num', 'Provider_Num', 'Score',
        'Acct_Name_Lookup', 'Reimbursement_Name_Lookup']
print(final_merge[cols].sort_values(
    by=['Account_Num', 'Score'], ascending=False))

# Save results to Excel for SME advice
final_merge.sort_values(by=['Account_Num', 'Score'],
                        ascending=False).to_excel('merge_list.xlsx',
                                                  index=False)

# Deduplicating data. Pass a single DataFrame against itself
hospital_dupes = pd.read_csv(
    'hospital_account_dupes.csv', index_col='Account_Num')

# Create indexer with a sorted neighbourhood block on "State"
dupe_indexer = recordlinkage.Index()
dupe_indexer.sortedneighbourhood(left_on='State')
dupe_candidate_links = dupe_indexer.index(hospital_dupes)

# Check for duplicates based on city, name and address
compare_dupes = recordlinkage.Compare()
compare_dupes.string('City', 'City', threshold=0.85, label='City')
compare_dupes.string('Phone Number',
                     'Phone Number',
                     threshold=0.85,
                     label='Phone_Num')
compare_dupes.string('Facility Name',
                     'Facility Name',
                     threshold=0.80,
                     label='Hosp_Name')
compare_dupes.string('Address',
                     'Address',
                     threshold=0.85,
                     label='Hosp_Address')
dupe_features = compare_dupes.compute(dupe_candidate_links, hospital_dupes)

print(dupe_features.sum(axis=1).value_counts().sort_index(ascending=False))

# Add score column
potential_dupes = dupe_features[dupe_features.sum(axis=1) > 1].reset_index()
potential_dupes['Score'] = potential_dupes.loc[:,
                                               'City':'Hosp_Address'].sum(axis=1)

print(potential_dupes.head(7))
