#!/usr/bin/python

import sys, re, os, time, commands

authfile = '/data/svn/auth.conf'
newauthfile = '/data/svn/newauth.conf'
passwdfile = '/data/svn/passwd'

def usage():
    print 'Usage:'
    print '\tsvnuser.py username passwd passwd_again'

def is_username_exists(username):
        try:
                p = open(passwdfile, 'r')
        except IOError, e:
                print '[ERROR] %s does not exist.' % passwdfile

        for line in p:
                if line.split(':')[0] == username:
                        return True
        return False


if len(sys.argv) != 4:
    usage()
    sys.exit(0)

username = sys.argv[1].strip()
passwd = sys.argv[2]
passwd_again = sys.argv[3]

if not re.match('[a-zA-Z]+\.[a-zA-Z]', username):
    print '[ERROR] Invalid username.'
    sys.exit(1)

if passwd != passwd_again:
    print '[ERROR] The password and confirmation password must match.'
    sys.exit(2)

if len(passwd) < 6:
    print '[ERROR] Passwd must be at least 6 chars long.'
    sys.exit(3)

# handle access file for user


try:
        f = open(authfile, 'r')
except IOError, e:
        print '[ERROR] %s does not exist.' % authfile

try:
        g = open(newauthfile, 'w+')
except IOError, e:
        print '[ERROR] %s does not exist.' % newauthfile

newuser = True

for line in f:
    if re.match('group=', line):
        if is_username_exists(username):
            print '[WARNING] Account %s already exists.' % username
            os.remove(newauthfile)
            newuser = False
            break
        else:
            newline = line[:-1] + ',' + username + '\n'
        g.write(newline)
    else:
        g.write(line)

if newuser:
        print '[INFO] New svn account %s created.' % username
        bakstamp = time.strftime('%Y%m%d_%H%M%S', time.localtime(os.path.getmtime(newauthfile)))
        bakfile = authfile + '.' + bakstamp
        os.rename(authfile, bakfile)
        os.rename(newauthfile, authfile)

f.close()
g.close()

#Add passwd for new user, or update passwd for existing user

pwdcmd = '/usr/local/apache/bin/htpasswd -b '+ passwdfile + ' ' + username + ' ' + passwd

status,output = commands.getstatusoutput(pwdcmd)
if status == 0:
    print '[INFO] ' + output
else:
    print '[ERROR] ' + output
