def list_title_validation(title, lsts):
    if not 1 <= len(title) <= 100:
        return 'list title must be between 1-100 characters'

    if any(title == lst['title'] for lst in lsts):
        return 'duplicate titles are not permitted'

    return None

def task_validator(task):
    if not 1 <= len(task) <= 100:
        return 'task title must be between 1-100 characters'
    return None

def find_list_by_id(lst_id, lists):
    return next((lst for lst in lists if lst['id']==lst_id), None)

def find_todo_in_todos(todo_id, todos):
    return next((todo for todo in todos if todo['id'] == todo_id), None)

def todos_completed(lst):
    return sum(1 for todo in lst['todos'] if todo['completed'] == True)

def is_list_completed(lst):
    return (todos_completed(lst) == len(lst['todos'])) and len(lst['todos']) > 0

def sort_lists(lsts):
    sorted_lsts = sorted(lsts, key=lambda lst: lst['title'].lower())
    incompleted_lsts = [lst for lst in sorted_lsts if not is_list_completed(lst)]
    completed_lsts = [lst for lst in sorted_lsts if is_list_completed(lst)]

    return incompleted_lsts + completed_lsts

def sort_todos(lst):
    sorted_lst = sorted(lst, key=lambda todo: todo['task'].lower())
    incompleted_lst=[todo for todo in sorted_lst if not todo['completed']]
    completed_lst=[todo for todo in sorted_lst if todo['completed']]
    return incompleted_lst + completed_lst
