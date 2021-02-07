from dm import Dm
import tempfile
from pathlib import Path


class TestDmPackage:
    def test_build_package(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            staging = Path(tempdir)
            # Build DEBIAN dir
            debian_dir = staging / "DEBIAN"
            debian_dir.mkdir()

            # Build control file
            control_file = debian_dir / "control"
            control_file.write_bytes(b"test123")

            # Write a data file
            some_file = staging / "package_file"
            some_file.write_bytes(b"1234567890")

            destination = staging / "test.deb"
            # When I build a deb
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
            assert b"data.tar." in written_package_bytes
