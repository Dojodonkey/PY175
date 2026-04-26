from flask import Flask, redirect, render_template, g, url_for
import yaml

app = Flask(__name__)

@app.before_request
def load_contents():
    with open("users.yaml", "r") as file:
        g.contents = yaml.safe_load(file)

@app.route("/")
def index():
    return redirect(url_for('users_list'))

@app.route("/users")
def users_list():
    names = g.contents.keys()
    return render_template('users.html', names = names)

@app.route("/users/<name>")
def user(name):
    user = g.contents.get(name, 'Name not found.')
    users = g.contents.keys()
    return render_template('user.html',
                           user=user,
                           name=name,
                           users=users)

@app.context_processor
def footer():
    total_users = len(g.contents)
    total_interests = 0
    for name in g.contents:
        total_interests += len(g.contents[name]['interests'])
    return dict(total_users=total_users,
                total_interests=total_interests)



if __name__ == '__main__':
    app.run(debug=True, port=5003)

# {'jamy': {'email': 'jamy.rustenburg@gmail.com', 'interests': ['woodworking', 'cooking', 'reading']},
#  'nora': {'email': 'nora.alnes@yahoo.com', 'interests': ['cycling', 'basketball', 'economics']},
#  'hiroko': {'email': 'hiroko.ohara@hotmail.com', 'interests': []}}