# Question 27 — Bash Scripting

## Énoncé

Solve this question on: `terminal`

Write a bash script `/opt/course/27/backup.sh` that:
1. Takes one argument: the directory to back up.
2. Creates a `tar.gz` archive named `<basename>-YYYYMMDD.tar.gz` under `/var/backups/`.
3. Exits with code `1` if the argument is missing or the directory does not exist.
4. Logs the result (success / failure) to `/var/log/backup.log` with a timestamp.

Make the script executable. Schedule it to run daily at 02:30 via cron for `/etc/`.

## Solution

```bash
sudo tee /opt/course/27/backup.sh > /dev/null <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

LOG=/var/log/backup.log
DEST=/var/backups

log() {
  echo "$(date '+%F %T') $*" >> "$LOG"
}

if [[ $# -lt 1 ]]; then
  log "ERROR missing argument"
  echo "Usage: $0 <directory>" >&2
  exit 1
fi

SRC=$1

if [[ ! -d "$SRC" ]]; then
  log "ERROR $SRC is not a directory"
  exit 1
fi

NAME=$(basename "$SRC")
DATE=$(date +%Y%m%d)
ARCHIVE="$DEST/${NAME}-${DATE}.tar.gz"

mkdir -p "$DEST"

if tar -czf "$ARCHIVE" -C "$(dirname "$SRC")" "$NAME"; then
  log "OK $ARCHIVE"
else
  log "FAIL $ARCHIVE"
  exit 1
fi
EOF

sudo chmod +x /opt/course/27/backup.sh
```

Add the cron entry:
```bash
echo '30 2 * * * root /opt/course/27/backup.sh /etc' | sudo tee /etc/cron.d/backup-etc
```

### Bash essentials worth recognising

**Shebang + safe flags**
```bash
#!/usr/bin/env bash
set -e          # exit on first error
set -u          # error on unset variable
set -o pipefail # fail if any pipe stage fails
set -x          # trace (debug)
```

**Variables and quoting**
```bash
name="alice"
echo "$name"            # expand
echo '$name'            # literal
echo "${name^^}"        # uppercase
echo "${file%.txt}"     # strip suffix
echo "${file##*/}"      # basename
echo "${file%/*}"       # dirname
echo "${var:-default}"  # default if unset
echo "${#name}"         # length
```

**Conditionals**
```bash
if [[ -f $file ]]; then ... fi          # file exists
if [[ -d $dir ]]; then ... fi           # directory
if [[ -z $var ]]; then ... fi           # empty
if [[ $a == $b ]]; then ... fi
if [[ $n -gt 10 ]]; then ... fi
[[ -r $f && -w $f ]] && echo "rw"
```

**Loops**
```bash
for f in *.log; do echo "$f"; done
for i in {1..10}; do echo $i; done
while read -r line; do echo "$line"; done < file.txt
until [[ -e /tmp/ready ]]; do sleep 1; done
```

**Functions and exit codes**
```bash
greet() {
  local name=$1
  echo "Hello $name"
  return 0
}
greet "Bob"
echo "last exit: $?"
```

**Arguments**

| Token | Meaning |
|---|---|
| `$0` | script name |
| `$1`…`$9` | positional args |
| `$#` | number of args |
| `$@` | all args (each quoted) |
| `$*` | all args (one string) |
| `$$` | current PID |
| `$?` | last exit code |
| `$!` | PID of last backgrounded job |

**Argument parsing with getopts**
```bash
while getopts "vf:" opt; do
  case $opt in
    v) verbose=1 ;;
    f) file=$OPTARG ;;
    *) echo "usage..." >&2; exit 1 ;;
  esac
done
shift $((OPTIND-1))
```

**Trap (cleanup on exit)**
```bash
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT
```

---

[← Question 26](q26-package-management.md) · [Index](Certifications/LFCS/notes.md) · [Question 28 →](q28-permissions-and-acl.md)
