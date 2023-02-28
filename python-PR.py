#!/usr/bin/env python3

from datetime import datetime
import json
import os
import requests
import re
import subprocess
import sys
import time

def git_exec(command):
    print(command)
    if command.find("git commit") >= 0:
        command_splitted = ["git", "commit", "-m"]
        command_splitted.append(command.split('git commit -m ')[1])
    else:
        command_splitted = command.split()
    command_e = subprocess.Popen(command_splitted, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, cwd=resolved_path, text=True)
    e = command_e.communicate()[0].split('\n')[0]
    if e.find('fatal:') >= 0:
        print(
            f'В папке {resolved_path} не найден git репозиторий.')
        exit()
    return e


token = "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"
if token == "":
    print(f"""
\t!!! переменная "token" пуста, задайте парметр !!!

\thttps://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
""")
    exit()

try:
    if sys.argv[1]:
        message = " ".join(sys.argv[1:])
except IndexError:
    print(
        f"Введите сообщение для реквеста\n")
    exit()

path = "./"
resolved_path = os.path.normpath(os.path.abspath(
    os.path.expanduser(os.path.expandvars(path))))

try:
    origin_push_url = git_exec("git remote get-url --push origin")
except FileNotFoundError:
    print(
        f'Не удалось найти папку {path}'
    )
    exit()

if origin_push_url.find('fatal:') >= 0:
    print(
        f'В папке {resolved_path} не найден git репозиторий.')
    exit()

gh_acc, gh_repo = re.split('git@github.com:|/|.git', origin_push_url)[1:3]

repo_url = f'https://api.github.com/repos/{gh_acc}/{gh_repo}'

headers = {"Authorization": f"token {token}",
           "Accept": "application/vnd.github.v3+json"}

git_status = subprocess.Popen(["git", "status", "--porcelain"], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, cwd=resolved_path, text=True).communicate()[0].split('\n')

cur_time = datetime.now()
branch_name = f"""{datetime.strftime(cur_time, "%Y-%m-%d_%H%M%S")}-config-local-edit"""
date_commit_text = datetime.strftime(cur_time, "%Y-%m-%d %H:%M:%S")

# exit()
if len(git_status) > 1 or git_status[0] != '':
    git_exec(f"git checkout -b {branch_name}")
    git_exec(f"git add .")
    git_exec(f"git commit -m 'config local edit at {date_commit_text}'")
    git_exec(f"git push --set-upstream origin {branch_name}")
    r = requests.get(f"{repo_url}/branches/{branch_name}", headers=headers)
    git_exec(f"git checkout main")
    while r.status_code >= 300:
        r = requests.get(f"{repo_url}/branches/{branch_name}", headers=headers)
        print(f'Ещё не создан репозиторий. GitHub: {r}, {r.content}')
        time.sleep(1)
    payload = {"title": branch_name, "body": message,
               "head": branch_name, "base": "main"}
    r = requests.post(f"{repo_url}/pulls", headers=headers,
                      data=json.dumps(payload))
    if r.status_code >= 300:
        print(
            f"Ошибка! Ответ GitHub API на создание Pull Request: {r}\n\n{r.content}\n")
        exit()
    else:
        print(f'Ответ GitHub на создание Pull Request: {r}')
        git_exec(f"git branch -D {branch_name}")
    pull_req_merge_url = f"{r.json()['url']}/merge"
    payload = {"commit_title": f"MERGED {branch_name} into main"}
    r = requests.put(pull_req_merge_url, headers=headers,
                     data=json.dumps(payload))
    if r.status_code >= 300:
        print(
            f"Ошибка! Ответ GitHub API на слияние Pull Request: {r}\n\n{r.content}\n")
        exit()
    else:
        print(f'Ответ GitHub на слияние Pull Request: {r}')
        git_exec(f"git push origin -d {branch_name}")
        print(f'\nЗагрузка изменений main:\n')
        os.popen(f"cd {resolved_path} && git pull").read()
        print(f'\n')
