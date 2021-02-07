import tarfile
import tempfile
from pathlib import Path

import pytest
from dm import Dm


class TestControlArchive:
    def test_build_control_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            staging = Path(tempdir)
            # Given a valid control directory
            debian_dir = staging / "DEBIAN"
            debian_dir.mkdir()

            # And a control file
            control_file = debian_dir / "control"
            control_file.write_bytes(b"Package: com.test\nVersion: 1.0\nArchitecture: arm64")

            # When the control archive is created
            control_archive = Dm._build_control_archive(staging)

            # Archive data is returned
            archive_data = control_archive.getvalue()
            assert len(archive_data) > 10

            # And its gzip data
            assert archive_data[0:4] == b"\x1f\x8b\x08\x00"

            # When the archive is ungzipped
            control_archive.seek(0)
            with tarfile.open(fileobj=control_archive, mode="r:gz") as tarf:
                # It contains the control file
                ctrl_file = tarf.extractfile(tarf.getmember("control"))
                assert ctrl_file is not None
                # And the file has the correct contents
                assert ctrl_file.read() == b"Package: com.test\nVersion: 1.0\nArchitecture: arm64"

    def test_control_archive_debian_scripts(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            staging = Path(tempdir)
            # Given a valid control directory
            debian_dir = staging / "DEBIAN"
            debian_dir.mkdir()

            # And a control file
            control_file = debian_dir / "control"
            control_file.write_bytes(b"Package: com.test\nVersion: 1.0\nArchitecture: arm64")

            # And a postinst and preinst
            postinst = debian_dir / "postinst"
            postinst.write_bytes(b"echo 1234")
            preinst = debian_dir / "preinst"
            preinst.write_bytes(b"echo done")

            # When the control archive is created
            control_archive = Dm._build_control_archive(staging)

            # Archive data is returned
            archive_data = control_archive.getvalue()
            assert len(archive_data) > 10

            # And its gzip data
            assert archive_data[0:4] == b"\x1f\x8b\x08\x00"

            # When the archive is ungzipped
            control_archive.seek(0)
            with tarfile.open(fileobj=control_archive, mode="r:gz") as tarf:
                # It contains all of the expected files
                assert "control" in tarf.getnames()
                assert "preinst" in tarf.getnames()
                assert "postinst" in tarf.getnames()

    def test_control_archive__bad_permissions__high(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            staging = Path(tempdir)
            # Given a valid control directory
            debian_dir = staging / "DEBIAN"
            debian_dir.mkdir()

            # And a control file with an invalid mode
            control_file = debian_dir / "control"
            control_file.write_bytes(b"Package: com.test\nVersion: 1.0\nArchitecture: arm64")
            control_file.chmod(777)

            # When the control archive is created
            with pytest.raises(Exception) as exc_info:
                Dm._build_control_archive(staging)
            # An exception is raised due to invalid file permissions
            assert str(exc_info.value) == "invalid file permissions"

    def test_control_archive__bad_permissions__low(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            staging = Path(tempdir)
            # Given a valid control directory
            debian_dir = staging / "DEBIAN"
            debian_dir.mkdir()

            # And a control file with an invalid mode
            control_file = debian_dir / "control"
            control_file.write_bytes(b"Package: com.test\nVersion: 1.0\nArchitecture: arm64")
            control_file.chmod(550)

            # When the control archive is created
            with pytest.raises(Exception) as exc_info:
                Dm._build_control_archive(staging)
            # An exception is raised due to invalid file permissions
            assert str(exc_info.value) == "invalid file permissions"

    def test_control_archive__invalid_package(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            staging = Path(tempdir)
            # Given a valid control directory
            debian_dir = staging / "DEBIAN"
            debian_dir.mkdir()

            # And a control file with an invalid mode
            control_file = debian_dir / "control"
            control_file.write_bytes(b"Package: com.testINVALID\nVersion: 1.0\nArchitecture: arm64")

            # When the control archive is created
            with pytest.raises(Exception) as exc_info:
                Dm._build_control_archive(staging)
            # An exception is raised
            assert str(exc_info.value) == "Package name has characters that aren't lowercase alphanums or '-+.'."

    def test_control_archive__invalid_version(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            staging = Path(tempdir)
            # Given a valid control directory
            debian_dir = staging / "DEBIAN"
            debian_dir.mkdir()

            # And a control file with an invalid mode
            control_file = debian_dir / "control"
            control_file.write_bytes(b"Package: com.test\nVersion: womp\nArchitecture: arm64")

            # When the control archive is created
            with pytest.raises(Exception) as exc_info:
                Dm._build_control_archive(staging)
            # An exception is raised
            assert str(exc_info.value) == "Package version womp doesn't contain any digits."
