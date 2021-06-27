# AppMemDumper

## Description

This tool automates the research of some artifacts for forensics purpose in memory dumps based upon Volatility for a series of common Windows applications.

It can also open multiple archive formats. In case of an archive, the tool will extract all its files to a temporary directory and then try to open each file as a memory dump (except files named README or README.md).

## Code

See [this GitHub repository](https://github.com/dhondta/AppmemDumper).

## Help

```sh
$ app-mem-dumper -h
usage: app-mem-dumper [-a APPS] [-d DUMP_DIR] [-f] [-p PLUGINS_DIR]
                      [-t TEMP_DIR] [-h] [-v]
                      dump

AppMemDumper v2.1.3
Author   : Alexandre D'Hondt
Copyright: © 2019 A. D'Hondt
License  : AGPLv3 (http://www.gnu.org/licenses/agpl.html)

This tool automates the research of some artifacts for forensics purpose in
 memory dumps based upon Volatility for a series of common Windows applications.

It can also open multiple archive formats (it uses pyunpack). In case of an
 archive, the tool will extract all its files to a temporary directory and then
 try to open each file as a memory dump.

positional arguments:
  dump                  memory dump file path

optional arguments:
  -a APPS               comma-separated list of integers designating applications to be parsed (default: *)
                         Currently supported: 
                          [0] AdobeReader
                          [1] Clipboard*
                          [2] CriticalProcessesInfo*
                          [3] DumpInfo*
                          [4] Firefox
                          [5] FoxitReader
                          [6] InternetExplorer
                          [7] KeePass
                          [8] MSPaint
                          [9] MediaPlayerClassic
                          [10] Mimikatz*
                          [11] Notepad
                          [12] OpenOffice
                          [13] PDFLite
                          [14] SumatraPDF
                          [15] TrueCrypt
                          [16] UserHashes*
                          [17] Wordpad
                         (*: general-purpose dumper) (default: all)
  -d DUMP_DIR, --dump-dir DUMP_DIR
                        dump directory (default: ./files/) (default: files)
  -f, --force           force profile search, do not use cached profile (default: false) (default: False)
  -p PLUGINS_DIR, --plugins-dir PLUGINS_DIR
                        path to custom plugins directory (default: none) (default: None)
  -t TEMP_DIR, --temp-dir TEMP_DIR
                        temporary directory for decompressed images (default: ./.temp/) (default: .temp)

extra arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose mode (default: False)

Usage examples:
  app-mem-dumper memory.dmp
  app-mem-dumper my-dumps.tar.gz
  app-mem-dumper dump.raw -a 0,1 -f

```

## Execution

```sh
$ app-mem-dumper memory.dump -v -p plugins
[appmemdumper] XX:XX:XX [DEBUG] Attempting to decompress 'memory.dump'...
[appmemdumper] XX:XX:XX [DEBUG] Not an archive, continuing...
[appmemdumper] XX:XX:XX [DEBUG] Setting output directory to 'files/memory.dump'...
[appmemdumper] XX:XX:XX [INFO] Opening dump file 'memory.dump'...
[appmemdumper] XX:XX:XX [INFO] Getting profile...
[appmemdumper] XX:XX:XX [INFO] Getting processes...
[appmemdumper] XX:XX:XX [DEBUG] > Executing command 'pslist'...
[appmemdumper] XX:XX:XX [DEBUG] Found       : mspaint.exe
[appmemdumper] XX:XX:XX [DEBUG] Not handled : audiodg.exe, csrss.exe, dllhost.exe, [...]
[appmemdumper] XX:XX:XX [DEBUG] Profile: Win7SP0x86
[appmemdumper] XX:XX:XX [INFO] Processing dumper 'dumpinfo'...
[appmemdumper] XX:XX:XX [INFO] Processing dumper 'mspaint'...
[appmemdumper] XX:XX:XX [DEBUG] Dumping for PID XXXX
[appmemdumper] XX:XX:XX [DEBUG] > Calling command 'memdump'...
[appmemdumper] XX:XX:XX [DEBUG] >> volatility --plugins=/path/to/plugins --file=[...]
[appmemdumper] XX:XX:XX [INFO] > /path/to/files/memory.dump/mspaint-2640-memdump.data
[appmemdumper] XX:XX:XX [WARNING] 
The following applies to collected objects of:
- mspaint

Raw data (.data files) requires manual handling ;
Follow this procedure:
 1. Open the collected resources with Gimp
 2. Set the width and height to the expected screen resolution
 3. Set another color palette than 'RVB'
Restart this procedure by setting other parameters for width|height|palette.

```
