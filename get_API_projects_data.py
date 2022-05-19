import pandas as pd
from tqdm import tqdm
from github_quality_analytics.quality_analytics import FileUsage
from github_quality_analytics.instance_manager import InstanceManager
tqdm.pandas()

# place enough access tokens here, so that you will not reach the API limit
KEYS = ['TOKEN_1', 'TOKEN_2', 'TOKEN_3', 'TOKEN_4', 'TOKEN_5']

InstanceManager(KEYS)

INPUT_CSV = "./data/selected_projects.csv" # the input file: csv file of selected projects
OUTPUT_CSV = "./data/selected_projects_add.csv" # the collected data will be stored here

df = pd.read_csv(INPUT_CSV)

# ASAT Tools
checkstyle_usage = FileUsage('checkstyle')
df['checkstyle'] = df['Name'].progress_apply(lambda x: checkstyle_usage.gather_data(x)[0])
df.to_csv(OUTPUT_CSV, index=False)

findbugs_usage = FileUsage('.fbprefs')
df['findbugs'] = df['Name'].progress_apply(lambda x: findbugs_usage.gather_data(x)[0])
df.to_csv(OUTPUT_CSV, index=False)

# Build Tools
maven_usage = FileUsage('pom.xml')
df['maven'] = df['Name'].progress_apply(lambda x: maven_usage.gather_data(x)[0])
df.to_csv(OUTPUT_CSV, index=False)

gradle_usage = FileUsage('build.gradle')
df['gradle'] = df['Name'].progress_apply(lambda x: gradle_usage.gather_data(x)[0])
df.to_csv(OUTPUT_CSV, index=False)

gradle_usage_on_root = FileUsage('build.gradle', only_root=True)
df['gradle_on_root'] = df['Name'].progress_apply(lambda x: gradle_usage_on_root.gather_data(x)[0])
df.to_csv(OUTPUT_CSV, index=False)

maven_usage_on_root = FileUsage('pom.xml', only_root=True)
df['maven_usage_on_root'] = df['Name'].progress_apply(lambda x: maven_usage_on_root.gather_data(x)[0])
df.to_csv(OUTPUT_CSV, index=False)

spotbugs_usage = FileUsage('spotbugs')
df['spotbugs'] = df['Name'].progress_apply(lambda x: spotbugs_usage.gather_data(x)[0])
df.to_csv(OUTPUT_CSV, index=False)

android_usage = FileUsage('AndroidManifest.xml')
df['android'] = df['Name'].progress_apply(lambda x: android_usage.gather_data(x)[0])
df.to_csv(OUTPUT_CSV, index=False)

print("Finish getting additional data from GithubAPI.")
