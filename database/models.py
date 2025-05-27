from .db import get_connection

def get_parent_by_id(parent_id):
    cursor = get_connection().cursor()
    cursor.execute("SELECT * FROM parents WHERE parent_id = ?", (parent_id,))
    return cursor.fetchone()

def get_students_by_parent(parent_id):
    cursor = get_connection().cursor()
    cursor.execute("SELECT * FROM students WHERE parent_id = ?", (parent_id,))
    return cursor.fetchall()

def get_schedule_for_student(student_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, student_id, date, time, topic
        FROM schedule
        WHERE student_id = ?
        ORDER BY date, time ASC
    """, (student_id,))
    return cursor.fetchall()

def log_action(user_id: int, action: str, details: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs (user_id, action, timestamp, details)
        VALUES (?, ?, datetime('now', 'localtime'), ?)
    """, (user_id, action, details))
    conn.commit()
 
def get_notifications_settings(user_id: int, student_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT schedule_changes, reminder_2h, homework_ready
        FROM notifications_settings
        WHERE user_id = ? AND student_id = ?
    """, (user_id, student_id))
    row = cursor.fetchone()
    if row:
        return {
            "schedule_changes": bool(row[0]),
            "reminder_2h": bool(row[1]),
            "homework_ready": bool(row[2])
        }
    else:
        # Если нет записи, создать пустую
        cursor.execute("""
            INSERT INTO notifications_settings (user_id, student_id, schedule_changes, reminder_2h, homework_ready)
            VALUES (?, ?, 1, 1, 1)
        """, (user_id, student_id))
        conn.commit()
        return {
            "schedule_changes": True,
            "reminder_2h": True,
            "homework_ready": True
        }

def toggle_notification_setting(user_id: int, student_id: int, field: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE notifications_settings
        SET {field} = CASE WHEN {field} = 1 THEN 0 ELSE 1 END
        WHERE user_id = ? AND student_id = ?
    """, (user_id, student_id))
    conn.commit()
 