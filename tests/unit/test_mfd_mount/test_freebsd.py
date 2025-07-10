# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

import pytest
from mfd_connect import RPyCConnection
from mfd_connect.base import ConnectionCompletedProcess

from mfd_mount import FreeBSDMount
from mfd_mount.exceptions import CIFSMountException, CIFSUpdatingNSMBConfFileException, MountException


class TestFreeBSDMount:
    @pytest.fixture()
    def mount(self, mocker):
        return FreeBSDMount(connection=mocker.create_autospec(RPyCConnection))

    def test_mount_cifs(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_cifs(mount_point="/mnt/shared", share_path="10.10.10.10/to_share", username="foo")
        mount._conn.execute_command.assert_called_once_with(
            "mount_smbfs -I 10.10.10.10 //foo@10.10.10.10/to_share /mnt/shared", custom_exception=CIFSMountException
        )

    def test_mount_cifs_no_username(self, mount):
        with pytest.raises(MountException):
            mount.mount_cifs(mount_point="/mnt/shared", share_path="10.10.10.10/to_share")

    def test_mount_cifs_with_password_existing_in_nsmb_file(self, mount):
        mount._conn.path().read_text.return_value = "[10.10.10.10:FOO]\npassword=pass"
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_cifs(mount_point="/mnt/shared", share_path="10.10.10.10/to_share", username="foo", password="pass")
        mount._conn.execute_command.assert_called_once_with(
            "mount_smbfs -I 10.10.10.10 //foo@10.10.10.10/to_share /mnt/shared", custom_exception=CIFSMountException
        )

    def test_mount_cifs_with_password_not_existing_in_nsmb_file(self, mount):
        mount._conn.path().read_text.side_effect = ["", "[10.10.10.10:FOO]\npassword=pass"]
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        mount.mount_cifs(mount_point="/mnt/shared", share_path="10.10.10.10/to_share", username="foo", password="pass")
        mount._conn.execute_command.assert_called_with(
            "mount_smbfs -I 10.10.10.10 //foo@10.10.10.10/to_share /mnt/shared", custom_exception=CIFSMountException
        )

    def test_mount_cifs_with_password_not_existing_in_nsmb_file_failed_file_update(self, mount):
        mount._conn.path().read_text.side_effect = ["", ""]
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        with pytest.raises(
            CIFSUpdatingNSMBConfFileException, match="nsmb.conf file does not have credentials. Updating file failed!"
        ):
            mount.mount_cifs(
                mount_point="/mnt/shared", share_path="10.10.10.10/to_share", username="foo", password="pass"
            )

    def test_mount_cifs_context_manager(self, mount):
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        with mount.mount_cifs(mount_point="/mnt/shared", share_path="10.10.10.10/to_share", username="foo"):
            mount._conn.execute_command.assert_called_with(
                "mount_smbfs -I 10.10.10.10 //foo@10.10.10.10/to_share /mnt/shared",
                custom_exception=CIFSMountException,
            )
        assert mount._conn.execute_command.call_count == 2

    def test_mount_cifs_with_password_existing_in_nsmb_file_context_manager(self, mount):
        mount._conn.path().read_text.return_value = "[10.10.10.10:FOO]\npassword=pass"
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        with mount.mount_cifs(
            mount_point="/mnt/shared", share_path="10.10.10.10/to_share", username="foo", password="pass"
        ):
            mount._conn.execute_command.assert_called_with(
                "mount_smbfs -I 10.10.10.10 //foo@10.10.10.10/to_share /mnt/shared",
                custom_exception=CIFSMountException,
            )
        assert mount._conn.execute_command.call_count == 2

    def test_mount_cifs_with_password_not_existing_in_nsmb_file_context_manager(self, mount):
        mount._conn.path().read_text.side_effect = ["", "[10.10.10.10:FOO]\npassword=pass"]
        mount._conn.execute_command.return_value = ConnectionCompletedProcess(args="", return_code=0)
        with mount.mount_cifs(
            mount_point="/mnt/shared", share_path="10.10.10.10/to_share", username="foo", password="pass"
        ):
            mount._conn.execute_command.assert_called_with(
                "mount_smbfs -I 10.10.10.10 //foo@10.10.10.10/to_share /mnt/shared",
                custom_exception=CIFSMountException,
            )
        assert mount._conn.execute_command.call_count == 3
