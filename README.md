#REST API FOR CHECK IN *

##Set up a virtual environment using virtualenv

```
pip install virtualenv
mkdir SENIOR-SER
cd SENIOR-SER
virtualenv flaskapi
```
######activate the virtual envirement 

```
flaskapi\Scripts\activate
```

######Install packages using pip

The requirements.txt file contain the needed packages.
>Flask  
>datetime 
>uuid
>Flask-SQLAlchemy
>PyJWT

Install them with pip.
```
pip install -r requirements.txt
```

##Set up a database

######install sqlite and run add the path to the envirement variables 

######Create the database using the following command:

```
sqlite3 senior.db
```

Generate Tables On the terminal, type the following code inside the virtual environment to generate or create tables :

```
python 
from app import db
db.create_all()
exit()
```

##Run the App :
```
python app.py 
```
>it will be listening at http://127.0.0.1:5000






