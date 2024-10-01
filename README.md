# Django Custom Middleware

## Overview

This project is a Django-based web application that includes advanced middleware functionalities for logging user activity, rate-limiting based on user roles, and restricting access based on authentication status. It also integrates pre-commit hooks to ensure code quality.

---

## **Steps to Run the Project from Scratch**

### 1. **Clone the Repository**

The first step is to clone the repository from GitHub (or any other version control system you're using). To do this, open your terminal and run:

```bash
git clone https://github.com/ShehzadDev/custommiddleware
cd custommiddleware
```

### 2. **Set Up a Virtual Environment**

It's best practice to use a virtual environment to keep your project's dependencies isolated. Here’s how to create and activate a virtual environment:

- On macOS/Linux:

  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

- On Windows:
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

### 3. **Install Dependencies**

Once your virtual environment is activated, install the project dependencies using `pip`:

```bash
pip install -r requirements.txt
```

### 4. **Database Setup**

This project uses PostgreSQL as its default database. However, you can configure it to use any database you prefer (such as SQLite for simpler setups).

1. **Install PostgreSQL** (if you haven't already).
2. Create a new PostgreSQL database using the command:
   ```bash
   createdb DB_NAME
   ```
3. In the `settings.py` file, update the `DATABASES` section with your PostgreSQL credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'PROJECT_NAME',
        'USER': 'DB_USER',
        'PASSWORD': 'PASSWORD',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

4. **Run Migrations**:
   Migrations are necessary to create the required database tables. Run:
   ```bash
   python manage.py migrate
   ```

### 5. **Create a Superuser (Optional)**

To access the Django Admin interface for user management or other operations, create a superuser account:

```bash
python manage.py createsuperuser
```

Follow the prompts to create a username, email, and password.

### 6. **Run the Development Server**

Now that everything is set up, you can run the server:

```bash
python manage.py runserver
```

Navigate to `http://127.0.0.1:8000/` in your browser to access the application.

---

## **Middleware Functionality**

### 1. **Logging Middleware**

The **Logging Middleware** tracks and logs incoming requests to the application. Each log captures:

- **Request Time**: The timestamp when the request was made.
- **User**: The identity of the user making the request (if authenticated).
- **IP Address**: The IP address from where the request originated.

This helps in maintaining an audit trail for tracking user actions and monitoring suspicious behavior.

### 2. **Rate-Limiting Middleware**

The **Rate-Limiting Middleware** ensures that users cannot overwhelm the server with too many requests in a short amount of time. The system imposes a request limit per minute for each user or IP address (for unauthenticated users). Once the limit is reached, further requests are blocked temporarily.

- **Unauthenticated Users**: Limited to 1 request per minute.
- **Authenticated Users**: Limits are based on user roles.

### 3. **Role-Based Rate-Limiting Middleware**

The **Role-Based Rate-Limiting Middleware** assigns different rate limits based on the user's role. Here's the breakdown:

- **Gold**: 10 requests per minute
- **Silver**: 5 requests per minute
- **Bronze**: 2 requests per minute
- **Unauthenticated**: 1 request per minute (IP-based)

This mechanism allows for more flexibility, giving premium users (Gold members) higher access and protecting server resources from misuse.

---

## **Rate-Limiting Rules**

1. **Time Window**: The rate limit applies over a sliding window of 60 seconds.
2. **Limit Reset**: If a user exceeds their request limit within this time window, they will receive a `429 Too Many Requests` error. Their request counter resets after 1 minute.
3. **Handling Unauthenticated Users**: Unauthenticated users are tracked based on their IP address, and the rate limit is stricter (1 request/minute).
4. **Blocking Response**: If the request limit is exceeded, the user will receive an error message:
   ```
   { "error": "Request limit exceeded. Try again later." }
   ```

---

## **Pre-Commit Setup**

This project uses **pre-commit hooks** to ensure that the code meets formatting and linting standards before allowing any commits. The hooks include tools like **Flake8**, **isort**, and **Black**.

### **Tools in Use**:

- **Flake8**: Ensures the code is free from common Python errors and follows coding standards.
- **isort**: Automatically sorts Python imports based on the Black formatting style.
- **Black**: A code formatter that ensures uniformity in the project's coding style.

### **How to Set Up Pre-Commit**:

1. **Install Pre-commit**:
   Install the pre-commit package using pip:

   ```bash
   pip install pre-commit
   ```

2. **Install Pre-commit Hooks**:
   Inside the project directory, run:

   ```bash
   pre-commit install
   ```

   This will install the pre-defined hooks.

3. **Run Pre-commit Manually**:
   If you want to check all files for issues manually:
   ```bash
   pre-commit run --all-files
   ```

This ensures that all code adheres to the project's coding standards before any changes are committed.

---

# Testing Middleware and Views in Django

## Running Tests

To execute your test cases, follow these steps:

- **Run the tests** using the Django management command:

```bash
python manage.py test
```

This command will discover and run all tests within your project.

### Viewing Detailed Output

For more detailed test output, including the names of the tests being run, you can use the `-v` (verbosity) option:

```bash
python manage.py test -v 2
```

### Running Specific Tests

To run specific tests or test cases, use the following syntax:

```bash
python manage.py test PROJECT.tests.ClassName.test_method_name
```

### Checking Test Coverage (Optional)

To check which parts of your code are covered by tests, you can use the `coverage.py` tool.

1. **Install coverage** if you haven't already:

   ```bash
   pip install coverage
   ```

2. **Run tests with coverage**:

   ```bash
   coverage run manage.py test
   ```

3. **Generate a coverage report**:

   ```bash
   coverage report
   ```

## **Usage**

1. **Register as a New User**:
   Navigate to the registration page (`/register`). Provide your email, password, and select a role (Gold, Silver, or Bronze). If no role is selected, the "default" role will be applied.

2. **Login**:
   After registering, you can log in at `/login` using your email and password.

3. **Protected View**:
   If logged in, you can access a protected view that greets you with your email and role. This view is rate-limited based on your role. Access the view at `/protected`.

4. **Logout**:
   You can log out using the logout link provided in the navigation bar.

---

## **Additional Notes**

- **Unauthenticated Users**: If you're not logged in, any attempt to access the protected view will result in a redirect to the login page.
- **Rate-Limiting**: All requests are tracked, and limits are enforced to protect the server from abuse. After exceeding your rate limit, you will have to wait 60 seconds before making further requests.
