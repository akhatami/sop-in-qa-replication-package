import os
from git import Repo
import subprocess
import pandas as pd
from datetime import datetime


create_directories = ['./gradle_build_logs/successful',
                        './gradle_build_logs/failed',
                        './gradle_build_logs/unclear',
                        './gradle_build_logs/error',
                        './cloned_repos']

for directory in create_directories:
    if not os.path.exists(directory):
        os.makedirs(directory)

def print_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

FOLDER_NAME = "cloned_repos"
INPUT_CSV = "./data/selected_projects_add.csv"

df = pd.read_csv(INPUT_CSV, dtype=str)
df = df[(df['gradle'] == '1') & (df['android'] != '1') & (df['gradle_on_root'] == '1')]
count_all = df.shape[0]
print("Count all: {0}".format(count_all))
i = 0
for index, row in df.iterrows():
    print("State: {0}/{1}".format(i,count_all))
    i+=1
    repo_name = row['Name']
    last_commit_sha = row['Last Commit SHA']
    log_path = "gradle_build_logs/"
    try:
        repo_path = os.path.join(FOLDER_NAME, repo_name.replace("/", "_"))
        
        if os.path.isfile(log_path + "failed/" + repo_name.replace("/", "_") + ".txt") or os.path.isfile(log_path + "successful/" + repo_name.replace("/", "_") + ".txt") or os.path.isfile(log_path + "unclear/" + repo_name.replace("/", "_") + ".txt") or os.path.isfile(log_path + "error/" + repo_name.replace("/", "_") + ".txt"):
            print('already logged')
            continue

        if not os.path.exists(repo_path):
            print("cloning " + repo_name)
            repo = Repo.clone_from("https://null:null@github.com/" + repo_name + ".git", repo_path)
            print(repo_name + " cloned!")
            repo.git.checkout(last_commit_sha)
            print(repo_name + " checked out!")
        else:
            print("Already cloned:  " + repo_name)

        print_time()

        # 60 minutes limit
        command = "cd {0}; chmode +x gradlew; ./gradlew clean assemble --stacktrace; echo '**DONE-EXECUTING**' ".format(repo_path)
        print("running command: "+ command)
        output = subprocess.run(command, shell=True, check=True, timeout=3600,  capture_output=True, text=True)
        print(output.stdout)
        print("command ran")
        # delete after command run
        os.system('chmod -R +w '+ repo_path)
        os.system('rm -rf ' + repo_path)
        print("repository removed")

        print_time()
        
        if "BUILD SUCCESSFUL" in output.stdout:
            log_path += "successful"
            print("1!")
        elif "BUILD FAILED" in output.stdout:
            log_path += "failed"
            print("0!")
        else:
            log_path += "unclear"
            print("?!")

        with open(log_path + '/' + repo_name.replace("/", "_") + '.txt', 'w+') as log_file:
            log_file.write(output.stdout)

    except Exception as e:
        print("Error in " + repo_name + " :")
        print(e)
        log_path += "error"
        with open(log_path + '/' + repo_name.replace("/", "_") + '.txt', 'w+') as log_file:
            log_file.write(str(e))

