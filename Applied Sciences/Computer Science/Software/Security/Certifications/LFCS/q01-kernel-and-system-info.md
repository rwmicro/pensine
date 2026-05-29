# Question 1 — Kernel and System Info

## Énoncé

Solve this question on: `terminal`

Write the Linux Kernel release into `/opt/course/1/kernel`.

Write the current value of Kernel parameter `ip_forward` into `/opt/course/1/ip_forward`.

Write the system timezone into `/opt/course/1/timezone`.

> If no server is mentioned in the question text, you'll need to create your solution on the default `terminal`

## Solution

```bash
# display kernel version
uname -r
# output value of kernel parameter
cat /proc/sys/net/ipv4/ip_forward
# get current timezone
date +%Z
cat /etc/timezone # also possible
```

The files should look like:
```bash
# /opt/course/1/kernel
5.15.0-69-generic
# /opt/course/1/ip_forward
1
# /opt/course/1/timezone
UTC
```
