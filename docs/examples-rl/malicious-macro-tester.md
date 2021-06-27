# Malicious Macro Tester

## Description

This CLI tool automates the classification of Office documents with macros using MaliciousMacroBot. It allows to analyze a folder of sample files and to generate a report in multiple output formats.

## Code

See [this GitHub repository](https://github.com/dhondta/malicious-macro-tester).

## Help

```sh
$ malicious-macro-tester -h
usage: malicious-macro-tester [-d] [-f] [-l] [-q] [-r] [-s] [-u]
                              [--api-key VT_KEY]
                              [--output {es,html,json,md,pdf,xml}] [--send]
                              [-h] [-v]
                              FOLDER

MaliciousMacroTester v2.4
Author   : Alexandre D'Hondt
Copyright: © 2019 A. D'Hondt
License  : GNU Affero General Public License v3.0
Reference: INFOM444 - Machine Learning - Hot Topic

This tool uses MaliciousMacroBot to classify a list of samples as benign or
 malicious and provides a report. Note that it only works on an input folder
 and list every file to run it against mmbot.

positional arguments:
  FOLDER                folder with the samples to be tested OR
                        pickle name if results are loaded with -l

optional arguments:
  -d                    dump the VBA macros (default: False)
  -f                    filter only DOC and XLS files (default: False)
  -l                    load previous pickled results (default: False)
  -q                    do not display results report (default: False)
  -r                    when loading pickle, retry VirusTotal hashes with None results
                         (default: False)
  -s                    pickle results to a file (default: False)
  -u                    when loading pickle, update VirusTotal results (default: False)
  --api-key VT_KEY      VirusTotal API key (default: None)
                         NB: key as a string or file path to the key
  --output {es,html,json,md,pdf,xml}
                        report file format (default: None)
  --send                send the data to ElasticSearch (default: False)
                         NB: only applies to 'es' format
                             the configuration is loaded with the following precedence:
                             1. ./elasticsearch.conf
                             2. /etc/elasticsearch/elasticsearch.conf

extra arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose mode (default: False)

Usage examples:
  malicious-macro-tester my_samples_folder
  malicious-macro-tester my_samples_folder --api-key virustotal-key.txt -lr
  malicious-macro-tester my_samples_folder -lsrv --api-key 098fa24...be724a0
  malicious-macro-tester my_samples_folder -lf --output pdf
  malicious-macro-tester my_samples_folder --output es --sent

```

## Execution

```session
$ python malicious-macro-tester.py samples -vfqs --output xml
17:08:09 [INFO] Instantiating and initializing MaliciousMacroBot...
17:09:09 [INFO] Processing samples...
17:09:09 [DEBUG] MMBot: classifying 'file_003.xls'...
17:09:09 [DEBUG] MMBot: classifying 'file_001.doc'...
17:09:09 [DEBUG] MMBot: classifying 'file_005.xls'...
17:09:09 [DEBUG] MMBot: classifying 'file_000.doc'...
17:09:09 [DEBUG] MMBot: classifying 'file_004.xls'...
17:09:10 [DEBUG] MMBot: classifying 'file_002.doc'...
17:09:10 [INFO] Saving results to pickle...
17:09:10 [INFO] Parsing results...
17:09:10 [DEBUG] Generating the JSON report (text only)...
17:09:10 [DEBUG] Generating the XML report...
```
