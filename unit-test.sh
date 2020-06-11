#!/bin/sh

cat unit-test/body.txt | ./simplelist.py --sender=sergi.casbas@rstic.es --recipient=subscribe-milista@lists.rstic.es --local=subscribe-milista --domain=lists.rstic.es --mailbox=Inbox

