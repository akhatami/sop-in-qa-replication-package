from lxml import etree
import re
import os
import subprocess
import pandas as pd
from git import Repo

ns = {'POM4': 'http://maven.apache.org/POM/4.0.0'}

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

INPUT_CSV = "./data/maven_build_results.csv"

print("start running auto_jacoco_maven.py")

df = pd.read_csv(INPUT_CSV, dtype=str)

def write_xml(root, path):
    et = etree.ElementTree(root)
    et.write(path, pretty_print=True)

def get_xml_root(path):
    tree = etree.parse(path)
    return tree.getroot()

def delete_jacoco(path):
    root = get_xml_root(path)
    for element in root.findall('POM4:build/POM4:pluginManagement/POM4:plugins/POM4:plugin/POM4:artifactId', ns):
        if element.text == 'jacoco-maven-plugin':
            parent = element.getparent()
            parent.getparent().remove(parent)
        
    for element in root.findall('POM4:build/POM4:plugins/POM4:plugin/POM4:artifactId', ns):
        if element.text == 'jacoco-maven-plugin':
            parent = element.getparent()
            parent.getparent().remove(parent)

    write_xml(root, path)


def avoid_skip_tests(path):
    root = get_xml_root(path)
    properties_skip_tests_xml = """
    <properties>
        <skipTests>false</skipTests>
    </properties>
    """
    # <properties>
    properties_elem = root.find('POM4:properties', ns)
    if properties_elem is not None:
        # <skipTests>
        skipTests_elem = properties_elem.find("POM4:skipTests", ns)
        if skipTests_elem is not None:
            skipTests_elem.text = "false"
        else:
            skipTests_elem = etree.Element("skipTests")
            skipTests_elem.text = "false"
            properties_elem.append(skipTests_elem)

        # <maven.test.skip>
        mavenTestSkip_elem = properties_elem.find("POM4:maven.test.skip", ns)
        if mavenTestSkip_elem is not None:
            mavenTestSkip_elem.text = "false"
    else:
        root.insert(0,etree.XML(properties_skip_tests_xml))
    
    # <profiles><profile><properties><maven.test.skip>
    for maven_test_skip_elem in root.findall('POM4:profiles/POM4:profile/POM4:properties/POM4:maven.test.skip', ns):
        if maven_test_skip_elem.text == 'true':
            maven_test_skip_elem.text = 'false'

    write_xml(root, path)


def edit_surefire(path):
    root = get_xml_root(path)
    surefire_xml = """
            <plugin>
				<groupId>org.apache.maven.plugins</groupId>
				<artifactId>maven-surefire-plugin</artifactId>
				<version>3.0.0-M5</version>
				<configuration>
					<testFailureIgnore>true</testFailureIgnore>
                </configuration>
			</plugin>
    """
    surefire_found = False
    for surefire_artifact_elem in root.findall('POM4:build/POM4:plugins/POM4:plugin/POM4:artifactId', ns):
        # is maven-surefire-plugin already there
        if surefire_artifact_elem.text == 'maven-surefire-plugin':
            surefire_found = True
            config_elem = surefire_artifact_elem.getparent().find("POM4:configuration", ns)
            # is <configuration> already there
            if config_elem is not None:
                # <testFailureIgnore>
                if config_elem.find("POM4:testFailureIgnore", ns) is not None:
                    config_elem.find("POM4:testFailureIgnore", ns).text = "true"
                else:
                    test_ignore_elem = etree.Element("testFailureIgnore")
                    test_ignore_elem.text = "true"
                    config_elem.append(test_ignore_elem)
                
                # <skipTests>
                if config_elem.find("POM4:skipTests", ns) is not None:
                    config_elem.find("POM4:skipTests", ns).text = "false"
                else:
                    skip_tests_elem = etree.Element("skipTests")
                    skip_tests_elem.text = "false"
                    config_elem.append(skip_tests_elem)

            else:
                # no <configuration>
                config_elem = etree.Element("configuration")
                
                # <testFailureIgnore>
                test_ignore_elem = etree.Element("testFailureIgnore")
                test_ignore_elem.text = "true"
                config_elem.append(test_ignore_elem)

                # <skipTests>
                skip_tests_elem = etree.Element("skipTests")
                skip_tests_elem.text = "false"
                config_elem.append(skip_tests_elem)

                surefire_artifact_elem.getparent().append(config_elem)
                
    if not surefire_found:
        element = root.find('POM4:build/POM4:plugins', ns)
        if element is not None:
            element.insert(0,etree.XML(surefire_xml))
        else:
            element = root.find('POM4:build', ns)
            if element is None:
                root.insert(0,etree.XML("""
                <build>
                    <plugins>
                    {0}
                        </plugins>
                    </build>""".format(surefire_xml)))
            else:
                element.insert(0,etree.XML("""
                <plugins>
                {0}
                    </plugins>""".format(surefire_xml)))

    write_xml(root, path)


def insert_jacoco(path):
    root = get_xml_root(path)

    property_name = None
    for jacoco_artifact_elem in root.findall('POM4:build/POM4:plugins/POM4:plugin/POM4:artifactId', ns):
        # is jacoco-maven-plugin already there
        if jacoco_artifact_elem.text == 'jacoco-maven-plugin':
            config_elem = jacoco_artifact_elem.getparent().find("POM4:configuration", ns)
            # is <configuration> already there
            if config_elem is not None:
                if config_elem.find("POM4:propertyName", ns) is not None:
                    property_name = config_elem.find("POM4:propertyName", ns).text

    if property_name is None:
        jacoco_xml = """
                <plugin>
                    <groupId>org.jacoco</groupId>
                    <artifactId>jacoco-maven-plugin</artifactId>
                    <version>0.8.7</version>
                    <executions>
                        <execution>
                            <goals>
                                <goal>prepare-agent</goal>
                            </goals>
                        </execution>
                        <execution>
                            <id>jacoco-report</id>
                            <phase>test</phase>
                            <goals>
                                <goal>report</goal>
                            </goals>
                            <!-- default target/jscoco/site/* -->
                            <configuration>
                                <outputDirectory>target/jacoco-report</outputDirectory>
                            </configuration>
                        </execution>
                    </executions>
                </plugin> """
    else:
        jacoco_xml = """
                <plugin>
                    <groupId>org.jacoco</groupId>
                    <artifactId>jacoco-maven-plugin</artifactId>
                    <version>0.8.7</version>
                    <configuration>
                        <propertyName>{0}</propertyName>
                    </configuration>
                    <executions>
                        <execution>
                            <goals>
                                <goal>prepare-agent</goal>
                            </goals>
                        </execution>
                        <execution>
                            <id>jacoco-report</id>
                            <phase>test</phase>
                            <goals>
                                <goal>report</goal>
                            </goals>
                            <!-- default target/jscoco/site/* -->
                            <configuration>
                                <outputDirectory>target/jacoco-report</outputDirectory>
                            </configuration>
                        </execution>
                    </executions>
                </plugin> """.format(property_name)

    delete_jacoco(path)
    
    root = get_xml_root(path)
    element = root.find('POM4:build/POM4:plugins', ns)
    if element is not None:
        element.insert(0,etree.XML(jacoco_xml))
    else:
        element = root.find('POM4:build', ns)
        if element is None:
            root.insert(0,etree.XML("""
            <build>
                <plugins>
                {0}
                    </plugins>
                </build>""".format(jacoco_xml)))
        else:
            element.insert(0,etree.XML("""
            <plugins>
            {0}
                </plugins>""".format(jacoco_xml)))

    write_xml(root, path)

def get_coverage(path, repo_name, index):

    command = "cd {0}; mvn clean test; echo '**DONE-EXECUTING-Test**' ".format(path)
    print("running command: "+ command)
    output_build = subprocess.run(command, shell=True, check=True, timeout=3600,  capture_output=True, text=True)
    print(output_build.stdout)

    # in case that builds fails because of codestyle check on pom.xml
    if "mvn spotless:apply" in output_build.stdout:
        command = "cd {0}; mvn spotless:apply; echo '**DONE-EXECUTING-spotless:apply**' ".format(path)
        print("running command: "+ command)
        subprocess.run(command, shell=True, check=True, timeout=3600)
        command = "cd {0}; mvn clean test; echo '**DONE-EXECUTING-Test**' ".format(path)
        print("running command: "+ command)
        output_build = subprocess.run(command, shell=True, check=True, timeout=3600,  capture_output=True, text=True)

    log_path = "jacoco_maven_logs/"
    if "BUILD SUCCESS" in output_build.stdout:
        log_path += "successful"
        output_path = "./jacoco_maven_output/{0}{1}".format(repo_name.replace("/", "_"), index)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        command = "mv {0}/target/jacoco-report/jacoco.csv {1}; echo '**DONE-EXECUTING-move-output**' ".format(path, output_path)
        print("running command: "+ command)
        subprocess.run(command, shell=True, check=True, timeout=60)
        command = "echo {0} > {1}/path.txt; echo '**DONE-EXECUTING-echo-path**' ".format(path, output_path)
        print("running command: "+ command)
        subprocess.run(command, shell=True, check=True, timeout=60)
        
    elif "BUILD FAILURE" in output_build.stdout:
        log_path += "failed"
    else:
        log_path += "unclear"

    with open(log_path + '/' + repo_name.replace("/", "_") + str(index) + '.txt', 'w+') as log_file:
        log_file.write(path + "\n" + output_build.stdout)


def remove_ns(s):
    return re.sub(r'{.+?}', '', s)


df = df[df['success'] == '1']
count_all = df.shape[0]
print("Count all: {0}".format(count_all))
i = 0
for index, row in df.iterrows():

    print("State: {0}/{1}".format(i,count_all))
    i+=1

    repo_name = row['repo_name']
    last_commit_sha = row['last_commit_sha']
    repo_path = os.path.join('cloned_repos', repo_name.replace("/", "_"))

    if os.path.isfile("jacoco_maven_logs/cloning_error/" + repo_name.replace("/", "_") + ".txt") or os.path.isfile("jacoco_maven_logs/error_paths/" + repo_name.replace("/", "_") + ".txt") or os.path.isfile("jacoco_maven_logs/no_src_test_paths/" + repo_name.replace("/", "_") + ".txt") or os.path.isfile("jacoco_maven_logs/no_src_code_paths/" + repo_name.replace("/", "_") + ".txt"):
        print('already logged (paths)')
        continue

    try:
        if not os.path.exists(repo_path):
            print("cloning " + repo_name)
            repo = Repo.clone_from("https://null:null@github.com/" + repo_name + ".git", repo_path)
            print(repo_name + " cloned!")
            repo.git.checkout(last_commit_sha)
            print(repo_name + " checked out!")
        else:
            print(repo_name + ' already cloned!')
    except Exception as e:
        print("Error when cloning: " + repo_name + ", error :")
        print(e)
        with open('jacoco_maven_logs/cloning_error/' + repo_name.replace("/", "_") + '.txt', 'w+') as log_file:
            log_file.write(str(e))
        continue
    
    index = 0
    no_test_paths_with_pom = []
    no_code_paths_with_pom = []
    error_paths_with_pom = []

    for path, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith("pom.xml"):
                try:
                    pom_path = path+"/pom.xml"

                    src_main_exists = os.path.isdir(os.path.join(path, 'src/main'))
                    src_test_exists = os.path.isdir(os.path.join(path, 'src/test'))

                    if src_main_exists and src_test_exists:
                        index += 1
                        if os.path.isfile("jacoco_maven_logs/successful/" + repo_name.replace("/", "_") + str(index) + ".txt") or os.path.isfile("jacoco_maven_logs/failed/" + repo_name.replace("/", "_") + str(index) + ".txt") or os.path.isfile("jacoco_maven_logs/unclear/" + repo_name.replace("/", "_") + str(index) + ".txt"):
                            print('already logged (results)')
                            continue
                        avoid_skip_tests(pom_path)
                        edit_surefire(pom_path)
                        insert_jacoco(pom_path)
                        get_coverage(path, repo_name, index)
                    else:
                        if src_main_exists and not(src_test_exists):
                            no_test_paths_with_pom.append(path)
                        else:
                            no_code_paths_with_pom.append(path)

                except Exception as e:
                    print('Error when processing ***' + path +'***')
                    print('Error is:')
                    print(e)
                    error_paths_with_pom.append(path)

    if len(no_test_paths_with_pom) > 0:
        log = ''
        for path in no_test_paths_with_pom:
            log = log + path + '\n'
        with open('jacoco_maven_logs/no_src_test_paths/' + repo_name.replace("/", "_") + '.txt', 'w+') as log_file:
            log_file.write(log)
    
    if len(no_code_paths_with_pom) > 0:
        log = ''
        for path in no_code_paths_with_pom:
            log = log + path + '\n'
        with open('jacoco_maven_logs/no_src_code_paths/' + repo_name.replace("/", "_") + '.txt', 'w+') as log_file:
            log_file.write(log)

    if len(error_paths_with_pom) > 0:
        log = ''
        for path in error_paths_with_pom:
            log = log + path + '\n'
        with open('jacoco_maven_logs/error_paths/' + repo_name.replace("/", "_") + '.txt', 'w+') as log_file:
            log_file.write(log)

    # delete repo after
    os.system('chmod -R +w {0}'.format(repo_path))
    os.system('rm -rf {0}'.format(repo_path))
    print('{0} removed'.format(repo_path))

print('== Done executing auto_jacoco_maven.py ==')
