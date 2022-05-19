import logging
import os
import subprocess
import pandas as pd
from git import Repo


LOGGER = logging.getLogger('my_logger')
LOGGER.setLevel(level=logging.DEBUG)
STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setLevel(logging.DEBUG)
LOG_FORMATTER = logging.Formatter('%(asctime)s:%(levelname)s:%(funcName)s:%(lineno)d:%(message)s')
STREAM_HANDLER.setFormatter(LOG_FORMATTER)
LOGGER.addHandler(STREAM_HANDLER)

create_directories = ['./jacoco_gradle_logs/successful',
                        './jacoco_gradle_logs/failed',
                        './jacoco_gradle_logs/unclear',
                        './jacoco_gradle_logs/no_src_test_paths',
                        './jacoco_gradle_logs/no_src_code_paths',
                        './jacoco_gradle_logs/error_paths',
                        './jacoco_gradle_logs/cloning_error',
                        './jacoco_gradle_output',
                        './cloned_repos']

for directory in create_directories:
    if not os.path.exists(directory):
        os.makedirs(directory)

INPUT_CSV = "./data/gradle_build_results.csv"

df = pd.read_csv(INPUT_CSV, dtype=str)

def find_phrase_in_content_list(plugin_name: str, content_list: list[str]) -> bool:
    for index, line in enumerate(content_list):
        if plugin_name in line.lower():
            LOGGER.info("plugin found")
            return True
    LOGGER.info("plugin not found")
    return False

def add_jacoco_to_kotlin_project(content_list: list[str]) -> list[str]:
    if not find_phrase_in_content_list('jacoco', content_list):
        jacoco_index_plugins = -1
        for index, line in enumerate(content_list):
            if 'plugins {' in line:
                jacoco_index_plugins = index + 1

        if jacoco_index_plugins == -1:
            # plugins block not found
            LOGGER.info("no plugins block")
            plugin_block = """
plugins {
    jacoco
}
"""
            content_list.insert(0, plugin_block)
        else:
            # plugins block found
            LOGGER.info("plugins block found")
            content_list.insert(jacoco_index_plugins, '    jacoco\n')

    content_list = add_jacoco_config_kotlin(content_list)
    LOGGER.info("jacoco added to kotlin project")
    return content_list

def read_contents(path) -> list[str]:
    f = open(path, 'r')
    contents = f.readlines()
    f.close()
    return contents

def write_contents(path, contents):
    with open(path, "w") as f:
        contents = "".join(contents)
        f.write(contents)
    f.close()

def add_jacoco_config_kotlin(content_list):
    config = """
jacoco {
    toolVersion = "0.8.7"
}

tasks.test {
    finalizedBy(tasks.jacocoTestReport)
}

tasks.jacocoTestReport {
    dependsOn(tasks.test)
    reports {
        xml.required.set(false)
        csv.required.set(true)
        html.required.set(false)
    }
}
"""
    content_list.append(config)
    LOGGER.info("jacoco config kotlin added")
    return content_list

def add_all_projects_groovy(content_list, config_counts):
    config_with_subprojects = """
subprojects {
  apply plugin: 'jacoco'
  task {
      dependsOn(jacocoTestReport)
  }
  test {
      finalizedBy jacocoTestReport
  }
  jacocoTestReport {
      reports {
          csv.enabled = true
          html.enabled = false
          xml.enabled = false
      }
  }
  jacoco {
      toolVersion = "0.8.7"
  }
}
"""
    config = """
apply plugin: 'jacoco'
task {
    dependsOn(jacocoTestReport)
}
test {
    finalizedBy jacocoTestReport
}
jacocoTestReport {
    reports {
        csv.enabled = true
        html.enabled = false
        xml.enabled = false
    }
}
jacoco {
    toolVersion = "0.8.7"
}
"""
    if  config_counts > 1:
        content_list.append(config_with_subprojects)
    else:
        content_list.append(config)

    LOGGER.info("jacoco subprojects groovy added")
    return content_list

def get_results(path, repo_name, index):

    output_path = "./jacoco_gradle_output/{0}{1}".format(repo_name.replace("/", "_"), index)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    src_main_exists = os.path.isdir(os.path.join(path, 'src/main'))
    src_test_exists = os.path.isdir(os.path.join(path, 'src/test'))

    if src_main_exists and not(src_test_exists):
        LOGGER.info('no test found for '+ path)
        no_test_paths_with_pom.append(path)
    elif not(src_main_exists) and not(src_test_exists):
        LOGGER.info('no test and code found for '+ path)
        no_code_paths_with_pom.append(path)
    else:
        if os.path.isfile("{0}/build/reports/jacoco/test/jacocoTestReport.csv".format(path)):

            command = "mv {0}/build/reports/jacoco/test/jacocoTestReport.csv {1}; echo '**DONE-EXECUTING-move-output**' ".format(path, output_path)
            LOGGER.info("running command: {0}".format(command))
            subprocess.run(command, shell=True, check=True, timeout=60)

        else:
            LOGGER.info("no jacoco csv output")

        command = "echo {0} > {1}/path.txt; echo '**DONE-EXECUTING-write-path-to-output**' ".format(path, output_path)
        LOGGER.info("running command: {0}".format(command))
        subprocess.run(command, shell=True, check=True, timeout=60)

def handle_add_jacoco(path, config_counts, is_kotlin):
    if is_kotlin:
        gradle_path = path + '/build.gradle.kts'
        contents = read_contents(gradle_path)
        contents = add_jacoco_config_kotlin(contents)
        write_contents(gradle_path, contents)
    else:
        gradle_path = path + '/build.gradle'
        contents = read_contents(gradle_path)
        contents = add_all_projects_groovy(contents, config_counts)
        write_contents(gradle_path, contents)

def get_coverage(path, repo_name):

    command = "cd {0}; ./gradlew clean test --continue; echo '**DONE-EXECUTING-Test**' ".format(path)
    LOGGER.info("running command: {0}".format(command))
    output_build = subprocess.run(command, shell=True, check=True, timeout=3600,  capture_output=True, text=True)

    # in case that builds fails because of codestyle check
    if "spotlessApply" in output_build.stdout:
        command = "cd {0}; ./gradlew :spotlessApply; echo '**DONE-EXECUTING-spotlessApply**' ".format(path)
        LOGGER.info("running command: {0}".format(command))
        subprocess.run(command, shell=True, check=True, timeout=3600)
        command = "cd {0}; ./gradlew clean test --continue; echo '**DONE-EXECUTING-Test**' ".format(path)
        LOGGER.info("running command: {0}".format(command))
        output_build = subprocess.run(command, shell=True, check=True, timeout=3600,  capture_output=True, text=True)

    log_path = "jacoco_gradle_logs/"
    if "BUILD SUCCESSFUL" in output_build.stdout:
        log_path += "successful"
        LOGGER.info(path + "successful build")
    elif "BUILD FAILED" in output_build.stdout:
        log_path += "failed"
        LOGGER.info(path + "failed build")
    else:
        log_path += "unclear"
        LOGGER.info(path + "unclear build")

    with open(log_path + '/' + repo_name.replace("/", "_") + '.txt', 'w+') as log_file:
        output_build = path + "\n" + output_build.stdout
        log_file.write(output_build)
    
    if log_path == "jacoco_gradle_logs/successful" or log_path == "jacoco_gradle_logs/unclear":
        return True
    else:
        return False

def handle_project_clone(repo_path, last_commit_sha):
    try:
        if not os.path.exists(repo_path):
            LOGGER.info("cloning " + repo_name)
            repo = Repo.clone_from("https://null:null@github.com/" + repo_name + ".git", repo_path)
            LOGGER.info(repo_name + " cloned!")
            repo.git.checkout(last_commit_sha)
            LOGGER.info(repo_name + " checked out!")
            return('cloned')
        else:
            LOGGER.info(repo_name + ' already cloned!')
            return('continue')
    except Exception as e:
        LOGGER.warning('Error when cloning: '+ repo_path)
        LOGGER.warning('Error is: '+ str(e))
        with open('jacoco_gradle_logs/cloning_error/' + repo_name.replace("/", "_") + '.txt', 'w+') as log_file:
            log_file.write(str(e))
        return('continue')

df = df[df['success'] == '1']
count_all = df.shape[0]
print("Count all: {0}".format(count_all))
i = 0
TESTING = False
for index, row in df.iterrows():
    
    LOGGER.info("State: {0}/{1}".format(i,count_all))
    i+=1

    repo_name = row['repo_name']
    last_commit_sha = row['last_commit_sha']
    repo_path = os.path.join('cloned_repos', repo_name.replace("/", "_"))
    if not TESTING:
        if os.path.isfile("jacoco_gradle_logs/cloning_error/" + repo_name.replace("/", "_") + ".txt") or os.path.isfile("jacoco_gradle_logs/error_paths/" + repo_name.replace("/", "_") + ".txt") or os.path.isfile("jacoco_gradle_logs/no_src_test_paths/" + repo_name.replace("/", "_") + ".txt") or os.path.isfile("jacoco_gradle_logs/no_src_code_paths/" + repo_name.replace("/", "_") + ".txt") or os.path.isfile("jacoco_gradle_logs/successful/" + repo_name.replace("/", "_") + ".txt") or os.path.isfile("jacoco_gradle_logs/unclear/" + repo_name.replace("/", "_") + ".txt"):
            LOGGER.info('{0} already logged'.format(repo_name))
            continue

    handle_project_clone_output = handle_project_clone(repo_path, last_commit_sha)
    if handle_project_clone_output == 'continue':
        continue
    
    config_counts = 0
    for path, dirs, files in os.walk(repo_path):  
        for file in files:
            if file.endswith("build.gradle") or file.endswith("build.gradle.kts"):
                config_counts += 1

    no_test_paths_with_pom = []
    no_code_paths_with_pom = []
    error_paths_with_pom = []

    coverage_processed = False
    add_jacoco_handeled = False
    for file in os.listdir(repo_path):

        if file.endswith("build.gradle"): 
            handle_add_jacoco(repo_path, config_counts, is_kotlin=False)
            add_jacoco_handeled = True

        elif file.endswith("build.gradle.kts"):
            handle_add_jacoco(repo_path, config_counts, is_kotlin=True)
            add_jacoco_handeled = True

    if add_jacoco_handeled:
        try:
            coverage_processed = get_coverage(repo_path, repo_name)
        except Exception as e:
            LOGGER.warning('Error when processing '+ repo_path)
            LOGGER.warning('Error is: '+ str(e))
            error_paths_with_pom.append(repo_path)
    else:
        # no config file
        log = "no build.gradle or build.gradle.kts found"
        with open('jacoco_gradle_logs/error_paths/' + repo_name.replace("/", "_") + '.txt', 'w+') as log_file:
            log_file.write(log)
        continue

    if coverage_processed:
        index = 0
        for path, dirs, files in os.walk(repo_path):  
            for file in files:
                if file.endswith("build.gradle") or file.endswith("build.gradle.kts"):
                    get_results(path, repo_name, index)
                    index += 1

    if len(no_test_paths_with_pom) > 0:
        log = ''
        for path in no_test_paths_with_pom:
            log = log + path + '\n'
        with open('jacoco_gradle_logs/no_src_test_paths/' + repo_name.replace("/", "_") + '.txt', 'w+') as log_file:
            log_file.write(log)
    
    if len(no_code_paths_with_pom) > 0:
        log = ''
        for path in no_code_paths_with_pom:
            log = log + path + '\n'
        with open('jacoco_gradle_logs/no_src_code_paths/' + repo_name.replace("/", "_") + '.txt', 'w+') as log_file:
            log_file.write(log)

    if len(error_paths_with_pom) > 0:
        log = ''
        for path in error_paths_with_pom:
            log = log + path + '\n'
        with open('jacoco_gradle_logs/error_paths/' + repo_name.replace("/", "_") + '.txt', 'w+') as log_file:
            log_file.write(log)

    # delete repo after
    os.system('chmod -R +w {0}'.format(repo_path))
    os.system('rm -rf {0}'.format(repo_path))
    print('{0} removed'.format(repo_path))
