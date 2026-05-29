# Question 31 — Network Configuration

## Énoncé

Solve this question on: `web-srv1`

1. Assign the static IPv4 address `192.168.50.10/24` to interface `eth1`, with gateway `192.168.50.1` and DNS `1.1.1.1`. Make it persistent.
2. Add a static route to `10.20.0.0/16` via `192.168.50.254`.
3. Set the system hostname to `web-srv1.lan` persistently.
4. Write the MAC address of `eth0` into `/opt/course/31/mac`.

## Solution

### Inspect the current configuration

```bash
ip addr show                                    # ip a
ip -br addr                                     # brief
ip link show
ip route                                        # routing table
ip -6 route
ip neigh                                        # ARP / neighbours
ss -tulnp                                       # listening sockets
resolvectl status                               # DNS resolver (systemd-resolved)
cat /etc/resolv.conf
```

### Step 1 — Static IP

#### NetworkManager (`nmcli`) — RHEL/Fedora/Ubuntu desktop

```bash
nmcli con show                                  # list profiles
nmcli con add type ethernet ifname eth1 con-name eth1-static \
      ipv4.method manual \
      ipv4.addresses 192.168.50.10/24 \
      ipv4.gateway 192.168.50.1 \
      ipv4.dns "1.1.1.1 9.9.9.9"
nmcli con up eth1-static
nmcli con mod eth1-static ipv4.dns-search "lan"
```

#### Netplan (Ubuntu server)

Edit `/etc/netplan/01-netcfg.yaml`:
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth1:
      addresses: [192.168.50.10/24]
      routes:
        - to: default
          via: 192.168.50.1
      nameservers:
        addresses: [1.1.1.1, 9.9.9.9]
```
Apply:
```bash
sudo netplan try            # apply with rollback on failure
sudo netplan apply
```

#### systemd-networkd

Create `/etc/systemd/network/10-eth1.network`:
```ini
[Match]
Name=eth1

[Network]
Address=192.168.50.10/24
Gateway=192.168.50.1
DNS=1.1.1.1
```
```bash
sudo systemctl restart systemd-networkd
```

#### `/etc/network/interfaces` (legacy Debian)

```ini
auto eth1
iface eth1 inet static
    address 192.168.50.10/24
    gateway 192.168.50.1
    dns-nameservers 1.1.1.1
```
```bash
sudo ifup eth1
```

### Step 2 — Routes

Temporary (lost on reboot):
```bash
sudo ip route add 10.20.0.0/16 via 192.168.50.254
sudo ip route del 10.20.0.0/16
sudo ip route add default via 192.168.50.1
```

Persistent via NetworkManager:
```bash
nmcli con mod eth1-static +ipv4.routes "10.20.0.0/16 192.168.50.254"
nmcli con up eth1-static
```

### Step 3 — Hostname

```bash
hostnamectl set-hostname web-srv1.lan
cat /etc/hostname
# also update /etc/hosts to map 127.0.1.1 web-srv1.lan web-srv1
```

### Step 4 — MAC address

```bash
ip -br link show eth0 | awk '{print $3}' > /opt/course/31/mac
# or:
cat /sys/class/net/eth0/address > /opt/course/31/mac
```

### Diagnostics

```bash
ping -c 4 1.1.1.1
ping6 -c 4 fe80::1%eth0
traceroute 8.8.8.8
mtr 8.8.8.8
dig +short example.com
nslookup example.com
host example.com
ss -s                                  # socket summary
nmap -sn 192.168.50.0/24               # discover hosts (with permission)
tcpdump -i eth0 -nn port 80            # capture
```

### IPv6 quick reference

```bash
ip -6 addr add 2001:db8::1/64 dev eth0
ip -6 route add default via 2001:db8::ff
sysctl -w net.ipv6.conf.all.autoconf=0
sysctl -w net.ipv6.conf.all.accept_ra=0
```

Disable IPv6: see [[q25-sysctl-kernel-parameters]].

