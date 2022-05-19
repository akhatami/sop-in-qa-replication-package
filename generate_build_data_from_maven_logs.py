from os import listdir
from os.path import isfile, join
import pandas as pd
import os

create_directories = ['./maven_build_logs/successful',
                        './maven_build_logs/failed',
                        './maven_build_logs/unclear',
                        './maven_build_logs/error']

for directory in create_directories:
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_files_name_list(mypath):
    files_list = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    if ".DS_Store" in files_list: files_list.remove(".DS_Store")
    return files_list

def insert_repo(df, repo_name, build_tool, last_commit_sha):
    df.loc[-1] = [repo_name,build_tool,last_commit_sha,0,0,0,0]  # adding a row
    df.index = df.index + 1  # shifting index
    df = df.sort_index(axis=0, ascending=True)  # sorting by index

def insert_column_value(df, repo_name, column_name):
    df.loc[df.repo_name == repo_name, column_name] = df.loc[df.repo_name == repo_name, column_name] + 1

def generate_data(build_tool_name, column_name, df_projects):
    repo_name = s.rpartition('.')[0].replace('_', '/', 1)
    last_commit_sha = df_projects.loc[df_projects['Name'] == repo_name, 'Last Commit SHA'].values[0]
    insert_repo(df, repo_name, build_tool_name, last_commit_sha)
    insert_column_value(df, repo_name, column_name)

print("start getting the maven build results from logs into a dataframe...")

df = pd.DataFrame(columns=['repo_name', 'build_tool', 'last_commit_sha', 'success','fail','unclear','error'])

df_projects = pd.read_csv('./data/selected_projects_add.csv', dtype=str)

success_path = './maven_build_logs/successful'
fail_path = './maven_build_logs/failed'
unclear_path = './maven_build_logs/unclear'
error_path = './maven_build_logs/error'

for s in get_files_name_list(success_path):
    generate_data('maven', 'success', df_projects)

for s in get_files_name_list(fail_path):
    generate_data('maven', 'fail', df_projects)
    
for s in get_files_name_list(unclear_path):
    generate_data('maven', 'unclear', df_projects)

for s in get_files_name_list(error_path):
    generate_data('maven', 'error', df_projects)
    
df = df.sort_index(axis=0, ascending=True)

print("saving maven results...")
df.to_csv("./data/maven_build_results.csv", index=False)
print("maven build results saved to csv")
