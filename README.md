# servicedesk plus python scripts
Servicedesk plus python scripts.

## SDP close
http interfaced server, to simplify close work orders

## SDP monitoring
continous work order time checker and alerting to telegram  
add simple text files:  
telegram.group - telegram group id. U can obtain that with @relaybot /lockedurl message in the same group  
token.key - sdp token

### REST API for native app
https://servicedeskplusmsp.wiki.zoho.com/REST-API-for-native-app.html

### service-desk-msp help admin guide api
https://www.manageengine.com/products/service-desk-msp/help/adminguide/api/worklog-operations.html

### instructions
Install python at sdp server, not in users path. C:\Python for example. With flag py and for all users.

To send prameters from sdp to script with triggers, use:
py custom_log.py $COMPLETE_JSON_FILE

### Jira  
The URIs for resources have the following structure:  
https://<site-url>/rest/api/3/<resource-name>  
For example, https://your-domain.atlassian.net/rest/api/3/issue/DEMO-1  