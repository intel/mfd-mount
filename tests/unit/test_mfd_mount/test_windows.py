# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
import pytest
import subprocess
from mfd_connect import RPyCConnection
from mfd_connect.base import ConnectionCompletedProcess

from mfd_mount.exceptions import NFSMountException, CIFSMountException, UnmountException
from mfd_mount.windows import WindowsMount
from mfd_mount.base import Mount

from mfd_typing.os_values import OSName


class TestWindowsMount:
    @pytest.fixture(params=[Mount, WindowsMount])
    def mount(self, mocker, request):
        conn = mocker.create_autospec(RPyCConnection)
        conn.get_os_name.return_value = OSName.WINDOWS
        return request.param(connection=conn)

    def test_mount_class_type(self, mount):
        assert isinstance(mount, WindowsMount), "Mount object is not of type WindowsMount"

    def test_mount_nfs(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_nfs(mount_point="Z:", share_path="10.10.10.10:/to_share")
        mount._conn.execute_command.assert_called_once_with(
            "mount 10.10.10.10:/to_share Z:", custom_exception=NFSMountException
        )

    def test_mount_nfs_context_manager(self, mocker, mount):
        def conn_stdout(command, custom_exception):
            if command == "mount 10.10.10.10:/to_share Z:":
                return ConnectionCompletedProcess(args="", return_code=0)
            else:
                return ConnectionCompletedProcess(args="", return_code=0, stdout="Z: was deleted successfully.")

        mount._conn.execute_command = mocker.Mock(side_effect=conn_stdout)
        with mount.mount_nfs(mount_point="Z:", share_path="10.10.10.10:/to_share"):
            mount._conn.execute_command.assert_called_with(
                "mount 10.10.10.10:/to_share Z:", custom_exception=NFSMountException
            )

        mount._conn.execute_command.assert_called_with("net use Z: /delete", custom_exception=UnmountException)
        assert mount._conn.execute_command.call_count == 2

    def test_mount_nfs_with_user(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_nfs(mount_point="Z:", share_path="10.10.10.10:/to_share", username="admin")
        mount._conn.execute_command.assert_called_once_with(
            "mount -u:admin 10.10.10.10:/to_share Z:", custom_exception=NFSMountException
        )

    def test_mount_nfs_with_user_context_manager(self, mocker, mount):
        def conn_stdout(command, custom_exception):
            if command == "mount -u:admin 10.10.10.10:/to_share Z:":
                return ConnectionCompletedProcess(args="", return_code=0)
            else:
                return ConnectionCompletedProcess(args="", return_code=0, stdout="Z: was deleted successfully.")

        mount._conn.execute_command = mocker.Mock(side_effect=conn_stdout)
        with mount.mount_nfs(mount_point="Z:", share_path="10.10.10.10:/to_share", username="admin"):
            mount._conn.execute_command.assert_called_with(
                "mount -u:admin 10.10.10.10:/to_share Z:", custom_exception=NFSMountException
            )

        mount._conn.execute_command.assert_called_with("net use Z: /delete", custom_exception=UnmountException)
        assert mount._conn.execute_command.call_count == 2

    def test_mount_nfs_with_user_password(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_nfs(mount_point="Z:", share_path="10.10.10.10:/to_share", username="admin", password="pass")
        mount._conn.execute_command.assert_called_once_with(
            "mount -u:admin -p:pass 10.10.10.10:/to_share Z:", custom_exception=NFSMountException
        )

    def test_mount_nfs_with_user_password_context_manager(self, mocker, mount):
        def conn_stdout(command, custom_exception):
            if command == "mount -u:admin -p:pass 10.10.10.10:/to_share Z:":
                return ConnectionCompletedProcess(args="", return_code=0)
            else:
                return ConnectionCompletedProcess(args="", return_code=0, stdout="Z: was deleted successfully.")

        mount._conn.execute_command = mocker.Mock(side_effect=conn_stdout)
        with mount.mount_nfs(mount_point="Z:", share_path="10.10.10.10:/to_share", username="admin", password="pass"):
            mount._conn.execute_command.assert_called_with(
                "mount -u:admin -p:pass 10.10.10.10:/to_share Z:", custom_exception=NFSMountException
            )

        mount._conn.execute_command.assert_called_with("net use Z: /delete", custom_exception=UnmountException)
        assert mount._conn.execute_command.call_count == 2

    def test_mount_cifs(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_cifs(mount_point="Z:", share_path=r"\\10.10.10.10\to_share")
        mount._conn.execute_command.assert_called_once_with(
            r"net use Z: \\10.10.10.10\to_share /persistent:no", custom_exception=CIFSMountException
        )

    def test_mount_cifs_with_user(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_cifs(mount_point="Z:", share_path=r"\\10.10.10.10\to_share", username="admin")
        mount._conn.execute_command.assert_called_once_with(
            r"net use Z: \\10.10.10.10\to_share /persistent:no /user:admin", custom_exception=CIFSMountException
        )

    def test_mount_cifs_with_user_password(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_cifs(mount_point="Z:", share_path=r"\\10.10.10.10\to_share", username="admin", password="pass")
        mount._conn.execute_command.assert_called_once_with(
            r"net use Z: \\10.10.10.10\to_share /persistent:no /user:admin pass", custom_exception=CIFSMountException
        )

    def test_mount_cifs_context_manager(self, mount):
        mount._conn.execute_command.side_effect = [
            ConnectionCompletedProcess(args="", return_code=0),
            ConnectionCompletedProcess(args="", return_code=0, stdout="Z: was deleted successfully."),
        ]
        with mount.mount_cifs(mount_point="Z:", share_path=r"\\10.10.10.10\to_share"):
            mount._conn.execute_command.assert_called_once_with(
                r"net use Z: \\10.10.10.10\to_share /persistent:no", custom_exception=CIFSMountException
            )
        mount._conn.execute_command.assert_called_with("net use Z: /delete", custom_exception=UnmountException)
        assert mount._conn.execute_command.call_count == 2

    def test_mount_cifs_with_user_context_manager(self, mount):
        mount._conn.execute_command.side_effect = [
            ConnectionCompletedProcess(args="", return_code=0),
            ConnectionCompletedProcess(args="", return_code=0, stdout="Z: was deleted successfully."),
        ]
        with mount.mount_cifs(mount_point="Z:", share_path=r"\\10.10.10.10\to_share", username="admin"):
            mount._conn.execute_command.assert_called_with(
                r"net use Z: \\10.10.10.10\to_share /persistent:no /user:admin", custom_exception=CIFSMountException
            )
        assert mount._conn.execute_command.call_count == 2

    def test_mount_cifs_with_user_password_context_manager(self, mount):
        mount._conn.execute_command.side_effect = [
            ConnectionCompletedProcess(args="", return_code=0),
            ConnectionCompletedProcess(args="", return_code=0, stdout="Z: was deleted successfully."),
        ]
        with mount.mount_cifs(
            mount_point="Z:", share_path=r"\\10.10.10.10\to_share", username="admin", password="pass"
        ):
            mount._conn.execute_command.assert_called_once_with(
                r"net use Z: \\10.10.10.10\to_share /persistent:no /user:admin pass",
                custom_exception=CIFSMountException,
            )
        assert mount._conn.execute_command.call_count == 2

    def test_is_mounted_true(self, mount):
        mount_point = "shared_directory"
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        assert mount.is_mounted(mount_point) is True
        mount._conn.execute_command.assert_called_once_with(f"net use {mount_point}")

    def test_is_mounted_false(self, mount):
        mount_point = "shared_directory"
        mount._conn.execute_command.side_effect = subprocess.CalledProcessError(1, "")
        assert mount.is_mounted(mount_point) is False
        mount._conn.execute_command.assert_called_once_with(f"net use {mount_point}")

    def test_umount_failure(self, mount):
        output = "Z: was not successfully deleted."
        mount._conn.execute_command.side_effect = UnmountException(cmd="", returncode=1, stderr=output)
        with pytest.raises(UnmountException):
            mount.umount(mount_point="Z:")

    def test_umount_failure_confirmation(self, mount):
        output = "Z: was not successfully deleted."
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0, stdout=output)
        with pytest.raises(UnmountException):
            mount.umount(mount_point="Z:")

    def test_umount(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(
            args="", return_code=0, stdout="Z: was deleted successfully."
        )
        mount.umount(mount_point="Z:")
        mount._conn.execute_command.assert_called_once_with("net use Z: /delete", custom_exception=UnmountException)
