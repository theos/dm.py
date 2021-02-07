# dm.py
A python module for creating .deb files without dpkg installed. It works as a drop-in replacement for `dpkg-deb -b`, with compatible flags.

## Synopsis
```
python dm.py [options] <directory> <package>
```

## Options
* **`-b`**: This option exists solely for compatibility with dpkg-deb.
* **`-Z<compression>`**: Specify the package compression type. Valid values are gzip (default), bzip2, and lzma (not legacy lzma)
* **`-z<compress-level>`**: Specify the package compression level. Valid values are between 0 and 9. Default is 9. Refer to **gzip(1)**, **bzip2(1)**, **xz(1)** for explanations of what effect each compression level has.
* **`--help`, `-h`**: Print a brief help message and exit.

## License
Licensed under the MIT License. Refer to [LICENSE.md](LICENSE.md).