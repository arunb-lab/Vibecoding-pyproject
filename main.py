from db import init_db
from teachers import add_teacher, list_teachers, find_teacher_by_id
from attendance import mark_check_in, mark_check_out, daily_report, monthly_summary
from biometric.manual import ManualProvider

def print_teachers():
    rows = list_teachers()
    if not rows:
        print("No teachers found.")
        return
    for r in rows:
        print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | biometric_ref={r[4]}")

def main():
    init_db()
    provider = ManualProvider()  # swap later: FingerprintProvider(), FaceProvider()

    while True:
        print("\n--- Teacher Attendance System ---")
        print("1) Add Teacher")
        print("2) List Teachers")
        print("3) Check-in (Identify)")
        print("4) Check-out (Identify)")
        print("5) Daily Report")
        print("6) Monthly Summary (Teacher)")
        print("0) Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            tid = input("Teacher ID: ").strip()
            name = input("Full Name: ").strip()
            phone = input("Phone: ").strip()
            dept = input("Department: ").strip()
            desg = input("Designation: ").strip()
            add_teacher(tid, name, phone, dept, desg)
            print("Teacher added.")

        elif choice == "2":
            print_teachers()

        elif choice == "3":
            tid = provider.identify()
            if not find_teacher_by_id(tid):
                print("Unknown Teacher ID.")
                continue
            result = mark_check_in(tid)
            print("Check-in:", result)

        elif choice == "4":
            tid = provider.identify()
            if not find_teacher_by_id(tid):
                print("Unknown Teacher ID.")
                continue
            result = mark_check_out(tid)
            print("Check-out:", result)

        elif choice == "5":
            rows = daily_report()
            if not rows:
                print("No attendance marked today.")
                continue
            for d, tid, name, tin, tout, status in rows:
                print(f"{d} | {tid} | {name} | IN={tin} | OUT={tout} | {status}")

        elif choice == "6":
            tid = input("Teacher ID: ").strip()
            year = int(input("Year (e.g., 2026): ").strip())
            month = int(input("Month (1-12): ").strip())
            rows = monthly_summary(tid, year, month)
            if not rows:
                print("No records.")
                continue
            for d, tin, tout, status in rows:
                print(f"{d} | IN={tin} | OUT={tout} | {status}")

        elif choice == "0":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
