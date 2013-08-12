#!/usr/local/bin/php
<?php

/**
 * Calls any CodeIginter controller action from the command line like:
 *
 * Named params -
 * php -q /var/www/api/cli.php controller_name action_name param1:value1 param2:value2 ...
 * 		Is the CLI equivalent of http://<host>/controller_name/action_name/param1:value1/param2:value2
 *
 * or
 *
 * Positional params -
 * php -q /var/www/api/cli.php controller_name action_name value1 value2 ...
 * 		Is the CLI equivalent of http://<host>/controller_name/action_name/value1/value2
 */

// make sure this isn't being called by a web browser
if (isset($_SERVER['REMOTE_ADDR'])) die('Permission denied.');

define('CMD', 1);

// manually set the URI path based on command line arguments.
unset($argv[0]); // but not the first one, which is the file that is executed (cli.php)
$_SERVER['QUERY_STRING'] =  $_SERVER['PATH_INFO'] = $_SERVER['REQUEST_URI'] = '/' . implode('/', $argv) . '/';


include_once('index.php');