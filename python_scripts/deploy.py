#!/usr/bin/python

#
# Modules Import
#
import os, sys, shlex, subprocess, socket, json, cgi, cgitb

#
# Variables Definition
#
workspace = '<repository_root_folder>'

#
# Main
#

# For execution through HTTP request
print "Content-Type: text/html\n"

# Change position to the repository root folder
os.chdir(workspace)

# Get the project environment
vm_env = os.getenv('FACTER_vm_env')

# Get the data recieved through POST request body from webhook
webhook_data = cgi.FieldStorage()
payload = webhook_data.value

# If the webhook Payload has been recieved, decode the JSON and get the pushed branch
if (payload) and (os.getenv('REQUEST_METHOD') == 'POST'):
    payload = json.loads(payload)
    try:
        branch = payload['push']['changes'][0]['new']['name']
    except TypeError:
        print "The received Payload not includes new commits belonging to a branch, so it is not necessary to execute any Jenkins task"
        exit(1)
else:
    print "The Payload sent from Bitbucket webhook has not been recieved"
    exit(1)

# If the pushed branch is not included in ci_branches list, finish the script execution with exit code 1
if (branch != 'develop') and (branch != 'master'):
    print "The pushed branch is not enabled for automatic deployments"
    exit(1)

if (branch == 'develop' and vm_env == 'quality') or (branch == 'master' and vm_env == 'live'):
    print "Verify that there are not local changes in '" + workspace + "' path of the target server:"
    command = shlex.split('git diff --exit-code')
    command_exec = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = command_exec.communicate()
    if command_exec.returncode != 0:
        print "It is not possible to deploy in '" + workspace + "' path due to there are local changes on the target server"
        exit(1)
    print "OK"

    print "\nPull the existent new commits from origin on the target server:"
    command = shlex.split('git pull')
    output, error = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if output != '':
        print output
    if error != '':
        print error
else:
    print "The pushed branch is '" + branch + "' and the project environment is '" + vm_env + "', so it is not necessary to deploy anything"
