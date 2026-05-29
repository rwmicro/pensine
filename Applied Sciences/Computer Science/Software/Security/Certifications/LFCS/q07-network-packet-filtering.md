# Question 7 — Network Packet Filtering

## Énoncé

Solve this question on: `data-002`

Server `data-002` is used for big data and provides internally used apis for various data operations. You're asked to implement network packet filters on interface `eth0` on `data-002`:
1. Port `5000` should be closed
2. Redirect all traffic on port `6000` to local port `6001`
3. Port `6002` should only be accessible from IP `192.168.10.80` (server `data-001`)
4. Block all outgoing traffic to IP `192.168.10.70` (server `app-srv1`)

> In case of misconfiguration you can still access the instance using `sudo lxc exec data-002 bash`

## Solution

First we could test the mentioned ports on `data-002` from remote:
```bash
curl data-002:5000
app on port 5000
curl data-002:6000
curl: (7) Failed to connect to data-002 port 6000 after 4 ms: Connection refused
curl data-002:6001
app on port 6001
curl data-002:6002
app on port 6002
```

Further we can check for existing iptables rules and interfaces, because we're asked to implement the filters for `eth0`:
```bash
ssh data-002
root@data-002:~$ iptables -L
Chain INPUT (policy ACCEPT)
target     prot opt source               destination
Chain FORWARD (policy ACCEPT)
target     prot opt source               destination
Chain OUTPUT (policy ACCEPT)
target     prot opt source               destination
root@data-002:~$ iptables -L -t nat
Chain PREROUTING (policy ACCEPT)
target     prot opt source               destination
Chain INPUT (policy ACCEPT)
target     prot opt source               destination
Chain OUTPUT (policy ACCEPT)
target     prot opt source               destination
Chain POSTROUTING (policy ACCEPT)
target     prot opt source               destination
root@data-002:~$ ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
26: eth0@if27: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 00:16:3e:6c:54:78 brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet 192.168.10.90/24 metric 100 brd 192.168.10.255 scope global dynamic eth0
       valid_lft 2752sec preferred_lft 2752sec
    inet6 fd42:a4f:8f61:21e3:216:3eff:fe6c:5478/64 scope global dynamic mngtmpaddr noprefixroute
       valid_lft 3305sec preferred_lft 3305sec
    inet6 fe80::216:3eff:fe6c:5478/64 scope link
       valid_lft forever preferred_lft forever
```

Above we can see the `etc0` interface and that there are no existing iptables rules implemented.

### Step 1
We're asked to close port `5000` and are going to use iptables for it:
```bash
root@data-002:~$ iptables -A INPUT -i eth0 -p tcp --dport 5000 -j DROP
root@data-002:~$ iptables -L
Chain INPUT (policy ACCEPT)
target     prot opt source               destination
DROP       tcp  --  anywhere             anywhere             tcp dpt:5000 # new rule
Chain FORWARD (policy ACCEPT)
target     prot opt source               destination
Chain OUTPUT (policy ACCEPT)
target     prot opt source               destination
```

Done, let's give it a test:
```bash
root@data-002:~$ curl localhost:5000   # still works on localhost
app on port 5000
root@data-002:~$ exit
curl data-001:5000                     # blocked from remote
curl: (7) Failed to connect to data-001 port 5000 after 0 ms: Connection refused
```

### Step 2
Now we're going to perform some NAT for connections on port `6000`:
```bash
root@data-002:~$ iptables -A PREROUTING -i eth0 -t nat -p tcp --dport 6000 -j REDIRECT --to-port 6001
View existing NAT rules:
root@data-002:~$ iptables -L -t nat
Chain PREROUTING (policy ACCEPT)
target     prot opt source               destination
REDIRECT   tcp  --  anywhere             anywhere             tcp dpt:x11 redir ports 6001 # new rule
Chain INPUT (policy ACCEPT)
target     prot opt source               destination
Chain OUTPUT (policy ACCEPT)
target     prot opt source               destination
Chain POSTROUTING (policy ACCEPT)
target     prot opt source               destination
```

If we would like to clear these we could run `iptables -F -t nat`. Let's test the result:
```bash
root@data-002:~$ curl localhost:6000 # fail
curl: (7) Failed to connect to localhost port 6000 after 0 ms: Connection refused
root@data-002:~$ exit
curl data-002:6000 # fail
app on port 6001
```

Above we see the redirect from `6000` to `6001` works.

### Step 3
Now we're asked to open port `6002` only from a specific source IP:
```bash
root@data-002:~$ iptables -A INPUT -i eth0 -p tcp --dport 6002 -s 192.168.10.80 -j ACCEPT
root@data-002:~$ iptables -A INPUT -i eth0 -p tcp --dport 6002 -j DROP
```

The idea there is that we first allow that IP and then deny all other traffic on that port. Let's verify it:
```bash
curl data-002:6002
^C # timeout
ssh data-001
root@data-001:~$ curl data-002:6002
app on port 6002 # success
```

### Step 4
In the final step we need to drop outgoing packages:
```bash
root@data-002:~$ nc app-srv1 22
SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.1
^C  # success
root@data-002:~$ iptables -A OUTPUT -d 192.168.10.70 -p tcp -j DROP
root@data-002:~$ nc app-srv1 22
^C  # timeout
root@data-002:~$ nc data-001 22
SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.1
^C  # success
```

Above we can see that outgoing connections to `app-srv1` no longer work and they time out.