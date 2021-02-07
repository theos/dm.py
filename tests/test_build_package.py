import tempfile
import time
from io import BytesIO
from pathlib import Path

import pytest
from dm import Dm, CompressionType


class TestDmPackage:
    def test_build_package__lzma(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            staging = Path(tempdir)
            # Given an input dir with a valid control dir and file
            debian_dir = staging / "DEBIAN"
            debian_dir.mkdir()
            control_file = debian_dir / "control"
            control_file.write_bytes(b"test123")

            # And some valid test data
            some_file = staging / "package_file"
            some_file.write_bytes(b"1234567890")

            # When I build a deb
            destination = staging / "test.deb"
            Dm.build_package(tempdir, destination.as_posix())

            # The destination file is created
            assert destination.exists()

            # And it contains bytes
            written_package_bytes = destination.read_bytes()
            assert len(written_package_bytes) > 100

            # And it starts with an ar header
            assert written_package_bytes[0:8] == b"!<arch>\n"

            # And it contains the expected files
            assert b"debian-binary" in written_package_bytes
            assert b"control.tar.gz" in written_package_bytes
            assert b"data.tar.xz" in written_package_bytes

    def test_build_package__bz2(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            staging = Path(tempdir)
            # Given an input dir with a valid control dir and file
            debian_dir = staging / "DEBIAN"
            debian_dir.mkdir()
            control_file = debian_dir / "control"
            control_file.write_bytes(b"test123")

            # And some valid test data
            some_file = staging / "package_file"
            some_file.write_bytes(b"1234567890")

            # When I build a deb
            destination = staging / "test.deb"
            Dm.build_package(tempdir, destination.as_posix(), CompressionType.BZIP2)

            # The destination file is created
            assert destination.exists()

            # And it contains bytes
            written_package_bytes = destination.read_bytes()
            assert len(written_package_bytes) > 100

            # And it starts with an ar header
            assert written_package_bytes[0:8] == b"!<arch>\n"

            # And it contains the expected files
            assert b"debian-binary" in written_package_bytes
            assert b"control.tar.gz" in written_package_bytes
            assert b"data.tar.bz2" in written_package_bytes

    def test_build_package__gzip(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            staging = Path(tempdir)
            # Given an input dir with a valid control dir and file
            debian_dir = staging / "DEBIAN"
            debian_dir.mkdir()
            control_file = debian_dir / "control"
            control_file.write_bytes(b"test123")

            # And some valid test data
            some_file = staging / "package_file"
            some_file.write_bytes(b"1234567890")

            # When I build a deb
            destination = staging / "test.deb"
            Dm.build_package(tempdir, destination.as_posix(), CompressionType.GZIP)

            # The destination file is created
            assert destination.exists()

            # And it contains bytes
            written_package_bytes = destination.read_bytes()
            assert len(written_package_bytes) > 100

            # And it starts with an ar header
            assert written_package_bytes[0:8] == b"!<arch>\n"

            # And it contains the expected files
            assert b"debian-binary" in written_package_bytes
            assert b"control.tar.gz" in written_package_bytes
            assert b"data.tar.gz" in written_package_bytes

    def test_build_package__no_DEBIAN_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            staging = Path(tempdir)
            # Given an input dir with no DEBIAN directory
            debian_dir = staging / "XEBIAN"
            debian_dir.mkdir()

            # When I build a deb
            with pytest.raises(Exception) as exc_info:
                destination = staging / "test.deb"
                Dm.build_package(tempdir, destination.as_posix())

            # An exception is raised about invalid control directory
            assert str(exc_info.value) == "control directory is invalid"

            # And no output file is created
            assert destination.exists() is False

    def test_build_package__no_control_file(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            staging = Path(tempdir)
            # Given an input dir
            debian_dir = staging / "DEBIAN"
            debian_dir.mkdir()

            # With no control file
            control_file = debian_dir / "c4ntrol"
            control_file.write_bytes(b"test123")

            # When I build a deb
            with pytest.raises(Exception) as exc_info:
                destination = staging / "test.deb"
                Dm.build_package(tempdir, destination.as_posix())

            # An exception is raised about invalid control directory
            assert str(exc_info.value) == "control file missing"

            # And no output file is created
            assert destination.exists() is False

    def test_add_file_to_archive__even_bytes(self) -> None:
        # Given a file with some test data
        test_file = BytesIO()
        test_file_data = b"test1234"
        test_file.write(test_file_data)

        # And an ar archive
        ar_archive = BytesIO()

        # When the file is added to the archive
        Dm.add_file_to_archive("testfile", test_file, ar_archive)
        # Data was written to the archive
        data = ar_archive.getvalue()
        assert data is not None

        # And the file record is correct
        # Filename
        assert data[0:16].strip() == b"testfile"
        # Timestamp
        timestamp = int(data[16:28])
        assert int(time.time()) == timestamp
        # UID and GID
        assert int(data[28:34]) == 0
        assert int(data[34:40]) == 0
        # File mode
        assert int(data[40:48]) == 100644
        # File data length
        assert int(data[48:58]) == len(test_file_data)
        # File metadata footer
        assert data[58:60] == b"`\n"

        # And the file data is correct
        assert data[60:] == b"test1234"

    def test_add_file_to_archive__odd_bytes(self) -> None:
        # Given a file with an odd-number amount of test data
        test_file = BytesIO()
        test_file_data = b"test12345"
        test_file.write(test_file_data)

        # And an ar archive
        ar_archive = BytesIO()

        # When the file is added to the archive
        Dm.add_file_to_archive("testfile", test_file, ar_archive)
        # Data was written to the archive
        data = ar_archive.getvalue()
        assert data is not None

        # And the file record is correct
        # Filename
        assert data[0:16].strip() == b"testfile"
        # Timestamp
        timestamp = int(data[16:28])
        assert int(time.time()) == timestamp
        # UID and GID
        assert int(data[28:34]) == 0
        assert int(data[34:40]) == 0
        # File mode
        assert int(data[40:48]) == 100644
        # File data length
        assert int(data[48:58]) == len(test_file_data)
        # File metadata footer
        assert data[58:60] == b"`\n"

        # And the file data is correct
        # And the file contains the "odd bytes" padding
        assert data[60:] == b"test12345\n"
