# Solitaire Cipher

## Description

This tool implements Bruce Schneier's [Solitaire Cipher](https://www.schneier.com/academic/solitaire/).

## Code

See [this GitHub repository](https://github.com/dhondta/solitaire-cipher).

## Help

```sh
$ solitaire-cipher --help
usage: solitaire-cipher [-r INI] [-w INI] [-h] [-v] {decrypt,encrypt} ...

SolitaireCipher v1.1
Author   : Alexandre D'Hondt
Copyright: © 2019 A. D'Hondt
License  : GNU Affero General Public License v3.0
Reference: https://www.schneier.com/academic/solitaire/

This tool implements the Solitaire Encryption Algorithm of Bruce Schneier.

positional arguments:
  {decrypt,encrypt}     commands
    decrypt             decrypt message
    encrypt             encrypt message

config arguments:
  -r INI, --read-config INI
                        read args from a config file (default: None)
                         NB: this overrides other arguments
  -w INI, --write-config INI
                        write args to a config file (default: None)

extra arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose mode (default: False)

Usage examples:
  solitaire-cipher encrypt "AAAAA AAAAA" -p my_super_secret -s
  solitaire-cipher decrypt "AAAAA AAAAA" -p my_super_secret -d deck.txt

```

```sh
$ solitaire-cipher encrypt --help
usage: solitaire-cipher encrypt [-h] [-a A] [-b B] [-d DECK] -p PASSPHRASE
                                [-o OUTPUT] [-s]
                                message

positional arguments:
  message        message to be handled

optional arguments:
  -a A           joker A (default: 53)
  -b B           joker B (default: 54)
  -d DECK        deck file or list of integers (default: 1,2,...,53,54)
  -p PASSPHRASE  passphrase (default: None)
  -o OUTPUT      save the encoded deck to (default: deck.txt)
  -s             shuffle the deck (default: False)

extra arguments:
  -h, --help     show this help message and exit

```

```sh
$ solitaire-cipher decrypt --help
usage: solitaire-cipher decrypt [-h] [-a A] [-b B] [-d DECK] -p PASSPHRASE
                                message

positional arguments:
  message        message to be handled

optional arguments:
  -a A           joker A (default: 53)
  -b B           joker B (default: 54)
  -d DECK        deck file or list of integers (default: 1,2,...,53,54)
  -p PASSPHRASE  passphrase (default: None)

extra arguments:
  -h, --help     show this help message and exit

```

## Execution

```sh
$ solitaire-cipher encrypt "TEST" -s -p my_super_secret
12:34:56 [INFO] IWEJ
12:34:56 [INFO] 28,48,10,24,3,23,2,38,34,6,30,40,8,4,9,11,15,20,31,47,22,35,45,41,49,43,5,13,25,39,19,12,37,33,36,7,16,B,46,29,50,42,26,1,21,A,17,51,14,27,18,44,32,52
12:34:56 [INFO] Saved the encoded deck to 'deck.txt'

```

```sh
$ solitaire-cipher decrypt "IWEJ" -d deck.txt -p my_super_secret
12:34:56 [INFO] TEST
12:34:56 [INFO] 28,48,10,24,3,23,2,38,34,6,30,40,8,4,9,11,15,20,31,47,22,35,45,41,49,43,5,13,25,39,19,12,37,33,36,7,16,B,46,29,50,42,26,1,21,A,17,51,14,27,18,44,32,52

```
