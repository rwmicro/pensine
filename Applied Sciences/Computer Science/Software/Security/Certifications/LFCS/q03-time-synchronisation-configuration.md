# Question 3 — Time synchronisation Configuration

## Énoncé

Solve this question on: `terminal`

Time synchronisation configuration needs to be updated:
1. Set `0.pool.ntp.org` and `1.pool.ntp.org` as main NTP servers
2. Set `ntp.ubuntu.com` and `0.debian.pool.ntp.org` as fallback NTP servers
3. The maximum poll interval should be `1000` seconds and the connection retry `20` seconds

## Solution

> ℹ️ Use `man timesyncd.conf` for help
A good idea would probably to take a look at the current situation:
```bash
timedatectl
               Local time: Sun 2023-06-11 16:29:05 UTC
           Universal time: Sun 2023-06-11 16:29:05 UTC
                 RTC time: Sun 2023-06-11 16:29:05
                Time zone: UTC (UTC, +0000)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no
```

Here we see for example the current local time and timezone. Let's open the configuration:
```bash
sudo vim /etc/systemd/timesyncd.conf
[Time]
NTP=0.de.pool.ntp.org 1.de.pool.ntp.org 2.de.pool.ntp.org
```

We see three german NTP servers currently configured via setting `NTP`.

**Test NTP servers**

We can test single NTP servers manually for a sense of certainty:
```bash
ntpdate -q 0.de.pool.ntp.org # just query, don't update
server 85.215.93.134, stratum 2, offset -0.000523, delay 0.05086
server 85.214.46.39, stratum 3, offset +0.001502, delay 0.04944
server 129.70.132.32, stratum 2, offset -0.003332, delay 0.04881
server 141.82.25.202, stratum 2, offset -0.001288, delay 0.04404
11 Jun 15:50:41 ntpdate[3043]: adjust time server 141.82.25.202 offset -0.001288 sec
ntpdate -q www.google.de # that one won't work
11 Jun 15:49:40 ntpdate[3042]: no server suitable for synchronization found
```

Above we see one successful request and one to `www.google.de` that failed. This is correct because the Google web-domain doesn't provide a NTP service.

### Step 1 — Main servers
We adjust the config:
```bash
sudo vim /etc/systemd/timesyncd.conf
[Time]
NTP=0.pool.ntp.org 1.pool.ntp.org
```

### Step 2 — Fallback servers
Often times various settings are already included in the `timesyncd.conf` but commented out. Here it seems that we've to work with a pretty clean file. Hence we can use `man timesyncd.conf` for help:

[Time]

NTP=0.pool.ntp.org 1.pool.ntp.org

FallbackNTP=ntp.ubuntu.com 0.debian.pool.ntp.org

### Step 3 — Remaining settings
Here we also use the man pages as help:

[Time]

NTP=0.pool.ntp.org 1.pool.ntp.org

FallbackNTP=ntp.ubuntu.com 0.debian.pool.ntp.org

PollIntervalMaxSec=1000

ConnectionRetrySec=20

### Final — Restart service
Now we restart the service:
```bash
sudo service systemd-timesyncd restart
```

Good to check the service status for warnings or errors:
```bash
sudo service systemd-timesyncd status
● systemd-timesyncd.service - Network Time Synchronization
     Loaded: loaded (/lib/systemd/system/systemd-timesyncd.service; enabled; vendor preset: enabled)
```

     Active: active (running) since Thu 2023-07-27 15:40:11 UTC; 2s ago

       Docs: man:systemd-timesyncd.service(8)

   Main PID: 161213 (systemd-timesyn)

     Status: "Initial synchronization to time server 162.159.200.123:123 (0.pool.ntp.org)."

      Tasks: 2 (limit: 2234)

     Memory: 1.3M

        CPU: 100ms

     CGroup: /system.slice/systemd-timesyncd.service

             └─161213 /lib/systemd/systemd-timesyncd

Jul 27 15:40:11 terminal systemd[1]: Starting Network Time Synchronization...

Jul 27 15:40:11 terminal systemd[1]: Started Network Time Synchronization.

Jul 27 15:40:11 terminal systemd-timesyncd[161213]: Initial synchronization to time server 162.159.200.123:123 (0.pool.ntp.org).

Status output looking good. In the logs above we can see which NTP server was used for synchronisation. We could also check the logs with:
```bash
sudo grep systemd-timesyncd /var/log/syslog
...
Jul 27 15:40:11 ubuntu2204 systemd[1]: systemd-timesyncd.service: Deactivated successfully.
```

Jul 27 15:40:11 ubuntu2204 systemd-timesyncd[161213]: Initial synchronization to time server 162.159.200.123:123 (0.pool.ntp.org).

Server `0.pool.ntp.org` was used here which means our configuration change worked.