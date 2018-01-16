### Monitoring tool

+ Simple website monitoring tool with command line utility. Uses the requests module.
+ Comments scattered throughout indicate places for improvement.
+ Single-page HTTP server interface in the same process that shows (HTML) each monitored web site and their current (last check) status. Usage: run `python -m http.server 8080` then access the url: `http://localhost:8080/`