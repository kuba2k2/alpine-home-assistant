# Alpine Linux - Home Assistant Supervised

**Note:** you need a kernel with AppArmor support (AppArmor 2.4 compatibility patch, whatever that means).

## Environment

Login as root to configure sudo, if you haven't done this yet.

```bash
# enable community repository
sed -i '/v3\.\d*\/community/s/^#//' /etc/apk/repositories
# update apk index
apk update
# install sudo
apk add sudo
```

Edit `/etc/sudoers` to enable `wheel` group. Add yourself to the group: `addgroup <yourname> wheel`.

(Re)login as a sudo-enabled, non-root user.

```bash
sudo apk add git alpine-sdk docker python3
sudo addgroup $(whoami) abuild
sudo mkdir -p /var/cache/distfiles
sudo chgrp abuild /var/cache/distfiles
sudo chmod g+w /var/cache/distfiles
abuild-keygen -a -i # skip if you already have a key
```

Add yourself to `docker` group (`addgroup <yourname> docker`).

Logout and login again.

```bash
cd ~
git clone https://github.com/kuba2k2/alpine-home-assistant
```

### NetworkManager

This is optional, but will enable more network-related features in Home Assistant.

Installing NetworkManager on Alpine seems simple, unless you spend many hours trying to fix it, because nobody has ever mentioned that `udev` is required for NM to work at all.

Run **as root**:
```bash
apk add eudev networkmanager networkmanager-cli networkmanager-tui
# errors are normal here
setup-devd udev
rc-update del hwdrivers sysinit
rc-update -a del networking
rc-update -a del wpa_supplicant
rc-update add networkmanager boot
rc-update add udev sysinit
rc-update add udev-postmount default
rc-update add udev-settle sysinit
rc-update add udev-trigger sysinit
```

Edit `/etc/network/interfaces` and remove all interfaces except `lo`.

Run `nmtui` to configure your network connections (you probably won't be able to activate them yet). Reboot to start NetworkManager and activate the network.

### logind

Optional, but (probably) enables more functionalities in HA, as the supervisor uses logind's DBus.

```bash
apk add elogind
```

## Build packages

Login as a sudo-enabled, non-root user.

```bash
cd ~/alpine-home-assistant/
source build_all.sh
```

### Install

```bash
# Home Assistant OS Agent
sudo apk add --repository ~/packages/alpine-home-assistant hassio-os-agent
# Additional DBus bindings
sudo apk add --repository ~/packages/alpine-home-assistant hassio-dbus-openrc
# Check if DBus bindings work
gdbus introspect --system --dest org.freedesktop.systemd1 --object-path /org/freedesktop/systemd1
# Install only if you have NetworkManager
sudo apk add --repository ~/packages/alpine-home-assistant hassio-supervised-nm
# Supervisor & AppArmor - this will install and start Home Assistant
sudo apk add --repository ~/packages/alpine-home-assistant hassio-supervised
```

See Docker containers starting up:

```bash
watch -n 3 docker ps
```
