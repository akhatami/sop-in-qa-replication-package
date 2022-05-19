import os
import pandas as pd

rootdirs = ['./jacoco_maven_output', './jacoco_gradle_output']

def get_repo_name_from_directory_name(s):
    return s.split('/')[-1].rstrip('0123456789').replace('_', '/', 1)

def get_file_ext(s):
    return s.split('.')[-1]

def insert_repo(df, repo_name, build_tool, path, values):
    df.loc[-1] = [repo_name, build_tool, path, values[0], values[1], values[2], values[3], values[4], 
    values[5], values[6], values[7], values[8], values[9]]  # adding a row
    df.index = df.index + 1  # shifting index
    df = df.sort_index(axis=0, ascending=True)  # sorting by index

df_out = pd.DataFrame(columns=['repo_name', 'build_tool', 'path', 'instruction_missed', 
'instruction_covered', 'branch_missed', 'branch_covered', 'line_missed', 'line_covered', 'complexity_missed', 
'complexity_covered', 'method_missed', 'method_covered'])

for rootdir in rootdirs:
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            repo_name = get_repo_name_from_directory_name(subdir)
            file_ext = get_file_ext(file)
            if file_ext == "csv":
                df = pd.read_csv(os.path.join(subdir, file))
                if df.shape[0] == 0 or df.shape[1] == 0:
                    print('Error for {}'.format(os.path.join(subdir, file)))
                    pass

                build_tool = 'maven' if file == 'jacoco.csv' else 'gradle'

                path = ''
                with open(os.path.join(subdir, 'path.txt')) as f:
                    first_line = f.readline()
                    path = first_line.lstrip('cloned_repos/')

                insert_repo(df_out, repo_name, build_tool, path, [
                    df.INSTRUCTION_MISSED.sum(),
                    df.INSTRUCTION_COVERED.sum(),
                    df.BRANCH_MISSED.sum(),
                    df.BRANCH_COVERED.sum(),
                    df.LINE_MISSED.sum(),
                    df.LINE_COVERED.sum(),
                    df.COMPLEXITY_MISSED.sum(),
                    df.COMPLEXITY_COVERED.sum(),
                    df.METHOD_MISSED.sum(),
                    df.METHOD_COVERED.sum(),
                ])

df_out.to_csv("./data/jacoco_coverage_results.csv", index=False)
