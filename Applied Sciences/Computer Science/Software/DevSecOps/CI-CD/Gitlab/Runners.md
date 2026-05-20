---
title: "GitLab Runners"
domain: "Applied Sciences"
subdomain: "Computer Science > DevSecOps > CI-CD > Gitlab"
tags: [sciences-appliquées, informatique, devsecops]
date: "2025-05-04"
---

# GitLab Runners

## Install Gitlab-runner

A GitLab Runner is an agent that executes jobs in your CI/CD pipelines. 

```sh
# Download package
curl -L --output /usr/local/bin/gitlab-runner https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-linux-amd64

# Give running permission
chmod +x /usr/local/bin/gitlab-runner

# Create a dedicated user
useradd --comment 'GitLab Runner' --create-home gitlab-runner --shell /bin/bash

# Install and run the service
gitlab-runner install --user=gitlab-runner --working-directory=/home/gitlab-runner
gitlab-runner start
```

Here is the link from the Official GitLab Documentation for a Linux install : https://docs.gitlab.com/runner/install/linux-manually.html

## Registering your Runner

Once you’ve installed gitlab-runner on your system, you now have to register it as a runner. To do so, follow these steps:
On gitlab, go to **settings**,**CI/CD**, and expand the “**runners**” option. 

### Configuration of th Gitlab Runner
Now that you registered the runner you need to configure the parameters and follow the steps. 

```bash
sudo gitlab-runner register
```

### Modify the default parameters
Once the process is finished you can modify the default configuration. It may depends from the Linux distro but normally the file is under the path : `/etc/gitlab-runner/config.toml`.

You can check the configuration options on the Official GitLab Documentation : https://docs.gitlab.com/runner/configuration/advanced-configuration.html
