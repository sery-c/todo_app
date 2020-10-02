from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://Sere@localhost:5432/todoapp'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    todo_list_id = db.Column(db.Integer, db.ForeignKey('todo_lists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'


class TodoList(db.Model):
    __tablename__ = 'todo_lists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=True)
    todos = db.relationship('Todo', backref='list', lazy=True)

@app.route('/todo_lists/<todo_list_id>')
def get_todo_lists(todo_list_id):
    return render_template(
        'index.html',
        data=Todo.query.filter_by(todo_list_id=todo_list_id).order_by('id').all()
    )

@app.route('/')
def index():
    return redirect(url_for('get_todo_lists', todo_list_id=1))

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    try:
        todo_description = request.form.get('desc', '')
        todo = Todo(description=todo_description)
        db.session.add(todo)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        return redirect(url_for('index'))
    else:
        abort(400)

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    error = False
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        return redirect(url_for('index'))
    else:
        abort(400)

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    error = False
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        return render_template('index.html', data=Todo.query.order_by('id').all())
    else:
        abort(400)
