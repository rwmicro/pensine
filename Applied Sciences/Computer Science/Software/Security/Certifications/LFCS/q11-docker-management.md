# Question 11 — Docker Management

## Énoncé

Solve this question on: `terminal`

Someone overheard that you're a Containerisation Specialist, so the following should be easy for you! Please:
1. Stop the Docker container named `frontend_v1`
2. Gather information from Docker container named `frontend_v2`:
    - Write its assigned ip address into `/opt/course/11/ip-address`
    - It has one volume mount. Write the volume mount destination directory into `/opt/course/11/mount-destination`
3. Start a new detached Docker container:
    - Name: `frontend_v3`
    - Image: `nginx:alpine`
    - Memory limit: `30m` (30 Megabytes)
    - TCP Port map: `1234/host` => `80/container`

## Solution

_Dockerfile_: list of commands from which an _Image_ can be build

_Image_: binary file which includes all data/requirements to be run as a _Container_

_Container_: running instance of an _Image_

_Registry_: place where we can push/pull _Images_ to/from

We first list all Docker containers:
```bash
sudo docker ps
CONTAINER ID   IMAGE          COMMAND                  CREATED          STATUS          PORTS     NAMES
a9b334cfaae0   nginx:alpine   "/docker-entrypoint.…"   11 minutes ago   Up 11 minutes   80/tcp    frontend_v1
e68fa28f231d   nginx:alpine   "/docker-entrypoint.…"   7 minutes ago    Up 7 minutes    80/tcp    frontend_v2
```

### Step 1
For the first step we stop the container:
```bash
sudo docker stop frontend_v1
frontend_v1
sudo docker ps -a  # show also stopped containers using "ps -a"
CONTAINER ID   IMAGE          ...  CREATED          STATUS                      PORTS     NAMES
e68fa28f231d   nginx:alpine   ...  8 minutes ago    Up 8 minutes                80/tcp    frontend_v2
a9b334cfaae0   nginx:alpine   ...  13 minutes ago   Exited (0) 45 seconds ago             frontend_v1
```

### Step 2
Docker inspect provides the container configuration in JSON format which contains all information asked for in this task:
```bash
sudo docker inspect frontend_v2
        "Mounts": [
            {
                "Type": "bind",
                "Source": "/var/www",
                "Destination": "/srv",                 # WE NEED THIS
                "Mode": "",
                "RW": true,
                "Propagation": "rprivate"
            }
        ],
...
        "NetworkSettings": {
            "Bridge": "",
            "SandboxID": "a550576248b3f6c15211c2ad10efc421c7b48285cd69d57b64d8dc7b1b59e0ef",
            "HairpinMode": false,
...
            "Networks": {
                "bridge": {
                    "IPAMConfig": null,
                    "Links": null,
                    "Aliases": null,
                    "NetworkID": "5889aae0b056e4f944d6fb9afd8edd26ecd589c5e45b7533b59c878138fb5625",
                    "EndpointID": "954fcc88c2b64ef9ba3809eb130060ceb064301c4906b4a7ab0902be6153eedb",
                    "Gateway": "172.17.0.1",
                    "IPAddress": "172.17.0.3",         # WE NEED THIS
                    "IPPrefixLen": 16,
                    "IPv6Gateway": "",
                    "GlobalIPv6Address": "",
                    "GlobalIPv6PrefixLen": 0,
                    "MacAddress": "02:42:ac:11:00:03",
                    "DriverOpts": null
                }
            }
        }
```

It's probably a good idea to search in the inspect output for specific values. For this we could open the output directly in vim:
```bash
sudo docker inspect frontend_v2 | vim -
```

Now we only have to create the required files with their correct content (your container ip address might differ):
```bash
echo "172.17.0.3" > /opt/course/11/ip-address
echo "/srv" > /opt/course/11/mount-destination
```

Which results in:
```bash
# /opt/course/11/ip-address
172.17.0.3
# /opt/course/11/mount-destination
/srv
```

### Step 3
Finally we can start our own container! Unfortunately with very strict conditions to follow... so let's obey!

The help output for `docker run` usually provides all that's needed:
```bash
sudo docker run --help
Usage:  docker run [OPTIONS] IMAGE [COMMAND] [ARG...]      # the order of arguments is important
```

Run a command in a new container

Options:

      --add-host list                  Add a custom host-to-IP mapping (host:ip)

  -a, --attach list                    Attach to STDIN, STDOUT or STDERR

...

      --cpus decimal                   Number of CPUs

      --cpuset-cpus string             CPUs in which to allow execution (0-3, 0,1)

      --cpuset-mems string             MEMs in which to allow execution (0-3, 0,1)

  -d, --detach                         Run container in background and print container ID    # need this

      --detach-keys string             Override the key sequence for detaching a container

      --device list                    Add a host device to the container

      --device-cgroup-rule list        Add a rule to the cgroup allowed devices list

...

      --mount mount                    Attach a filesystem mount to the container

      --name string                    Assign a name to the container                        # need this

      --network network                Connect a container to a network

...

      --pids-limit int                 Tune container pids limit (set -1 for unlimited)

      --platform string                Set platform if server is multi-platform capable

      --privileged                     Give extended privileges to this container

  -p, --publish list                   Publish a containers port(s) to the host              # need this

  -P, --publish-all                    Publish all exposed ports to random ports

...

Using this we can build the necessary run command:
```bash
sudo docker run -d --name frontend_v3 --memory 30m -p 1234:80 nginx:alpine
1e7d4612df4aff82c96d2c65102966561038ebfb94a996c86afebf6e3cb1432a
```

In case the above command throws iptables errors we can restart the docker service:
```bash
sudo docker rm --force frontend_v3 # delete existing container
sudo service docker restart        # restart docker servier
```

Because of the port mapping we should now be able to do:
```bash
curl localhost:1234
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
html { color-scheme: light dark; }
body { width: 35em; margin: 0 auto;
font-family: Tahoma, Verdana, Arial, sans-serif; }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>
<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>
<p><em>Thank you for using nginx.</em></p>
</body>
</html>
```

---

[← Question 10](q10-sshfs-and-nfs.md) · [Index](Certifications/LFCS/notes.md) · [Question 12 →](q12-git-workflow.md)
