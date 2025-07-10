# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
from textwrap import dedent

import pytest
import subprocess
from mfd_connect.base import ConnectionCompletedProcess

from mfd_mount.exceptions import (
    NFSMountException,
    CIFSMountException,
    SSHFSMountException,
    TMPFSMountException,
    HUGETLBFSMountException,
    UnmountException,
)
from mfd_mount.posix import PosixMount
from mfd_mount.base import Mount
from mfd_connect import RPyCConnection

from mfd_typing.os_values import OSName


class TestPosixMount:
    @pytest.fixture(params=[Mount, PosixMount])
    def mount(self, mocker, request):
        conn = mocker.create_autospec(RPyCConnection)
        conn.get_os_name.return_value = OSName.LINUX
        return request.param(connection=conn)

    def test_mount_class_type(self, mount):
        assert isinstance(mount, PosixMount), "Mount object is not of type PosixMount"

    def test_mount_nfs(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_nfs(mount_point="/mnt/shared", share_path="10.10.10.10:/to_share")
        mount._conn.execute_command.assert_called_once_with(
            "mount -t nfs 10.10.10.10:/to_share /mnt/shared", custom_exception=NFSMountException
        )

    def test_mount_nfs_context_manager(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        with mount.mount_nfs(mount_point="/mnt/shared", share_path="10.10.10.10:/to_share"):
            mount._conn.execute_command.assert_called_with(
                "mount -t nfs 10.10.10.10:/to_share /mnt/shared", custom_exception=NFSMountException
            )

        mount._conn.execute_command.assert_called_with("umount /mnt/shared", custom_exception=UnmountException)
        assert mount._conn.execute_command.call_count == 2

    def test_mount_nfs_with_user(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_nfs(mount_point="/mnt/shared", share_path="10.10.10.10:/to_share", username="admin")
        mount._conn.execute_command.assert_called_once_with(
            "mount -t nfs -o username=admin 10.10.10.10:/to_share /mnt/shared", custom_exception=NFSMountException
        )

    def test_mount_nfs_with_user_context_manager(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        with mount.mount_nfs(mount_point="/mnt/shared", share_path="10.10.10.10:/to_share", username="admin"):
            mount._conn.execute_command.assert_called_with(
                "mount -t nfs -o username=admin 10.10.10.10:/to_share /mnt/shared", custom_exception=NFSMountException
            )

        mount._conn.execute_command.assert_called_with("umount /mnt/shared", custom_exception=UnmountException)
        assert mount._conn.execute_command.call_count == 2

    def test_mount_nfs_with_user_password(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_nfs(
            mount_point="/mnt/shared", share_path="10.10.10.10:/to_share", username="admin", password="pass"
        )
        mount._conn.execute_command.assert_called_once_with(
            "mount -t nfs -o username=admin,password=pass 10.10.10.10:/to_share /mnt/shared",
            custom_exception=NFSMountException,
        )

    def test_mount_nfs_with_user_password_context_manager(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        with mount.mount_nfs(
            mount_point="/mnt/shared", share_path="10.10.10.10:/to_share", username="admin", password="pass"
        ):
            mount._conn.execute_command.assert_called_with(
                "mount -t nfs -o username=admin,password=pass 10.10.10.10:/to_share /mnt/shared",
                custom_exception=NFSMountException,
            )

        mount._conn.execute_command.assert_called_with("umount /mnt/shared", custom_exception=UnmountException)
        assert mount._conn.execute_command.call_count == 2

    def test_mount_cifs(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_cifs(mount_point="/mnt/shared", share_path="//10.10.10.10/to_share")
        mount._conn.execute_command.assert_called_once_with(
            "mount -t cifs //10.10.10.10/to_share /mnt/shared", custom_exception=CIFSMountException
        )

    def test_mount_cifs_with_user(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_cifs(mount_point="/mnt/shared", share_path="//10.10.10.10/to_share", username="admin")
        mount._conn.execute_command.assert_called_once_with(
            "mount -t cifs -o username=admin //10.10.10.10/to_share /mnt/shared", custom_exception=CIFSMountException
        )

    def test_mount_cifs_with_user_password(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_cifs(
            mount_point="/mnt/shared", share_path="//10.10.10.10/to_share", username="admin", password="pass"
        )
        mount._conn.execute_command.assert_called_once_with(
            "mount -t cifs -o username=admin,password=pass //10.10.10.10/to_share /mnt/shared",
            custom_exception=CIFSMountException,
        )

    def test_mount_cifs_context_manager(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        with mount.mount_cifs(mount_point="/mnt/shared", share_path="//10.10.10.10/to_share"):
            mount._conn.execute_command.assert_called_with(
                "mount -t cifs //10.10.10.10/to_share /mnt/shared", custom_exception=CIFSMountException
            )
        assert mount._conn.execute_command.call_count == 2

    def test_mount_cifs_with_user_context_manager(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        with mount.mount_cifs(mount_point="/mnt/shared", share_path="//10.10.10.10/to_share", username="admin"):
            mount._conn.execute_command.assert_called_with(
                "mount -t cifs -o username=admin //10.10.10.10/to_share /mnt/shared",
                custom_exception=CIFSMountException,
            )
        assert mount._conn.execute_command.call_count == 2

    def test_mount_cifs_with_user_password_context_manager(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        with mount.mount_cifs(
            mount_point="/mnt/shared", share_path="//10.10.10.10/to_share", username="admin", password="pass"
        ):
            mount._conn.execute_command.assert_called_with(
                "mount -t cifs -o username=admin,password=pass //10.10.10.10/to_share /mnt/shared",
                custom_exception=CIFSMountException,
            )
        assert mount._conn.execute_command.call_count == 2

    def test_mount_sshfs(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_sshfs(mount_point="/shared", share_path="10.10.10.10:/to_share", username="root", password="root")
        assert_call = "sshfs -o password_stdin -o StrictHostKeyChecking=no root@10.10.10.10:/to_share /shared <<<'root'"
        mount._conn.execute_command.assert_called_once_with(
            assert_call, shell=True, custom_exception=SSHFSMountException
        )

    def test_mount_sshfs_context_manager(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        with mount.mount_sshfs(
            mount_point="/shared", share_path="10.10.10.10:/to_share", username="root", password="root"
        ):
            assert_call = (
                "sshfs -o password_stdin -o StrictHostKeyChecking=no root@10.10.10.10:/to_share /shared <<<'root'"
            )
            mount._conn.execute_command.assert_called_once_with(
                assert_call, shell=True, custom_exception=SSHFSMountException
            )
        mount._conn.execute_command.assert_called_with("umount /shared", custom_exception=UnmountException)
        assert mount._conn.execute_command.call_count == 2

    def test_mount_tmpfs(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_tmpfs(mount_point="/mnt/shared", share_path="//10.10.10.10/to_share", params="-o param")
        mount._conn.execute_command.assert_called_once_with(
            "mount -t tmpfs -o param //10.10.10.10/to_share /mnt/shared", custom_exception=TMPFSMountException
        )

    def test_mount_tmpfs_context_manager(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        with mount.mount_tmpfs(mount_point="/mnt/shared", share_path="//10.10.10.10/to_share"):
            mount._conn.execute_command.assert_called_with(
                "mount -t tmpfs //10.10.10.10/to_share /mnt/shared", custom_exception=TMPFSMountException
            )
        assert mount._conn.execute_command.call_count == 2

    def test_mount_tmpfs_with_params_context_manager(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        with mount.mount_tmpfs(mount_point="/mnt/shared", share_path="//10.10.10.10/to_share", params="-o params"):
            mount._conn.execute_command.assert_called_with(
                "mount -t tmpfs -o params //10.10.10.10/to_share /mnt/shared",
                custom_exception=TMPFSMountException,
            )
        assert mount._conn.execute_command.call_count == 2

    def test_mount_hugetlbfs(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_hugetlbfs(mount_point="/mnt/shared", share_path="//10.10.10.10/to_share", params="-o param")
        mount._conn.execute_command.assert_called_once_with(
            "mount -t hugetlbfs -o param //10.10.10.10/to_share /mnt/shared",
            custom_exception=HUGETLBFSMountException,
        )

    def test_mount_hugetlbfs_context_manager(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        with mount.mount_hugetlbfs(mount_point="/mnt/shared", share_path="//10.10.10.10/to_share"):
            mount._conn.execute_command.assert_called_with(
                "mount -t hugetlbfs //10.10.10.10/to_share /mnt/shared", custom_exception=HUGETLBFSMountException
            )
        assert mount._conn.execute_command.call_count == 2

    def test_mount_hugetlbfs_with_params_context_manager(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        with mount.mount_hugetlbfs(mount_point="/mnt/shared", share_path="//10.10.10.10/to_share", params="-o params"):
            mount._conn.execute_command.assert_called_with(
                "mount -t hugetlbfs -o params //10.10.10.10/to_share /mnt/shared",
                custom_exception=HUGETLBFSMountException,
            )
        assert mount._conn.execute_command.call_count == 2

    def test_is_mounted_true(self, mount):
        mount_point = "/shared_directory"
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        output = dedent(
            """
        Filesystem        1K-blocks    Used Available Use% Mounted on
        remote_filesystem 359061248 6105984 352955264   2% /shared_directory
        """
        )
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", stdout=output, return_code=0)
        assert mount.is_mounted(mount_point) is True
        mount._conn.execute_command.assert_called_once_with(f"df {mount_point}")

    def test_is_mounted_false(self, mount):
        mount_point = "shared_directory"
        mount._conn.execute_command.side_effect = subprocess.CalledProcessError(1, "")
        assert mount.is_mounted(mount_point) is False
        mount._conn.execute_command.assert_called_once_with(f"df {mount_point}")

    def test_umount_failure(self, mount):
        output = dedent(
            """\
        umount.nfs: remote share not in 'host:dir' format
        umount.nfs: /mnt/berta2: not mounted"""
        )
        mount._conn.execute_command.side_effect = UnmountException(cmd="", returncode=1, stderr=output)
        with pytest.raises(UnmountException):
            mount.umount(mount_point="/mnt/shared")

    def test_umount(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.umount(mount_point="/mnt/shared")
        mount._conn.execute_command.assert_called_once_with("umount /mnt/shared", custom_exception=UnmountException)
