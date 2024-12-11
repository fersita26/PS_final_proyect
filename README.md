# To-Do List Application

## **Project Description**
This is a to-do list application built using **Flask**, allowing users to:

- Register and log in securely.
- Create, edit, and delete tasks.
- Assign deadlines to tasks.
- Interact with the application via a web interface and a documented REST API.

The application is deployed in the cloud using **Render**.

---

## **Key Features**

### User Functionalities:
- **Secure Authentication:** Register, log in, and log out.
- **Task Management:**
  - Create tasks with content and deadlines.
  - Edit and delete existing tasks.
  - View all tasks organized.

### REST API:
- **Main Endpoints:**
  - Retrieve all tasks for the authenticated user.
  - Create, edit, and delete tasks via HTTP requests.
  - Query tasks by date.
- **Documentation:** Accessible at `/api/docs`.

### Deployment:
- Application available in the cloud via Render.
- Integrated with a GitHub repository for CI/CD.

---

## **Technologies Used**

- **Backend:** Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Login.
- **Frontend:** HTML, CSS (Bootstrap 5).
- **Database:** SQLite.
- **Testing:** Pytest.
- **Deployment:** Render.

---

## **Installation Instructions**

### Prerequisites
- Python 3.9 or higher.
- Git.

### Local Installation
1. Clone the repository:
   ```bash
   git clone <REPOSITORY-URL>
   cd <repository-name>
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On MacOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   flask db upgrade
   ```

5. Run the application locally:
   ```bash
   flask run
   ```
   Access the application at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## **API Usage**

### Main Endpoints

1. **Get all tasks:**
   ```http
   GET /api/tasks
   ```
   **Response:**
   ```json
   [
       {
           "id": 1,
           "content": "Task 1",
           "deadline": "2024-12-25"
       }
   ]
   ```

2. **Create a new task:**
   ```http
   POST /api/tasks
   ```
   **Request Body:**
   ```json
   {
       "content": "New Task",
       "deadline": "2024-12-20"
   }
   ```

3. **Update an existing task:**
   ```http
   PUT /api/tasks/<task_id>
   ```
   **Request Body:**
   ```json
   {
       "content": "Updated Task"
   }
   ```

4. **Delete a task:**
   ```http
   DELETE /api/tasks/<task_id>
   ```

5. **Query tasks by date:**
   ```http
   GET /api/tasks/by_date?date=2024-12-20
   ```

### Complete Documentation
Access the documentation at: `/api/docs`.

---

## **Running Tests**

1. Ensure you are in the virtual environment.
2. Run the tests:
   ```bash
   pytest
   ```
3. Check the results to ensure everything works correctly.

---

## **Deployment**

### Render
The application is deployed on [Render](https://render.com/). Follow these steps to update the deployment:

1. Make changes in the local repository.
2. Commit and push the changes to GitHub:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```
3. Render will automatically detect changes and update the application.

---

## **Contributions**

If you wish to contribute to the project:
1. Fork the repository.
2. Create a branch for your changes:
   ```bash
   git checkout -b feature/new-feature
   ```
3. Submit a pull request with a detailed description.


