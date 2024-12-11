import pytest
from flask import json
from app import app, db, User, Task
from datetime import datetime


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def login(client):
    with app.app_context():
        # Asegurarse de que el usuario existe
        if not User.query.filter_by(username='testuser').first():
            user = User(username='testuser', password='password123')
            db.session.add(user)
            db.session.commit()

    # Iniciar sesión
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })

def test_get_tasks(client):
    login(client)
    # Crear tareas de prueba
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        task1 = Task(content='Task 1', deadline=datetime(2024, 12, 25), user_id=user.id)
        task2 = Task(content='Task 2', deadline=None, user_id=user.id)
        db.session.add_all([task1, task2])
        db.session.commit()

    # Hacer petición GET
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]['content'] == 'Task 1'
    assert data[1]['deadline'] is None

def test_create_task(client):
    login(client)
    response = client.post('/api/tasks', json={
        'content': 'New Task',
        'deadline': '2024-12-20'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['content'] == 'New Task'
    assert data['deadline'] == '2024-12-20'

def test_update_task(client):
    login(client)

    # Crear tarea de prueba en el contexto de la aplicación
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        task = Task(content='Old Task', user_id=user.id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id  # Guardar el ID para usarlo fuera del contexto

    # Realizar la actualización usando el cliente de pruebas
    response = client.put(f'/api/tasks/{task_id}', json={
        'content': 'Updated Task'
    })
    
    # Verificar la respuesta de la API
    assert response.status_code == 200

    # Verificar que la tarea fue actualizada en un nuevo contexto
    with app.app_context():
        updated_task = Task.query.get(task_id)
        assert updated_task is not None
        assert updated_task.content == 'Updated Task'

def test_delete_task(client):
    login(client)

    # Crear tarea de prueba en el contexto de la aplicación
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        task = Task(content='Task to Delete', user_id=user.id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id  # Guardar el ID para usarlo fuera del contexto

    # Realizar la eliminación usando el cliente de pruebas
    response = client.delete(f'/api/tasks/{task_id}')
    assert response.status_code == 200

    # Verificar que la tarea fue eliminada en un nuevo contexto
    with app.app_context():
        deleted_task = Task.query.get(task_id)
        assert deleted_task is None

def test_user_model(client):
    with app.app_context():
        # Crear un usuario
        user = User(username='testuser', password='password123')
        db.session.add(user)
        db.session.commit()

        # Verificar que se ha añadido correctamente
        assert User.query.count() == 1

        # Comprobar los datos del usuario
        db_user = User.query.first()
        assert db_user.username == 'testuser'
        assert db_user.password == 'password123'
