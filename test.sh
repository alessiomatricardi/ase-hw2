echo 'Actual db will be renamed to old_mmiab.db'
echo 'Remember to rename it if you want to use'
mv -f mmiab.db old_mmiab.db || echo 'mmiab.db not exists... continue with tests'
echo 'monolith/static/attached folder has been moved into root directory'
mv -f monolith/static/attached ./old_attached
mkdir monolith/static/attached
pytest -s
if [[ $1 -eq 1 ]]
then
    rm -rf mmiab.db
    mv -f old_mmiab.db mmiab.db || echo 'old_mmiab.db not exists... impossible to restore it'
    rm -rf monolith/static/attached
    mv -f ./old_attached monolith/static/attached
fi