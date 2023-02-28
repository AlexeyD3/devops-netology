#!/usr/bin/env python3

import os
import sys

cdpath = os.getcwd()
if len(sys.argv) >= 2:
    cdpath=sys.argv[1]

bash_command = ["exec 2>&1", "cd "+cdpath, "git status"]
result_os = os.popen(' && '.join(bash_command)).read()

for result in result_os.split('\n'):

    if result.find('modified') != -1:
        prepare_result = result.replace('\tmodified:   ', '/')
        print("\033[34m{}".format(cdpath+prepare_result))

    if result.find("can't cd to") != -1:
        print("\033[31m{}".format('error: wrong argument, check path'))

    if result.find('fatal') != -1:
        print("\033[31m{}".format('error: .git repository is not found in this directory'))
