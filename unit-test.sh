#!/bin/sh
set -e
clear
echo "Empty" | ./simplelist.py --sender=sergi.casbas@rstic.es --local=subscribe             --domain=lists.rstic.es
echo "Empty" | ./simplelist.py --sender=sergi.casbas@rstic.es --local=help                  --domain=lists.rstic.es 
echo "Empty" | ./simplelist.py --sender=sergi.casbas@rstic.es --local=help-me               --domain=lists.rstic.es 
echo "Empty" | ./simplelist.py --sender=sergi.casbas@rstic.es --local=subscribe-unit-test   --domain=lists.rstic.es
echo "Empty" | ./simplelist.py --sender=sergi.casbas@rstic.es --local=unsubscribe-unit-test --domain=lists.rstic.es
echo "Empty" | ./simplelist.py --sender=sergi.casbas@rstic.es --local=subscribe-unit-test   --domain=lists.rstic.es
echo "Body " | ./simplelist.py --sender=sergi.casbas@rstic.es --local=unit-test             --domain=lists.rstic.es

cat unit-test/body-auto-generated-no.eml |    ./simplelist.py --sender=sergi.casbas@rstic.es --local=unit-test --domain=lists.rstic.es
cat unit-test/body-auto-generated.eml |    ./simplelist.py --sender=sergi.casbas@rstic.es --local=unit-test --domain=lists.rstic.es
cat unit-test/body-auto-submitted.eml |    ./simplelist.py --sender=sergi.casbas@rstic.es --local=unit-test --domain=lists.rstic.es

