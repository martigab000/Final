# 454_final #
##----------( SETUP / INSTALL )----------##
LINUX 
1.) Extract Code.zip in empty directory
2.) > cd into directory with manage.py
3.) > mkdir data
4.) Extract Data.zip in data directory
5.) cd back to main directory / > cd ..
6.) > virtualenv venv
7.) > source venv/bin/activate
8.) > pip install -r requirements.txt
13.) > flask db init -optional if app db is not initialized-
14.) > flask db upgrade
11.) [after waiting, populate the heat map data you need to run init](http://127.0.0.1:5000/init)


##----------( SETUP / INSTALL )----------##
WINDOWS 
1.) Extract Code.zip in empty directory
2.) > cd 454_final
3.) > mkdir data
4.) Extract Data.zip in data directory
5.) cd back to main directory / > cd ..
6.) > python -m venv venv
7.) > ./venv/Scripts/activate
8.) > pip install -r requirements.txt
9.) > -optional depending on db- flask db init
10.) > flask db upgrade
11.) [after waiting populate the heat map data you need to run init](http://127.0.0.1:5000/init)

##----------( RUNNING )----------## 
1.) flask --app ./manage.py run --debug
