"""subject.py - subject CRUD."""
import sqlite3

import database
from utils import ValidationError, validate_subject


def add_subject(data):
    d = validate_subject(data)
    try:
        new_id, _ = database.execute(
            "INSERT INTO subjects (subject_name, max_marks, semester, course, branch, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (d["subject_name"], d["max_marks"], d["semester"], d["course"], d["branch"], database.now()))
    except sqlite3.IntegrityError:
        raise ValidationError("This subject already exists for the same semester, course and branch.")
    return new_id


def update_subject(subject_id, data):
    if get_subject(subject_id) is None:
        raise ValidationError("Subject not found.")
    d = validate_subject(data)
    too_high = database.query_one(
        "SELECT COUNT(*) AS n FROM marks WHERE subject_id = ? AND obtained_marks > ?",
        (subject_id, d["max_marks"]))["n"]
    if too_high:
        raise ValidationError("Some students already have marks above this maximum. "
                              "Correct those marks first.")
    try:
        database.execute(
            "UPDATE subjects SET subject_name = ?, max_marks = ?, semester = ?, course = ?, branch = ? "
            "WHERE id = ?",
            (d["subject_name"], d["max_marks"], d["semester"], d["course"], d["branch"], subject_id))
    except sqlite3.IntegrityError:
        raise ValidationError("This subject already exists for the same semester, course and branch.")


def delete_subject(subject_id):
    """Deletes the subject and the marks entered for it (ON DELETE CASCADE)."""
    _, changed = database.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
    if changed == 0:
        raise ValidationError("Subject not found.")


def get_subject(subject_id):
    return database.query_one("SELECT * FROM subjects WHERE id = ?", (subject_id,))


def get_subjects(semester=None):
    sql = "SELECT * FROM subjects"
    params = []
    if semester:
        sql += " WHERE semester = ?"
        params.append(int(semester))
    sql += " ORDER BY semester, id"
    return database.query_all(sql, params)


def count_subjects():
    return database.query_one("SELECT COUNT(*) AS n FROM subjects")["n"]
