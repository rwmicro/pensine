# Question 38 — KVM Virtualization

## Énoncé

Solve this question on: `terminal`

1. Verify that the CPU supports hardware virtualization and that KVM modules are loaded.
2. Install `libvirt` + `qemu-kvm` and start the daemon.
3. Create a 10 GiB qcow2 disk and define a VM `lfcs-vm1` with 2 vCPU, 2 GiB RAM, attached to the default NAT network.
4. List running VMs into `/opt/course/38/vms`.

## Solution

### Step 1 — Hardware support

```bash
egrep -c '(vmx|svm)' /proc/cpuinfo       # >0 means CPU supports virt
lsmod | grep kvm                          # kvm_intel / kvm_amd loaded
ls /dev/kvm                               # device node exists
sudo kvm-ok                               # Ubuntu helper
sudo virt-host-validate                   # comprehensive checks
```

If KVM is missing, enable virtualization in BIOS/UEFI and:
```bash
sudo modprobe kvm_intel       # or kvm_amd
```

### Step 2 — Install libvirt stack

Debian:
```bash
sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients \
                 virtinst bridge-utils virt-manager
sudo systemctl enable --now libvirtd
sudo usermod -aG libvirt,kvm $USER
```

RHEL:
```bash
sudo dnf install qemu-kvm libvirt virt-install libguestfs-tools
sudo systemctl enable --now libvirtd
```

### Step 3 — Create a disk and define a VM

Create the disk:
```bash
sudo qemu-img create -f qcow2 /var/lib/libvirt/images/lfcs-vm1.qcow2 10G
qemu-img info /var/lib/libvirt/images/lfcs-vm1.qcow2
```

Install from an ISO (interactive):
```bash
sudo virt-install \
  --name lfcs-vm1 \
  --memory 2048 \
  --vcpus 2 \
  --disk path=/var/lib/libvirt/images/lfcs-vm1.qcow2,format=qcow2,bus=virtio \
  --cdrom /var/lib/libvirt/images/debian-12.iso \
  --os-variant debian12 \
  --network network=default,model=virtio \
  --graphics none --console pty,target_type=serial \
  --extra-args 'console=ttyS0,115200n8'
```

Common useful flags:
- `--import` — boot existing disk without an ISO
- `--cloud-init user-data=...,meta-data=...` — provision with cloud-init
- `--noautoconsole` — return immediately

### Step 4 — Day-to-day virsh commands

```bash
virsh list                            # running
virsh list --all                      # all defined
virsh start  lfcs-vm1
virsh shutdown lfcs-vm1               # graceful
virsh destroy  lfcs-vm1               # force off
virsh reboot  lfcs-vm1
virsh suspend lfcs-vm1
virsh resume  lfcs-vm1
virsh undefine lfcs-vm1               # delete definition (keep disks)
virsh undefine lfcs-vm1 --remove-all-storage

virsh dominfo lfcs-vm1
virsh domiflist lfcs-vm1              # network interfaces
virsh domblklist lfcs-vm1             # disks
virsh console lfcs-vm1                # attach to serial console (Ctrl+] to exit)
virsh edit lfcs-vm1                   # edit XML
virsh dumpxml lfcs-vm1 > vm1.xml

virsh list --state-running --name > /opt/course/38/vms
```

### Networks

```bash
virsh net-list --all
virsh net-start default
virsh net-autostart default
virsh net-dumpxml default
```

The `default` network is a NAT bridge (`virbr0`, 192.168.122.0/24) with built-in DHCP.

Custom bridged network — see [[q32-bonding-and-bridges]] then attach a VM with `--network bridge=br0`.

### Storage pools

```bash
virsh pool-list --all
virsh pool-info default
virsh vol-list default
virsh vol-create-as default vm2.qcow2 20G --format qcow2
```

### Snapshots and migration

```bash
virsh snapshot-create-as lfcs-vm1 snap1 "before upgrade"
virsh snapshot-list lfcs-vm1
virsh snapshot-revert lfcs-vm1 snap1
virsh snapshot-delete lfcs-vm1 snap1

virsh migrate --live lfcs-vm1 qemu+ssh://target-host/system
```

### Image manipulation

```bash
qemu-img convert -O qcow2 disk.raw disk.qcow2
qemu-img resize lfcs-vm1.qcow2 +5G
sudo virt-customize -a image.qcow2 --root-password password:secret \
                   --hostname new-host --update
sudo virt-sysprep -a image.qcow2          # remove machine-specific data
```

### LXC / containers via libvirt

`libvirt` also drives LXC containers, but most LFCS questions use Docker (see [[q11-docker-management]]) or `systemd-nspawn`.
