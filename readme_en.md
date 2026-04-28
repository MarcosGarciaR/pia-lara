# PIA LARA

## Installation

**Considerations**: I use the `python3` and `pip3` commands as that is how my system is configured. You should use the appropriate command (`python` vs. `python3` / `pip` vs. `pip3`) based on your specific environment.

Clone the repository

```
git clone git@github.com:PIALARA/pia-lara.git
```

Within the repository directory, create the virtual environment:

```
python3 -m venv venv
```

And activate the virtual environment (at this point, everyone should follow the procedure explained in class depending on whether they are using Windows, Linux, or Mac); for example, for Linux/Mac, we would use:

``` bash
source venv/bin/activate
```

**Note**: The `venv` directory is included in the `.gitignore` file to prevent it from being uploaded to the repository. If you name it something else, make sure to add it to your `.gitignore`.

Install the requirements:

``` bash
pip3 install -r requirements.txt
```
Note: If we have updates in the requirements when we update *master*, they must be updated:

``` bash
pip3 install --upgrade --force-reinstall -r requirements.txt
```

And finally, we run Flask:

``` bash
flask --app pialara --debug run
```

### Migrations

To run the migrations, once the virtual environment is activated, from the root, we will run the appropriate script:

``` python
python3 migrations/sylabus_migration.py
```

## Preparation of environment variables

You must create a file named `.ini` in the root of the repository and configure the environment variables:

``` title=".ini"
[PROD]
SECRET_KEY = eac5e91171438960ddec0c9c469a4c3dd42e96aea462afc5ab830f78527ad80e
PIALARA_DB_URI = mongodb+srv://usuario:contraseña@host
PIALARA_DB_NAME = pialara
BUCKET_NAME = pialara
GRADIO_URL = http://localhost:8080/gradio

[LOCAL]
SECRET_KEY = eac5e91171438960ddec0c9c469a4c3dd42e96aea462afc5ab830f78527ad80e
PIALARA_DB_URI = localhost
PIALARA_DB_NAME = prelara
BUCKET_NAME = prelara
GRADIO_URL = http://localhost:8080/gradio

aws_access_key_id=clave_aws
aws_secret_access_key=secret_aws
aws_session_token=token_aws
```
If you encounter an error with *Python* and the BSON library, it is recommended to (*upgrade*) the PyMongo version, which installs its own version of BSON that prevents these errors.

## Application Structure

The main application code is located in the directory `pialara`.

### Blueprints

In the blueprints directory, functionalities will be grouped to keep everything separate. For example, auth will have its own blueprint, syllabus (phrases) will have its own blueprint, etc.

When a blueprint is created, it is necessary to add it to ```__init__.py``` so that the application loads it.

### Views

Each *Blueprint* will have an associated directory with the same name inside the templates directory that will contain its views.

For example, the `auth` *Blueprint* will have the `templates/auth` directory to store its views.

### Models

Models will be used to access the database. Each model represents a collection and must extend the base class that has been created `MongoModel`. An example implementation for creating a model that will access the User collections would be:

```python
from pialara.models.MongoModel import MongoModel

class Usuario(MongoModel):
    collection_name = 'users'
```

It is necessary to override the collection_name property and assign it a string with the name of the collection.

Once the model is created, we can instantiate it as follows:

```python
u = Usuario()
```

With this, we would have all the methods inherited from MongoModel at our disposal without having to implement them. For example, we could retrieve all users with:

```python
db.users.find()
```

#### MongoModel Methods

The MongoModel methods are nothing more than wrappers for those offered by the PyMongo library. That is, the `user.find(...parameters...)` method would be the same as doing `db.users.find(...parameters...)`

- `find(self, params=None)`
- `update_one(self, mongo_filter, new_values, upsert=False)`
- `update_many(self, mongo_filter, new_values, upsert=False)`
- `insert_one(self, values)`
- `insert_many(self, values)`

#### Examples of Model Usage

**Example to insert a document**

```python
u.insert_one({ "nombre": "Test", "email": "test@test.com" })
```

**Example to insert multiple documents**

```python
u.insert_many([{ "nombre": "Test", "email": "test2@test2.com" },{ "nombre": "Test", "email": "test3@test3.com" }])
```

**Example to update a document**
```python
u.update_one({"email":"test3@test3.com"}, { "$set": {"nombre": "Test33"}})
```

**Example to update a document and create it if it does not exist**
```python
u.update_one({"email":"test3@test3.com"}, { "$set": {"nombre": "Test33"}}, upsert=True)
```

**Example to update multiple documents**
```python
u.update_many({"nombre": "Test"}, { "$set": {"email":"asddasd@asdads.com"}})
```

**Example to update multiple documents and create them if they do not exist**
```python
u.update_many({"nombre": "Test"}, { "$set": {"email":"asddasd@asdads.com"}}, upsert=True)
```

#### Protecting Routes by Roles

A decorator has been created in the decorators.py file so it can be used to verify that the user is logged in and has a specific role.

Its usage to check for the `admin` role for the `/profile` route would be:

```python
from pialara.decorators import rol_required
@bp.route('/profile')
@rol_required("admin")
def profile():
    return render_template('auth/profile.html')
```
