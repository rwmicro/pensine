# Question 23 — Process Management

## Notes d'apprentissage

Un processus est un programme en cours d'exécution, identifié par un **PID**. L'administrateur doit savoir les retrouver, ajuster leur priorité, et leur envoyer des signaux.

**Modèle mental : trouver → prioriser → signaler.**

**1. Retrouver un processus.** Plusieurs angles d'attaque selon ce qu'on connaît :
```bash
ps aux                    # photo de tous les processus
pgrep -u bob sleep        # PID par nom + utilisateur
ss -tlnp | grep :8080     # quel processus écoute sur un port
lsof -i :8080             # idem, autre outil
```
Relier un **port** à un **PID** (`ss -tlnp`) est un grand classique d'examen et de diagnostic réseau.

**2. Prioriser : la niceness.** Le *nice* règle la part de CPU qu'un processus accepte de céder.
```
-20 ◄──────────── priorité ────────────► +19
plus prioritaire        (0 = défaut)     plus "gentil" (cède le CPU)
```
Seul **root** peut *baisser* la valeur (rendre plus prioritaire). `nice` lance un processus avec une priorité, `renice` change celle d'un processus déjà en cours sans le tuer.

**3. Signaler.** Un signal est un message asynchrone envoyé à un processus :

| Signal | N° | Effet |
|---|---|---|
| `SIGHUP` | 1 | souvent « recharge ta config » |
| `SIGINT` | 2 | Ctrl+C |
| `SIGTERM` | 15 | arrêt **propre** (défaut de `kill`) |
| `SIGKILL` | 9 | tue sans recours (non interceptable) |
| `SIGSTOP`/`SIGCONT` | — | suspendre / reprendre |

Réflexe : toujours `SIGTERM` d'abord (laisse le processus se fermer proprement), `SIGKILL` seulement s'il résiste.

**Job control (premier/arrière-plan)** : `&` lance en arrière-plan, `jobs`/`fg`/`bg` gèrent les tâches du shell, `nohup`/`disown` les détachent pour survivre à la fermeture du terminal.

**Pièges** :
- `kill -9` (SIGKILL) ne laisse aucune chance au processus de nettoyer (fichiers temporaires, verrous) — dernier recours.
- `renice` vers une valeur négative exige root ; un utilisateur ne peut qu'augmenter sa niceness (jamais la diminuer).
- Tuer un processus supervisé (systemd) le fait **redémarrer** — voir [[q22-systemd-targets-and-services]] ; agir sur l'unit plutôt que sur le PID.
- `pkill`/`killall` ciblent par nom : attention à ne pas en attraper plus que prévu (filtrer par `-u utilisateur`).

## Énoncé

Solve this question on: `app-srv1`

1. Find the PID of the process listening on TCP port `8080` and write it into `/opt/course/23/pid`.
2. Renice the process `stress-ng` to priority `10` without killing it.
3. Send `SIGTERM` to all `sleep` processes owned by user `bob`.
4. Identify the top 3 memory-consuming processes and write their command names into `/opt/course/23/top-mem`.

## Solution

### Step 1 — Find the process behind a port

```bash
sudo ss -tlnp | grep :8080
# LISTEN 0 511 *:8080 *:* users:(("node",pid=1423,fd=18))
sudo ss -tlnp 'sport = :8080'
sudo lsof -i :8080
sudo fuser 8080/tcp
```

Pull just the PID:
```bash
sudo ss -tlnpH 'sport = :8080' | grep -oP 'pid=\K[0-9]+' > /opt/course/23/pid
```

### Step 2 — Change priority

Nice values range from `-20` (highest priority) to `19` (lowest). Only root can lower (more negative) the niceness.

```bash
ps -eo pid,ni,cmd | grep stress-ng
sudo renice -n 10 -p $(pgrep stress-ng)
# or rename whole process group / user
sudo renice -n 10 -u bob
sudo renice -n 10 -g 1234
```

Start a process with a given priority:
```bash
nice -n 15 ./long-job.sh
chrt -f 50 ./realtime-job                  # real-time scheduling
ionice -c 3 ./bulk-copy.sh                 # I/O idle class
```

### Step 3 — Kill processes selectively

```bash
pgrep -u bob sleep                          # list matching PIDs
sudo pkill -SIGTERM -u bob sleep            # signal them
sudo killall -u bob sleep                   # by name
```

Signals worth knowing:
- `SIGHUP` (1) — reload config (many daemons)
- `SIGINT` (2) — Ctrl+C
- `SIGKILL` (9) — uncatchable, immediate
- `SIGTERM` (15) — polite termination, default
- `SIGSTOP` / `SIGCONT` — pause / resume

### Step 4 — Top memory consumers

```bash
ps -eo pid,comm,%mem --sort=-%mem | head -n 4
ps -eo pid,comm,%mem --sort=-%mem | awk 'NR>1 && NR<=4 {print $2}' > /opt/course/23/top-mem
```

### Live monitoring

```bash
top                # interactive — press M (mem), P (cpu), k (kill)
htop               # nicer alternative
pidstat 1          # per-process CPU/mem every second
vmstat 1           # global counters
iotop              # I/O per process (needs root)
```

### Background and job control

```bash
./long.sh &                       # background
jobs                              # list shell jobs
fg %1                             # foreground job 1
bg %1
nohup ./long.sh &                 # survive shell logout
disown %1                         # detach existing job
```
