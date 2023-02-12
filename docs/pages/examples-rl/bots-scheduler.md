# Bots Scheduler

## Description

This tool is a launcher for the [Nextdoor Scheduler](https://github.com/Nextdoor/ndscheduler) with a set of jobs based on robots made with [PyBots](https://github.com/dhondta/pybots).

## Code

See [this GitHub repository](https://github.com/dhondta/bots-scheduler).

## Help

```sh
$ ./bots-scheduler --help
usage: ./bots-scheduler [-h] [-v] {run,clean} ...

BotsScheduler v1.0
Author   : Alexandre D'Hondt
Copyright: © 2019 A. D'Hondt
License  : GNU Affero General Public License v3.0
Reference: https://github.com/Nextdoor/ndscheduler

This tool is a launcher for the Nextdoor Scheduler with a set of jobs based on
 robots made with PyBots (https://github.com/dhondta/pybots)."

positional arguments:
  {run,clean}    command to be executed
    run          run the server
    clean        remove server's virtual environment

extra arguments:
  -h, --help     show this help message and exit
  -v, --verbose  verbose mode (default: False)

```

```sh
$ ./bots-scheduler run --help
usage: ./bots-scheduler run [-h] [-d] [-j JOBS] [-p PORT]
                            [--dbms {sqlite,postgresql,mysql}]
                            [--db-config DB_CONFIG]
                            [--executions-table EXECUTIONS_TABLE]
                            [--jobs-table JOBS_TABLE]
                            [--logs-table LOGS_TABLE] [--job-coalesce]
                            [--job-max-instances JOB_MAX]
                            [--job-misfire JOB_MISFIRE]
                            [--threadpool-size TP_SIZE] [--timezone TIMEZONE]
                            [--max-workers TWORKERS]

BotsScheduler v1.0
Author   : Alexandre D'Hondt
Copyright: © 2019 A. D'Hondt
License  : GNU Affero General Public License v3.0
Reference: https://github.com/Nextdoor/ndscheduler

This tool is a launcher for the Nextdoor Scheduler with a set of jobs based on
 robots made with PyBots (https://github.com/dhondta/pybots)."

extra arguments:
  -h, --help            show this help message and exit

base options:
  -d, --debug           run the server in debug mode (default: False)
  -j JOBS, --jobs JOBS  folder with jobs to be imported (default: ['jobs'])
  -p PORT, --port PORT  server's port number (default: 8888)

database options:
  --dbms {sqlite,postgresql,mysql}
                        database management system (default: sqlite)
  --db-config DB_CONFIG
                        database INI configuration file (default: db.conf)
  --executions-table EXECUTIONS_TABLE
                        executions table name (default: scheduler_execution)
  --jobs-table JOBS_TABLE
                        jobs table name (default: scheduler_jobs)
  --logs-table LOGS_TABLE
                        logs table name (default: scheduler_jobauditlog)

APScheduler options:
  --job-coalesce        Coalesce missed executions of a job (default: True)
  --job-max-instances JOB_MAX
                        Maximum number of concurrently executing instances of a job (default: 3)
  --job-misfire JOB_MISFIRE
                        Job misfire grace time in seconds (default: 3600)
  --threadpool-size TP_SIZE
                        Threadpool size (default: 2)
  --timezone TIMEZONE   server's timezone (default: UTC)

Tornado options:
  --max-workers TWORKERS
                        Maximum number of workers (default: 8)

```

## Execution

```sh
$ ./bots-scheduler run -d
                     ____ ____ ____ ____ ____ ____ ____ ____ ____ ____ ____ ____ ____                    
                    ||B |||o |||t |||s |||S |||c |||h |||e |||d |||u |||l |||e |||r ||                   
                    ||__|||__|||__|||__|||__|||__|||__|||__|||__|||__|||__|||__|||__||                   
                    |/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|                   
                                                                                                         
 
09:30:17 [INFO] Setting up the virtual environment...
09:30:20 [INFO] Starting the scheduling server...
09:30:21 [INFO] Scheduler started
09:30:21 [INFO] Running server at 127.0.0.1:8888 ...
09:30:21 [INFO] *** You can access scheduler web ui at http://localhost:8888 ***
09:30:31 [INFO] 200 GET / (127.0.0.1) 559.58ms
09:30:31 [INFO] 200 GET /static/css/vendor/bootstrap.css (127.0.0.1) 5.15ms
09:30:31 [INFO] 200 GET /static/css/vendor/bootstrap-switch.css (127.0.0.1) 0.87ms
09:30:31 [INFO] 200 GET /static/css/vendor/jquery.dataTables.css (127.0.0.1) 0.92ms
09:30:31 [INFO] 200 GET /static/css/vendor/select2.css (127.0.0.1) 1.00ms
09:30:31 [INFO] 200 GET /static/css/vendor/select2-bootstrap.css (127.0.0.1) 0.86ms
09:30:31 [INFO] 200 GET /static/css/vendor/highlightjs.min.css (127.0.0.1) 10.46ms
09:30:31 [INFO] 200 GET /static/js/vendor/require.js (127.0.0.1) 0.94ms
09:30:31 [INFO] 200 GET /static/css/main.css (127.0.0.1) 0.92ms
09:30:31 [INFO] 200 GET /static/js/app.js (127.0.0.1) 0.63ms
09:30:31 [WARNING] 404 GET /favicon.ico (127.0.0.1) 1.62ms
09:30:31 [INFO] 200 GET /static/js/views/jobs/jobs-view.js?bust=1573115431768 (127.0.0.1) 1.02ms
09:30:31 [INFO] 200 GET /static/js/models/logs.js?bust=1573115431768 (127.0.0.1) 0.77ms
09:30:31 [INFO] 200 GET /static/js/models/executions.js?bust=1573115431768 (127.0.0.1) 0.82ms
09:30:31 [INFO] 200 GET /static/js/models/jobs.js?bust=1573115431768 (127.0.0.1) 0.86ms
09:30:31 [INFO] 200 GET /static/js/views/logs/logs-view.js?bust=1573115431768 (127.0.0.1) 0.77ms
09:30:31 [INFO] 200 GET /static/js/views/executions/executions-view.js?bust=1573115431768 (127.0.0.1) 0.83ms
09:30:31 [INFO] 200 GET /static/js/vendor/underscore.js?bust=1573115431768 (127.0.0.1) 0.86ms
09:30:31 [INFO] 200 GET /static/js/vendor/jquery.js?bust=1573115431768 (127.0.0.1) 1.15ms
09:30:32 [INFO] 200 GET /static/js/views/jobs/add-job-view.js?bust=1573115431768 (127.0.0.1) 0.68ms
09:30:32 [INFO] 200 GET /static/js/config.js?bust=1573115431768 (127.0.0.1) 0.59ms
09:30:32 [INFO] 200 GET /static/js/models/log.js?bust=1573115431768 (127.0.0.1) 0.52ms
09:30:32 [INFO] 200 GET /static/js/utils.js?bust=1573115431768 (127.0.0.1) 0.54ms
09:30:32 [INFO] 200 GET /static/js/views/jobs/table-view.js?bust=1573115431768 (127.0.0.1) 0.63ms
09:30:32 [INFO] 200 GET /static/js/views/jobs/stats-view.js?bust=1573115431768 (127.0.0.1) 0.59ms
09:30:32 [INFO] 200 GET /static/js/models/execution.js?bust=1573115431768 (127.0.0.1) 0.62ms
09:30:32 [INFO] 200 GET /static/js/models/job.js?bust=1573115431768 (127.0.0.1) 0.97ms
09:30:32 [INFO] 200 GET /static/js/views/logs/filter-view.js?bust=1573115431768 (127.0.0.1) 1.17ms
09:30:32 [INFO] 200 GET /static/js/views/logs/table-view.js?bust=1573115431768 (127.0.0.1) 0.81ms
09:30:32 [INFO] 200 GET /static/js/views/executions/filter-view.js?bust=1573115431768 (127.0.0.1) 1.01ms
09:30:32 [INFO] 200 GET /static/js/views/executions/stats-view.js?bust=1573115431768 (127.0.0.1) 0.97ms
09:30:32 [INFO] 200 GET /static/js/views/executions/table-view.js?bust=1573115431768 (127.0.0.1) 1.12ms
09:30:32 [INFO] 200 GET /static/js/vendor/backbone.js?bust=1573115431768 (127.0.0.1) 1.09ms
09:30:32 [INFO] 200 GET /static/js/vendor/bootstrap.js?bust=1573115431768 (127.0.0.1) 1.09ms
09:30:32 [INFO] 200 GET /static/js/vendor/text.js?bust=1573115431768 (127.0.0.1) 1.01ms
09:30:32 [INFO] 200 GET /static/js/views/jobs/edit-job-view.js?bust=1573115431768 (127.0.0.1) 0.88ms
09:30:32 [INFO] 200 GET /static/js/views/jobs/run-job-view.js?bust=1573115431768 (127.0.0.1) 0.86ms
09:30:32 [INFO] 200 GET /static/js/vendor/select2.js?bust=1573115431768 (127.0.0.1) 1.12ms
09:30:32 [INFO] 200 GET /static/js/vendor/spin.js?bust=1573115431768 (127.0.0.1) 0.85ms
09:30:32 [INFO] 200 GET /static/js/vendor/moment-timezone-with-data.js?bust=1573115431768 (127.0.0.1) 1.57ms
09:30:32 [INFO] 200 GET /static/js/vendor/jquery.noty.js?bust=1573115431768 (127.0.0.1) 1.05ms
09:30:32 [INFO] 200 GET /static/js/vendor/jquery.dataTables.js?bust=1573115431768 (127.0.0.1) 1.27ms
09:30:32 [INFO] 200 GET /static/js/vendor/moment.js?bust=1573115431768 (127.0.0.1) 0.98ms
09:30:32 [INFO] 200 GET /static/js/templates/add-job.html?bust=1573115431768 (127.0.0.1) 0.99ms
09:30:32 [INFO] 200 GET /static/js/templates/run-job.html?bust=1573115431768 (127.0.0.1) 0.80ms
09:30:32 [INFO] 200 GET /static/js/templates/execution-result.html?bust=1573115431768 (127.0.0.1) 0.90ms
09:30:32 [INFO] 200 GET /static/js/templates/job-row-action.html?bust=1573115431768 (127.0.0.1) 0.79ms
09:30:32 [INFO] 200 GET /static/js/templates/job-row-name.html?bust=1573115431768 (127.0.0.1) 0.77ms
09:30:32 [INFO] 200 GET /static/js/templates/job-class-notes.html?bust=1573115431768 (127.0.0.1) 0.81ms
09:30:32 [INFO] 200 GET /static/js/templates/edit-job.html?bust=1573115431768 (127.0.0.1) 0.81ms
09:30:32 [INFO] 200 GET /static/js/vendor/bootstrap-switch.js?bust=1573115431768 (127.0.0.1) 0.73ms
09:30:32 [INFO] 200 GET /static/css/vendor/images/sort_asc.png (127.0.0.1) 0.65ms
09:30:32 [INFO] 200 GET /static/css/vendor/images/sort_both.png (127.0.0.1) 1.73ms
09:30:32 [INFO] 200 GET /api/v1/jobs (127.0.0.1) 3.40ms
^C09:30:36 [INFO] Stopping scheduler ...
09:30:36 [INFO] Done. Bye ~

```
