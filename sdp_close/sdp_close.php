<?php
$responce = file_get_contents('http://10.2.4.87:8080/bidclosebyjira?sdp_id='.$_GET['sdp_id'].'&subject='.urlencode($_GET['subject']).'&resolution='.urlencode($_GET['resolution']));
?>