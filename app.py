from flask import Flask, render_template, request, Response, redirect
import sqlite3
import csv
import io

app = Flask(__name__)


# Database connection
def get_db_connection():
    connection = sqlite3.connect("business.db")
    connection.row_factory = sqlite3.Row
    return connection


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Save investigation
@app.route("/investigate", methods=["POST"])
def investigate():
    business_name = request.form.get("businessName", "").strip()
    industry = request.form.get("industry", "").strip()
    location = request.form.get("location", "").strip()

    if not business_name or not industry or not location:
        return "Please fill in all fields.", 400

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO investigations
        (business_name, industry, location, status)
        VALUES (?, ?, ?, ?)
        """,
        (business_name, industry, location, "Pending")
    )

    connection.commit()
    connection.close()

    return render_template(
        "index.html",
        business_name=business_name,
        industry=industry,
        location=location
    )


# Dashboard
@app.route("/dashboard")
def dashboard():
    connection = get_db_connection()

    total_investigations = connection.execute(
        "SELECT COUNT(*) FROM investigations"
    ).fetchone()[0]

    total_businesses = connection.execute(
        "SELECT COUNT(DISTINCT business_name) FROM investigations"
    ).fetchone()[0]

    pending_count = connection.execute(
        "SELECT COUNT(*) FROM investigations WHERE status = 'Pending'"
    ).fetchone()[0]

    in_progress_count = connection.execute(
        "SELECT COUNT(*) FROM investigations WHERE status = 'In Progress'"
    ).fetchone()[0]

    completed_count = connection.execute(
        "SELECT COUNT(*) FROM investigations WHERE status = 'Completed'"
    ).fetchone()[0]

    industry_stats = connection.execute(
        """
        SELECT industry, COUNT(*) AS total
        FROM investigations
        GROUP BY industry
        ORDER BY total DESC
        """
    ).fetchall()

    recent_investigations = connection.execute(
        """
        SELECT * FROM investigations
        ORDER BY id DESC
        LIMIT 5
        """
    ).fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        total_investigations=total_investigations,
        total_businesses=total_businesses,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        completed_count=completed_count,
        industry_stats=industry_stats,
        recent_investigations=recent_investigations
    )


# Investigation History
@app.route("/history")
def history():
    connection = get_db_connection()

    investigations = connection.execute(
        "SELECT * FROM investigations ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "history.html",
        investigations=investigations
    )


# Update investigation status
@app.route("/update_status/<int:id>", methods=["POST"])
def update_status(id):
    status = request.form.get("status", "").strip()

    allowed_statuses = ["Pending", "In Progress", "Completed"]

    if status not in allowed_statuses:
        return "Invalid status selected.", 400

    connection = get_db_connection()

    investigation = connection.execute(
        "SELECT id FROM investigations WHERE id = ?",
        (id,)
    ).fetchone()

    if investigation is None:
        connection.close()
        return "Investigation not found.", 404

    connection.execute(
        "UPDATE investigations SET status = ? WHERE id = ?",
        (status, id)
    )

    connection.commit()
    connection.close()

    return redirect("/history")


# Export records to CSV
@app.route("/export")
def export():
    connection = get_db_connection()

    investigations = connection.execute(
        "SELECT * FROM investigations ORDER BY id DESC"
    ).fetchall()

    connection.close()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID", "Business Name", "Industry", "Location", "Status"
    ])

    for item in investigations:
        writer.writerow([
            item["id"],
            item["business_name"],
            item["industry"],
            item["location"],
            item["status"]
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=investigation_history.csv"
        }
    )


# Edit investigation
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_investigation(id):
    connection = get_db_connection()

    if request.method == "POST":
        business_name = request.form.get("businessName", "").strip()
        industry = request.form.get("industry", "").strip()
        location = request.form.get("location", "").strip()

        if not business_name or not industry or not location:
            connection.close()
            return "Please fill in all fields.", 400

        connection.execute(
            """
            UPDATE investigations
            SET business_name = ?, industry = ?, location = ?
            WHERE id = ?
            """,
            (business_name, industry, location, id)
        )

        connection.commit()
        connection.close()

        return redirect("/history")

    investigation = connection.execute(
        "SELECT * FROM investigations WHERE id = ?",
        (id,)
    ).fetchone()

    connection.close()

    if investigation is None:
        return "Investigation not found.", 404

    return render_template(
        "edit.html",
        investigation=investigation
    )


# Delete investigation
@app.route("/delete/<int:id>", methods=["POST"])
def delete_investigation(id):
    connection = get_db_connection()

    investigation = connection.execute(
        "SELECT id FROM investigations WHERE id = ?",
        (id,)
    ).fetchone()

    if investigation is None:
        connection.close()
        return "Investigation not found.", 404

    connection.execute(
        "DELETE FROM investigations WHERE id = ?",
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect("/history")


# Business Investigation Report
@app.route("/report/<int:id>")
def business_report(id):
    connection = get_db_connection()

    investigation = connection.execute(
        "SELECT * FROM investigations WHERE id = ?",
        (id,)
    ).fetchone()

    connection.close()

    if investigation is None:
        return "Investigation not found.", 404

    return render_template(
        "report.html",
        investigation=investigation
    )


# Run application
if __name__ == "__main__":
    app.run(debug=True)
