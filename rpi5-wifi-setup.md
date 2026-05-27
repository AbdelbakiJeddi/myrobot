# Add WiFi to RPi5 Ubuntu Server (No SSH / No Screen)

This guide explains how to add a new WiFi connection to a Raspberry Pi 5 running Ubuntu Server 24, when you have **no SSH access and no screen** — only direct access to the SD card.

---

## Prerequisites

- Another Linux/Mac computer (or Windows with WSL)
- SD card reader
- The RPi5 powered off

---

## Step 1 — Remove the SD Card

Power off the RPi5 and remove the SD card. Insert it into your secondary computer.

---

## Step 2 — Create the WiFi Connection File

Navigate to the NetworkManager connections directory:

```bash
cd /media/youruser/writable/etc/NetworkManager/system-connections/
```

Create a new connection file:

```bash
sudo touch phone-wifi.nmconnection
sudo nano phone-wifi.nmconnection
```

Paste the following content (replace `YOUR_WIFI_NAME` and `YOUR_WIFI_PASSWORD`):

```ini
[connection]
id=home-wifi
uuid=a1b2c3d4-e5f6-7890-abcd-ef1234567890
type=wifi
autoconnect=true

[wifi]
mode=infrastructure
ssid=YOUR_WIFI_NAME

[wifi-security]
auth-alg=open
key-mgmt=wpa-psk
psk=YOUR_WIFI_PASSWORD

[ipv4]
method=auto

[ipv6]
addr-gen-mode=stable-privacy
method=auto
```

> **Tip:** Generate a proper UUID with `uuidgen` and replace the placeholder above.

---

## Step 3 — Set Correct Permissions

> ⚠️ This is critical — NetworkManager will **ignore** the file if permissions are wrong.

Run this on your secondary computer (with the SD card still mounted):

```bash
sudo chmod 600 /media/youruser/writable/etc/NetworkManager/system-connections/phone-wifi.nmconnection
sudo chown root:root /media/youruser/writable/etc/NetworkManager/system-connections/phone-wifi.nmconnection
```

---

## Step 4 — Find the RPi5 IP and SSH In

Once booted, find the assigned IP address from your **router's admin panel** (look under DHCP client list).

Then SSH in:

```bash
ssh ubuntu@<IP_ADDRESS>
```

> Default Ubuntu Server credentials: `ubuntu` / `ubuntu`  
> You will be prompted to change the password on first login.

---

## Notes

- Replace `/dev/sdb2` and `/media/youruser/writable` with your actual device and mount paths (check with `lsblk`)
- On **Windows**, use WSL or a live Linux USB to properly set file permissions on the ext4 partition
- If you have multiple WiFi networks, create one `.nmconnection` file per network
