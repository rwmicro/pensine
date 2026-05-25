# Question 14 — Output redirection

## Énoncé

Solve this question on: `app-srv1`

On server `app-srv1` there is a program `/bin/output-generator` which, who would've guessed, generates some output. It'll always generate the very same output for every run:
1. Run it and redirect all `stdout` into `/var/output-generator/1.out`
2. Run it and redirect all `stderr` into `/var/output-generator/2.out`
3. Run it and redirect all `stdout` and `stderr` into `/var/output-generator/3.out`
4. Run it and write the exit code number into `/var/output-generator/4.out`

## Solution

We go ahead and check the program
```bash
ssh app-srv1
root@app-srv1:~$ output-generator
...
2021/07/20 08:58:20 32668 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 08:58:20 32669 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 08:58:20 32670 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 08:58:20 32671 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 08:58:20 32672 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 08:58:20 32673 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 08:58:20 32674 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 08:58:20 32675 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 08:58:20 32676 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 08:58:20 32677 - a99947a1-2f68-475e-9326-32dbd4876f60
```

**Investigation**

What a mess! Let's try to count the rows:
```bash
root@app-srv1:~$ output-generator | wc -l
...
2021/07/20 09:00:44 22670 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 09:00:44 22671 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 09:00:44 22672 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 09:00:44 22673 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 09:00:44 22674 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 09:00:44 22675 - a99947a1-2f68-475e-9326-32dbd4876f60
2021/07/20 09:00:44 22676 - a99947a1-2f68-475e-9326-32dbd4876f60
20342
```

It looks like `wc -l` does only count rows that are written to stdout.

We can investigate a bit further using `stdout` (1) and `stderr` (2) redirection
```bash
output-generator > /dev/null # no stdout rows
output-generator 1> /dev/null # no stdout rows (same command as above)
output-generator 1> /dev/null 2> /dev/null # no stdout or stderr
output-generator 2>&1 # stderr will be redirected into stdout
```

Using this we can count all lines:
```bash
root@app-srv1:~$ output-generator 2>&1 | wc -l
32678
```

**Solution**

We redirect as required:
```bash
root@app-srv1:~$ output-generator > /var/output-generator/1.out
root@app-srv1:~$ output-generator 2> /var/output-generator/2.out
root@app-srv1:~$ output-generator >> /var/output-generator/3.out 2>> /var/output-generator/3.out
root@app-srv1:~$ output-generator
root@app-srv1:~$ echo $? > /var/output-generator/4.out # get the exit code and redirect to file
```

Note that with `$?` we can access the exit code of the last command run. Which means we need to let `output-generator` finish properly and not interrupt it. We also can't run another command afterwards or else `$?` won't contain the `output-generator` exit code.

This should give us:
```bash
root@app-srv1:~$ cat /var/output-generator/1.out | wc -l
20342
root@app-srv1:~$ cat /var/output-generator/2.out | wc -l
12336
root@app-srv1:~$ cat /var/output-generator/3.out | wc -l
32678
root@app-srv1:~$ cat /var/output-generator/4.out
123
```

---

[← Question 13](q13-runtime-security-of-processes.md) · [Index](Certifications/LFCS/notes.md) · [Question 15 →](q15-build-and-install-from-source.md)
