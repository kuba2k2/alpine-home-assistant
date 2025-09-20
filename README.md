# Alpine Linux - Home Assistant Supervised

This guide, along with a few small software packages, allows to install Home Assistant Supervised on a host machine running Alpine Linux. Note that this is not a supported HA installation method, so YMMV. Personally, it works just fine on my ARMv7 machine.

> [!NOTE]
> Since July 2023, there are prebuilt APK packages available in this repo (for `x86`, `x86_64`, `armhf`, `armv7` and `aarch64`). The README below has been updated to reflect that. They are signed with the following public key:
>
> <details>
>
> <summary>Click to show public key</summary>
>
> ```
> -----BEGIN PUBLIC KEY-----
> MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAvrueY+eFZkILqfOsb8T8
> oxJ1tfM57VtIPJnGZeuEJchyd6AHbG7CCErdtLMRI7eWXJlAU23erFj6Wp/2zC5x
> XgfuE5ekMmq/8WwkvLYl9i9I/tgiFWklHkLAOsY8LkwtuQDeDEt3gMPFheY3uNaN
> FMWXKYWmknsQM10IV28TgDPfMLbVh7LagFbsKLWang50N+eGiMwQi+N1fZ/rrpk/
> Rco5opHpTOC1i+GTXCcVkuOisTFw741p7fFhWksgN7XZBwDXE472KLWV/he6mAqA
> /PbWmZHQxCdL1NwYJS5v9+K/c2sRUGb0dcHjC0bf9etrEg4otY7iydwZnM180mpt
> oMRxSLb63OFcfsNtJRu8+Wy/oZ28HzQeEqF9d7Z6o3OrXntoAqRneFNet/GMap5U
> 1fjDEh79X0sjcZuASTV8hb4VvXR9s8Drw/POnpYdX1wLDSRm+N4Z0CoJDP0+CxVr
> y11wSJmgyqkrZRfNyyQBW6H+zL+Pu5F15nq75fUlhE0eoBTi38THGgoGQSikBsHG
> UXNr4nUIenfq0fzEYSlPYG3kXe/8FSKvNjUCYhpbwBEmhQ/NRWRfqBnvRS6Si1wP
> +glz4VsR26fyMr2uH4SPL5c//GIgdCBZgfYusQsZjnJZkWDD8C61ijxBt+7cA0Sg
> FN0IX6Z7106y3qPUktG2f+cCAwEAAQ==
> -----END PUBLIC KEY-----
> ```
>
> </details>
>
> Building from source is also possible; the original guide is at the end of this document.

> [!NOTE]
> Since April 2024 the `MACHINE` variable in `/etc/hassio.json` created by this package is changed to reflect the correct system architecture. Upgrading to `hassio-supervised` v1.7.0 or newer will automatically rewrite that file with every update.

> [!NOTE]
> Since September 2025 the APK packages are published in a subdirectory matching the branch of Alpine Linux used to build it. Run the following commands to replace the old entry in `/etc/apk/repositories`:
>
> ```bash
> sudo sed -i '/kuba2k2.github.io\/alpine-home-assistant/d' /etc/apk/repositories
> RELEASE=$(cat /etc/alpine-release)
> echo "https://kuba2k2.github.io/alpine-home-assistant/v${RELEASE%.*}" | sudo tee -a /etc/apk/repositories
> cat /etc/apk/repositories
> ```

---

## Prerequisites

All steps of this guide (unless otherwise noted) are to be ran by a **non-root, sudo-enabled** user.

### Bind propagation

> [!IMPORTANT]
> Since v1.4.3, the Home Assistant Supervisor needs **bind propagation** support in the root filesystem (see [home-assistant/supervised-installer#293](https://github.com/home-assistant/supervised-installer/pull/293)).
>
> The `rshared` flag has to be enabled in `/etc/fstab`:
>
> ```
> UUID=the-uuid-is-usually-here       /       ext4    rw,relatime,rshared 0 1
> ```
>
> Remember to reboot after applying the changes (or, alternatively, run `sudo mount -o rshared,remount /`).

### Docker

```bash
# install git, Docker and Python 3
sudo apk add git docker python3
# start Docker
sudo service docker start
# add yourself to docker group
sudo addgroup $(whoami) docker
```

### AppArmor

You need a kernel with AppArmor support for best Home Assistant compatibility. Install and enable AppArmor, [as shown in the wiki](https://wiki.alpinelinux.org/wiki/AppArmor). Make sure to also install:

```bash
sudo apk add apparmor-profiles
```

Your kernel command line must have this as well:

```
lsm=landlock,yama,apparmor
```

Refer to [Alpine Wiki/AppArmor](https://wiki.alpinelinux.org/wiki/AppArmor) for details.

### NetworkManager

This is theoretically optional, but highly recommended, and will enable more network-related features in Home Assistant.

1. Run the following commands:

```bash
apk add eudev networkmanager networkmanager-cli networkmanager-tui
# install Wi-Fi support
apk add networkmanager-wifi
apk add wpa_supplicant
# configure udev
setup-devd udev
rc-update -a del networking
rc-update -a del wpa_supplicant
rc-update add networkmanager boot
# start NetworkManager
service networkmanager start
```

2. Edit `/etc/network/interfaces` and remove all interfaces except `lo`.
3. Check state of network interfaces with `nmcli dev`. If Wi-Fi is `unmanaged`, you'll most likely need to reboot.
4. Run `nmtui` to configure your network connections. If you're not able to activate any connections, reboot.

> [!NOTE]
> If Home Assistant shows a network DNS error during first setup, make sure the DNS server displayed is correct and just let it do its work. It should be still downloading in the background, and the error should go away after the installation finishes.

### logind

Optional, but (probably) enables more functionalities in HA, as the supervisor uses logind's DBus.

```bash
sudo apk add elogind
```

---

## Installing prebuilt packages

Enable the APK repository from this GitHub repo:

```bash
RELEASE=$(cat /etc/alpine-release)
echo "https://kuba2k2.github.io/alpine-home-assistant/v${RELEASE%.*}" | sudo tee -a /etc/apk/repositories
# install the public key
sudo wget -O /etc/apk/keys/actions@kuba2k2.github.io-64b57843.rsa.pub https://raw.githubusercontent.com/kuba2k2/alpine-home-assistant/master/actions@kuba2k2.github.io-64b57843.rsa.pub
# update repos
# APK should now show the "alpine-home-assistant" repo
sudo apk update
```

Finally, install the packages:

```bash
# Home Assistant OS Agent
sudo apk add hassio-os-agent
# Additional DBus bindings
sudo apk add hassio-dbus-openrc
# Check if DBus bindings work
gdbus introspect --system --dest org.freedesktop.systemd1 --object-path /org/freedesktop/systemd1
# Install only if you have NetworkManager
sudo apk add hassio-supervised-nm
# Supervisor & AppArmor - this will install and start Home Assistant
sudo apk add hassio-supervised
```

**Home Assistant will automatically be started** and added as an autostart service in OpenRC.

See Docker containers starting up:

```bash
watch -n 3 docker ps
```

---

## Building from source

<details>

### Basic setup

**Login as root** to configure sudo, if you haven't done this yet.

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

### Environment

(Re)login as a sudo-enabled, non-root user.

```bash
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

### Build packages

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

</details>
