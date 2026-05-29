# Question 12 — Git Workflow

## Énoncé

Solve this question on: `terminal`

You're asked to perform changes in the Git repository of the Auto-Verifier app:
1. Clone repository `/repositories/auto-verifier` to `/home/candidate/repositories/auto-verifier`.
    _Perform the following steps in the newly cloned directory_
2. Find the one of the branches `dev4`, `dev5` and `dev6` in which file `config.yaml` contains `user_registration_level: open`. Merge only that branch into branch `main`
3. In branch `main` create a new directory `logs` on top repository level. To ensure the directory will be committed create hidden empty file `.keep` in it
4. Commit your change with message `added log directory`

## Solution

### Step 1 — Clone Repository
Git is most often used to clone from and work with remote repositories on like Github or Gitlab. But most of Git functionality can also be used locally. We go ahead and clone the local directory:
```bash
git clone /repositories/auto-verifier ~/repositories/auto-verifier
Cloning into '/home/candidate/repositories/auto-verifier'...
done.
cd ~/repositories/auto-verifier
~/repositories/auto-verifier$ git status
```

On branch main

Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean

### Step 2 — Find the correct branch
First we list all branches:
```bash
~/repositories/auto-verifier$ git branch
```

* main
```bash
~/repositories/auto-verifier$ git branch -a
```

* main
  remotes/origin/HEAD -> origin/main

  remotes/origin/dev4

  remotes/origin/dev5

  remotes/origin/dev6

  remotes/origin/main

We can simply move through all branches and check the file content:
```bash
~/repositories/auto-verifier$ git checkout dev4
```

Branch 'dev4' set up to track remote branch 'dev4' from 'origin'.

Switched to a new branch 'dev4'
```bash
~/repositories/auto-verifier$ grep user_registration_level config.yaml
user_registration_level: closed
~/repositories/auto-verifier$ git checkout dev5
```

Branch 'dev5' set up to track remote branch 'dev5' from 'origin'.

Switched to a new branch 'dev5'
```bash
~/repositories/auto-verifier$ grep user_registration_level config.yaml
user_registration_level: open
# Match! We could've stopped here, but let's also check the final branch
~/repositories/auto-verifier$ git checkout dev6
```

Branch 'dev6' set up to track remote branch 'dev6' from 'origin'.

Switched to a new branch 'dev6'
```bash
~/repositories/auto-verifier$ grep user_registration_level config.yaml
user_registration_level: closed
```

We could also check the commit that actually performed the change:
```bash
~/repositories/auto-verifier$ git checkout dev5
```

Branch 'dev5' set up to track remote branch 'dev5' from 'origin'.

Switched to a new branch 'dev5'
```bash
~/repositories/auto-verifier$ git log
commit cdf23b8c4000a4ff280f4feced059888e99d63e4 (HEAD -> dev5, origin/dev5)
Author: manager <manager@auto-verifier>
Date:   Tue Jan 10 17:03:55 2023 +1000
    updated config.yaml
commit 40842892dd0858eb96533654d5682c2c8b2ccb5c (origin/main, origin/HEAD, main)
Author: manager <manager@auto-verifier>
Date:   Fri Jan 6 06:33:43 2023 +1000
    set user_registration_level to closed
commit 9b73a28f2c87c6b34b9a779f5e82b4ebbf8bc78c
Author: manager <manager@auto-verifier>
Date:   Thu Jan 5 20:19:58 2023 +1000
    start of something cool
~/repositories/auto-verifier$ git diff main
diff --git a/config.yaml b/config.yaml
index bbbfb9b..5d1ccb4 100755
--- a/config.yaml
+++ b/config.yaml
@@ -31,7 +31,7 @@ system_transport_50x_list: 50x
 system_transport_50x_dsn: 'srv://default?list=50x'
 system_transport_50x_retry_strategy:
 system_transport_50x_ax_retries: 3
-user_registration_level: closed
+user_registration_level: open   # the change
 user_registration_enabled: false
 user_free_labels_enabled: true
 user_email_verify_enabled: true
```

Another way could also be to compare from branch `main` without actually switching into another:
```bash
~/repositories/auto-verifier$ git branch -a
```

* main
  remotes/origin/HEAD -> origin/main

  remotes/origin/dev4

  remotes/origin/dev5

  remotes/origin/dev6

  remotes/origin/main
```bash
~/repositories/auto-verifier$ git diff origin/dev5
diff --git a/config.yaml b/config.yaml
index 5d1ccb4..bbbfb9b 100755
--- a/config.yaml
+++ b/config.yaml
@@ -31,7 +31,7 @@ system_transport_50x_list: 50x
 system_transport_50x_dsn: 'srv://default?list=50x'
 system_transport_50x_retry_strategy:
 system_transport_50x_ax_retries: 3
-user_registration_level: open
+user_registration_level: closed
 user_registration_enabled: false
 user_free_labels_enabled: true
 user_email_verify_enabled: true
```

Now we simply have to merge branch `dev5` into `main`:
```bash
~/repositories/auto-verifier$git checkout main
Switched to branch 'main'
```

Your branch is up to date with 'origin/main'.
```bash
~/repositories/auto-verifier$ git branch
  dev4
  dev5
  dev6
```

* main
```bash
~/repositories/auto-verifier$ git merge dev5
```

Updating 4084289..cdf23b8

Fast-forward

 config.yaml | 2 +-

 1 file changed, 1 insertion(+), 1 deletion(-)
```bash
~/repositories/auto-verifier$ grep user_registration_level config.yaml
user_registration_level: open
```

### Step 3 — Create new directory
We're asked to create new directory, let's see what happens if we try to commit it just like that:
```bash
~/repositories/auto-verifier$ mkdir logs
~/repositories/auto-verifier$ ls -l
total 20
-rwxrwxr-x 1 candidate candidate 2015 Jul 27 14:20 config.yaml
drwxrwxr-x 2 candidate candidate 4096 Jul 27 14:16 lib
drwxrwxr-x 2 candidate candidate 4096 Jul 27 14:29 logs
-rwxrwxr-x 1 candidate candidate  205 Jul 27 14:16 main.go
-rwxrwxr-x 1 candidate candidate  133 Jul 27 14:16 README.md
~/repositories/auto-verifier$ git status
```

On branch main

Your branch is ahead of 'origin/main' by 1 commit.

  (use "git push" to publish your local commits)

nothing to commit, working tree clean

Above we see that `git status` doesn't list the directory at all because it's empty. This means that it wouldn't be included in commits too. Now we add the requested file and see if things change:
```bash
~/repositories/auto-verifier$ touch logs/.keep
~/repositories/auto-verifier$ git status
```

On branch main

Your branch is ahead of 'origin/main' by 1 commit.

  (use "git push" to publish your local commits)

Untracked files:

  (use "git add <file>..." to include in what will be committed)

        logs/

nothing added to commit but untracked files present (use "git add" to track)

That looks better!

### Step 4 — Commit
Always best to confirm what's going to be committed:
```bash
~/repositories/auto-verifier$ git status
```

On branch main

Your branch is ahead of 'origin/main' by 1 commit.

  (use "git push" to publish your local commits)

Untracked files:

  (use "git add <file>..." to include in what will be committed)

        logs/
```bash
~/repositories/auto-verifier$ git add logs
~/repositories/auto-verifier$ git status
```

On branch main

Your branch is ahead of 'origin/main' by 1 commit.

  (use "git push" to publish your local commits)

Changes to be committed:

  (use "git restore --staged <file>..." to unstage)

        new file:   logs/.keep
```bash
~/repositories/auto-verifier$ git commit -m 'added log directory'
[main 3cc53ed] added log directory
 1 file changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 logs/.keep
```
