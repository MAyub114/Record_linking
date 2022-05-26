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
    return number_comparisons, runtime


# Load hospital data
hospital_accounts = pd.read_csv(
    'hospital_account_info.csv', index_col='Account_Num')
hospital_reimbursement = pd.read_csv(
    'hospital_reimbursement.csv', index_col='Provider_Num')

# Create an indexer object for recordlinkage
indexer = recordlinkage.Index()
# Full() indexes all pairs (14M)
indexer.full()

number_comparisons, runtime = comparisons_timed(indexer)
print(f"Number of comparisons using all pairs: {number_comparisons} in {runtime} seconds")


# Limit the number of comparisons using blocking
# We only compare hospitals that are in the same state leading to far fewer comparisons
indexer = recordlinkage.Index()
indexer.block(left_on='State', right_on='Provider State')

number_comparisons, runtime = comparisons_timed(indexer)
print(f"Number of comparisons using reduced pairs: {number_comparisons} in {runtime} seconds")


# This dataset is clean. For messier datasets where the state names are misspelt i.e. "Tenessee" and "Tennessee", use sortedneighbourhood()
indexer = recordlinkage.Index()
indexer.sortedneighbourhood(left_on='State', right_on='Provider State')

number_comparisons, runtime = comparisons_timed(indexer)
print(f"Number of comparisons reduced pairs and allowing minor spelling mistakes: {number_comparisons} in {runtime} seconds")