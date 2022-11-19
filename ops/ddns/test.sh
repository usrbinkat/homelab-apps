#!/bin/bash -x
curl https://usrbinkat:xxxxxxxxxxxxxxxxxxxxxxxxxxxxx@updates.dnsomatic.com/nic/update?hostname=home.usrbinkat.io&myip=$(curl myip.dnsomatic.com)&wildcard=NOCHG&mx=NOCHG&backmx=NOCHG
