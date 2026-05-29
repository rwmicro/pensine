# Question 2 — CronJobs

## Énoncé

Solve this question on: `data-001`

On server `data-001`, user `asset-manager` is responsible for timed operations on existing data. Some changes and additions are necessary.

Currently there is one system-wide cronjob configured that runs every day at 8:30pm. Convert it from being a system-wide cronjob to one owned and executed by user `asset-manager`. This means that user should see it when running `crontab -l`.

Create a new cronjob owned and executed by user `asset-manager` that runs `bash /home/asset-manager/clean.sh` every week on Monday and Thursday at 11:15am.

> You can connect to servers using ssh, for example `ssh data-001`

## Solution

### Step 1
Here we should move a cronjob from system-wide to user `asset-manager`. First we check out that cronjob:
```bash
ssh data-001
root@data-001:~$ vim /etc/crontab
# /etc/crontab: system-wide crontab
# Unlike any other crontab you don't have to run the `crontab'
# command to install the new version when you edit this file
# and files in /etc/cron.d. These files also have username fields,
# that none of the other crontabs do.
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
# Example of job definition:
# .---------------- minute (0 - 59)
# |  .------------- hour (0 - 23)
# |  |  .---------- day of month (1 - 31)
# |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
# |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
# |  |  |  |  |
# *  *  *  *  * user-name command to be executed
17 *  * * * root    cd / && run-parts --report /etc/cron.hourly
25 6  * * * root  test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6  * * 7 root  test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6  1 * * root  test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
30 20 * * * root bash /home/asset-manager/generate.sh   # THAT'S THE ONE executed at 8:30pm
```

We go ahead and cut this line from that file, or copy it and remove it later! Next we're going to add it to the users cronjobs:
```bash
root@data-001:~$ su asset-manager
asset-manager@data-001:/root$ cd
asset-manager@data-001:~$ pwd
/home/asset-manager
asset-manager@data-001:~$ crontab -l # list cronjobs
no crontab for asset-manager
asset-manager@data-001:~$ crontab -e # edit cronjobs
# Edit this file to introduce tasks to be run by cron.
#
# Each task to run has to be defined through a single line
# indicating with different fields when the task will be run
# and what command to run for the task
#
# To define the time you can provide concrete values for
# minute (m), hour (h), day of month (dom), month (mon),
# and day of week (dow) or use '*' in these fields (for 'any').
#
# Notice that tasks will be started based on the cron's system
# daemon's notion of time and timezones.
#
# Output of the crontab jobs (including errors) is sent through
# email to the user the crontab file belongs to (unless redirected).
#
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
#
# For more information see the manual pages of crontab(5) and cron(8)
#
# m h  dom mon dow   command
30 20 * * * bash /home/asset-manager/generate.sh   # MAKE SURE to remove the user
```

> Here we shouldn't specify this any longer!
The system-wide cronjobs in `/etc/crontab` always specify the user that executes the command. Now it's no longer necessary.

After saving the file we should be able to:
```bash
asset-manager@data-001:~$ crontab -l
# Edit this file to introduce tasks to be run by cron.
#
# Each task to run has to be defined through a single line
# indicating with different fields when the task will be run
# and what command to run for the task
#
# To define the time you can provide concrete values for
# minute (m), hour (h), day of month (dom), month (mon),
# and day of week (dow) or use '*' in these fields (for 'any').
#
# Notice that tasks will be started based on the cron's system
# daemon's notion of time and timezones.
#
# Output of the crontab jobs (including errors) is sent through
# email to the user the crontab file belongs to (unless redirected).
#
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
#
# For more information see the manual pages of crontab(5) and cron(8)
#
# m h  dom mon dow   command
30 20 * * * bash /home/asset-manager/generate.sh
```

Now we see that migrated cronjob!

### Step 2
For the next step we should add a new cronjob. We can just copy and then change the existing one to our needs:
```bash
asset-manager@data-001:~$ crontab -e
# Edit this file to introduce tasks to be run by cron.
#
# Each task to run has to be defined through a single line
# indicating with different fields when the task will be run
# and what command to run for the task
#
# To define the time you can provide concrete values for
# minute (m), hour (h), day of month (dom), month (mon),
# and day of week (dow) or use '*' in these fields (for 'any').
#
# Notice that tasks will be started based on the cron's system
# daemon's notion of time and timezones.
#
# Output of the crontab jobs (including errors) is sent through
# email to the user the crontab file belongs to (unless redirected).
#
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
#
# For more information see the manual pages of crontab(5) and cron(8)
#
# m h  dom mon dow   command
30 20 * * * bash /home/asset-manager/generate.sh
15 11 * * 1,4 bash /home/asset-manager/clean.sh   # the new one
```

Save and check:
```bash
asset-manager@data-001:~$ crontab -l
...
30 20 * * * bash /home/asset-manager/generate.sh
15 11 * * 1,4 bash /home/asset-manager/clean.sh
```

For guidance check the comments in `/etc/crontab`, they're really useful. Instead of numbers for the days we can also use the actual names of days:

15 11 * * mon,thu bash /home/asset-manager/clean.sh   # also possible

The files for user crontabs are stored at location `/var/spool/cron/crontabs` and user root can access those.

