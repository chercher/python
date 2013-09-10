#!/usr/bin/python

import sys,os

last_branches=sys.argv[1].split(',')

current_branch_1=sys.argv[2].strip()
current_branch_2=sys.argv[3].strip()
current_branch_3=sys.argv[4].strip()

branches=last_branches
branches.append(current_branch_1)
branches.append(current_branch_2)
branches.append(current_branch_3)

nondup_branches={}.fromkeys(branches).keys()

resetcmd='git reset --hard origin/master'
os.system('%s %s' % ('echo', resetcmd))
os.system(resetcmd)

cleancmd='git clean -df'
os.system('%s %s' % ('echo', cleancmd))
os.system(cleancmd)

pullcmd='git pull origin'
os.system('%s %s' % ('echo', pullcmd))
os.system(pullcmd)

save_branches='last_branches='

for branch in nondup_branches:
        if branch != '':
                save_branches=save_branches+','+branch

f=open('../lastbranches', 'w')
f.write(save_branches)
f.close

for branch in nondup_branches:
        if branch != '':
                os.system('%s %s%s' % ('echo', 'git merge origin/', branch))
                result=os.system('%s%s' % ('git merge origin/', branch))
                if result != 0:
                        sys.exit(1)
                        break
