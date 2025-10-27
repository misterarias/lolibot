import os
import sqlite3

from lolibot.services import TaskData, TaskResponse


def test_init_db_creates_table(tmp_path):
    db_path = tmp_path / "test.db"
    import lolibot.db as dbmod

    dbmod.get_db_path = lambda: str(db_path)
    if db_path.exists():
        db_path.unlink()
    dbmod.init_db()
    assert os.path.exists(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
    assert cursor.fetchone() is not None
    conn.close()


def test_save_task_to_db(tmp_path):
    db_path = tmp_path / "test2.db"
    import lolibot.db as dbmod

    dbmod.get_db_path = lambda: str(db_path)
    if db_path.exists():
        db_path.unlink()
    dbmod.init_db()

    class DummyTask(TaskData):
        task_type = "task"
        title = "T"
        description = "D"
        date = "2025-05-15"
        time = "10:00"
        invitees = ["a@example.com"]

        def __init__(self):
            pass

    class DummyTaskResponse(TaskResponse):
        def __init__(self):
            self.task = DummyTask()
            self.processed = True
            self.feedback = "Task saved successfully"

    dbmod.save_task_to_db("u1", "msg", DummyTaskResponse())
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id=?", ("u1",))
    row = cursor.fetchone()
    assert row is not None
    assert row[1] == "u1"
    assert row[10] == 1  # processed
    conn.close()
