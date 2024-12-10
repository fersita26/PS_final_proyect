import pytest
import sys
import os

# Añade la ruta del proyecto al sistema
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, User, Task

@pytest.fixture
def client():
    # Configurar la aplicación para pruebas
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_user_model(client):
    with app.app_context():
        # Crear un usuario
        user = User(username='testuser', password='password123')
        db.session.add(user)
        db.session.commit()

        # Verificar que se ha añadido correctamente
        assert User.query.count() == 1
        assert User.query.first().username == 'testuser'

def test_task_model(client):
    with app.app_context():
        # Crear un usuario y una tarea asociada
        user = User(username='testuser', password='password123')
        db.session.add(user)
        db.session.commit()

        task = Task(content='Test Task', user_id=user.id)
        db.session.add(task)
        db.session.commit()

        # Verificar que la tarea se ha añadido correctamente
        assert Task.query.count() == 1
        assert Task.query.first().content == 'Test Task'
        assert Task.query.first().user_id == user.id

# Registro de usuario
def test_register(client):
    with app.app_context():
        # Realizar un POST al formulario de registro
        response = client.post('/register', data={
            'username': 'newuser',
            'password': 'password123'
        })
        # Verificar que el usuario fue creado
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.username == 'newuser'

# Inicio de sesión
def test_login(client):
    with app.app_context():
        # Crear un usuario manualmente
        user = User(username='testuser', password='password123')
        db.session.add(user)
        db.session.commit()

        # Intentar iniciar sesión
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        # Verificar que la respuesta redirige a la página principal
        assert response.status_code == 302  # Redirección
        assert '/login' not in response.location  # No debería redirigir a login

# Crear tareas
def test_create_task(client):
    with app.app_context():
        # Crear un usuario manualmente
        user = User(username='testuser', password='password123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id  # Guardar el ID del usuario antes de salir del contexto

    # Simular inicio de sesión
    with client.session_transaction() as session:
        session['_user_id'] = str(user_id)  # Flask-Login utiliza _user_id como clave

    # Crear una tarea
    response = client.post('/add', data={
        'content': 'Test Task'
    }, follow_redirects=True)

    # Verificar que la tarea fue creada
    with app.app_context():
        task = Task.query.filter_by(content='Test Task').first()
        assert task is not None
        assert task.content == 'Test Task'


# Editar tareas
def test_edit_task(client):
    with app.app_context():
        # Crear un usuario y una tarea
        user = User(username='testuser', password='password123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id  # Guardar el ID del usuario antes de salir del contexto

        task = Task(content='Old Task', user_id=user_id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id  # Guardar el ID de la tarea

    # Simular inicio de sesión
    with client.session_transaction() as session:
        session['_user_id'] = str(user_id)  # Flask-Login utiliza _user_id como clave

    # Editar la tarea
    response = client.post(f'/edit/{task_id}', data={
        'content': 'Updated Task'
    }, follow_redirects=True)

    # Verificar que la tarea fue actualizada
    with app.app_context():
        updated_task = Task.query.get(task_id)
        assert updated_task.content == 'Updated Task'


# Eliminar tareas
def test_delete_task(client):
    with app.app_context():
        # Crear un usuario y una tarea
        user = User(username='testuser', password='password123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id  # Guardar el ID del usuario antes de salir del contexto

        task = Task(content='Task to Delete', user_id=user_id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id  # Guardar el ID de la tarea

    # Simular inicio de sesión
    with client.session_transaction() as session:
        session['_user_id'] = str(user_id)  # Flask-Login utiliza _user_id como clave

    # Eliminar la tarea
    response = client.get(f'/delete/{task_id}', follow_redirects=True)

    # Verificar que la tarea fue eliminada
    with app.app_context():
        deleted_task = Task.query.filter_by(id=task_id).first()
        assert deleted_task is None


