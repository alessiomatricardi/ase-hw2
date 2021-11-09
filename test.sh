#!/usr/bin/env bash

echo 'Actual db will be renamed to old_mmiab.db'
echo 'Remember to rename it if you want to use'
mv -f mmiab.db old_mmiab.db || echo 'mmiab.db not exists... continue with tests'
echo 'monolith/static/attachments folder has been moved into root directory'
mkdir attachments
mv monolith/static/attachments/* attachments || ( echo 'monolith/static/attachments folder not exists... continue with tests' && mkdir monolith/static/attachments )

pytest -s

mv -f mmiab.db mmiab_test.db
( mv -f old_mmiab.db mmiab.db && rm -f mmiab_test.db ) || ( echo 'old_mmiab.db not exists... mmiab.db from test will be held' && mv -f mmiab_test.db mmiab.db )
rm -rf monolith/static/attachments
mkdir monolith/static/attachments
mv attachments/* monolith/static/attachments/
rm -rf attachments

echo 'Test done!'