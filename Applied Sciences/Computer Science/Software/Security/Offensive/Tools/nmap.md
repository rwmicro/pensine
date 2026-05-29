---
title: "Why nmap choose to scan these ports ?"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Offensive > Tools"
tags: [sciences-appliquées, informatique, sécurité, réseau]
date: "2025-02-15"
---

nmap is a command line interface port scanner. 

> A ttl of 128 means that the operating system is probably Windows

# Why nmap choose to scan these ports ?
By default, nmap creates a map of the most frequently used ports. If the user performs a simple `nmap IP` scan. The command will scan the 1000 most used ports. You can find this map in the `/usr/share/nmap/nmap-services` file.

## Scanning Options

| **Nmap Option**      | **Description**                                                        |
| -------------------- | ---------------------------------------------------------------------- |
| `-sn`                | Disables port scanning.                                                |
| `-Pn`                | Disables ICMP Echo Requests                                            |
| `-n`                 | Disables DNS Resolution.                                               |
| `-PE`                | Performs the ping scan by using ICMP Echo Requests against the target. |
| `--packet-trace`     | Shows all packets sent and received.                                   |
| `--reason`           | Displays the reason for a specific result.                             |
| `--disable-arp-ping` | Disables ARP Ping Requests.                                            |
| `--top-ports=<num>`  | Scans the specified top ports that have been defined as most frequent. |
| `-p-`                | Scan all ports.                                                        |
| `-p22-110`           | Scan all ports between 22 and 110.                                     |
| `-p22,25`            | Scans only the specified ports 22 and 25.                              |
| `-F`                 | Scans top 100 ports.                                                   |
| `-sS`                | Performs an TCP SYN-Scan.                                              |
| `-sA`                | Performs an TCP ACK-Scan.                                              |
| `-sU`                | Performs an UDP Scan.                                                  |
| `-sV`                | Scans the discovered services for their versions.                      |
| `-sC`                | Perform a Script Scan with scripts that are categorized as "default".  |
| `--script <script>`  | Performs a Script Scan by using the specified scripts.                 |
| `-O`                 | Performs an OS Detection Scan to determine the OS of the target.       |
| `-A`                 | Performs OS Detection, Service Detection, and traceroute scans.        |
| `-D RND:5`           | Sets the number of random Decoys that will be used to scan the target. |
| `-e`                 | Specifies the network interface that is used for the scan.             |
| `-S 10.10.10.200`    | Specifies the source IP address for the scan.                          |
| `-g`                 | Specifies the source port for the scan.                                |
| `--dns-server <ns>`  | DNS resolution is performed by using a specified name server.          |

## Output Options

|**Nmap Option**|**Description**|
|---|---|
|`-oA filename`|Stores the results in all available formats starting with the name of "filename".|
|`-oN filename`|Stores the results in normal format with the name "filename".|
|`-oG filename`|Stores the results in "grepable" format with the name of "filename".|
|`-oX filename`|Stores the results in XML format with the name of "filename".|

## Performance Options

|**Nmap Option**|**Description**|
|---|---|
|`--max-retries <num>`|Sets the number of retries for scans of specific ports.|
|`--stats-every=5s`|Displays scan's status every 5 seconds.|
|`-v/-vv`|Displays verbose output during the scan.|
|`--initial-rtt-timeout 50ms`|Sets the specified time value as initial RTT timeout.|
|`--max-rtt-timeout 100ms`|Sets the specified time value as maximum RTT timeout.|
|`--min-rate 300`|Sets the number of packets that will be sent simultaneously.|
|`-T <0-5>`|Specifies the specific timing template.|


## Available scirpts
Nmap proposes a lot of script for specific usage each. 

|**Category**|**Description**|**Example Scripts**|
|---|---|---|
|**Auth**|Scripts for authentication bypass or testing.|`http-auth`, `ssh-auth-methods`, `smb-brute`|
|**Broadcast**|Discovers hosts on a network using broadcast and multicast.|`broadcast-dhcp-discover`, `broadcast-ping`|
|**Brute**|Performs brute-force password attacks.|`ftp-brute`, `http-brute`, `smtp-brute`|
|**Default**|Default scripts run with `-sC` or `--script=default`.|`ssl-cert`, `dns-service-discovery`, `http-title`|
|**Discovery**|Finds hosts, services, or information about the target.|`dns-zone-transfer`, `snmp-brute`, `ssh-hostkey`|
|**Dos**|Tests or executes Denial of Service (DoS) attacks.|`syn-flood`, `http-slowloris`|
|**Exploit**|Exploits vulnerabilities on the target system.|`http-shellshock`, `ms08-067`, `cve-2020-0796`|
|**External**|Uses external web services to gather information.|`ip-geolocation`, `whois`|
|**Fuzzer**|Fuzzes services to find potential vulnerabilities.|`ftp-fuzz`, `http-fuzz`|
|**Intrusive**|Performs intrusive or potentially harmful checks.|`http-sql-injection`, `smb-vuln-ms17-010`|
|**Malware**|Detects malware or backdoors.|`http-malware-host`, `irc-botnet-channels`|
|**Safe**|Scripts considered non-intrusive and safe for production systems.|`banner`, `http-headers`|
|**Version**|Enhances version detection for services.|`ssl-enum-ciphers`, `http-server-header`|
|**Vuln**|Detects known vulnerabilities in software.|`http-vuln-cve2017-5638`, `smb-vuln-ms08-067`|

To explore all available scripts on your system, you can use the following command:
```bash
ls /usr/share/nmap/scripts
```

You can count them via the command: 
```bash
ls /usr/share/nmap/scripts | wc -l
```

Or use `nmap` directly to list them:
```bash
nmap --script-help all
```
