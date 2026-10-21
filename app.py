from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-this-development-key"
DB_PATH = Path(__file__).with_name("estate.db")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_no TEXT NOT NULL UNIQUE,
            building TEXT NOT NULL,
            room_type TEXT NOT NULL,
            capacity INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Available',
            assigned_to TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            location TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'Medium',
            reported_by TEXT NOT NULL,
            reported_on TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            notes TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_name TEXT NOT NULL,
            asset_tag TEXT NOT NULL UNIQUE,
            location TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            condition_status TEXT NOT NULL DEFAULT 'Good',
            purchase_date TEXT DEFAULT ''
        );
        """)
        if con.execute("SELECT COUNT(*) FROM rooms").fetchone()[0] == 0:
            con.executemany("""INSERT INTO rooms(room_no,building,room_type,capacity,status,assigned_to)
                VALUES(?,?,?,?,?,?)""", [
                ("A-101","Academic Block A","Classroom",60,"Available",""),
                ("A-102","Academic Block A","Laboratory",35,"Allocated","Computer Science Lab"),
                ("B-201","Academic Block B","Faculty Room",12,"Allocated","MCA Faculty"),
                ("C-001","Admin Block","Meeting Room",20,"Available",""),
            ])
        if con.execute("SELECT COUNT(*) FROM assets").fetchone()[0] == 0:
            con.executemany("""INSERT INTO assets(asset_name,asset_tag,location,quantity,condition_status,purchase_date)
                VALUES(?,?,?,?,?,?)""", [
                ("Projector","AST-PRJ-001","A-101",1,"Good","2025-07-12"),
                ("Desktop Computer","AST-PC-014","Computer Science Lab",30,"Good","2025-08-01"),
                ("Office Chair","AST-CHR-022","Admin Block",8,"Needs Repair","2024-11-20"),
            ])
        if con.execute("SELECT COUNT(*) FROM maintenance").fetchone()[0] == 0:
            con.executemany("""INSERT INTO maintenance(title,location,category,priority,reported_by,reported_on,status,notes)
                VALUES(?,?,?,?,?,?,?,?)""", [
                ("Projector not powering on","A-101","Electrical","High","MCA Office",datetime.now().strftime("%Y-%m-%d"),"In Progress","Check power cable and lamp."),
                ("Water leakage near washroom","Academic Block B","Plumbing","Medium","Facilities Desk",datetime.now().strftime("%Y-%m-%d"),"Open","Inspection required."),
            ])

@app.route("/")
def dashboard():
    with db() as con:
        stats = {
            "rooms": con.execute("SELECT COUNT(*) FROM rooms").fetchone()[0],
            "available": con.execute("SELECT COUNT(*) FROM rooms WHERE status='Available'").fetchone()[0],
            "open_requests": con.execute("SELECT COUNT(*) FROM maintenance WHERE status!='Completed'").fetchone()[0],
            "assets": con.execute("SELECT COUNT(*) FROM assets").fetchone()[0],
        }
        requests_recent = con.execute("SELECT * FROM maintenance ORDER BY id DESC LIMIT 5").fetchall()
        rooms_recent = con.execute("SELECT * FROM rooms ORDER BY id DESC LIMIT 5").fetchall()
    return render_template("dashboard.html", stats=stats, requests=requests_recent, rooms=rooms_recent)

@app.route("/rooms", methods=["GET", "POST"])
def rooms():
    with db() as con:
        if request.method == "POST":
            try:
                con.execute("""INSERT INTO rooms(room_no,building,room_type,capacity,status,assigned_to)
                    VALUES(?,?,?,?,?,?)""", (
                    request.form["room_no"].strip(), request.form["building"].strip(),
                    request.form["room_type"], int(request.form.get("capacity") or 0),
                    request.form["status"], request.form.get("assigned_to","").strip()))
                flash("Room saved successfully.", "success")
            except sqlite3.IntegrityError:
                flash("Room number already exists. Use a unique room number.", "error")
            return redirect(url_for("rooms"))
        rows = con.execute("SELECT * FROM rooms ORDER BY building, room_no").fetchall()
    return render_template("rooms.html", rooms=rows)

@app.route("/rooms/<int:room_id>/status", methods=["POST"])
def update_room(room_id):
    status = request.form["status"]
    assigned_to = request.form.get("assigned_to", "").strip()
    with db() as con:
        con.execute("UPDATE rooms SET status=?, assigned_to=? WHERE id=?", (status, assigned_to, room_id))
    flash("Room allocation updated.", "success")
    return redirect(url_for("rooms"))

@app.route("/maintenance", methods=["GET", "POST"])
def maintenance():
    with db() as con:
        if request.method == "POST":
            con.execute("""INSERT INTO maintenance(title,location,category,priority,reported_by,reported_on,status,notes)
                VALUES(?,?,?,?,?,?,?,?)""", (
                request.form["title"].strip(), request.form["location"].strip(),
                request.form["category"], request.form["priority"],
                request.form["reported_by"].strip(), datetime.now().strftime("%Y-%m-%d"),
                "Open", request.form.get("notes","").strip()))
            flash("Maintenance request submitted.", "success")
            return redirect(url_for("maintenance"))
        rows = con.execute("SELECT * FROM maintenance ORDER BY id DESC").fetchall()
    return render_template("maintenance.html", requests=rows)

@app.route("/maintenance/<int:req_id>/status", methods=["POST"])
def update_maintenance(req_id):
    with db() as con:
        con.execute("UPDATE maintenance SET status=? WHERE id=?", (request.form["status"], req_id))
    flash("Maintenance status updated.", "success")
    return redirect(url_for("maintenance"))

@app.route("/assets", methods=["GET", "POST"])
def assets():
    with db() as con:
        if request.method == "POST":
            try:
                con.execute("""INSERT INTO assets(asset_name,asset_tag,location,quantity,condition_status,purchase_date)
                    VALUES(?,?,?,?,?,?)""", (
                    request.form["asset_name"].strip(), request.form["asset_tag"].strip().upper(),
                    request.form["location"].strip(), int(request.form.get("quantity") or 1),
                    request.form["condition_status"], request.form.get("purchase_date","")))
                flash("Asset added to inventory.", "success")
            except sqlite3.IntegrityError:
                flash("Asset tag already exists. Enter a unique tag.", "error")
            return redirect(url_for("assets"))
        rows = con.execute("SELECT * FROM assets ORDER BY id DESC").fetchall()
    return render_template("assets.html", assets=rows)

@app.route("/reports")
def reports():
    with db() as con:
        room_summary = con.execute("SELECT status, COUNT(*) AS total FROM rooms GROUP BY status").fetchall()
        maintenance_summary = con.execute("SELECT status, COUNT(*) AS total FROM maintenance GROUP BY status").fetchall()
        asset_summary = con.execute("SELECT condition_status, COUNT(*) AS total FROM assets GROUP BY condition_status").fetchall()
        all_requests = con.execute("SELECT * FROM maintenance ORDER BY id DESC").fetchall()
    return render_template("reports.html", room_summary=room_summary,
                           maintenance_summary=maintenance_summary,
                           asset_summary=asset_summary, requests=all_requests)

@app.route("/health")
def health():
    return {"status": "ok", "application": "Campus Estate & Facilities Management System"}

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
