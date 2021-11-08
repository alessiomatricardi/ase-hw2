echo 'Actual db will be renamed to old_mmiab.db'
echo 'Remember to rename it if you want to use'
mv -f mmiab.db old_mmiab.db || echo 'mmiab.db not exists... continue with tests'
echo 'monolith/static/attachments folder has been moved into root directory'
mv -f monolith/static/attachments ./old_attachments
mkdir monolith/static/attachments
pytest -s
if [[ $1 -eq 1 ]]
then
    rm -rf mmiab.db
    mv -f old_mmiab.db mmiab.db || echo 'old_mmiab.db not exists... impossible to restore it'
    rm -rf monolith/static/attachments
    mv -f ./old_attachments monolith/static/attachments
fi
echo 'Test done!'