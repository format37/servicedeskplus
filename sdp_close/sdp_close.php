<?php
$params='component='.urlencode($_GET['component']).'&jira_type='.$_GET['jira_type'].'&user='.$_GET['user'].'&sdp_id='.$_GET['sdp_id'].'&subject='.urlencode($_GET['subject']).'&issue_key='.$_GET['issue_key'];
$res = file_get_contents('http://10.2.4.87:8080/bidclosebyjira?'.$params);
//$log_message = "Close by jira [1]\nsdp_id: ".$_GET['sdp_id']."\nissue_key: ".$_GET['issue_key']."\ncomponent: ".$_GET['component']."\njira_type: ".$_GET['jira_type']."\nuser: ".$_GET['user']."\nsubject: ".$_GET['subject'];
//$link = "https://www.scriptlab.net/telegram/bots/relaybot/relaylocked.php?chat=-7022979&text=".urlencode($log_message);
//file_get_contents($link);
?>
