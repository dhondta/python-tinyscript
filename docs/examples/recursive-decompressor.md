### Description

This tool allows to recursively decompress nested archives according to various decompression algorithms.

### Code

See [this GitHub repository](https://github.com/dhondta/recursive-decompressor).

### Help

```sh
$ recursive-decompressor --help
usage: recursive-decompressor [-d] [-k N] [-h] [-v] archive

RecursiveDecompressor v2.0
Author   : Alexandre D'Hondt
Copyright: © 2019 A. D'Hondt
License  : GNU Affero General Public License v3.0
Training : ZSIS CTF - Trivia - Shining (4 points)

This tool allows to recursively decompress an archive, using multiple Linux decompression
 tools. It currently supports the following tools:
- 7za
- arj
- bzip2
- gunzip
- lzma
- tar
- unrar
- unxz
- unzip

positional arguments:
  archive         input archive

optional arguments:
  -d              display last decompressed file in terminal (default: False)
  -k N, --keep N  keep the last N levels of archives (default: 1)

extra arguments:
  -h, --help      show this help message and exit
  -v, --verbose   verbose mode (default: False)

Usage examples:
  recursive-decompressor archive.zip
  recursive-decompressor archive.zip -d
  recursive-decompressor archive.zip -d -k 3

```

### Execution

```sh
$ ./recursive-decompressor archive.zip -d
12:34:56 [INFO] Decompressing 'archive.zip'...
12:34:56 [INFO] Decompressing 'lbuj21a60q18.lzma'...
[...]
12:45:01 [INFO] Decompressing 'x0x4mf7s7vx4.bz2'...
12:45:01 [WARNING] Nothing more to decompress
12:45:01 [INFO] Files: secret.txt
12:45:01 [SUCCESS] s3cr37

```
