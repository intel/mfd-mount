# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

# Put here only the dependencies required to run the module.
# Development and test requirements should go to the corresponding files.
from mfd_connect import LocalConnection
from mfd_mount import Mount

"""
Command below will instantiate proper subclass based on local OS type
e.g. when working on POSIX system, it will return PosixMount
"""
mounter = Mount(connection=LocalConnection())
mounter.mount_nfs(mount_point="/mnt/shared", share_path="10.10.10.10:/shared")
