# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
from mfd_connect import SSHConnection
from mfd_mount import PosixMount

mounter = PosixMount(connection=SSHConnection("10.10.10.10", username="root", password="***"))
mounter.mount_sshfs(mount_point="/mnt/shared", share_path="10.10.10.11:/shared", username="root", password="***")

# or
with mounter.mount_sshfs(
    mount_point="/mnt/shared", share_path="10.10.10.11:/shared", username="root", password="***"
):
    # will unmount share afterwards
    mounter.is_mounted(mount_point="/mnt/shared")
