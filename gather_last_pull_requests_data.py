import pandas as pd
import os.path
from github_quality_analytics.instance_manager import InstanceManager
from github_quality_analytics.quality_analytics import CodeReviewUsage
from github_quality_analytics.utils import Utils

INPUT_CSV = "./data/selected_projects.csv"
OUTPUT_CSV = "./data/pull_details.csv"

input_df = pd.read_csv(INPUT_CSV)

if os.path.isfile(OUTPUT_CSV):
    output_df = pd.read_csv(OUTPUT_CSV)
else:
    output_df = pd.DataFrame(columns=['repo_name', 'last_commit_sha', 'pull_number', 'count_review_requests', 'count_all_reviews', 'count_all_review_comments', 'count_all_comments', 'count_changed_files', 'count_total_changed_lines'])

# Add GitHub access tokens here
KEYS = ['TOKEN_1',
        'TOKEN_2',
        'TOKEN_3',
        'TOKEN_4',
        'TOKEN_5']

InstanceManager(KEYS)

def insert_row(df, repo_name, sha, item):
    df.loc[-1] = [repo_name, sha, item[0], item[1], item[2], item[3], item[4], item[5], item[6]]  # adding a row
    df.index = df.index + 1  # shifting index
    df = df.sort_index(axis=0, ascending=True)  # sorting by index

code_review_usage = CodeReviewUsage()

count=0
Utils.LOGGER.info("Count all repos: {0}".format(input_df.shape[0]))
for index, row in input_df.iterrows():
    count += 1
    if row["Name"] in output_df["repo_name"].unique():
        Utils.LOGGER.info("{0} is already logged, skipped!".format(row["Name"]))
        continue
    Utils.LOGGER.info("State : {0} / {1}".format(count, input_df.shape[0]))
    data = code_review_usage.gather_data(row["Name"], row["Last Commit SHA"])
    for item in data:
        if item != 'not_found' and item != 'access_blocked' and item != 'no_commit_found' and item != 'error':
            insert_row(output_df, row["Name"], row["Last Commit SHA"], item)
    output_df.to_csv(OUTPUT_CSV, index=False)
