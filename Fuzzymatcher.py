import pandas as pd
from pathlib import Path
import fuzzymatcher

print("FUZZY MATCHER")
hospital_accounts = pd.read_csv('hospital_account_info.csv')
hospital_reimbursement = pd.read_csv('hospital_reimbursement.csv')

print("Hospital Accounts")
print(hospital_accounts.head())

print("\nHospital Reimbursement")
print(hospital_reimbursement.head())

print("Running Fuzzy match..")
left_on = ["Facility Name", "Address", "City", "State"]
right_on = ["Provider Name", "Provider Street Address",
            "Provider City", "Provider State"]
matched_results = fuzzymatcher.fuzzy_left_join(hospital_accounts,
                                               hospital_reimbursement,
                                               left_on,
                                               right_on,
                                               left_id_col="Account_Num",
                                               right_id_col="Provider_Num")

cols = [
    "best_match_score", "Facility Name", "Provider Name", "Address", "Provider Street Address",
    "Provider City", "City", "Provider State", "State"
]

print("Top 5 best matched")
print(matched_results[cols].sort_values(
    by=['best_match_score'], ascending=False).head(5))

print("Bottom 5")
print(matched_results[cols].sort_values(
    by=['best_match_score'], ascending=True).head(5))

print("Scores under 0.8")
print(matched_results[cols].query("best_match_score <= .80").sort_values(
    by=['best_match_score'], ascending=False).head(5))