from db import get_conn
from datetime import datetime, date

def today_str():
    return date.today().isoformat()

def now_time():
    return datetime.now().strftime("%H:%M:%S")

def mark_check_in(teacher_id, status="Present"):
    d = today_str()
    t = now_time()

    with get_conn() as conn:
        cur = conn.execute("SELECT time_in, time_out FROM attendance WHERE teacher_id=? AND date=?;", (teacher_id, d))
        row = cur.fetchone()

        if row is None:
            conn.execute("""
                INSERT INTO attendance (teacher_id, date, time_in, time_out, status)
                VALUES (?, ?, ?, NULL, ?);
            """, (teacher_id, d, t, status))
            return "CHECKED_IN_CREATED"

        time_in, time_out = row
        if time_in and not time_out:
            return "ALREADY_IN"
        if time_in and time_out:
            return "ALREADY_COMPLETE"

        conn.execute("""
            UPDATE attendance SET time_in=?, status=? WHERE teacher_id=? AND date=?;
        """, (t, status, teacher_id, d))
        return "CHECKED_IN_UPDATED"

def mark_check_out(teacher_id):
    d = today_str()
    t = now_time()

    with get_conn() as conn:
        cur = conn.execute("SELECT time_in, time_out FROM attendance WHERE teacher_id=? AND date=?;", (teacher_id, d))
        row = cur.fetchone()

        if row is None:
            # If no check-in record exists, still create and mark absent/irregular.
            conn.execute("""
                INSERT INTO attendance (teacher_id, date, time_in, time_out, status)
                VALUES (?, ?, NULL, ?, ?);
            """, (teacher_id, d, t, "Irregular"))
            return "CHECKED_OUT_CREATED_IRREGULAR"

        time_in, time_out = row
        if time_out:
            return "ALREADY_OUT"

        conn.execute("""
            UPDATE attendance SET time_out=? WHERE teacher_id=? AND date=?;
        """, (t, teacher_id, d))
        return "CHECKED_OUT_UPDATED"

def daily_report(d=None):
    d = d or today_str()
    with get_conn() as conn:
        cur = conn.execute("""
            SELECT a.date, t.teacher_id, t.full_name, a.time_in, a.time_out, a.status
            FROM attendance a
            JOIN teachers t ON t.teacher_id = a.teacher_id
            WHERE a.date = ?
            ORDER BY t.full_name;
        """, (d,))
        return cur.fetchall()

def monthly_summary(teacher_id, year, month):
    # month: 1..12
    month_str = f"{month:02d}"
    prefix = f"{year}-{month_str}-"
    with get_conn() as conn:
        cur = conn.execute("""
            SELECT date, time_in, time_out, status
            FROM attendance
            WHERE teacher_id = ? AND date LIKE ?
            ORDER BY date;
        """, (teacher_id, prefix + "%"))
        return cur.fetchall()
