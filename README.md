## License

These codes are licensed under CC0.

[![CC0](http://i.creativecommons.org/p/zero/1.0/88x31.png "CC0")](http://creativecommons.org/publicdomain/zero/1.0/deed.ja)

<br/>
<br/>
<br/>

# To use this app, execute following commands.
heroku buildpacks:add heroku/jvm -a  
heroku config:set PAGE_ACCESS_TOKEN= -a  
heroku config:set VERIFY_TOKEN= -a  
heroku config:set client_access_token= -a  
heroku config:set session_id= -a  

# set database and queue
heroku addons:create heroku-postgresql:hobby-dev -a  
heroku addons:create redistogo:nano -a  

# check secret keys
heroku config -a  
**Put database_url, redistogo_url, page_aceess_token, verify_token to heroku env variables.**  
**Also set session_id and client_access_token of dialogflow**  

# Prepare database.
**install psql with pip if first time**  
pip install psql

**on new db, execute following commands**  
heroku pg:psql -a  

**create tables with this command**  
\i db/ddl.sql;    
