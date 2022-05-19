from os import listdir
from os.path import isfile, join
import os
import pandas as pd

def get_files_name_list(mypath):
    return [f for f in listdir(mypath) if isfile(join(mypath, f))]

def get_sub_directories_list(path):
    return [ f.name for f in os.scandir(path) if f.is_dir() ]

def insert_repo(df, repo_name, build_tool):
    df.loc[-1] = [repo_name,build_tool,0,0,0,0,0,0,0,0]  # adding a row
    df.index = df.index + 1  # shifting index
    df = df.sort_index(axis=0, ascending=True)  # sorting by index

def count_lines(path):
    file = open(path, "r")
    line_count = 0
    for line in file:
        if line != "\n":
            line_count += 1
    file.close()

    return line_count

def check_csv(path):
    return 1 if any(os.path.splitext(f)[1] == '.csv' for f in os.listdir(path)) else 0

def check_no_csv(path):
    return 0 if any(os.path.splitext(f)[1] == '.csv' for f in os.listdir(path)) else 1

def insert_column_value(df, repo_name, column_name, path=None):
    if column_name in ['no_code', 'no_test', 'error']:
        df.loc[df.repo_name == repo_name, column_name] = count_lines(path)
    elif column_name == 'csv':
        df.loc[df.repo_name == repo_name, column_name] = df.loc[df.repo_name == repo_name, column_name] + check_csv(path)
    elif column_name == 'no_csv':
        df.loc[df.repo_name == repo_name, column_name] = df.loc[df.repo_name == repo_name, column_name] + check_no_csv(path)
    else:
        df.loc[df.repo_name == repo_name, column_name] = df.loc[df.repo_name == repo_name, column_name] + 1

def get_repo_name_from_file_name(s):
    return s.rpartition('.')[0].rstrip('0123456789').replace('_', '/', 1)

def get_repo_name_from_directory_name(s):
    return s.rstrip('0123456789').replace('_', '/', 1)

create_directories = ['./jacoco_gradle_logs/successful',
                        './jacoco_gradle_logs/failed',
                        './jacoco_gradle_logs/unclear',
                        './jacoco_gradle_logs/no_src_test_paths',
                        './jacoco_gradle_logs/no_src_code_paths',
                        './jacoco_gradle_logs/error_paths',
                        './jacoco_gradle_logs/cloning_error',
                        './jacoco_gradle_output']

for directory in create_directories:
    if not os.path.exists(directory):
        os.makedirs(directory)

df = pd.DataFrame(columns=['repo_name', 'build_tool', 'success','fail','unclear','error','csv','no_code','no_test', 'no_csv'])

success_path = './jacoco_maven_logs/successful'
fail_path = './jacoco_maven_logs/failed'
unclear_path = './jacoco_maven_logs/unclear'
no_test_path = './jacoco_maven_logs/no_src_test_paths'
no_code_path = './jacoco_maven_logs/no_src_code_paths'
error_path = './jacoco_maven_logs/error_paths'
outputs_path = './jacoco_maven_output'

for s in get_files_name_list(success_path):
    repo_name = get_repo_name_from_file_name(s)
    if (df[df['repo_name'] == repo_name].shape[0] == 0):
        insert_repo(df, repo_name, 'maven')
    insert_column_value(df, repo_name, 'success')

for s in get_files_name_list(fail_path):
    repo_name = get_repo_name_from_file_name(s)
    if (df[df['repo_name'] == repo_name].shape[0] == 0):
        insert_repo(df, repo_name, 'maven')
    insert_column_value(df, repo_name, 'fail')
    
for s in get_files_name_list(unclear_path):
    repo_name = get_repo_name_from_file_name(s)
    if (df[df['repo_name'] == repo_name].shape[0] == 0):
        insert_repo(df, repo_name, 'maven')
    insert_column_value(df, repo_name, 'unclear')
    
for s in get_files_name_list(no_test_path):
    repo_name = get_repo_name_from_file_name(s)
    if (df[df['repo_name'] == repo_name].shape[0] == 0):
        insert_repo(df, repo_name, 'maven')
    insert_column_value(df, repo_name, 'no_test', no_test_path+"/"+s)
    
for s in get_files_name_list(no_code_path):
    repo_name = get_repo_name_from_file_name(s)
    if (df[df['repo_name'] == repo_name].shape[0] == 0):
        insert_repo(df, repo_name, 'maven')
    insert_column_value(df, repo_name, 'no_code', no_code_path+"/"+s)
    
for s in get_files_name_list(error_path):
    repo_name = get_repo_name_from_file_name(s)
    if (df[df['repo_name'] == repo_name].shape[0] == 0):
        insert_repo(df, repo_name, 'maven')
    insert_column_value(df, repo_name, 'error', error_path+"/"+s)
    
for s in get_sub_directories_list(outputs_path):
    repo_name = get_repo_name_from_directory_name(s)
    if (df[df['repo_name'] == repo_name].shape[0] == 0):
        insert_repo(df, repo_name, 'maven')
    insert_column_value(df, repo_name, 'csv', outputs_path+"/"+s)

for s in get_sub_directories_list(outputs_path):
    repo_name = get_repo_name_from_directory_name(s)
    if (df[df['repo_name'] == repo_name].shape[0] == 0):
        insert_repo(df, repo_name, 'maven')
    insert_column_value(df, repo_name, 'no_csv', outputs_path+"/"+s)

df = df.sort_index(axis=0, ascending=True)

create_directories = ['./jacoco_maven_logs/successful',
                        './jacoco_maven_logs/failed',
                        './jacoco_maven_logs/unclear',
                        './jacoco_maven_logs/no_src_test_paths',
                        './jacoco_maven_logs/no_src_code_paths',
                        './jacoco_maven_logs/error_paths',
                        './jacoco_maven_logs/cloning_error',
                        './jacoco_maven_output']

for directory in create_directories:
    if not os.path.exists(directory):
        os.makedirs(directory)

success_path = './jacoco_gradle_logs/successful'
fail_path = './jacoco_gradle_logs/failed'
unclear_path = './jacoco_gradle_logs/unclear'
no_test_path = './jacoco_gradle_logs/no_src_test_paths'
no_code_path = './jacoco_gradle_logs/no_src_code_paths'
error_path = './jacoco_gradle_logs/error_paths'
outputs_path = './jacoco_gradle_output'

for s in get_files_name_list(success_path):
    repo_name = get_repo_name_from_file_name(s)
    if (df[df['repo_name'] == repo_name].shape[0] == 0):
        insert_repo(df, repo_name, 'gradle')
    insert_column_value(df, repo_name, 'success')

for s in get_files_name_list(fail_path):
    repo_name = get_repo_name_from_file_name(s)
    if (df[df['repo_name'] == repo_name].shape[0] == 0):
        insert_repo(df, repo_name, 'gradle')
    insert_column_value(df, repo_name, 'fail')
    
for s in get_files_name_list(unclear_path):
    repo_name = get_repo_name_from_file_name(s)
    if (df[df['repo_name'] == repo_name].shape[0] == 0):
        insert_repo(df, repo_name, 'gradle')
    insert_column_value(df, repo_name, 'unclear')
    
for s in get_files_name_list(no_test_path):
    repo_name = get_repo_name_from_file_name(s)
    if (df[df['repo_name'] == repo_name].shape[0] == 0):
        insert_repo(df, repo_name, 'gradle')
    insert_column_value(df, repo_name, 'no_test', no_test_path+"/"+s)
    
for s in get_files_name_list(no_code_path):
    repo_name = get_repo_name_from_file_name(s)
    if (df[df['repo_name'] == repo_name].shape[0] == 0):
        insert_repo(df, repo_name, 'gradle')
    insert_column_value(df, repo_name, 'no_code', no_code_path+"/"+s)
    
for s in get_files_name_list(error_path):
    repo_name = get_repo_name_from_file_name(s)
    if (df[df['repo_name'] == repo_name].shape[0] == 0):
        insert_repo(df, repo_name, 'gradle')
    insert_column_value(df, repo_name, 'error', error_path+"/"+s)
    
for s in get_sub_directories_list(outputs_path):
    repo_name = get_repo_name_from_directory_name(s)
    if (df[df['repo_name'] == repo_name].shape[0] == 0):
        insert_repo(df, repo_name, 'gradle')
    insert_column_value(df, repo_name, 'csv', outputs_path+"/"+s)

for s in get_sub_directories_list(outputs_path):
    repo_name = get_repo_name_from_directory_name(s)
    if (df[df['repo_name'] == repo_name].shape[0] == 0):
        insert_repo(df, repo_name, 'gradle')
    insert_column_value(df, repo_name, 'no_csv', outputs_path+"/"+s)

df = df.sort_index(axis=0, ascending=True)


df.to_csv("./data/jacoco_results.csv", index=False)
