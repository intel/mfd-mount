# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
import logging
from pathlib import Path

from mfd_connect import RPyCConnection

from mfd_mount import WindowsMount

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

mounter = WindowsMount(connection=RPyCConnection(ip="11.11.11.11", port=18813))
mounter.mount_cifs(mount_point="Z:", share_path=Path(r"\\10.10.10.10\shared"), username="user", password="***")
# or using as context manager
with mounter.mount_cifs(mount_point="Z:", share_path=Path(r"\\10.10.10.10\shared"), username="user", password="***"):
    mounter.is_mounted("Z:")
