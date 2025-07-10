# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

# Put here only the dependencies required to run the module.
# Development and test requirements should go to the corresponding files.
from mfd_connect import SSHConnection
from mfd_mount import ESXiMount

mounter = ESXiMount(connection=SSHConnection(ip="10.10.10.10", username="root", password="***"))
with mounter.mount_nfs(mount_point="main", share_path="path.to.share.com:/shared/"):  # will unmount share afterwards
    mounter.is_mounted(mount_point="main")
