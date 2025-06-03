# Arch Linux Installation Guide (Using `pacstrap`)

This guide covers the steps to install Arch Linux using the `pacstrap` tool. It assumes you're starting from the official Arch ISO and stops just before transitioning to a full installation from the mounted disk.

---

## Step 1: Boot into the Live Environment

* Boot from the Arch ISO (USB or other media).
* Verify internet connectivity:

  ```bash
  ping -c 3 archlinux.org
  ```

---

## Step 2: Partition the Disk

Use `fdisk`, `cfdisk`, or `parted` to partition your target disk.

Example layout for UEFI:

* `/dev/sda1` — EFI System Partition (512 MiB, type EFI System)
* `/dev/sda2` — Root partition (rest of disk, type Linux filesystem)

---

## Step 3: Format the Partitions

```bash
mkfs.fat -F32 /dev/sda1        # EFI
mkfs.ext4 /dev/sda2            # Root
```

(Optional) If using swap:

```bash
mkswap /dev/sda3
swapon /dev/sda3
```

---

## Step 4: Mount the Filesystems

```bash
mount /dev/sda2 /mnt           # Mount root
mkdir -p /mnt/boot             # Create boot dir
mount /dev/sda1 /mnt/boot      # Mount EFI
```

---

## Step 5: Install the Base System

Use `pacstrap` to install the minimal base system:

```bash
pacstrap /mnt base linux linux-firmware
```

Optionally include other essential packages:

```bash
pacstrap /mnt base linux linux-firmware vim sudo
```

---

## Step 6: Generate `fstab`

```bash
genfstab -U /mnt >> /mnt/etc/fstab
```

Verify the contents of `/mnt/etc/fstab`:

```bash
cat /mnt/etc/fstab
```

---

## Step 7: Change Root into the New System

Now you can enter the new Arch environment:

```bash
arch-chroot /mnt
```

> You are now working inside your new Arch Linux system and no longer relying on the USB environment. Continue with post-install configuration from here.

---

**End of Pre-Chroot Installation Phase**

From this point forward, all commands are executed within the installed system.
