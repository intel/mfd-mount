# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
import pytest
from textwrap import dedent
from mfd_connect import RPyCConnection
from mfd_connect.base import ConnectionCompletedProcess

from mfd_mount.exceptions import NFSMountException, MountException, MountTypeNotSupported, UnmountException
from mfd_mount.esxi import ESXiMount
from mfd_mount.base import Mount

from mfd_typing.os_values import OSName


class TestESXiMount:
    @pytest.fixture(params=[Mount, ESXiMount])
    def mount(self, mocker, request):
        conn = mocker.create_autospec(RPyCConnection)
        conn.get_os_name.return_value = OSName.ESXI
        return request.param(connection=conn)

    def test_mount_class_type(self, mount):
        assert isinstance(mount, ESXiMount), "Mount object is not of type ESXiMount"

    @pytest.mark.parametrize("share", ["10.10.10.10:/to_share", "10.10.10.10/to_share"])
    def test_mount_nfs(self, mount, share):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_nfs(mount_point="shared", share_path=share)
        mount._conn.execute_command.assert_called_once_with(
            "esxcli storage nfs add -H 10.10.10.10 -s /to_share -v shared", custom_exception=NFSMountException
        )

    @pytest.mark.parametrize("share", ["10.10.10.10:/to_share", "10.10.10.10/to_share"])
    def test_mount_nfs_context_manager(self, mocker, mount, share):
        def conn_stdout(command, custom_exception):
            if command == "mount 10.10.10.10:/to_share Z:":
                return ConnectionCompletedProcess(args="", return_code=0)
            else:
                return ConnectionCompletedProcess(args="", return_code=0, stdout="Z: was deleted successfully.")

        mount._conn.execute_command = mocker.Mock(side_effect=conn_stdout)
        with mount.mount_nfs(mount_point="shared", share_path=share):
            mount._conn.execute_command.assert_called_with(
                "esxcli storage nfs add -H 10.10.10.10 -s /to_share -v shared", custom_exception=NFSMountException
            )

        mount._conn.execute_command.assert_called_with(
            "esxcli storage nfs remove -v shared", custom_exception=UnmountException
        )
        assert mount._conn.execute_command.call_count == 2

    def test_mount_nfs_incorrect_share_path(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        with pytest.raises(MountException):
            mount.mount_nfs(mount_point="shared", share_path="10.10.10.10\\to_share")

    def test_mount_cifs(self, mount):
        with pytest.raises(
            MountTypeNotSupported, match="CIFS mount is not supported for ESXi. " "Use other mount method."
        ):
            mount.mount_cifs(mount_point="shared", share_path="10.10.10.10/to_share")

    def test_is_mounted_true(self, mount):
        output = dedent(
            """
        Volume Name  Host          Share        Accessible  Mounted  Read-Only   isPE  Hardware Acceleration
        -----------  ------------  -----------  ----------  -------  ---------  -----  ---------------------
        nfs_mount    10.10.10.10   /mount_test        true     true      false  false  Not Supported
        nfs_mount2   10.10.10.11   /mount_test2       true     true      false  false  Not Supported
        """
        )
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(
            return_code=0, args="command", stdout=output, stderr="stderr"
        )

        assert mount.is_mounted("nfs_mount") is True
        mount._conn.execute_command.assert_called_once_with("esxcli storage nfs list")

    def test_is_mounted_false(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(
            return_code=0, args="command", stdout="", stderr="stderr"
        )

        assert mount.is_mounted("nfs_mount") is False
        mount._conn.execute_command.assert_called_once_with("esxcli storage nfs list")

    def test_umount_failure(self, mount):
        output = "Error performing operation: NFS Error: Unable to Unmount filesystem: Busy."
        mount._conn.execute_command.side_effect = UnmountException(cmd="", returncode=1, stderr=output)
        with pytest.raises(UnmountException):
            mount.umount(mount_point="Shared")

    def test_umount(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.umount(mount_point="Shared")
        mount._conn.execute_command.assert_called_once_with(
            "esxcli storage nfs remove -v Shared", custom_exception=UnmountException
        )
