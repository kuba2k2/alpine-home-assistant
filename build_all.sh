#!/bin/sh

cd hassio-os-agent/
abuild -r
cd ../hassio-supervised/
abuild -r
cd ../hassio-supervised-nm/
abuild -r
cd ../hassio-dbus-openrc/
abuild -r
