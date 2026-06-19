# Question 32 — Bonding and Bridges

## Notes d'apprentissage

Bonding et bridge combinent des interfaces réseau, mais dans des buts **opposés** : l'un pour la robustesse/débit, l'autre pour connecter des machines virtuelles. Ne pas les confondre est l'essentiel.

**Modèle mental : agréger vs commuter.**

```
BOND (agrégation)                         BRIDGE (commutateur logiciel)
eth1 ┐                                    eth3 ──┐
     ├──► bond0 (1 IP)                           ├── br0 (switch virtuel)
eth2 ┘   plusieurs liens physiques        VM1 ───┤        + IP
         vus comme un seul                VM2 ───┘
   → tolérance de panne / débit              → relie VM et physique sur le même L2
```

- **Bond** : plusieurs cartes physiques fusionnées en une interface logique pour la **redondance** (si un câble lâche, l'autre prend le relais) ou le **débit** cumulé.
- **Bridge** : un commutateur Ethernet logiciel ; on y attache des interfaces (physiques et virtuelles) qui se retrouvent sur le **même segment réseau**. C'est le mécanisme standard pour brancher des VM (KVM, voir [[q38-kvm-virtualization]]).

**Les modes de bonding** — le seul vraiment à retenir est `active-backup` :

| Mode | Nom | Idée |
|---|---|---|
| 1 | `active-backup` | un lien actif, les autres en secours — **le plus fiable, sans config switch** |
| 0 | `balance-rr` | round-robin (débit, mais peut désordonner) |
| 4 | `802.3ad` | LACP — exige un switch compatible configuré |

`active-backup` ne demande **aucune configuration côté switch**, d'où sa popularité pour la simple tolérance de panne. Les modes d'agrégation de débit (`802.3ad`) exigent un switch coopérant.

**Le paramètre `miimon`** (ex. `miimon=100`) définit la fréquence (ms) de surveillance de l'état physique des liens — c'est lui qui détecte la coupure et bascule.

**Pièges** :
- Confondre bond (redondance/débit) et bridge (connecter des VM) est l'erreur conceptuelle classique.
- `802.3ad` ne fonctionne que si le switch est configuré en LACP des deux côtés.
- Les interfaces esclaves d'un bond/bridge ne portent **pas** d'IP propre : l'IP est sur `bond0`/`br0`.
- Avec `nmcli`, il faut créer la maîtresse (`bond0`/`br0`) **puis** rattacher chaque esclave avec `master`, et activer toutes les connexions.

## Énoncé

Solve this question on: `data-002`

1. Create a network bond `bond0` aggregating `eth1` and `eth2` in `active-backup` mode.
2. Assign IP `10.0.0.5/24` to `bond0`.
3. Create a bridge `br0` containing `eth3`, with IP `10.0.1.1/24`, so virtual machines can attach to it.

## Solution

### Bond modes

| Mode | Name | Behaviour |
|---|---|---|
| 0 | `balance-rr` | round-robin across slaves |
| 1 | `active-backup` | one slave active, others standby — most reliable |
| 2 | `balance-xor` | XOR hash for outgoing frames |
| 3 | `broadcast` | every frame on every slave |
| 4 | `802.3ad` | LACP — needs switch support |
| 5 | `balance-tlb` | adaptive transmit load balancing |
| 6 | `balance-alb` | adaptive load balancing (TX + RX) |

### Step 1 — Bonding with nmcli

```bash
sudo nmcli con add type bond ifname bond0 con-name bond0 mode active-backup
sudo nmcli con mod bond0 ipv4.addresses 10.0.0.5/24 ipv4.method manual
sudo nmcli con mod bond0 +bond.options "miimon=100,primary=eth1"

sudo nmcli con add type ethernet ifname eth1 master bond0 con-name bond-eth1
sudo nmcli con add type ethernet ifname eth2 master bond0 con-name bond-eth2

sudo nmcli con up bond-eth1
sudo nmcli con up bond-eth2
sudo nmcli con up bond0
```

Inspect:
```bash
cat /proc/net/bonding/bond0
ip -br link
```

### Step 1bis — Bonding by hand (no NM)

Load the module + create the master:
```bash
sudo modprobe bonding
echo "+bond0" | sudo tee /sys/class/net/bonding_masters

# configure mode BEFORE adding slaves
echo active-backup | sudo tee /sys/class/net/bond0/bonding/mode
echo 100           | sudo tee /sys/class/net/bond0/bonding/miimon

sudo ip link set eth1 down
sudo ip link set eth2 down
echo "+eth1" | sudo tee /sys/class/net/bond0/bonding/slaves
echo "+eth2" | sudo tee /sys/class/net/bond0/bonding/slaves

sudo ip addr add 10.0.0.5/24 dev bond0
sudo ip link set bond0 up
```

Make persistent: drop a config under `/etc/modules-load.d/bonding.conf` with `bonding` and a NetworkManager / netplan / networkd profile as above.

### Step 2 — Netplan equivalent for the bond

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth1: {dhcp4: no}
    eth2: {dhcp4: no}
  bonds:
    bond0:
      interfaces: [eth1, eth2]
      addresses: [10.0.0.5/24]
      parameters:
        mode: active-backup
        primary: eth1
        mii-monitor-interval: 100
```

### Step 3 — Bridge

```bash
sudo nmcli con add type bridge ifname br0 con-name br0
sudo nmcli con mod br0 ipv4.addresses 10.0.1.1/24 ipv4.method manual
sudo nmcli con mod br0 bridge.stp no

sudo nmcli con add type ethernet ifname eth3 master br0 con-name br-eth3
sudo nmcli con up br-eth3
sudo nmcli con up br0
```

Manual variant with `ip`:
```bash
sudo ip link add name br0 type bridge
sudo ip link set br0 up
sudo ip link set eth3 master br0
sudo ip addr add 10.0.1.1/24 dev br0
```

Inspect:
```bash
bridge link show
ip -br link show master br0
brctl show                     # legacy tool, still common
```

Netplan bridge example:
```yaml
network:
  version: 2
  bridges:
    br0:
      interfaces: [eth3]
      addresses: [10.0.1.1/24]
      parameters:
        stp: false
```

### VLAN (often paired in exams)

```bash
sudo ip link add link eth0 name eth0.10 type vlan id 10
sudo ip addr add 192.168.10.5/24 dev eth0.10
sudo ip link set eth0.10 up
```

Persistent (nmcli):
```bash
nmcli con add type vlan con-name eth0.10 dev eth0 id 10 ip4 192.168.10.5/24
```
