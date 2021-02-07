import gzip
import tarfile
import time
from io import BytesIO
from pathlib import Path


class Dm(object):

    @classmethod
    def validate(cls, directory: Path) -> None:
        control_directory = directory / "DEBIAN"
        if not control_directory.exists() or not control_directory.is_dir():
            raise Exception("control directory is invalid")

        control_file = control_directory / "control"
        if not control_file.exists():
            raise Exception("control file missing")

    @classmethod
    def add_file_to_archive(cls, name: str, data: BytesIO, archive) -> None:
        """ Add a file into an AR archive
        """
        filename = name.ljust(16, " ").encode("utf-8")
        archive.write(filename)

        timestamp = str(int(time.time())).ljust(12, " ").encode("utf-8")
        archive.write(timestamp)

        uid = "0".ljust(6, " ").encode("utf-8")
        archive.write(uid)

        gid = "0".ljust(6, " ").encode("utf-8")
        archive.write(gid)

        mode = "0100644".ljust(8, " ").encode("utf-8")
        archive.write(mode)

        file_data = data.getvalue()
        size = str(len(file_data)).ljust(10, " ").encode("utf-8")
        archive.write(size)

        archive.write(b"`\n")

        archive.write(file_data)
        if len(file_data) % 2 == 1:
            archive.write(b"\n")

    @classmethod
    def build_package(cls, in_directory: str, destination: str) -> None:
        """ Build a deb file from the contents of the provided directory
        """
        TARGET = Path(in_directory)
        Dm.validate(TARGET)

        debian_bin = BytesIO()
        debian_bin.write(b"2.0 ")

        # Build the control archive
        control_tar = BytesIO()
        control_directory = TARGET / "DEBIAN"
        with tarfile.open(fileobj=control_tar, mode="w:gz") as tarf:
            for f in control_directory.iterdir():
                tarf.add(f.as_posix(), arcname=f.name)

        # Build the data archive
        data_archive = BytesIO()
        with tarfile.open(fileobj=data_archive, mode="w:xz") as tarf:
            for f in TARGET.glob("**/*"):
                if f.parent.name == "DEBIAN":
                    continue

                if f.is_dir() or f.name == ".DS_Store":
                    continue

                relative_path = f.relative_to(TARGET)
                tarf.add(f.as_posix(), arcname=f"/{relative_path.as_posix()}")

        with open(destination, mode="wb") as debf:
            debf.write(b"!<arch>\n")
            Dm.add_file_to_archive("debian-binary", debian_bin, debf)
            Dm.add_file_to_archive("control.tar.gz", control_tar, debf)
            Dm.add_file_to_archive("data.tar.xz", data_archive, debf)


Dm.build_package("/Users/user/Desktop/carplay-cast/.theos/_", "final.deb")