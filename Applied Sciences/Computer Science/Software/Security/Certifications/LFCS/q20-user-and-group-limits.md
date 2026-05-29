# Question 20 — User and Group limits

## Énoncé

Solve this question on: `web-srv1`

User Jackie caused an issue with her account on server `web-srv1`. She did run a program which created too many subprocesses for the server to handle. A coworker of yours already solved it temporarily and limited the number of processes user `jackie` can run.

For this the coworker added a command into `.bashrc` in the home directory of `jackie`. But the command just sets the soft limit and not the hard limit. Jackie's password is `brown` in case needed.

Configure the number-of-processes limitation as a hard limit for user `jackie`. Use the same number currently set as a soft limit for that user. Do it in the proper way, not via `.bashrc`.

On the same server you should enforce that group `operators` can only ever log in once at the same time, use `maxlogins` for this.

> It's not possible to test/verify the `maxlogins` after configuration due to how the server has been configured

## Solution

### Step 1
Well, that's a lot. We check out that user and its limits first:
```bash
ssh web-srv1
root@web-srv1:~$ su jackie
jackie@web-srv1:/root$ cd
jackie@web-srv1:~$
jackie@web-srv1:~$ ulimit -a
core file size          (blocks, -c) 0
data seg size           (kbytes, -d) unlimited
scheduling priority             (-e) 0
file size               (blocks, -f) unlimited
pending signals                 (-i) 7815
max locked memory       (kbytes, -l) 64
max memory size         (kbytes, -m) unlimited
open files                      (-n) 1024
pipe size            (512 bytes, -p) 8
POSIX message queues     (bytes, -q) 819200
real-time priority              (-r) 0
stack size              (kbytes, -s) 8192
cpu time               (seconds, -t) unlimited
max user processes              (-u) 1024 # that's he one!
virtual memory          (kbytes, -v) unlimited
file locks                      (-x) unlimited
```

Using `ulimit` we can see all configured limits, and there is `max user processes` set to 1024. We should check how it has been set in `.bashrc`:
```bash
jackie@web-srv1:~$ if ! shopt -oq posix; then
...
ulimit -S -u 1024 # current implementation
```

This works, but user `jackie` could change it herself like this:
```bash
jackie@web-srv1:~$ ulimit -u # list current
1024
jackie@web-srv1:~$ ulimit -S -u 1100
jackie@web-srv1:~$ ulimit -u
1100
```

First we remove that line that was added as a temporary fix
```bash
root@web-srv1:~$ vim /home/jackie/.bashrc # remove the ulimit setting
```

Next we go ahead and configure it via `/etc/security/limits.conf` (we need to be root for this). In that file there are already some useful examples on the bottom. We add a new line
```bash
root@web-srv1:~$ vim /etc/security/limits.conf
...
jackie         hard    nproc           1024     # add a new line
```

Now we can confirm our change:
```bash
jackie@web-srv1:~$ ulimit -u
1024
jackie@web-srv1:~$ ulimit -S -u 1100
bash: ulimit: max user processes: cannot modify limit: Invalid argument
```

User `jackie` is not able any longer to change that limit herself.

### Step 2
The other ticket was about implementing a limitation for group `operators`, so we add it to the file as well:
```bash
root@web-srv1:~$ vim /etc/security/limits.conf
...
jackie          hard    nproc           1024
@operators      hard    maxlogins       1 # add this line
```

We might not be able to test this setting due to how the server has been configured.

