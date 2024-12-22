import subprocess
import json
import os
import requests
import shutil
from pathlib import Path




"""
Filename: git.py
Author: Amiel WExler
Date: 2024-11-17
Description: This functions handels the git repos for the biot organizations.
"""


def repo_exists(repo_name,github_token):
    """
    Check if a GitHub repository already exists.

    Parameters:
    repo_name (str): The name of the repository to check.
    github_token (str): Personal access token for GitHub API authentication.

    Returns:
    bool: True if the repository exists, False otherwise.
    """
    url = f"https://{github_token}@github.com/xtrodesorg/{repo_name}.git"
    response = requests.get(url)
    return response.status_code == 200

def clone_git_repo(repo_name,github_token):

    """
    Clone a GitHub repository. If it already exists locally, remove it and clone again.
    
    Parameters:
    repo_name (str): The name of the repository to clone.
    github_token (str): Personal access token for GitHub API authentication.
    """

    if os.path.exists(repo_name):
        shutil.rmtree(repo_name)
    if not repo_exists(repo_name,github_token):
        create_repo(repo_name, github_token)
    commands = [
        f'git clone https://{github_token}@github.com/xtrodesorg/{repo_name}.git {repo_name}',
        f'git remote set-url origin https://{github_token}@github.com/xtrodesorg/{repo_name}.git']
    for command in commands:
        subprocess.run(command, shell=True)

def create_branches(github_token, repo_name):
    """
    Create 'production' and 'development' branches in the cloned repository.

    Parameters:
    github_token (str): Personal access token for GitHub API authentication.
    repo_name (str): The name of the repository where branches will be created.
    """

    clone_git_repo(repo_name,github_token)
    os.chdir(repo_name)

    # Rename the default branch to 'production'
    subprocess.run(['git', 'branch', '-M', 'production'])

    # Create an initial commit on the 'production' branch
    with open('README.md', 'w') as f:
        f.write('# Initial README for production branch')
    subprocess.run(['git', 'add', 'README.md'])
    subprocess.run(['git', 'commit', '-m', 'Initial commit on production branch'])
    subprocess.run(['git', 'push', 'origin', 'production'])

    # Create and switch to the 'development' branch from 'production'
    subprocess.run(['git', 'checkout', '-b', 'development'])

    # Create an initial commit on the 'development' branch
    with open('README.md', 'w') as f:
        f.write('# Initial README for development branch')
    subprocess.run(['git', 'add', 'README.md'])
    subprocess.run(['git', 'commit', '-m', 'Initial commit on development branch'])
    subprocess.run(['git', 'push', 'origin', 'development'])

    print(f"Repository '{repo_name}' created with branches 'production' and 'development'.")
    
    os.chdir('..')
    shutil.rmtree(repo_name)


def create_repo(repo_name, github_token):

    """
    Create a new GitHub repository.

    Parameters:
    repo_name (str): The name of the new repository.
    github_token (str): Personal access token for GitHub API authentication.

    Returns:
    int: HTTP status code from the API response.
    """

    url = f"https://api.github.com/orgs/xtrodesorg/repos"
    session = requests.Session()
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name
    }
    response = session.post(url, headers=headers, data=json.dumps(data))
    if response.status_code==201:
        create_branches(github_token, repo_name)
    return response.status_code





def checkout_branch(branch_name):
    """
    Switch to a specified branch, creating it if it doesn't exist.

    Parameters:
    branch_name (str): The name of the branch to switch to.
    """
    # Check if the branch exists
    branch_exists = subprocess.run(['git', 'show-ref', '--quiet', '--verify', f'refs/heads/{branch_name}'], stderr=subprocess.DEVNULL).returncode == 0

    if branch_exists:
        # If the branch exists, check it out
        subprocess.run(['git', 'checkout', branch_name])
        print(f"Switched to branch {branch_name}")
    else:
        # If the branch doesn't exist, create it and check it out
        subprocess.run(['git', 'checkout', '-b', branch_name])
        print(f"Created and switched to new branch {branch_name}")



def commit_file(repo_name, branch_name,github_token,file_name):
    """
    Commit a file to a specified branch in a GitHub repository.

    Parameters:
    repo_name (str): The name of the repository.
    branch_name (str): The branch where the file will be committed.
    github_token (str): Personal access token for GitHub API authentication.
    file_name (str): The name of the file to be committed.
    """
    
    clone_git_repo(repo_name,github_token)
    os.chdir(repo_name)
    #subprocess.call(["git","checkout",f"{branch_name}"])
    checkout_branch(branch_name)
    os.chdir(str(Path(os.getcwd()).parents[0])) 
    subprocess.call(["mv" ,f"{file_name}", f"{repo_name}/{file_name}"])
    os.chdir(repo_name)
    subprocess.run(["git" ,'add', f"{file_name}"])

    commit_message = 'updated org by org manager build whatever' # todo change later
    subprocess.run(["git","commit",'-m',f'{commit_message}'])
    subprocess.run(["git","push",'-u','origin',f'{branch_name}','--force-with-lease'])


def create_realese(GITHUB_TOKEN,repo_name,tag_name,release_body):
    
    url = f'https://api.github.com/repos/xtrodesorg/{repo_name}/releases'

    # Headers for the request
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Data for the release
    data = {
        'tag_name': tag_name,
        'target_commitish': 'main',  # or the branch you want to release from
        'name': release_body,
        'body': release_body,
        'draft': False,
        'prerelease': False
    }

    # Make the POST request to create the release
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check the response
    if response.status_code == 201:
        print('Release created successfully!')
        print(response.json())
    else:
        print(f'Failed to create release: {response.status_code}')
        print(response.json())
    


