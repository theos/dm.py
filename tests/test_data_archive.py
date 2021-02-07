import tarfile
import tempfile
from pathlib import Path

from dm import Dm, CompressionType


class TestDataArchive:
    def test_build_data_archive__lzma(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            staging = Path(tempdir)
            # Given some test files
            for fname in ["test1", "test2", "test3"]:
                f = staging / fname
                f.write_bytes(b"file data 123")

            # When an lzma data archive is created
            data_archive = Dm._build_data_archive(staging, CompressionType.LZMA)

            # Archive data is returned
            archive_data = data_archive.getvalue()
            assert len(archive_data) > 10

            # And its lzma data
            assert archive_data[0:4] == b"\xfd7zX"

            # When the archive is decompressed
            data_archive.seek(0)
            with tarfile.open(fileobj=data_archive, mode="r:xz") as tarf:
                # It contains all of the expected files
                assert "test1" in tarf.getnames()
                assert "test2" in tarf.getnames()
                assert "test3" in tarf.getnames()

    def test_build_data_archive__bz2(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            staging = Path(tempdir)
            # Given some test files
            for fname in ["test1", "test2", "test3"]:
                f = staging / fname
                f.write_bytes(b"file data 123")

            # When an lzma data archive is created
            data_archive = Dm._build_data_archive(staging, CompressionType.BZIP2)

            # Archive data is returned
            archive_data = data_archive.getvalue()
            assert len(archive_data) > 10

            # And its bz2 data
            assert archive_data[0:4] == b"BZh9"

            # When the archive is decompressed
            data_archive.seek(0)
            with tarfile.open(fileobj=data_archive, mode="r:bz2") as tarf:
                # It contains all of the expected files
                assert "test1" in tarf.getnames()
                assert "test2" in tarf.getnames()
                assert "test3" in tarf.getnames()

    def test_build_data_archive__gzip(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            staging = Path(tempdir)
            # Given some test files
            for fname in ["test1", "test2", "test3"]:
                f = staging / fname
                f.write_bytes(b"file data 123")

            # When an lzma data archive is created
            data_archive = Dm._build_data_archive(staging, CompressionType.GZIP)

            # Archive data is returned
            archive_data = data_archive.getvalue()
            assert len(archive_data) > 10

            # And its bz2 data
            assert archive_data[0:4] == b"\x1f\x8b\x08\x00"

            # When the archive is decompressed
            data_archive.seek(0)
            with tarfile.open(fileobj=data_archive, mode="r:gz") as tarf:
                # It contains all of the expected files
                assert "test1" in tarf.getnames()
                assert "test2" in tarf.getnames()
                assert "test3" in tarf.getnames()
