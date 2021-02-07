import tarfile
import tempfile
from pathlib import Path

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
            control_file.write_bytes(b"test123")

            # When the control archive is created
            control_archive = Dm._build_control_archive(staging)
            control_archive.flush()
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
                assert ctrl_file.read() == b"test123"

    def test_control_archive_debian_scripts(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            staging = Path(tempdir)
            # Given a valid control directory
            debian_dir = staging / "DEBIAN"
            debian_dir.mkdir()

            # And a control file
            control_file = debian_dir / "control"
            control_file.write_bytes(b"test123")

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
