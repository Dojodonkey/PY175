import bcrypt
import yaml
import os
from markdown import markdown
from functools import wraps
from flask import (Flask,
                   flash,
                   redirect,
                   render_template,
                   request,
                   send_from_directory,
                   session,
                   url_for,
                   )

app = Flask(__name__)
app.secret_key = 'secret1' #for session

#load user data
def get_user_data():
    filename = "users.yaml"
    root = os.path.dirname(__file__)
    if app.config['TESTING']:
        data_path = os.path.join(root, 'tests', filename)
    else:
        data_path = os.path.join(root, 'cms', filename)

    with open(data_path, "r") as file:
        return yaml.safe_load(file)


# path configuration stuff
def get_data_path():
    if app.config['TESTING']:
        return os.path.join(os.path.dirname(__file__), 'tests', 'data')
    else:
        return os.path.join(os.path.dirname(__file__), 'cms', 'data')

def file_path(file_title):
    return os.path.join(get_data_path(), file_title)

#signed in function decorator
def signed_in_dec(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('username', '') != 'admin':
            flash('You must login to do that.')
            return redirect(url_for('show_signin'))
        return func(*args, **kwargs)
    return wrapper


@app.route("/")
def index():
    files = [os.path.basename(path) for path in os.listdir(get_data_path())]
    return render_template('index.html', files=files)

@app.route("/<file_title>")
@signed_in_dec
def file_content(file_title):
    file_path = os.path.join(get_data_path(), file_title)

    if os.path.isfile(file_path): #returns True if path exists and is regular file.
        if file_title.endswith(".md"):
            with open(file_path, "r") as file:
                contents = file.read()
            return render_template('markdown.html', contents=markdown(contents))
        else:
            return send_from_directory(get_data_path(), file_title)

    else:
        flash(f"{file_title} does not exist.", "error")
        return redirect(url_for('index'))
# ^^^^ Relative path equivalent ^^^^:
# @app.route("/<file_title>")
# def txt_file(file_title):
#     with open(f"cms/data/{file_title}", "r") as file:
#         contents = file.read()
#     formatted_contents = contents.replace('\n', '<br>')
#     return render_template('txt_file.html',
#                            file_title = file_title,
#                            formatted_contents=formatted_contents,)

@app.route("/<file_title>/edit")
@signed_in_dec
def edit_content(file_title):
    if os.path.isfile(file_path(file_title)):
        with open(file_path(file_title), "r") as file:
            content = file.read()
        return render_template('edit.html',
                            file_title=file_title,
                            content=content)
    else:
        flash(f"{file_title} does not exist", "error")
        return redirect(url_for('index'))

@app.route("/<file_title>", methods=["POST"])
@signed_in_dec
def save_file(file_title):
    content = request.form['content']
    with open(file_path(file_title), "w") as file:
        file.write(content)
    flash(f"{file_title} has been updated..")
    return redirect(url_for('index'))

@app.route("/new")
@signed_in_dec
def new_file():
    return render_template('new_file.html')

@app.route("/file_upload", methods=["POST"])
@signed_in_dec
def upload_new_file():
    filename = request.form.get('filename', '').strip()
    file_path = os.path.join(get_data_path(), filename)

    if not filename:
        flash("Input is required.", "error")
        return render_template('new_file.html'), 422 #Unprocessable Entity Error
    elif os.path.exists(file_path):
        flash(f"{filename} already exists.", "error")
        return render_template('new_file.html'), 422 #Unprocessable Entity Error
    else:
        # creates the file since it doesn't exist yet.
        with open(file_path, "w") as file:
            file.write('')
        flash(f"{filename} has been created.")
        return redirect(url_for('index'))

@app.route("/<file_title>/delete", methods=["POST"])
@signed_in_dec
def delete_file(file_title):
    file_path = os.path.join(get_data_path(), file_title)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f"{file_title} has been deleted.", "success")
    else:
        flash(f"{file_title} not found.", "error")
    return redirect(url_for('index'))


@app.route("/users/signin")
def show_signin():
    return render_template('signin.html')

def validate_sign_in(username, password):
    credentials = get_user_data()
    if username in credentials:
        stored_password = credentials[username].encode('utf-8') #bcrypt works with bytes not strings!
        return bcrypt.checkpw(password.encode('utf-8'), stored_password)

@app.route("/users/signin", methods=["POST"])
def signin():
    username = request.form.get('username')
    password = request.form.get('password')

    if validate_sign_in(username, password):
        session['username'] = username #for behavior of actions requiring signed in user.
        flash("Welcome!", "success")
        return redirect(url_for('index'))
    else:
        flash("Invalid Credentials", "error")
        return render_template('signin.html'), 422

@app.route("/users/signout", methods=["POST"])
def signout():
    del session['username']
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5003)


"""
Things to keep building:

Validate that document names contain an extension that the application supports.
Add a "duplicate" button that creates a new document based on an old one.
Extend this project with a user signup form.
Add the ability to upload images to the CMS (which could be referenced within markdown files).
Modify the CMS so that each version of a document is preserved as changes are made to it.
"""