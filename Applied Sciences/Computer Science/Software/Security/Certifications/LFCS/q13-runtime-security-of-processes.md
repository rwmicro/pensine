# Question 13 — Runtime Security of processes

## Énoncé

Solve this question on: `web-srv1`

There was a security alert which you need to follow up on. On server `web-srv1` there are three processes: `collector1`, `collector2`, and `collector3`. It was alerted that any of these might run periodically the per custom policy forbidden syscall `kill`.

End the process and remove the executable for those where this is true.

> You can use `strace -p PID`

## Solution

We should check the server for the mentioned processes:
```bash
ssh web-srv1
root@web-srv1:~$ ps aux | grep collector
root        3611  0.0  0.0 101924   624 ?        Sl   13:23   0:00 /bin/collector1
root        3612  0.0  0.0 101916   612 ?        Sl   13:23   0:00 /bin/collector2
root        3613  0.0  0.0 101928   616 ?        Sl   13:23   0:00 /bin/collector3
```

Now we investigate the kernel syscalls of `collector1`:
```bash
root@web-srv1:~$ strace -p 3611 # your PID will be different!
restart_syscall(<... resuming interrupted read ...>) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d4bb0, FUTEX_WAKE_PRIVATE, 1)  = 1
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
futex(0x4d7460, FUTEX_WAIT_PRIVATE, 0, {tv_sec=0, tv_nsec=999999757}) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d4bb0, FUTEX_WAKE_PRIVATE, 1)  = 1
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
futex(0x4d7460, FUTEX_WAIT_PRIVATE, 0, {tv_sec=0, tv_nsec=999999756}) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d4bb0, FUTEX_WAKE_PRIVATE, 1)  = 1
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
futex(0x4d7460, FUTEX_WAIT_PRIVATE, 0, {tv_sec=0, tv_nsec=999999699}) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d4bb0, FUTEX_WAKE_PRIVATE, 1)  = 1
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
...
```

After watching for a while, there don't seem to be any kill syscalls. Next one is `collector2`:
```bash
root@web-srv1:~$ strace -p 3612
restart_syscall(<... resuming interrupted read ...>) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d2db0, FUTEX_WAKE_PRIVATE, 1)  = 1
kill(666, SIGTERM)                      = -1 ESRCH (No such process)
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
futex(0x4d5660, FUTEX_WAIT_PRIVATE, 0, {tv_sec=0, tv_nsec=999999449}) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d2db0, FUTEX_WAKE_PRIVATE, 1)  = 1
kill(666, SIGTERM)                      = -1 ESRCH (No such process)
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
futex(0x4d5660, FUTEX_WAIT_PRIVATE, 0, {tv_sec=0, tv_nsec=999999593}) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d2db0, FUTEX_WAKE_PRIVATE, 1)  = 1
```

kill(666, SIGTERM) # there we go!

...

Gotcha! Seems like `collector2` is one bad process. Still we need to check the last one, `collector3`:
```bash
root@web-srv1:~$ strace -p 3613
restart_syscall(<... resuming interrupted read ...>) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d5bb0, FUTEX_WAKE_PRIVATE, 1)  = 1
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
futex(0x4d8460, FUTEX_WAIT_PRIVATE, 0, {tv_sec=0, tv_nsec=999999731}) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d5bb0, FUTEX_WAKE_PRIVATE, 1)  = 1
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
futex(0x4d8460, FUTEX_WAIT_PRIVATE, 0, {tv_sec=0, tv_nsec=999999722}) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d5bb0, FUTEX_WAKE_PRIVATE, 1)  = 1
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
futex(0x4d8460, FUTEX_WAIT_PRIVATE, 0, {tv_sec=0, tv_nsec=999999635}) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d5bb0, FUTEX_WAKE_PRIVATE, 1)  = 1
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
futex(0x4d8460, FUTEX_WAIT_PRIVATE, 0, {tv_sec=0, tv_nsec=999999641}) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d5bb0, FUTEX_WAKE_PRIVATE, 1)  = 1
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
...
```

Seems like only `collector2` should be terminated. First we run `ps` again to see the binary path:
```bash
root@web-srv1:~$ ps aux | grep collector2
root        3612  0.0  0.0 101916   612 ?        Sl   13:23   0:00 /bin/collector2
root@web-srv1:~$ kill 3612 # your PID will be different!
root@web-srv1:~$ ps aux | grep collector2
root@web-srv1:~$ rm /bin/collector2
```