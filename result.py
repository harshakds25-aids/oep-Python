"""result.py - all result calculations (total, percentage, grade, PASS/FAIL) and statistics.

Nothing here is typed by the user - everything is calculated from the marks in SQLite.
"""
import marks as marks_module
import student as student_module
import subject as subject_module
from utils import ValidationError

PASS_PERCENT = 40  # minimum percentage needed in EVERY subject

# (minimum percentage, grade) - checked from the top
GRADE_BANDS = [(90, "A+"), (80, "A"), (70, "B"), (60, "C"), (50, "D"), (40, "E")]
GRADES = ["A+", "A", "B", "C", "D", "E", "F"]


def calculate_total(subject_rows):
    """Total obtained marks."""
    return sum(row["obtained"] for row in subject_rows)


def calculate_max_total(subject_rows):
    """Total maximum marks."""
    return sum(row["max"] for row in subject_rows)


def calculate_percentage(total, max_total):
    """Percentage = total obtained / total maximum x 100."""
    if max_total <= 0:
        return 0.0
    return round(total / max_total * 100, 2)


def calculate_grade(percentage):
    """90-100 A+, 80-89 A, 70-79 B, 60-69 C, 50-59 D, 40-49 E, below 40 F."""
    for minimum, grade in GRADE_BANDS:
        if percentage >= minimum:
            return grade
    return "F"


def subject_passed(obtained, maximum):
    """A subject is passed when marks are at least 40% of its maximum (40 out of 100)."""
    return obtained * 100 >= PASS_PERCENT * maximum


def calculate_result_status(subject_rows):
    """PASS only if every subject is passed, otherwise FAIL."""
    if all(subject_passed(r["obtained"], r["max"]) for r in subject_rows):
        return "PASS"
    return "FAIL"


def get_failed_subjects(subject_rows):
    """Names of the subjects where the student scored below the pass mark."""
    return [r["name"] for r in subject_rows if not subject_passed(r["obtained"], r["max"])]


def evaluate(subject_rows, expected_count=None):
    """Calculate everything for a list of {'name', 'max', 'obtained'} rows.

    status is PENDING (no marks yet), INCOMPLETE (some subjects missing), PASS or FAIL.
    """
    if expected_count is None:
        expected_count = len(subject_rows)
    total = calculate_total(subject_rows)
    max_total = calculate_max_total(subject_rows)
    percentage = calculate_percentage(total, max_total)
    if not subject_rows:
        status = "PENDING"
    elif len(subject_rows) < expected_count:
        status = "INCOMPLETE"
    else:
        status = calculate_result_status(subject_rows)
    complete = status in ("PASS", "FAIL")
    return {
        "total": total,
        "max_total": max_total,
        "percentage": percentage,
        "grade": calculate_grade(percentage) if complete else "-",
        "status": status,
        "complete": complete,
        "failed_subjects": get_failed_subjects(subject_rows),
        "entered": len(subject_rows),
        "expected": expected_count,
    }


def generate_result(student_id):
    """Full result of one student (student details, subject rows, totals, grade, status)."""
    student = student_module.get_student(student_id)
    if student is None:
        raise ValidationError("No student record found.")
    table = marks_module.get_marks_table(student_id)
    rows = [{"name": r["subject_name"], "max": r["max_marks"], "obtained": r["obtained"]}
            for r in table if r["obtained"] is not None]
    summary = evaluate(rows, expected_count=len(table))
    for row in rows:
        row["grade"] = calculate_grade(row["obtained"] / row["max"] * 100)
        row["passed"] = subject_passed(row["obtained"], row["max"])
    summary["student"] = dict(student)
    summary["subjects"] = rows
    return summary


def get_student_results(students):
    """[(student_row, result_dict), ...] - used by the student list and dashboard."""
    return [(s, generate_result(s["id"])) for s in students]


def get_report_statistics(branch=None, semester=None, academic_year=None):
    """Class statistics. Only students whose marks are complete (PASS/FAIL) are counted in the results."""
    students = student_module.get_students(semester=semester, branch=branch, academic_year=academic_year)
    results = [generate_result(s["id"]) for s in students]
    evaluated = [r for r in results if r["complete"]]
    passed = sum(1 for r in evaluated if r["status"] == "PASS")
    failed = len(evaluated) - passed
    percentages = [r["percentage"] for r in evaluated]
    grade_counts = {g: 0 for g in GRADES}
    for r in evaluated:
        grade_counts[r["grade"]] += 1
    return {
        "total_students": len(students),
        "evaluated": len(evaluated),
        "passed": passed,
        "failed": failed,
        "pass_percentage": round(passed / len(evaluated) * 100, 2) if evaluated else 0.0,
        "average": round(sum(percentages) / len(percentages), 2) if percentages else 0.0,
        "highest": max(percentages) if percentages else 0.0,
        "lowest": min(percentages) if percentages else 0.0,
        "grade_counts": grade_counts,
    }


def get_dashboard_statistics():
    stats = get_report_statistics()
    stats["total_subjects"] = subject_module.count_subjects()
    return stats
