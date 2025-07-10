# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
from mfd_connect import LocalConnection, RPyCConnection
from mfd_mount import PosixMount, FreeBSDMount

mounter = PosixMount(connection=LocalConnection())
mounter.mount_cifs(mount_point="/mnt/share", share_path="//10.10.10.10/share", username="user", password="***")

# Separate implementation for FreeBSD
mounter = FreeBSDMount(connection=RPyCConnection(ip="11.11.11.11", port=18813))
mounter.mount_cifs(mount_point="/mnt/share", share_path="12.12.12.12/share", username="user", password="***")

# or using as context manager
with mounter.mount_cifs(mount_point="/mnt/share", share_path="12.12.12.12/share", username="user", password="***"):
    mounter.is_mounted("/mnt/share")
