# tpg offline APNs Server

### Description

**flask_server** This is the server to get devices ids and preferences from device. You must have Python 3.6 and install some dependencies: ``` pip3 install flask flask-migrate pymysql ```

**notifications.py** This is the script to fetch disruptions and send them to devices. You must have Python 3.6 and install some dependencies: ``` pip3 install apns2 requests pymysql ```. You have to use a cron job to run the script every minutes.

You will need a MySql server.

### Install

```
git clone https://github.com/RemyDCF/tpg-offline-apns.git
pip3 install flask flask-migrate pymysql apns2 requests pymysql
nano notification.py (edit MySQL config and tpg API key)
nano flask_server/config.py (edit MySQL config)
crontab -e (<- */1 * * * * python3 /home/user/notification.py)
export FLASK_APP=/home/user/flask_server/apns.py
flask db migrate
flask db upgrade
flask run

```

Also, put your key.pem file in the same directory as notifications.py

### Author

Rémy Da Costa Faro

### License

tpg offline and tpg offline APNs are available under the MIT license. See the LICENCE file for more information.
