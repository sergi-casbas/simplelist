#!/bin/sh

# Dummy smtp server:
# python -m smtpd -c DebuggingServer -n localhost:2525

set -e
clear
echo "Empty" | ./simplelist.py --sender=me@dummy.domain --local=subscribe             --domain=lists.dummy.domain
echo "Empty" | ./simplelist.py --sender=me@dummy.domain --local=help                  --domain=lists.dummy.domain 
echo "Empty" | ./simplelist.py --sender=me@dummy.domain --local=help-me               --domain=lists.dummy.domain 
echo "Empty" | ./simplelist.py --sender=me@dummy.domain --local=subscribe-unit-test   --domain=lists.dummy.domain
echo "Empty" | ./simplelist.py --sender=me@dummy.domain --local=unsubscribe-unit-test --domain=lists.dummy.domain
echo "Empty" | ./simplelist.py --sender=me@dummy.domain --local=subscribe-unit-test   --domain=lists.dummy.domain
echo "Body " | ./simplelist.py --sender=me@dummy.domain --local=unit-test             --domain=lists.dummy.domain

echo "Empty" | ./simplelist.py --sender=alter.ego@dummy.domain --local=subscribe-unit-test             --domain=lists.dummy.domain

cat unit-test/body-auto-generated-no.eml |    ./simplelist.py --sender=me@dummy.domain --local=unit-test --domain=lists.dummy.domain
cat unit-test/body-auto-generated.eml |    ./simplelist.py --sender=me@dummy.domain --local=unit-test --domain=lists.dummy.domain
cat unit-test/body-auto-submitted.eml |    ./simplelist.py --sender=me@dummy.domain --local=unit-test --domain=lists.dummy.domain

