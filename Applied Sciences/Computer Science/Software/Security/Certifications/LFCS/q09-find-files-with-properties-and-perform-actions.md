# Question 9 — Find files with properties and perform actions

## Énoncé

Solve this question on: `data-001`

There is a backup folder on server `data-001` at `/var/backup/backup-015`, it needs to be cleaned up.

First:
- Delete all files modified before `01/01/2020`
Then for the remaining:
- Find all files smaller than `3KiB` and move these to `/var/backup/backup-015/small/`
- Find all files larger than `10KiB` and move these to `/var/backup/backup-015/large/`
- Find all files with permission `777` and move these to `/var/backup/backup-015/compromised/`

## Solution

First we find the backup location:
```bash
ssh data-001
root@data-001:~$ cd /var/backup/backup-015
root@data-001:/var/backup/backup-015$ ls | grep backup | wc -l
300
```

Seems to contain good amount of files! Now we need to clean it up. A good way for this is to use `find` with arguments and a command to execute, like:

find -exec echo {} \; # will find all files and runs "echo FILE" for each

find -exec echo {} +  # will find all files and runs "echo FILE1 FILE2 FILE3 ..."

man find # search for "exec" to see info and explanation

man find # search for "-newerXY" to find files "newer than date"

**Delete files before date**

Using this we can delete all files created before 2020. Always "debug" a command first by just listing without executing a command:
```bash
root@data-001:/var/backup/backup-015$ find ! -newermt "01/01/2020" -type f
...
root@data-001:/var/backup/backup-015$ find ! -newermt "01/01/2020" -type f | wc -l
21
root@data-001:/var/backup/backup-015$ find ! -newermt "01/01/2020" -type f -exec rm {} \;
root@data-001:/var/backup/backup-015$ ls | grep backup | wc -l
279 # 21 deleted
```

**Move small files**

Now we move all small files into the subfolder:
```bash
root@data-001:/var/backup/backup-015$ find -maxdepth 1 -size -3k -type f # find
...
root@data-001:/var/backup/backup-015$ find -maxdepth 1 -size -3k -type f | wc -l
24
root@data-001:/var/backup/backup-015$ find -maxdepth 1 -size -3k -type f -exec mv {} ./small \; # move
```

**Move large files**

Next we move all larger files into the subfolder:
```bash
root@data-001:/var/backup/backup-015$ find -maxdepth 1 -size +10k -type f # find
...
root@data-001:/var/backup/backup-015$ find -maxdepth 1 -size +10k -type f | wc -l
11
root@data-001:/var/backup/backup-015$ find -maxdepth 1 -size +10k -type f -exec mv {} ./large \; # move
```

**Move open permission files**

And finally we move all files with too open permissions into the subfolder:
```bash
root@data-001:/var/backup/backup-015$ find -maxdepth 1 -perm 777 -type f # find
...
root@data-001:/var/backup/backup-015$ find -maxdepth 1 -perm 777 -type f | wc -l
12
root@data-001:/var/backup/backup-015$ find -maxdepth 1 -perm 777 -type f -exec mv {} ./compromised \; # move
```

### Result
```bash
root@data-001:/var/backup/backup-015$ ls | grep backup | wc -l
232
root@data-001:/var/backup/backup-015$ ls small/ | wc -l
24
root@data-001:/var/backup/backup-015$ ls large/ | wc -l
11
root@data-001:/var/backup/backup-015$ ls compromised/ | wc -l
12
```

---

[← Question 8](q08-disk-management.md) · [Index](Certifications/LFCS/notes.md) · [Question 10 →](q10-sshfs-and-nfs.md)
