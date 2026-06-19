# Question 13 — Runtime Security of processes

## Notes d'apprentissage

Tout ce qu'un programme demande au noyau (ouvrir un fichier, créer un processus, envoyer un signal) passe par un **appel système** (*syscall*). Observer les syscalls d'un processus, c'est voir ce qu'il fait réellement, au-delà de son nom.

**Modèle mental : le syscall, frontière entre programme et noyau.**

```
processus (espace utilisateur)
      │  open(), read(), execve(), kill(), socket()...   ← syscalls
      ▼
   noyau (espace privilégié) ── exécute l'opération, renvoie un code
```

Un syscall comme `kill(666, SIGTERM)` signifie « envoyer le signal SIGTERM au PID 666 ». Surveiller ces appels permet de repérer un comportement interdit par une politique de sécurité.

**`strace` : tracer les syscalls en direct.**
```bash
strace -p <PID>            # s'attacher à un processus en cours et voir ses syscalls
strace -f commande         # tracer une commande ET ses processus enfants (-f = follow)
strace -e trace=kill -p PID  # ne montrer que les syscalls "kill"
strace -c -p PID           # résumé statistique par syscall
```
On laisse tourner quelques secondes pour capturer les appels périodiques. Ici, seul `collector2` émet un `kill(...)` — c'est le coupable.

**Identifier puis neutraliser un processus :**
```bash
ps aux | grep collector             # PID + chemin de l'exécutable
ls -l /proc/<PID>/exe               # chemin réel de l'exécutable (lien)
kill <PID>                          # SIGTERM : demande d'arrêt propre
kill -9 <PID>                       # SIGKILL : arrêt forcé (si SIGTERM ignoré)
rm /bin/collector2                  # supprimer le binaire
```

**Les signaux courants** : `SIGTERM` (15, arrêt propre, par défaut), `SIGKILL` (9, tue sans recours), `SIGHUP` (1, souvent « recharge ta config »), `SIGSTOP`/`SIGCONT` (suspendre/reprendre).

**Pièges** :
- `strace` peut **ralentir fortement** le processus tracé — à éviter sur un service critique en production.
- Un processus relancé par un superviseur (systemd, un parent) **réapparaît** après `kill` : supprimer le binaire et/ou désactiver le service, sinon il revient.
- Tracer demande des privilèges (root, ou même utilisateur que le processus) ; `ptrace` peut être restreint par `kernel.yama.ptrace_scope`.
- Lié à la sécurité d'exécution : seccomp (filtrage de syscalls) et le MAC, voir [[q44-selinux-and-apparmor]].

## Énoncé

Solve this question on: `web-srv1`

There was a security alert which you need to follow up on. On server `web-srv1` there are three processes: `collector1`, `collector2`, and `collector3`. It was alerted that any of these might run periodically the per custom policy forbidden syscall `kill`.

End the process and remove the executable for those where this is true.

> You can use `strace -p PID`

## Solution

We should check the server for the mentioned processes:
```bash
ssh web-srv1
root@web-srv1:~$ ps aux | grep collector
root        3611  0.0  0.0 101924   624 ?        Sl   13:23   0:00 /bin/collector1
root        3612  0.0  0.0 101916   612 ?        Sl   13:23   0:00 /bin/collector2
root        3613  0.0  0.0 101928   616 ?        Sl   13:23   0:00 /bin/collector3
```

Now we investigate the kernel syscalls of `collector1`:
```bash
root@web-srv1:~$ strace -p 3611 # your PID will be different!
restart_syscall(<... resuming interrupted read ...>) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d4bb0, FUTEX_WAKE_PRIVATE, 1)  = 1
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
futex(0x4d7460, FUTEX_WAIT_PRIVATE, 0, {tv_sec=0, tv_nsec=999999757}) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d4bb0, FUTEX_WAKE_PRIVATE, 1)  = 1
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
futex(0x4d7460, FUTEX_WAIT_PRIVATE, 0, {tv_sec=0, tv_nsec=999999756}) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d4bb0, FUTEX_WAKE_PRIVATE, 1)  = 1
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
futex(0x4d7460, FUTEX_WAIT_PRIVATE, 0, {tv_sec=0, tv_nsec=999999699}) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d4bb0, FUTEX_WAKE_PRIVATE, 1)  = 1
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
...
```

After watching for a while, there don't seem to be any kill syscalls. Next one is `collector2`:
```bash
root@web-srv1:~$ strace -p 3612
restart_syscall(<... resuming interrupted read ...>) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d2db0, FUTEX_WAKE_PRIVATE, 1)  = 1
kill(666, SIGTERM)                      = -1 ESRCH (No such process)
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
futex(0x4d5660, FUTEX_WAIT_PRIVATE, 0, {tv_sec=0, tv_nsec=999999449}) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d2db0, FUTEX_WAKE_PRIVATE, 1)  = 1
kill(666, SIGTERM)                      = -1 ESRCH (No such process)
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
futex(0x4d5660, FUTEX_WAIT_PRIVATE, 0, {tv_sec=0, tv_nsec=999999593}) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d2db0, FUTEX_WAKE_PRIVATE, 1)  = 1
```

kill(666, SIGTERM) # there we go!

...

Gotcha! Seems like `collector2` is one bad process. Still we need to check the last one, `collector3`:
```bash
root@web-srv1:~$ strace -p 3613
restart_syscall(<... resuming interrupted read ...>) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d5bb0, FUTEX_WAKE_PRIVATE, 1)  = 1
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
futex(0x4d8460, FUTEX_WAIT_PRIVATE, 0, {tv_sec=0, tv_nsec=999999731}) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d5bb0, FUTEX_WAKE_PRIVATE, 1)  = 1
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
futex(0x4d8460, FUTEX_WAIT_PRIVATE, 0, {tv_sec=0, tv_nsec=999999722}) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d5bb0, FUTEX_WAKE_PRIVATE, 1)  = 1
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
futex(0x4d8460, FUTEX_WAIT_PRIVATE, 0, {tv_sec=0, tv_nsec=999999635}) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d5bb0, FUTEX_WAKE_PRIVATE, 1)  = 1
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
futex(0x4d8460, FUTEX_WAIT_PRIVATE, 0, {tv_sec=0, tv_nsec=999999641}) = -1 ETIMEDOUT (Connection timed out)
futex(0x4d5bb0, FUTEX_WAKE_PRIVATE, 1)  = 1
futex(0xc0000324c8, FUTEX_WAKE_PRIVATE, 1) = 1
...
```

Seems like only `collector2` should be terminated. First we run `ps` again to see the binary path:
```bash
root@web-srv1:~$ ps aux | grep collector2
root        3612  0.0  0.0 101916   612 ?        Sl   13:23   0:00 /bin/collector2
root@web-srv1:~$ kill 3612 # your PID will be different!
root@web-srv1:~$ ps aux | grep collector2
root@web-srv1:~$ rm /bin/collector2
```