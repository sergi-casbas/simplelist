#!/bin/sh
clear
echo "Empty" | ./simplelist.py --verbose=6 --sender=sergi.casbas@rstic.es --recipient=subscribe-milista@lists.rstic.es --local=subscribe-milista --domain=lists.rstic.es --mailbox=Inbox
echo "Empty" | ./simplelist.py --verbose=6 --sender=sergi.casbas@gft.com --recipient=subscribe-milista@lists.rstic.es --local=subscribe-milista --domain=lists.rstic.es --mailbox=Inbox
echo "Empty" | ./simplelist.py --verbose=6 --sender=sergi.casbas@gft.com --recipient=unsubscribe-milista@lists.rstic.es --local=unsubscribe-milista --domain=lists.rstic.es --mailbox=Inbox
echo "Empty" | ./simplelist.py --verbose=6 --sender=sergi@casbas.cat --recipient=subscribe-milista@lists.rstic.es --local=subscribe-milista --domain=lists.rstic.es --mailbox=Inbox
cat unit-test/body.txt | ./simplelist.py --verbose=6 --sender=sergi.casbas@rstic.es --recipient=milista@lists.rstic.es --local=milista --domain=lists.rstic.es --mailbox=Inbox

