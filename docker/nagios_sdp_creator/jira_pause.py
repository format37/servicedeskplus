from jira import JIRA

def set_pause(assignee,issuekey):
	jira_options = {'server': 'http://10.2.4.14'}
	with open('jira.key','r') as key_file:
		jira_key = key_file.read()
	jira = JIRA(options=jira_options, basic_auth=('ServiceDesk', jira_key))
	#assignee = '557058:f0548e8f-6a09-44bd-bfb5-43a0a40531bb'
	#issuekey = 'HELP1C-413'
	issues = jira.search_issues(jql_str='assignee="'+assignee+'" and status="In Progress" and issuekey !="'+issuekey+'"')
	pause_id    = '161'
	for issue in issues:
		print('read',str(issue))		
		for transition in jira.transitions(issue):
			if transition['id']==pause_id:
				print('set', str(issue))
				jira.transition_issue(issue, pause_id)
				print('ok',str(issue))