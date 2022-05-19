import requests
import json
import pandas as pd

class graphQL:
	headers = {"Authorization": "token YOUR_TOKEN"}

	"""docstring for graphQL"""
	def __init__(self, variables, output_df):
		super(graphQL, self).__init__()
		self.variables = variables
		self.output_df = output_df

	def run_query(self, query): # A simple function to use requests.post to make the API call. Note the json= section.
		request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': self.variables}, headers=self.headers)
		if request.status_code == 200:
			return json.loads(request.text)
		else:
			raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))
	
	def insert_row(self, item):
		self.output_df.loc[-1] = item # adding a row
		self.output_df.index = self.output_df.index + 1  # shifting index
		output_df = self.output_df.sort_index(axis=0, ascending=True)  # sorting by index

	def getStatusDetails(self):

		repo_name = self.variables['owner'] + '/' + self.variables['name']
		last_commit_SHA = self.variables['oid']

		results_remaining = True
		page = 1
		index = 0

		while results_remaining:
			query = '''
				query ($name: String!, $owner: String!, $oid: GitObjectID!, $first: Int!, $after: String!) {
	repository(name: $name, owner: $owner) {
		id
		name
		object(oid: $oid) {
		oid
		... on Commit {
			statusCheckRollup {
			...StatusCheckRollupFragment
			}
		}
		}
	}
	}

	fragment StatusCheckRollupFragment on StatusCheckRollup {
	state
	id
	contexts(first: $first, after: $after) {
		totalCount
		edges {
		cursor
		node {
			... on CheckRun {
			id
			name
			completedAt
			conclusion
			detailsUrl
			status
			text
			summary
			title
			url
			steps {
				totalCount
			}
			checkSuite {
				app {
				name
				slug
				url
				}
				workflowRun {
				runNumber
				url
				workflow {
					id
					name
				}
				}
			}
			}
			... on StatusContext {
			id
			creator {
				login
			}
			description
			state
			targetUrl
			context
			}
		}
		}
	}
	}'''

			result = self.run_query(query) #execute query
			if result['data']['repository']['object']['statusCheckRollup'] is None:
				return None
			state = result['data']['repository']['object']['statusCheckRollup']['state']
			count = result['data']['repository']['object']['statusCheckRollup']['contexts']['totalCount']
			
			for edge in result['data']['repository']['object']['statusCheckRollup']['contexts']['edges']:
				node = edge['node']
				item = []
				index += 1

				if 'name' in node:
					# node is check
					type = 'check'
					check_name = node['name']
					check_status = node['status']
					check_conclusion = node['conclusion']
					check_summary = node['summary']
					check_text = node['text']
					check_title = node['title']
					check_url = node['url']
					check_completedAt = node['completedAt']
					check_detailsUrl = node['detailsUrl']
					check_steps_totalCount = node['steps']['totalCount'] if node['steps'] is not None else None

					if node['checkSuite']['app'] is not None:
						check_suite_app_name = node['checkSuite']['app']['name']
						check_suite_app_slug = node['checkSuite']['app']['slug']
						check_suite_app_url = node['checkSuite']['app']['url']
					else:
						check_suite_app_name = None
						check_suite_app_slug = None
						check_suite_app_url = None

					if node['checkSuite']['workflowRun'] is not None:
						check_suite_workflowRun_runNumber = node['checkSuite']['workflowRun']['runNumber']
						check_suite_workflowRun_url = node['checkSuite']['workflowRun']['url']
						check_suite_workflowRun_workflow_name = node['checkSuite']['workflowRun']['workflow']['name']
					else:
						check_suite_workflowRun_runNumber = None
						check_suite_workflowRun_url = None
						check_suite_workflowRun_workflow_name = None

					status_context = None
					status_description = None
					status_state = None
					status_targetUrl = None
					status_creator_login = None
				else:
					type = 'status'
					status_context = node['context']
					status_description = node['description']
					status_state = node['state']
					status_targetUrl = node['targetUrl']
					if node['creator'] is not None:
						status_creator_login = node['creator']['login']
					else:
						status_creator_login = None

					check_name = None
					check_status = None
					check_conclusion = None
					check_summary = None
					check_text = None
					check_title = None
					check_url = None
					check_completedAt = None
					check_detailsUrl = None
					check_steps_totalCount = None
					check_suite_app_name = None
					check_suite_app_slug = None
					check_suite_app_url = None
					check_suite_workflowRun_runNumber = None
					check_suite_workflowRun_url = None
					check_suite_workflowRun_workflow_name = None

				# repo attributes
				item.append(repo_name)
				item.append(last_commit_SHA)
				item.append(state)
				item.append(count)
				# common attributes
				item.append(index)
				item.append(type)
				# check attributes
				item.append(check_name)
				item.append(check_status)
				item.append(check_conclusion)
				item.append(check_summary)
				item.append(check_text)
				item.append(check_title)
				item.append(check_url)
				item.append(check_completedAt)
				item.append(check_detailsUrl)
				item.append(check_steps_totalCount)
				item.append(check_suite_app_name)
				item.append(check_suite_app_slug)
				item.append(check_suite_app_url)
				item.append(check_suite_workflowRun_runNumber)
				item.append(check_suite_workflowRun_url)
				item.append(check_suite_workflowRun_workflow_name)
				#  status attributes
				item.append(status_context)
				item.append(status_description)
				item.append(status_state)
				item.append(status_targetUrl)
				item.append(status_creator_login)

				self.insert_row(item)
				print(index, 'inserted!')

			print('Count checks:', count)
			if count > (100*page):
				print(repo_name, 'has more than', 100*page ,'checks!')
				self.variables['after'] = result['data']['repository']['object']['statusCheckRollup']['contexts']['edges'][99]['cursor']
				page += 1
			else:
				print(repo_name, 'has less than', 100*page ,'checks.')
				results_remaining = False

		output_df.to_csv(OUTPUT_CSV, index=False)

INPUT_CSV = "./data/selected_projects.csv"
OUTPUT_CSV = "./data/graphql_checks_statuses.csv"

input_df = pd.read_csv(INPUT_CSV)

columns = [
	'repo_name',
	'last_commit_SHA',
	'state',
	'count',
	'index',
	'type',
	'check_name',
	'check_status',
	'check_conclusion',
	'check_summary',
	'check_text',
	'check_title',
	'check_url',
	'check_completedAt',
	'check_detailsUrl',
	'check_steps_totalCount',
	'check_suite_app_name',
	'check_suite_app_slug',
	'check_suite_app_url',
	'check_suite_workflowRun_runNumber',
	'check_suite_workflowRun_url',
	'check_suite_workflowRun_workflow_name',
	'status_context',
	'status_description',
	'status_state',
	'status_target_url',
	'status_creator_login'
]

output_df = pd.DataFrame(columns=columns)
count = 0
for index, row in input_df.iterrows():
	count+=1
	print(count, 'from', input_df.shape[0])
	print('repo: ', row["Name"])
	print('sha: ', row["Last Commit SHA"])

	variables = {
		"name": row["Name"].split('/')[1],
		"owner": row["Name"].split('/')[0],
		"oid": row["Last Commit SHA"],
		"first": 100,
		"after": ""
	}
	graphQL(variables=variables, output_df=output_df).getStatusDetails()
		