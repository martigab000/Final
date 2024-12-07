# 454_final #
##----------( SETUP / INSTALL )----------##
LINUX 
1.) Extract Code.zip in empty directory
2.) > cd into directory with manage.py
3.) > mkdir data
4.) Extract Data.zip in data directory
5.) If not using 5k_crawler_state.pkl - Change gabewhoosh.py lines 26 and 29 to reflect chosen pkl file
6.) cd back to main directory / > cd ..
7.) > virtualenv venv
8.) > source venv/bin/activate
9.) > pip install -r requirements.txt
10.) > flask db upgrade
11.) [after waiting, populate the heat map data you need to run init](http://127.0.0.1:5000/init)


##----------( SETUP / INSTALL )----------##
WINDOWS 
1.) Extract Code.zip in empty directory
2.) > cd 454_final
3.) > mkdir data
4.) Extract Data.zip in data directory
5.) If not using 5k_crawler_state.pkl - Change gabewhoosh.py lines 26 and 29 to reflect chosen pkl file
6.) cd back to main directory / > cd ..
7.) > python -m venv venv
8.) > ./venv/Scripts/activate
9.) > pip install -r requirements.txt
10.) > flask db upgrade
11.) [after waiting populate the heat map data you need to run init](http://127.0.0.1:5000/init)

##----------( RUNNING )----------## 
1.) flask --app ./manage.py run --debug
