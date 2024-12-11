from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from models import db, User, Task
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    with current_app.app_context():
        return db.session.get(User, int(user_id))

with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe', 'error')
            return redirect(url_for('register'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Usuario registrado con éxito', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        flash('Credenciales inválidas', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        task_content = request.form['content']
        deadline = request.form.get('deadline')  # Obtener el campo deadline del formulario
        # Convertir el deadline a un objeto de fecha si no es None
        if deadline:
            deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
        else:
            deadline_date = None

        # Crear la nueva tarea
        new_task = Task(content=task_content, deadline=deadline_date, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_task.html')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == 'POST':
        task.content = request.form['content']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_task.html', task=task)

@app.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

######

# Listar todas las tareas del usuario autenticado
@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': task.id,
        'content': task.content,
        'deadline': task.deadline.strftime('%Y-%m-%d') if task.deadline else None
    } for task in tasks])

# Agregar una nueva tarea
@app.route('/api/tasks', methods=['POST'])
@login_required
def create_task():
    data = request.get_json()
    task_content = data.get('content')
    deadline = data.get('deadline')
    deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date() if deadline else None

    new_task = Task(content=task_content, deadline=deadline_date, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        'id': new_task.id,
        'content': new_task.content,
        'deadline': new_task.deadline.strftime('%Y-%m-%d') if new_task.deadline else None
    }), 201

# Actualizar una tarea
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    data = request.get_json()

    task.content = data.get('content', task.content)
    deadline = data.get('deadline')
    if deadline:
        task.deadline = datetime.strptime(deadline, '%Y-%m-%d').date()

    db.session.commit()

    return jsonify({
        'id': task.id,
        'content': task.content,
        'deadline': task.deadline.strftime('%Y-%m-%d') if task.deadline else None
    })

# Eliminar una tarea
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task_api(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()

    return jsonify({'message': 'Task deleted successfully'}), 200
########

@app.route('/api/task/<int:task_id>/set_deadline', methods=['POST'])
@login_required
def set_deadline(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return {"error": "Task not found or not authorized"}, 404

    deadline = request.json.get('deadline')
    try:
        task.deadline = datetime.strptime(deadline, '%Y-%m-%d').date()
        db.session.commit()
        return {"message": "Deadline set successfully"}
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}, 400

@app.route('/api/tasks/by_date', methods=['GET'])
@login_required
def get_tasks_by_date():
    date = request.args.get('date')
    try:
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
        tasks = Task.query.filter_by(user_id=current_user.id, deadline=target_date).all()
        return {"tasks": [{"id": t.id, "content": t.content, "deadline": t.deadline.strftime('%Y-%m-%d')} for t in tasks]}
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}, 400

@app.route('/api/docs')
def api_docs():
    return render_template('api_documentation.html')

if __name__ == '__main__':
    app.run(debug=True)
