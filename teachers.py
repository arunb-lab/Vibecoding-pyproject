from db import get_conn

def add_teacher(teacher_id, full_name, phone="", department="", designation="", biometric_ref=None):
    with get_conn() as conn:
        conn.execute("""
        INSERT INTO teachers (teacher_id, full_name, phone, department, designation, biometric_ref)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (teacher_id, full_name, phone, department, designation, biometric_ref))

def list_teachers():
    with get_conn() as conn:
        cur = conn.execute("SELECT teacher_id, full_name, department, designation, biometric_ref FROM teachers ORDER BY full_name;")
        return cur.fetchall()

def find_teacher_by_id(teacher_id):
    with get_conn() as conn:
        cur = conn.execute("""
        SELECT teacher_id, full_name, department, designation, biometric_ref
        FROM teachers WHERE teacher_id = ?;
        """, (teacher_id,))
        return cur.fetchone()

def find_teacher_by_biometric_ref(bio_ref):
    with get_conn() as conn:
        cur = conn.execute("""
        SELECT teacher_id, full_name FROM teachers WHERE biometric_ref = ?;
        """, (bio_ref,))
        return cur.fetchone()

def set_biometric_ref(teacher_id, bio_ref):
    with get_conn() as conn:
        conn.execute("UPDATE teachers SET biometric_ref = ? WHERE teacher_id = ?;", (bio_ref, teacher_id))
