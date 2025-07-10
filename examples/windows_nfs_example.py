# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
import logging

from mfd_connect import RPyCConnection

from mfd_mount import WindowsMount

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

mounter = WindowsMount(connection=RPyCConnection(ip="10.10.10.10"))
with mounter.mount_nfs(
    mount_point="Z:", share_path="path.to.share.com:/shared/Public"
):  # will unmount share afterwards
    mounter.is_mounted(mount_point="Z:")
