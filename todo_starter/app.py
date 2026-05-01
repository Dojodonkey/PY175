from werkzeug.exceptions import NotFound
from todos.utils import (list_title_validation,
                         find_list_by_id,
                         find_todo_in_todos,
                         is_list_completed,
                         sort_lists,
                         sort_todos,
                         task_validator,
                         todos_completed,)
from uuid import uuid4
from functools import wraps
from flask import (Flask,
                   flash,
                   render_template,
                   request,
                   redirect,
                   session,
                   url_for)

app = Flask(__name__)
# session secret key
app.secret_key = 'secret1'

#custom decorators
def require_list(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        lst_id = kwargs.get('lst_id')
        lst = find_list_by_id(lst_id, session['lists'])
        if not lst:
            raise NotFound(description="List not found")
        return f(lst=lst, *args, **kwargs)

    return decorated_function

def require_todo(f):
    @wraps(f)
    @require_list
    def decorated_function(lst, *args, **kwargs):
        todo_id = kwargs.get('todo_id')
        todo = find_todo_in_todos(todo_id, lst['todos'])
        if not todo:
            raise NotFound(description="Todo not found")
        return f(lst=lst, todo=todo, *args, **kwargs)

    return decorated_function

# research more about this tomorrow. why the dictionary and how does flask interpret it.
@app.context_processor
def list_utilities_processor():
    return dict(
        is_list_completed=is_list_completed,
        )


#initialize session data (session object is a dict)
@app.before_request
def init_session():
    if 'lists' not in session:
        session['lists'] = []

# home
@app.route("/")
def index():
    return redirect(url_for('get_lists'))

#new list button
@app.route("/lists/new")
def add_new_list():
    return render_template('new_list.html')

# cancel button on new list / display lists
@app.route('/lists')
def get_lists():
    lists = sort_lists(session['lists'])
    return render_template('lists.html',
                           lists=lists,
                           todos_completed=todos_completed,)


# submitting new list to session
@app.route("/lists", methods=["POST"])
def create_list():
    title = request.form['list_title'].strip() # 'name' parameter in input tag
    # validation
    error = list_title_validation(title, session['lists'])
    if error:
        flash(error, 'error')
        return render_template('new_list.html', title=title) #('value=' keeps input sticky)

    session['lists'].append({'id': str(uuid4()),
                             'title': title,
                             'todos': []})

    print('create_list called')
    flash(f"'{title}' list successfully created", "success")
    session.modified = True
    return redirect(url_for('get_lists'))

#listing a list
@app.route("/lists/<lst_id>")
@require_list
def display_list(lst_id, lst):
    lst['todos'] = sort_todos(lst['todos'])
    return render_template('list.html', lst=lst)

# create a new task
@app.route("/lists/<lst_id>/todos", methods=["POST"])
@require_list
def create_task(lst_id, lst):
    task = request.form['todo'].strip()
    # validate title
    error = task_validator(task)
    if error:
        flash(error, 'error')
        return render_template('list.html', lst=lst)
    # add task to todos
    lst['todos'].append({'id': str(uuid4()),
                         'task': task,
                         'completed': False,})
    flash(f"'{task}' added to {lst['title']}.", "success")
    session.modified = True
    return redirect(url_for('display_list', lst_id=lst_id))

#complete the task in list (lst.id and todo.id are template variables)
@app.route("/lists/<lst_id>/todos/<todo_id>/toggle", methods=["POST"])
@require_todo
def update_task(lst, lst_id, todo, todo_id):
    todo['completed'] = (request.form['completed'] == 'True')  # <input type="hidden" name="completed" value="True" /> Flask reads bool as string
    flash(f"'{todo['task']}' status changed", "success")
    session.modified = True
    return redirect(url_for('display_list', lst_id=lst_id))

#delete a task from a list
@app.route("/lists/<lst_id>/todos/<todo_id>/delete", methods=["POST"]) # lst_id=lst.id, todo_id=todo.id
def delete_todo(lst_id, todo_id):
    lst = find_list_by_id(lst_id, session['lists'])
    todo = find_todo_in_todos(todo_id, lst['todos'])
    lst['todos'].remove(todo)
    flash(f"'{todo['task']}' has been deleted from '{lst['title']}'")
    session.modified = True
    return redirect(url_for('display_list', lst_id=lst_id))

#complete all todos in list
@app.route("/lists/<lst_id>/complete_all", methods=["POST"]) #lst_id=lst.id
def complete_all(lst_id):
    lst = find_list_by_id(lst_id, session['lists'])
    for todo in lst['todos']:
        todo['completed'] = True
    flash('All tasks updated', 'success')
    session.modified = True
    return redirect(url_for('display_list', lst_id=lst_id))

# edit list button
@app.route("/lists/<lst_id>/edit")
@require_list
def edit_list(lst_id, lst):
    return render_template('edit_list.html', lst=lst)

#new title for list
@app.route("/lists/<lst_id>", methods=["POST"])
def update_list_title(lst_id):
    lst = find_list_by_id(lst_id, session['lists'])
    new_title = request.form["list_title"].strip()
    error = list_title_validation(new_title, session['lists'])
    if error:
        flash(error, 'error')
        return redirect(url_for('edit_list', lst_id=lst_id))
    lst['title'] = new_title
    flash('list title updated', 'success')
    session.modified = True
    return render_template('list.html', lst=lst)

# delete the list
@app.route("/lists/<lst_id>/delete", methods=["POST"])
@require_list
def delete_lst(lst_id, lst):
    session['lists'].remove(lst)
    flash("Tracker updated", "success")
    session.modified = True
    return redirect(url_for('get_lists'))


if __name__ == "__main__":
    app.run(debug=True, port=5003)