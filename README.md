# 🎬 Cinepacho Backend

Backend para el sistema de gestión de cines **Cinepacho**, construido con **FastAPI**, **SQLAlchemy**, y **SQLite/PostgreSQL**.

## 📋 Requisitos

- Python 3.10+
- pip
- Git

## 🚀 Guía Rápida de Inicio

### 1. Clonar e instalar
```bash
cd cinepachobackend
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

### 2. Ejecutar la aplicación
```bash
python run.py
```

Accede a: **http://localhost:8000/docs**

## 📚 Documentación

| Recurso | URL |
|---------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |

## 🔑 Variables de Entorno (.env)

```
DATABASE_URL=postgresql://cinepacho_user:123456@localhost:5432/cinepacho
SECRET_KEY=tu-clave-secreta
DEBUG=True
```

## 📁 Estructura

```
app/
├── api/              # Controllers
├── domain/           # Servicios de negocio
├── infrastructure/   # Repositorios
└── models/          # Entidades ORM
```

## 🧪 Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## 📝 Licencia

MIT


You’ll start by editing this README file to learn how to edit a file in Bitbucket.

1. Click **Source** on the left side.
2. Click the README.md link from the list of files.
3. Click the **Edit** button.
4. Delete the following text: *Delete this line to make a change to the README from Bitbucket.*
5. After making your change, click **Commit** and then **Commit** again in the dialog. The commit page will open and you’ll see the change you just made.
6. Go back to the **Source** page.

---

## Create a file

Next, you’ll add a new file to this repository.

1. Click the **New file** button at the top of the **Source** page.
2. Give the file a filename of **contributors.txt**.
3. Enter your name in the empty file space.
4. Click **Commit** and then **Commit** again in the dialog.
5. Go back to the **Source** page.

Before you move on, go ahead and explore the repository. You've already seen the **Source** page, but check out the **Commits**, **Branches**, and **Settings** pages.

---

## Clone a repository

Use these steps to clone from SourceTree, our client for using the repository command-line free. Cloning allows you to work on your files locally. If you don't yet have SourceTree, [download and install first](https://www.sourcetreeapp.com/). If you prefer to clone from the command line, see [Clone a repository](https://confluence.atlassian.com/x/4whODQ).

1. You’ll see the clone button under the **Source** heading. Click that button.
2. Now click **Check out in SourceTree**. You may need to create a SourceTree account or log in.
3. When you see the **Clone New** dialog in SourceTree, update the destination path and name if you’d like to and then click **Clone**.
4. Open the directory you just created to see your repository’s files.

Now that you're more familiar with your Bitbucket repository, go ahead and add a new file locally. You can [push your change back to Bitbucket with SourceTree](https://confluence.atlassian.com/x/iqyBMg), or you can [add, commit,](https://confluence.atlassian.com/x/8QhODQ) and [push from the command line](https://confluence.atlassian.com/x/NQ0zDQ).