
These python scripts are examples of connecting to a Substrata server and doing some things:

## substrata_chatbot_demo.py

Creates a user avatar, logs in, walks in circles, and says "Beep Boop" every 5 seconds.

You could extend this example to make the bot chat to a user, follow a user around or whatever.


See https://www.youtube.com/watch?v=j-ja0_GcB4s for a video of it.

## substrata_bot_demo.py

NOTE: Fixing this script up!!!

This script is an example of updating an object on a Substrata server.

It updates an existing text object on the server with the current Eth price, fetched from api.coinbase.com.

Note that you will need to update an object in a parcel you own for this script to have any effect.

NOTE: Fixing this script up!!!


## Running

You will need to put a file called config.txt with contents like this in the script directory, before running the script:

```
[connection]
server_hostname = localhost

[credentials]
Username = MyUserName
Password = MyPassword
```
Where the credentials are for a user account on the substrata server you are connecting to.

You can test on your own substrata server (see https://substrata.info/running_your_own_server) with

```
server_hostname = localhost
```
or on the main substrata server with 
```
server_hostname = substrata.info
```
Please be careful though!  Don't spam messages or create too many objects on the main server.
