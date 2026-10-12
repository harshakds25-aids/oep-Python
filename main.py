import os, sys, time
sys.path.insert(0, "/tmp/claude-0/run"); os.chdir("/tmp/claude-0/run")
import tkinter as tk
from tkinter import messagebox, ttk
import database, main, student
database.init_database()
app = main.App(); app.geometry("1240x760+0+0")
def pump(sec=0.0):
    end = time.time() + sec
    app.update_idletasks(); app.update()
    while time.time() < end:
        app.update_idletasks(); app.update(); time.sleep(0.02)
cap = tk.Label(app, text="", bg="#102a43", fg="white", font=("Segoe UI", 13, "bold"), padx=16, pady=8)
def caption(t, sec=1.6):
    cap.configure(text=t); cap.place(relx=0.5, rely=0.965, anchor="s"); cap.lift(); pump(sec)
banner = {"w": None}
def show_msg(kind, title, msg):
    colors = {"showinfo": "#1b7f4c", "showwarning": "#b45f06", "showerror": "#b3261e"}
    w = tk.Label(app, text=f"  {title}:  {msg}  ", bg=colors.get(kind, "#1b7f4c"), fg="white", font=("Segoe UI", 13, "bold"), pady=10)
    w.place(relx=0.5, rely=0.08, anchor="n"); w.lift(); pump(2.0); w.destroy(); pump()
for n in ("showinfo", "showwarning", "showerror"):
    setattr(messagebox, n, lambda t, m, n=n: show_msg(n, t, m))
messagebox.askyesno = lambda t, m: True
def typ(var, text, d=0.05):
    for i in range(1, len(text) + 1):
        var.set(text[:i]); pump(d)
def page(): return app.content.winfo_children()[0]
def find(w, cls):
    if isinstance(w, cls): return w
    for c in w.winfo_children():
        r = find(c, cls)
        if r: return r

pump(1.5)
caption("1. Login screen  (Login | Register | Exit)", 2)
app.show_register(); pump(0.5)
caption("2. Register a new account - and you are logged in automatically", 1.2)
rs = app.screen.winfo_children()[0]
typ(rs.vars["username"], "harsha"); typ(rs.vars["password"], "secret1", 0.07); typ(rs.vars["confirm"], "secret1", 0.07)
pump(0.6); rs.register(); pump(1.5)
caption("3. Dashboard - live statistics from SQLite", 3)
app.navigate("students"); pump(0.8)
caption("4. Students - search by name", 1)
sp = page(); typ(sp.text_var, "Priya"); sp.search(); pump(2)
sp.text_var.set(""); sp.show_all(); pump(1)
app.navigate("add_student"); pump(0.8)
caption("5. Add a new student", 1)
form = find(page(), main.StudentForm)
for k, v in (("roll_number", "DS105"), ("name", "Ananya Joshi"), ("course", "CSE Data Science"), ("branch", "Data Science"), ("semester", "3"), ("email", "ananya@example.com"), ("phone", "9876543210")):
    typ(form.vars[k], v, 0.04) if k not in ("semester",) else form.vars[k].set(v)
pump(0.8); form.save(); pump(0.5)
sid = [s for s in student.get_students() if s["roll_number"] == "DS105"][0]["id"]
app.navigate("marks", student_id=sid); pump(0.6)
caption("6. Enter marks - subject by subject", 1)
mp = page(); mp.box.set(next(l for l, i in mp.ids.items() if i == sid)); mp.student_var.set(mp.box.get()); mp.load_student(); pump(1)
for iid, val in zip(mp.tree.get_children(), ["78", "34", "71", "85", "69"]):
    mp.tree.selection_set(iid); mp.tree.see(iid); pump(0.2)
    typ(mp.entry_var, val, 0.1); mp.apply(); pump(0.4)
caption("Total, percentage, grade and PASS/FAIL are calculated automatically", 2.2)
mp.save(); pump(0.4)
mp.view_result(); pump(1)
caption("7. Result marksheet - DBMS 34 < 40, so the student FAILS", 3)
rp = page()
rp.generate_report(); pump(0.5)
caption("8. Generate Report (.txt marksheet with signatures)", 3.5)
rp.show_result(); pump(1)
app.navigate("reports"); pump(0.8)
caption("9. Reports & Statistics - grade distribution, filters", 3)
app.navigate("settings"); pump(0.8)
caption("10. Settings - college name, username, change password", 2.5)
app.logout(); pump(0.6)
caption("Logout returns to the login screen. Data stays saved in database.db", 2.5)
app.destroy()
