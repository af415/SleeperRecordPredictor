READ ME:

This is a program to predict the Wins and Losses for a fantasy football league, This has been tailored to a custom
league.
Future work will be done to get the team set up and scoring info so this can be used more widely.

Needed for this to work:
 - MySQL installed locally
 - PIP packages: requests, json, mysql-connector-python
 - command line argument of '-L' or '--League' with a valid league ID, this is used to get the info on the league
 - A 'config.json' file with the following info "host": the host name for the database such as 'localhost',
 "user": the DB user, "password": the password for the user. This needs to be in the sam directory as the python files.
