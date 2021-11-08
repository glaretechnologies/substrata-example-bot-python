This script is an example of updating an object on the Substata server (the substrata test server, test.substrata.info in particular).

This script makes a network connection to the substrata server and communicates via the Substrata protocol.

It updates the transform of a particular object every 0.1 seconds by sending a ObjectTransformUpdate message to the server.

Note that you will need to update an object in a parcel you own for this script to have any effect.


You will need to put a file call config.txt with contents like this in the script directory, before running the script:
[credentials]
Username = MyUserName
Password = MyPassword
