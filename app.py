from flask import Flask, request, redirect
import psycopg
import os

app = Flask(__name__)


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "db"),
        dbname=os.getenv("POSTGRES_DB", "finance_db"),
        user=os.getenv("POSTGRES_USER", "finance_user"),
        password=os.getenv("POSTGRES_PASSWORD", "finance_password")
    )


def create_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT DEFAULT 'À faire',
                    priority TEXT DEFAULT 'Normale'
                )
            """)

            cur.execute("""
                ALTER TABLE tasks
                ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'À faire'
            """)

            cur.execute("""
                ALTER TABLE tasks
                ADD COLUMN IF NOT EXISTS priority TEXT DEFAULT 'Normale'
            """)


@app.route("/")
def accueil():
    create_table()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, status, priority FROM tasks ORDER BY id"
            )
            tasks = cur.fetchall()

    liste = ""

    for task in tasks:
        options_status = ""

        for status in ["À faire", "En cours", "Terminée"]:
            selected = "selected" if task[2] == status else ""

            options_status += f"""
                <option value="{status}" {selected}>
                    {status}
                </option>
            """

        liste += f"""
        <li>
            {task[1]}
            | Statut : {task[2]}
            | Priorité : {task[3]}

            <form action="/edit/{task[0]}" method="post" style="display:inline;">
                <input
                    type="text"
                    name="title"
                    placeholder="Nouveau titre"
                    required
                >
                <button type="submit">Modifier</button>
            </form>

            <form action="/status/{task[0]}" method="post" style="display:inline;">
                <select name="status">
                    {options_status}
                </select>

                <button type="submit">Changer statut</button>
            </form>

            <form action="/delete/{task[0]}" method="post" style="display:inline;">
                <button type="submit">Supprimer</button>
            </form>
        </li>
        """

    return f"""
    <h1>Finance Task Manager</h1>

    <form action="/add" method="post">
        <input
            type="text"
            name="title"
            placeholder="Nouvelle tâche"
            required
        >

        <select name="status">
            <option value="À faire">À faire</option>
            <option value="En cours">En cours</option>
            <option value="Terminée">Terminée</option>
        </select>

        <select name="priority">
            <option value="Basse">Basse</option>
            <option value="Normale" selected>Normale</option>
            <option value="Haute">Haute</option>
        </select>

        <button type="submit">Ajouter</button>
    </form>

    <h2>Mes tâches</h2>

    <ul>
        {liste}
    </ul>
    """


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form["title"]
    status = request.form["status"]
    priority = request.form["priority"]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tasks (title, status, priority)
                VALUES (%s, %s, %s)
                """,
                (title, status, priority)
            )

    return redirect("/")


@app.route("/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    new_title = request.form["title"]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET title = %s WHERE id = %s",
                (new_title, task_id)
            )

    return redirect("/")


@app.route("/status/<int:task_id>", methods=["POST"])
def update_status(task_id):
    new_status = request.form["status"]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET status = %s WHERE id = %s",
                (new_status, task_id)
            )

    return redirect("/")


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM tasks WHERE id = %s",
                (task_id,)
            )

    return redirect("/")


@app.route("/api/tasks", methods=["GET"])
def api_tasks():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, status, priority
                FROM tasks
                ORDER BY id
            """)

            tasks = cur.fetchall()

    return {
        "tasks": [
            {
                "id": task[0],
                "title": task[1],
                "status": task[2],
                "priority": task[3]
            }
            for task in tasks
        ]
    }


@app.route("/api/tasks", methods=["POST"])
def api_add_task():
    data = request.get_json(silent=True)

    if not data or "title" not in data:
        return {
            "error": "Le champ title est obligatoire"
        }, 400

    title = data["title"]
    status = data.get("status", "À faire")
    priority = data.get("priority", "Normale")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tasks (title, status, priority)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (title, status, priority)
            )

            task_id = cur.fetchone()[0]

    return {
        "message": "Tâche créée avec succès",
        "task": {
            "id": task_id,
            "title": title,
            "status": status,
            "priority": priority
        }
    }, 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def api_update_task(task_id):
    data = request.get_json(silent=True)

    if not data:
        return {
            "error": "Données JSON manquantes"
        }, 400

    title = data.get("title")
    status = data.get("status")
    priority = data.get("priority")

    if not title or not status or not priority:
        return {
            "error": "title, status et priority sont obligatoires"
        }, 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE tasks
                SET title = %s,
                    status = %s,
                    priority = %s
                WHERE id = %s
                RETURNING id
                """,
                (title, status, priority, task_id)
            )

            result = cur.fetchone()

    if result is None:
        return {
            "error": "Tâche introuvable"
        }, 404

    return {
        "message": "Tâche modifiée avec succès",
        "task": {
            "id": task_id,
            "title": title,
            "status": status,
            "priority": priority
        }
    }


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def api_delete_task(task_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM tasks
                WHERE id = %s
                RETURNING id
                """,
                (task_id,)
            )

            result = cur.fetchone()

    if result is None:
        return {
            "error": "Tâche introuvable"
        }, 404

    return {
        "message": "Tâche supprimée avec succès",
        "id": task_id
    }

@app.route("/health", methods=["GET"])
def health():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()

        return {
            "status": "healthy",
            "database": "connected"
        }, 200

    except Exception:
        return {
            "status": "unhealthy",
            "database": "disconnected"
        }, 503
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)