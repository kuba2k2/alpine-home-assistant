# Alpine Linux - Home Assistant Supervised

## Basic setup

Login as root to configure sudo, if you haven't done this yet.

```bash
# enable community repository
sed -i '/v3\.\d*\/community/s/^#//' /etc/apk/repositories
# update apk index
apk update
# install sudo
apk add sudo
# abuild seems to require doas, do this if you don't have it
ln -s $(which sudo) /usr/bin/doas
# enable for 'wheel' group
echo "%wheel ALL=(ALL:ALL) ALL" > /etc/sudoers.d/wheel
# same without password
echo "%wheel ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/wheel-nopw
```

## Environment

(Re)login as a sudo-enabled, non-root user.

```bash
# install Docker and Python 3
sudo apk add git docker python3
# start Docker
sudo service docker start
# add yourself to docker group
sudo addgroup $(whoami) docker
# install Alpine SDK
sudo apk add alpine-sdk
sudo addgroup $(whoami) abuild
sudo mkdir -p /var/cache/distfiles
sudo chgrp abuild /var/cache/distfiles
sudo chmod g+w /var/cache/distfiles
abuild-keygen -a -i # skip if you already have a key
```

Logout and login again.

```bash
cd ~
git clone https://github.com/kuba2k2/alpine-home-assistant
```

### NetworkManager

This is optional, but will enable more network-related features in Home Assistant.

Refer to [`alpine-custom-setup`](https://github.com/kuba2k2/alpine-custom-setup/blob/master/alpine.md#networkmanager).

### logind

Optional, but (probably) enables more functionalities in HA, as the supervisor uses logind's DBus.

```bash
sudo apk add elogind
```

### AppArmor

You need a kernel with AppArmor support for best Home Assistant compatibility. Install and enable AppArmor, [as shown in the wiki](https://wiki.alpinelinux.org/wiki/AppArmor). Make sure to also install:

```bash
sudo apk add apparmor-profiles
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
