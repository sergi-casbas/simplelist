#!/bin/sh
clear
echo "Empty" | ./simplelist.py --sender=sergi.casbas@rstic.es --local=help-me               --domain=lists.rstic.es 
echo "Empty" | ./simplelist.py --sender=sergi.casbas@rstic.es --local=subscribe-unit-test   --domain=lists.rstic.es
echo "Empty" | ./simplelist.py --sender=sergi.casbas@rstic.es --local=unsubscribe-unit-test --domain=lists.rstic.es
echo "Empty" | ./simplelist.py --sender=sergi.casbas@rstic.es --local=subscribe-unit-test   --domain=lists.rstic.es
echo "Body " | ./simplelist.py --sender=sergi.casbas@rstic.es --local=unit-test            --domain=lists.rstic.es

