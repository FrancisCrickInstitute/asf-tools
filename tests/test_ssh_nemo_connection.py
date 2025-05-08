"""
Tests for the Nemo module.
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,invalid-name

from unittest.mock import MagicMock, patch

from assertpy import assert_that

from asf_tools.ssh.nemo import Nemo


class TestNemoConnection:

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_init_with_key_file(self, MockConnection):
        nemo = Nemo(host="login.nemo.thecrick.org", user="svc-asf-seq", key_file="/path/to/key")
        MockConnection.assert_called_once_with(host="login.nemo.thecrick.org", user="svc-asf-seq", connect_kwargs={"key_filename": "/path/to/key"})
        assert_that(nemo.connection).is_not_none()

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_init_with_password(self, MockConnection):
        nemo = Nemo(host="login.nemo.thecrick.org", user="svc-asf-seq", password="password")
        MockConnection.assert_called_once_with(host="login.nemo.thecrick.org", user="svc-asf-seq", connect_kwargs={"password": "password"})
        assert_that(nemo.connection).is_not_none()

    def test_nemo_init_without_key_or_password(self):
        assert_that(Nemo).raises(ValueError).when_called_with(host="login.nemo.thecrick.org", user="svc-asf-seq")

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_disconnect(self, MockConnection):
        nemo = Nemo(host="login.nemo.thecrick.org", user="svc-asf-seq", password="password")
        nemo.disconnect()
        MockConnection().close.assert_called_once()
        assert_that(nemo.connection).is_none()

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_run_command(self, MockConnection):
        mock_result = MagicMock()
        mock_result.stdout.strip.return_value = "command output"
        mock_result.stderr.strip.return_value = "error output"
        MockConnection().run.return_value = mock_result

        nemo = Nemo(host="login.nemo.thecrick.org", user="user", password="password")
        stdout, stderr = nemo.run_command("ls -las")

        MockConnection().run.assert_called_once_with("ls -las", hide=True)
        assert_that(stdout).is_equal_to("command output")
        assert_that(stderr).is_equal_to("error output")

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_list_directory_objects(self, MockConnection):
        mock_result = MagicMock()
        mock_result.stdout.strip.return_value = (
            "total 8\n"
            "drwxr-xr-x 2 user group 4096 2023-10-01 12:34 .\n"
            "drwxr-xr-x 3 user group 4096 2023-10-01 12:34 ..\n"
            "-rw-r--r-- 1 user group 1234 2023-10-01 12:34 test_file.txt\n"
            "lrwxrwxrwx 1 user group 1234 2023-10-01 12:34 link -> target"
        )
        MockConnection().run.return_value = mock_result

        nemo = Nemo(host="login.nemo.thecrick.org", user="user", password="password")
        files = nemo.list_directory_objects("~")

        MockConnection().run.assert_called_once_with("cd ~ && ls -la --time-style=long-iso", hide=True)
        assert_that(files).is_length(4)
        assert_that(files[0].name).is_equal_to(".")
        assert_that(files[1].name).is_equal_to("..")
        assert_that(files[2].name).is_equal_to("test_file.txt")
        assert_that(files[3].name).is_equal_to("link")
        assert_that(files[3].link_target).is_equal_to("target")

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_list_directory(self, MockConnection):
        mock_result = MagicMock()
        mock_result.stdout.strip.return_value = (
            "total 8\n"
            "drwxr-xr-x 2 user group 4096 2023-10-01 12:34 .\n"
            "drwxr-xr-x 3 user group 4096 2023-10-01 12:34 ..\n"
            "-rw-r--r-- 1 user group 1234 2023-10-01 12:34 test_file.txt\n"
            "lrwxrwxrwx 1 user group 1234 2023-10-01 12:34 link -> target"
        )
        MockConnection().run.return_value = mock_result

        nemo = Nemo(host="login.nemo.thecrick.org", user="user", password="password")
        files = nemo.list_directory("~")

        MockConnection().run.assert_called_once_with("cd ~ && ls -la --time-style=long-iso", hide=True)
        assert_that(files).is_length(4)
        assert_that(files[0]).is_equal_to(".")
        assert_that(files[1]).is_equal_to("..")
        assert_that(files[2]).is_equal_to("test_file.txt")
        assert_that(files[3]).is_equal_to("link")

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_exists(self, MockConnection):
        mock_result = MagicMock()
        mock_result.ok = True
        MockConnection().run.return_value = mock_result

        nemo = Nemo(host="login.nemo.thecrick.org", user="user", password="password")
        result = nemo.exists("~")

        MockConnection().run.assert_called_once_with("test -e ~", hide=True)
        assert_that(result).is_true()

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_exists_with_pattern(self, MockConnection):
        mock_result = MagicMock()
        mock_result.stdout.strip.return_value = "test_file.txt"
        MockConnection().run.return_value = mock_result

        nemo = Nemo(host="login.nemo.thecrick.org", user="user", password="password")
        result = nemo.exists_with_pattern("/home/user", "test_file.txt")

        MockConnection().run.assert_called_once_with("find /home/user -maxdepth 1 -name 'test_file.txt'", hide=True)
        assert_that(result).is_true()

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_make_dirs(self, MockConnection):
        nemo = Nemo(host="login.nemo.thecrick.org", user="user", password="password")
        nemo.make_dirs("/some/new/directory")
        MockConnection().run.assert_called_once_with("mkdir -p /some/new/directory", hide=True)

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_write_file(self, MockConnection):
        nemo = Nemo(host="login.nemo.thecrick.org", user="user", password="password")
        nemo.write_file("/some/path/to/file.txt", "file content")
        MockConnection().run.assert_called_once_with("cat <<'EOF' > /some/path/to/file.txt\nfile content\nEOF", hide=True)

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_read_file(self, MockConnection):
        mock_result = MagicMock()
        mock_result.stdout.strip.return_value = "file content"
        MockConnection().run.return_value = mock_result

        nemo = Nemo(host="login.nemo.thecrick.org", user="user", password="password")
        content = nemo.read_file("/some/path/to/file.txt")

        MockConnection().run.assert_called_once_with("cat /some/path/to/file.txt", hide=True)
        assert_that(content).is_equal_to("file content")

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_chmod(self, MockConnection):
        nemo = Nemo(host="login.nemo.thecrick.org", user="user", password="password")
        nemo.chmod("/some/path/to/file.txt", "755")
        MockConnection().run.assert_called_once_with("chmod 755 /some/path/to/file.txt", hide=True)

    # def test_nemo_check_slurm_job_status(self):
    #     # Load key from file into memory
    #     with open("/Users/cheshic/.ssh/svc_asf", "r") as key_file:
    #         key_data = key_file.read()

    #     nemo = Nemo(host="login007.nemo.thecrick.org", user="svc-asf-seq", key_string=key_data)
    #     result = nemo.check_slurm_job_status("nf-bcl2fastq_default_(ReformattedSampleSheet.csv)", "svc-asf-seq")
    #     print(result)

    #     raise NotImplementedError("Test not implemented")

    # def test_nemo_memory_key(self):
    #     # Load key from file into memory
    #     with open("/Users/cheshic/.ssh/nemo_rsa", "r") as key_file:
    #         key_data = key_file.read()

    #     nemo = Nemo(host="login007.nemo.thecrick.org", user="cheshic", key_string=key_data)
    #     test = nemo.exists_with_pattern(".", ".v*")
    #     print(test)

    #     raise NotImplementedError("Test not implemented")

    # def test_nemo_walk(self):
    #     # Load key from file into memory
    #     with open("/Users/cheshic/.ssh/svc_asf", "r") as key_file:
    #         key_data = key_file.read()

    #     nemo = Nemo(host="login007.nemo.thecrick.org", user="svc-asf-seq", key_string=key_data)
    #     for root, dirs, files in nemo.walk("/camp/home/svc-asf-seq/instruments/ONT/ONT_run/20241210_1742_2H_PBA41341_980ccace/results/grouped"):
    #         print(f"Root: {root}")
    #         print(f"Dirs: {dirs}")
    #         print(f"Files: {files}")

    #     raise NotImplementedError("Test not implemented")
