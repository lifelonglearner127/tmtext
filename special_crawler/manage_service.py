from flask import Flask, jsonify, request, render_template
import os, subprocess
import re

app = Flask(__name__)

@app.route('/switch_branch', methods=['GET', 'POST'])
def switch_branch():
	# show branches
	branches = get_branches()

	# if method is POST switch branch before rendering list of available branches
	if request.method == 'POST':
		# get value of target branch from submitted value from form
		checkout_branch(request.form['Branches'], branches['branches'])

		#TODO: also restart crawler service!

	# TODO: more optimal - don't do this twice? but that would mean keeping some state
	branches = get_branches()
	return render_template('show_branches.html', branches = branches['branches'], current_branch = branches['current_branch'])
	

"""Switch to given branch in target repo
"""
def checkout_branch(branchname, all_branches):
	# TODO: handle error in checking out branch
	# verify branchname is among branches in this repo - from get_branches()
	# TODO: error message if not
	if branchname in all_branches:
		return_val = subprocess.call(['git', 'checkout', branchname])
	else:
		print "Error: ", branchname, " not in available branches: ", branches

"""Get list of local branches in the tmtext repo
Return:
	dictionary containing list of branches and current branch
"""
def get_branches():
	# list branches

	branches_s = subprocess.check_output(['git', 'branch'])
	branches = branches_s.split('\n')

	# get current branch
	current_branch = filter(lambda branch: branch.startswith("*"), branches)[0]
	current_branch = clean_branchname(current_branch)

	# clean branches names
	branches = filter(None, map(clean_branchname, branches))

	return {"branches":branches, "current_branch": current_branch}

"""Clean branches names received as output from `git branch`
	remove leading spaces and * for current branch
Return:
	cleaned branch name
"""
def clean_branchname(branchname):
	branchname = re.sub("^\*", "", branchname)
	branchname = branchname.strip()
	return branchname

if __name__ == '__main__':

    app.run('0.0.0.0', port=8080)