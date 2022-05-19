     # "State-Of-The-Practice in Quality Assurance in Open Source Software Development" Replication Package

This is a description of the replication package associated with *State-Of-The-Practice in Quality Assurance in Open Source Software Development* paper.

This replication package consists of three main sections:

- **Data collection**: Docker files and Python scripts used to crawl data from GitHub's API, build projects, and apply the JaCoCo plugin
- **Datasets**: Brief description of the CSV files provided as the dataset of the study
- **Data analysis**: Jupyter notebooks used to do the data analysis part of the study, which generates results and figures of the paper

Here is a quick guide if you only want to generate the results related to the research questions:

- **RQ1 What is the current state-of-the-practice in quality assurance in open source software development?**
  - **RQ1.1 What is the prevalence of quality assurance approaches like software testing, modern code review, automated static analysis, and buildability?**
    - **Local Buildability**: [1. Local build analysis](#1-local-build-analysis)
    - **ASAT Usage**: [2. ASAT usage analysis](#2-asat-usage-analysis)
    - **Continuous Integration**: [3. CI usage analysis](#3-ci-usage-analysis)
    - **Code Review**: [4. Code review analysis](#4-code-review-analysis)
    - **Testing**: [5. Testing analysis](#5-testing-analysis)
  - **RQ1.2 Which quality assurance approaches are being used in conjunction?** <br />
    [6. Combined results analysis](#6-combined-results-analysis)
- **RQ2 What challenges and obstacles do practitioners or researchers face for each of the quality assurance practices?** <br />
    According to challenges when doing [1. Data collection](#1-data-collection) and considering all the steps of [3. Data analysis](#3-data-analysis).


# Table of the Contents
- ["State-Of-The-Practice in Quality Assurance in Open Source Software Development" Replication Package](#state-of-the-practice-in-quality-assurance-in-open-source-software-development-replication-package)
- [Table of the Contents](#table-of-the-contents)
- [1. Data collection](#1-data-collection)
  - [Before starting the data collection](#before-starting-the-data-collection)
  - [1. Additional data for selected projects](#1-additional-data-for-selected-projects)
  - [2. Local builds](#2-local-builds)
    - [2.1. Maven](#21-maven)
    - [2.2. Gradle](#22-gradle)
  - [3. CI status checks](#3-ci-status-checks)
  - [4. Pull Details](#4-pull-details)
  - [5. JaCoCo results](#5-jacoco-results)
    - [5.1. Maven](#51-maven)
  - [5.2. Gradle](#52-gradle)
- [2. Datasets](#2-datasets)
- [3. Data analysis](#3-data-analysis)
  - [1. Local build analysis](#1-local-build-analysis)
  - [2. ASAT usage analysis](#2-asat-usage-analysis)
  - [3. CI usage analysis](#3-ci-usage-analysis)
  - [4. Code review analysis](#4-code-review-analysis)
  - [5. Testing analysis](#5-testing-analysis)
  - [6. Combined results analysis](#6-combined-results-analysis)
# 1. Data collection
This part explains the data collection steps of the study. Using this information you should be able to reproduce the dataset used in the study. We used a specific commit hash for each of the projects' repositories to collect the information related to a specific state of them, which makes it possible to reproduce results. However, due to unavoidable changes in the projects' repositories (e.g. making them private, or deleting all or some parts of them), you might not be able to collect the exact same data. If you need the exact dataset used in our study you can find them inside the `data` directory. More information about the dataset is presented in the next section (Dataset).

Also, using the materials provided in this part you will be able to replicate the study for any other set of Java projects on GitHub. This includes automatically building them and calculating their code coverage, collecting information about their ASATs (Automated Static Analysis Tools) & CI (Continuous Integration) usage, and code reviews taking place in their pull requests.
## Before starting the data collection
To use the docker files inside this replication package, run the mentioned commands on the root directory of the replication package. Before running the commands you need to change the variables accordingly:

- ``ROOT_PATH``: the root path of this replication package on your system.
- ``M2_PATH``: arbitrary path for Maven local repository that keeps projects' dependencies (library jars, plugin jars, etc.).
- ``GRADLE_HOME_PATH``: arbitrary path for Gradle to store global configuration properties and initialization scripts as well as caches and log files.
## 1. Additional data for selected projects
This step provides the additional data for the set of selected projects. The information includes projects' ASATs usage, their build systems (Gradle or Maven), and if they are Android projects.

This step uses the ``Dockerfile-additional-data`` docker file to run the ``get_API_projects_data.py`` which uses the ``selected_projects.csv`` file. Before building the docker image make sure the ``data/selected_projects.csv`` file exists in the replication package. Also, add enough GitHub access tokens inside ``get_API_projects_data.py`` to avoid reaching the API limit.

First, run the following command to build the docker image:
```
docker build --tag akhatami/gh-analysis-add-data -f Dockerfile-additional-data .
```
Then, run the container using the image you just built:
```
docker run -itd --tty -v ROOT_PATH/data:/root/gh-quality-analytics/data --name gh_analysis_add_data akhatami/gh-analysis-add-data
```
Afterward, find the collected data in ``data/selected_projects_add.csv``.
## 2. Local builds
This step provides the local build results and consists of two docker files to build Maven and Gradle projects separately. Before this step, you need to have the additional data collected from the first step (``data/selected_projects_add.csv``).
### 2.1. Maven
This step uses the ``Dockerfile-maven-build`` docker file to run the ``auto_build_maven.py`` which uses the ``selected_projects_add.csv`` file to filter Maven projects, build them, and store their build logs. The stored build logs are in the ``maven_build_logs`` directory. You can already access our study's Maven build logs in the ``maven_build_logs.zip`` file. Before building the docker image make sure to use the right JAVA_HOME path according to the CPU architecture of your local machine (use arm64 for a machine with an M8 processor).

First, run the following command to build the docker image:
```
docker build --tag akhatami/gh-analysis-build-maven -f Dockerfile-maven-build .
```
Then, run the container using the image you just built:
```
docker run -itd --tty -v ROOT_PATH/maven_build_logs:/root/gh-quality-analytics/maven_build_logs -v M2_PATH:/root/.m2 -v ROOT_PATH/data:/root/gh-quality-analytics/data --name gh_analysis_build_maven akhatami/gh-analysis-build-maven
```
Afterwards find Maven build logs in ``maven_build_logs`` directory.
### 2.2. Gradle
This step uses the ``Dockerfile-gradle-build`` docker file to run the ``auto_build_gradle.py`` which uses the ``selected_projects_add.csv`` file to filter Gradle projects, build them, and store their build logs. The stored build logs are in the ``gradle_build_logs`` directory. You can already access our study's Gradle build logs in the ``gradle_build_logs.zip`` file. Before building the docker image make sure to use the right JAVA_HOME path according to the CPU architecture of your local machine (use arm64 for a machine with an M8 processor).

First, run the following command to build the docker image:
```
docker build --tag akhatami/gh-analysis-build-gradle -f Dockerfile-gradle-build .
```
Then, run the container using the image you just built:
```
docker run -itd --tty -v ROOT_PATH/gradle_build_logs:/root/gh-quality-analytics/gradle_build_logs -v GRADLE_HOME_PATH:/root/.gradle -v ROOT_PATH/data:/root/gh-quality-analytics/data --name gh_analysis_build_gradle akhatami/gh-analysis-build-gradle
```
Afterward, find Gradle build logs in the ``gradle_build_logs`` directory.
## 3. CI status checks
This step uses the ``Dockerfile-ci-status-checks`` docker file to run ``graphql_crawler.py`` which uses the ``selected_projects_add.csv`` file to collect projects' commit status and checks related information from GitHub's GraphQL API. Before building the docker image make sure to add your GitHub access token in ``graphql_crawler.py``.

First, run the following command to build the docker image:
```
docker build --tag akhatami/gh-analysis-ci-status-checks -f Dockerfile-ci-status-checks .
```
Then, run the container using the image you just built:
```
docker run -itd --tty -v ROOT_PATH/data:/root/gh-quality-analytics/data --name gh_analysis_ci_status_checks akhatami/gh-analysis-ci-status-checks
```
Afterward, find the collected data in ``data/graphql_checks_statuses.csv``.
## 4. Pull Details
This step uses the ``Dockerfile-pull-reqs-details`` docker file to run ``gather_last_pull_requests_data.py`` which uses the ``selected_projects.csv`` file to collect projects' pull request related information from GitHub's REST API. Make sure to add enough GitHub access tokens inside ``gather_last_pull_requests_data.py`` to avoid reaching the API limit. The collected data is then stored in ``data/pull_details.csv``.

First, run the following command to build the docker image:
```
docker build --tag akhatami/gh-analysis-pull-details -f Dockerfile-pull-reqs-details .
```
Then, run the container using the image you just built:
```
docker run -itd --tty -v ROOT_PATH/data:/root/gh-quality-analytics/data --name gh_analysis_pull_details akhatami/gh-analysis-pull-details
```
Afterward, find the collected data in ``data/pull_details.csv``.
## 5. JaCoCo results
This step provides the code coverage results and consists of two docker files to apply and run JaCoCo on Maven and Gradle projects separately. Before this step you need to have the local build logs: generated from the second step or unzipped from ``maven_build_logs.zip`` and ``gradle_build_logs.zip`` files. In addition to that, you also need ``data/selected_projects_add.csv`` collected from the first step.
### 5.1. Maven
This step uses the ``Dockerfile-jacoco-maven`` docker file to run ``auto_jacoco_maven.sh`` which runs ``generate_build_data_from_maven_logs.py`` to create ``data/maven_build_results.csv`` from Maven build logs, and after that runs ``auto_jacoco_maven.py`` to apply JaCoCo to projects' Maven configuration file and then generate code coverage details.

First, run the following command to build the docker image:
```
docker build --tag akhatami/gh-analysis-jacoco-maven -f Dockerfile-jacoco-maven .
```
Then, run the container using the image you just built:
```
docker run -itd --tty -v ROOT_PATH/jacoco_maven_logs:/root/gh-quality-analytics/jacoco_maven_logs -v ROOT_PATH/jacoco_maven_output:/root/gh-quality-analytics/jacoco_maven_output -v M2_PATH:/root/.m2 -v ROOT_PATH/data:/root/gh-quality-analytics/data --name gh_analysis_jacoco_maven akhatami/gh-analysis-jacoco-maven
```
Afterward, find the generated build logs and code coverage outputs in ``jacoco_maven_logs`` and ``jacoco_maven_output`` directories.
## 5.2. Gradle
This step uses ``Dockerfile-jacoco-gradle`` docker file to run ``auto_jacoco_gradle.sh`` which runs ``generate_build_data_from_gradle_logs.py`` to create ``data/gradle_build_results.csv`` from Gradle build logs, and after that runs ``auto_jacoco_gradle.py`` to apply JaCoCo to projects' Gradle configuration file and then generate code coverage details.

First, run the following command to build the docker image:
```
docker build --tag akhatami/gh-analysis-jacoco-gradle -f Dockerfile-jacoco-gradle .
```
Then, run the container using the image you just built:
```
docker run -itd --tty -v ROOT_PATH/jacoco_gradle_logs:/root/gh-quality-analytics/jacoco_gradle_logs -v ROOT_PATH/jacoco_gradle_output:/root/gh-quality-analytics/jacoco_gradle_output -v GRADLE_HOME_PATH:/root/.gradle -v ROOT_PATH/data:/root/gh-quality-analytics/data --name gh_analysis_jacoco_gradle akhatami/gh-analysis-jacoco-gradle
```
Afterwards find the generated build logs and code coverage outputs in ``jacoco_gradle_logs`` and ``jacoco_gradle_output`` directories.
# 2. Datasets
In the table below you see the description of each of the files of our dataset.

| File Name                       | Description                                                                                               |
| :------------------------------ | :-------------------------------------------------------------------------------------------------------- |
| ``selected_projects.csv``       | Initial dataset collected from GHS                                                                        | 
| ``selected_projects_add.csv``   | Initial dataset with additional information, including: ASATs usage information, their build system, etc. |
| ``maven_build_results.csv``     | Maven local build outputs                                                                                 |
| ``gradle_build_results.csv``    | Gradle local build outputs                                                                                |
| ``local_build_results.csv``     | Aggregated local build outputs                                                                            |
| ``graphql_checks_statuses.csv`` | Checks and statuses information                                                                           |
| ``pull_details.csv``            | Code review related information on pull requests                                                          |
| ``jacoco_results.csv``          | Code coverage availability results for projects and their modules                                         |
| ``jacoco_coverage_results.csv`` | Code coverage results                                                                                     |
| ``combined_results.csv``        | Aggregated results of all steps of the study, including all quality assurance practices                   |

For more details about each of the data files refer to the next section (Data analysis), where you can see how they are used inside Jupyter notebooks to derive the results of our study.
# 3. Data analysis
This part explains how to reproduce the data analysis part of the study. The goal is to see how we got from the data to the results and analysis used to answer the research questions.

First, use the provided ``virtualenv-requirements.txt`` to install required libraries using a new virtual environment using pip:
```
python3 -m venv <venv-name>
virtualenv <venv-name>
source <venv-name>/bin/activate
pip install -r virtualenv-requirements.txt
```
Second, we need two other data files before running the Jupyter notebooks related to data analysis. To create them run the following commands after activating the virtual environment you just created:
```
python3 generate_jacoco_data_from_logs.py
```
```
python3 aggregate_coverage_results.py
```
The first command generates the ``data/jacoco_results.csv`` file using the build logs and JaCoCo outputs generated from the last step of the data collection part (or extracted from the provided zip files). And the second command aggregates the coverage results of each project from the JaCoCo outputs and stores them in ``data/jacoco_coverage_results.csv``.

Finally, run the Jupyter notebook using the following command:
```
jupyter notebook
```
Next, continue with the following data analysis steps using the provided notebook files inside the ``jupyter-notebooks`` directory. 
## 1. Local build analysis
To produce the results related to our local build analysis use ``jupyter-notebooks/local_build_analysis.ipynb`` notebook. This notebook requires the following data files:

- ``data/gradle_build_results.csv``
- ``data/maven_build_results.csv``

and produces the followings:

- ``data/local_build_results.csv``: Aggregated results of local builds for both Maven and Gradle projects.
- ``figures/local-builds-bar-chart.pdf``: Local builds bar chart used in section 4.1 of the paper.
- ``data/combined_results.csv``: This file is created in this step, will be updated during the next steps, and then will be used in step 6 of data analysis.

Also, you can find other related results in the mentioned notebook.
## 2. ASAT usage analysis
To produce the results related to the ASATs usage analysis use ``jupyter-notebooks/ASAT_analysis.ipynb`` notebook. 
This notebook requires the following data file:

- ``data/selected_projects_add.csv``
## 3. CI usage analysis
To produce the results related to the CI usage analysis use ``jupyter-notebooks/CI_usage_analysis.ipynb`` notebook. 
 This notebook requires the following data files:

- ``data/selected_projects.csv``
- ``data/graphql_checks_statuses.csv``

and produces the followings:

- ``figures/ci-status-checks.pdf``: Box plot of the count of CI status checks, related to section 4.3.1 of the paper.
## 4. Code review analysis
To produce the results related to the code review analysis use ``jupyter-notebooks/code_review_analysis.ipynb`` notebook. 
This notebook requires the following data file: 

- ``data/selected_projects.csv``

and produces the followings:

- ``figures/code-review-reviews-bar-chart.pdf``: Distribution of count of code review reviews bar chart used in section 4.4 of the paper.
- ``figures/code-review-comments-bar-chart.pdf``: Distribution of count of code review comments bar chart used in section 4.4 of the paper.

Also, you can find other related results in the mentioned notebook.
## 5. Testing analysis
To produce the results related to the code review analysis use ``jupyter-notebooks/testing_analysis.ipynb`` notebook. 
This notebook requires the following data files: 

- ``data/jacoco_results.csv``
- ``data/local_build_results``
- ``data/jacoco_coverage_results.csv``

and produces the followings:

- ``figures/branches_coverage.pdf``: Box chart of branch coverage of projects with complete and partial coverage results.

## 6. Combined results analysis
To produce the results related to the combined results analysis (section 4.6 of the paper) use ``jupyter-notebooks/combined_results.ipynb`` notebook. 
This notebook requires the following data files: 

- ``data/combined_results.csv``: Created and updated during the previous 5 steps. This data contains the main output of all other data analysis steps.

and produces the followings:

- ``figures/ci-usage-bar-chart.pdf``: Bar chart used in section 4.3.1 of the paper.
- ``figures/ci-local-builds-bar-chart.pdf``: Bar chart used in section 4.3.2 of the paper.
- ``figures/code-review-metric-before-after.pdf``: Box chart used in section 4.6 of the paper.
- ``figures/cc-cr-asat-ci.pdf``: Figure used in section 4.6 of the paper.

Also, you can find the details of correlation analysis in the mentioned notebook.
