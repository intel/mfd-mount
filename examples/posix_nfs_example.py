# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
from mfd_connect import LocalConnection
from mfd_mount import PosixMount

mounter = PosixMount(connection=LocalConnection())
with mounter.mount_nfs(mount_point="/mnt/shared", share_path="10.10.10.10:/shared"):  # will unmount share afterwards
    mounter.is_mounted(mount_point="/mnt/shared")
