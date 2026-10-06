from flask import Flask, request
import sqlite3

app = Flask(__name__)

DATABASE = "hostel.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =========================================================
# CREATE DATABASE
# =========================================================

def create_database():

    conn = get_db()

    # Rooms table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_no TEXT UNIQUE,
            capacity INTEGER,
            occupied INTEGER
        )
    """)

    # Applications table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            student_id TEXT,
            phone TEXT,
            gender TEXT,
            room_no TEXT,
            status TEXT DEFAULT 'Active'
        )
    """)

    # Remove duplicate active applications from older databases before
    # creating the uniqueness rule for student IDs.
    conn.execute("""
        DELETE FROM applications
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM applications
            WHERE status = 'Active'
            GROUP BY student_id
        )
        AND status = 'Active'
    """)

    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_applications_student_id_active
        ON applications(student_id)
        WHERE status = 'Active'
    """)

    # Check if status column exists
    columns = conn.execute(
        "PRAGMA table_info(applications)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

    # Add status column if old database does not have it
    if "status" not in column_names:
        conn.execute("""
            ALTER TABLE applications
            ADD COLUMN status TEXT DEFAULT 'Active'
        """)

    # Add sample rooms only if database is empty
    room_count = conn.execute(
        "SELECT COUNT(*) FROM rooms"
    ).fetchone()[0]

    if room_count == 0:

        rooms = [
            ("A-101", 2, 2),
            ("A-102", 2, 1),
            ("A-103", 3, 1),
            ("A-104", 2, 0),
            ("A-105", 3, 2),
            ("A-106", 2, 0),
            ("B-101", 2, 1),
            ("B-102", 3, 0)
        ]

        conn.executemany("""
            INSERT INTO rooms
            (room_no, capacity, occupied)
            VALUES (?, ?, ?)
        """, rooms)

    conn.commit()
    conn.close()


# =========================================================
# CSS DESIGN
# =========================================================

STYLE = """

<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');


* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}


body {
    font-family: 'Poppins', Arial, sans-serif;
    background: #f5f7fb;
    color: #172b4d;
}


/* ================= NAVBAR ================= */

.navbar {
    background: #172b4d;
    padding: 18px 7%;

    display: flex;
    justify-content: space-between;
    align-items: center;

    flex-wrap: wrap;
}


.logo {
    color: white;
    font-size: 22px;
    font-weight: 700;
}


.nav-links {
    display: flex;
    gap: 25px;
    flex-wrap: wrap;
}


.nav-links a {
    color: white;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
}


.nav-links a:hover {
    color: #43d9a3;
}


/* ================= CONTAINER ================= */

.container {
    width: 86%;
    max-width: 1200px;
    margin: 40px auto;
}


/* ================= HERO ================= */

.hero {
    background: linear-gradient(
        135deg,
        #172b4d,
        #274b7a
    );

    color: white;

    padding: 55px;

    border-radius: 22px;

    margin-bottom: 30px;
}


.hero h1 {
    font-size: 40px;
    margin-bottom: 12px;
}


.hero p {
    font-size: 16px;
    opacity: 0.9;
}


/* ================= BUTTON ================= */

.btn {
    display: inline-block;

    padding: 11px 20px;

    border-radius: 9px;

    text-decoration: none;

    border: none;

    cursor: pointer;

    font-family: inherit;

    font-weight: 600;

    background: #43d9a3;

    color: #172b4d;
}


.btn:hover {
    opacity: 0.85;
}


.btn-danger {
    background: #ef5350;
    color: white;
}


.btn-blue {
    background: #4b7bec;
    color: white;
}


/* ================= STATISTICS ================= */

.stats {

    display: grid;

    grid-template-columns:
        repeat(4, 1fr);

    gap: 18px;

    margin-bottom: 35px;
}


.stat-card {

    background: white;

    padding: 25px;

    border-radius: 16px;

    box-shadow:
        0 5px 20px rgba(0,0,0,0.06);
}


.stat-card h2 {

    font-size: 30px;

    margin-bottom: 5px;
}


.stat-card p {

    color: #777;
}


/* ================= ROOM GRID ================= */

.room-grid {

    display: grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 22px;
}


.room-card {

    background: white;

    padding: 25px;

    border-radius: 17px;

    box-shadow:
        0 5px 20px rgba(0,0,0,0.06);
}


.room-card h3 {

    margin-bottom: 10px;

    font-size: 22px;
}


.room-card p {

    margin: 7px 0;

    color: #555;
}


.available {

    color: #1a9c6d;

    font-weight: 600;
}


.full {

    color: #e53935;

    font-weight: 600;
}


/* ================= FORM ================= */

.form-box {

    background: white;

    padding: 30px;

    border-radius: 18px;

    box-shadow:
        0 5px 20px rgba(0,0,0,0.06);

    max-width: 700px;

    margin: auto;
}


.form-box h2 {

    margin-bottom: 20px;
}


.form-group {

    margin-bottom: 18px;
}


.form-group label {

    display: block;

    margin-bottom: 7px;

    font-weight: 600;
}


.form-group input,
.form-group select {

    width: 100%;

    padding: 12px;

    border: 1px solid #ddd;

    border-radius: 9px;

    font-family: inherit;
}


/* ================= TABLE ================= */

.table-box {

    background: white;

    padding: 25px;

    border-radius: 18px;

    box-shadow:
        0 5px 20px rgba(0,0,0,0.06);

    overflow-x: auto;
}


table {

    width: 100%;

    border-collapse: collapse;
}


th,
td {

    padding: 14px;

    border-bottom: 1px solid #eee;

    text-align: left;
}


th {

    background: #172b4d;

    color: white;
}


.active {

    color: #159b6b;

    font-weight: 600;
}


.left {

    color: #e53935;

    font-weight: 600;
}


/* ================= MESSAGE ================= */

.message {

    padding: 15px;

    border-radius: 10px;

    margin-bottom: 20px;

    background: #dff8ed;

    color: #147a55;
}


.error {

    background: #ffe1e1;

    color: #c62828;
}


/* ================= FOOTER ================= */

.footer {

    margin-top: 50px;

    background: #172b4d;

    color: white;

    text-align: center;

    padding: 25px;
}


/* ================= RESPONSIVE ================= */

@media(max-width: 800px) {

    .stats {

        grid-template-columns:
            repeat(2, 1fr);
    }


    .room-grid {

        grid-template-columns:
            repeat(2, 1fr);
    }


    .hero h1 {

        font-size: 30px;
    }
}


@media(max-width: 550px) {

    .stats,
    .room-grid {

        grid-template-columns: 1fr;
    }


    .navbar {

        gap: 15px;
    }


    .hero {

        padding: 30px;
    }
}

</style>

"""


# =========================================================
# NAVIGATION BAR
# =========================================================

def navbar():

    return """

    <div class="navbar">

        <div class="logo">
            HOSTEL MANAGEMENT SYSTEM
        </div>

        <div class="nav-links">

            <a href="/hostel-management-system">
                Home
            </a>

            <a href="/rooms">
                Rooms
            </a>

            <a href="/apply">
                Apply
            </a>

            <a href="/applications">
                Applications
            </a>

        </div>

    </div>

    """


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
@app.route("/hostel-management-system")
def home():

    conn = get_db()

    rooms = conn.execute("""
        SELECT * FROM rooms
        ORDER BY room_no
    """).fetchall()

    total_rooms = len(rooms)

    total_beds = sum(
        room["capacity"]
        for room in rooms
    )

    occupied_beds = sum(
        room["occupied"]
        for room in rooms
    )

    available_beds = (
        total_beds - occupied_beds
    )

    conn.close()


    room_cards = ""


    for room in rooms:

        available = (
            room["capacity"]
            - room["occupied"]
        )


        if available > 0:

            status = f"""
                <p class="available">
                    ✓ {available} Bed(s) Available
                </p>
            """

        else:

            status = """
                <p class="full">
                    ✕ Room Full
                </p>
            """


        room_cards += f"""

        <div class="room-card">

            <h3>
                Room {room["room_no"]}
            </h3>

            <p>
                Capacity:
                {room["capacity"]}
            </p>

            <p>
                Occupied:
                {room["occupied"]}
            </p>

            {status}

        </div>

        """


    return f"""

    <!DOCTYPE html>

    <html>

    <head>

        <title>
            HOSTEL MANAGEMENT SYSTEM
        </title>

        {STYLE}

    </head>


    <body>

        {navbar()}


        <div class="container">


            <div class="hero">

                <h1>
                    HOSTEL MANAGEMENT SYSTEM
                </h1>

                <p>
                    Manage hostel rooms,
                    student applications
                    and real-time room vacancies
                    easily.
                </p>

                <br>

                <a
                    href="/apply"
                    class="btn"
                >
                    Apply for Hostel
                </a>

            </div>


            <div class="stats">


                <div class="stat-card">

                    <h2>
                        {total_rooms}
                    </h2>

                    <p>
                        Total Rooms
                    </p>

                </div>


                <div class="stat-card">

                    <h2>
                        {total_beds}
                    </h2>

                    <p>
                        Total Beds
                    </p>

                </div>


                <div class="stat-card">

                    <h2>
                        {occupied_beds}
                    </h2>

                    <p>
                        Occupied Beds
                    </p>

                </div>


                <div class="stat-card">

                    <h2>
                        {available_beds}
                    </h2>

                    <p>
                        Available Beds
                    </p>

                </div>


            </div>


            <h2 style="margin-bottom:20px;">

                Room Availability

            </h2>


            <div class="room-grid">

                {room_cards}

            </div>


        </div>


        <div class="footer">

            Hostel Management System © 2026

        </div>


    </body>

    </html>

    """


# =========================================================
# ROOMS PAGE
# =========================================================

@app.route("/rooms")
def rooms():

    conn = get_db()

    rooms = conn.execute("""
        SELECT * FROM rooms
        ORDER BY room_no
    """).fetchall()

    conn.close()


    room_cards = ""


    for room in rooms:

        available = (
            room["capacity"]
            - room["occupied"]
        )


        if available > 0:

            status = f"""

            <p class="available">

                ✓ Available Beds:
                {available}

            </p>

            """

        else:

            status = """

            <p class="full">

                ✕ Room Full

            </p>

            """


        room_cards += f"""

        <div class="room-card">

            <h3>
                Room {room["room_no"]}
            </h3>

            <p>
                Total Capacity:
                {room["capacity"]}
            </p>

            <p>
                Occupied:
                {room["occupied"]}
            </p>

            {status}

        </div>

        """


    return f"""

    <!DOCTYPE html>

    <html>

    <head>

        <title>
            Rooms - HOSTEL MANAGEMENT SYSTEM
        </title>

        {STYLE}

    </head>


    <body>

        {navbar()}


        <div class="container">

            <h1 style="margin-bottom:25px;">

                Hostel Rooms

            </h1>


            <div class="room-grid">

                {room_cards}

            </div>

        </div>


        <div class="footer">

            Hostel Management System © 2026

        </div>


    </body>

    </html>

    """


# =========================================================
# HOSTEL APPLICATION
# =========================================================

@app.route(
    "/apply",
    methods=["GET", "POST"]
)
def apply():

    message = ""

    message_class = "message"


    conn = get_db()


    if request.method == "POST":

        name = request.form["name"]

        student_id = request.form["student_id"]

        phone = request.form["phone"]

        gender = request.form["gender"]

        room_no = request.form["room_no"]

        existing_application = conn.execute("""
            SELECT id
            FROM applications
            WHERE student_id = ?
            AND status = 'Active'
            LIMIT 1
        """, (student_id,)).fetchone()

        room = conn.execute("""
            SELECT * FROM rooms
            WHERE room_no = ?
        """, (room_no,)).fetchone()


        if existing_application is not None:

            message = (
                "An active application already exists for this student ID."
            )

            message_class = "message error"


        elif room is None:

            message = (
                "Selected room does not exist."
            )

            message_class = "message error"


        elif room["occupied"] >= room["capacity"]:

            message = (
                "Sorry, this room is already full."
            )

            message_class = "message error"


        else:

            conn.execute("""
                INSERT INTO applications
                (
                    name,
                    student_id,
                    phone,
                    gender,
                    room_no,
                    status
                )

                VALUES
                (?, ?, ?, ?, ?, 'Active')
            """,
            (
                name,
                student_id,
                phone,
                gender,
                room_no
            ))


            conn.execute("""
                UPDATE rooms

                SET occupied =
                    occupied + 1

                WHERE room_no = ?
            """, (room_no,))


            conn.commit()


            message = """
                Application submitted successfully!
                Room vacancy has been updated automatically.
            """


    # Only available rooms
    available_rooms = conn.execute("""
        SELECT * FROM rooms

        WHERE occupied < capacity

        ORDER BY room_no
    """).fetchall()


    conn.close()


    options = ""


    for room in available_rooms:

        available = (
            room["capacity"]
            - room["occupied"]
        )


        options += f"""

        <option value="{room["room_no"]}">

            Room {room["room_no"]}
            -
            {available}
            Bed(s) Available

        </option>

        """


    return f"""

    <!DOCTYPE html>

    <html>

    <head>

        <title>
            Apply - HOSTEL MANAGEMENT SYSTEM
        </title>

        {STYLE}

    </head>


    <body>

        {navbar()}


        <div class="container">


            <div class="form-box">


                <h2>
                    Hostel Application
                </h2>


                {
                    f'<div class="{message_class}">{message}</div>'
                    if message
                    else ''
                }


                <form method="POST">


                    <div class="form-group">

                        <label>
                            Full Name
                        </label>

                        <input
                            type="text"
                            name="name"
                            placeholder="Enter full name"
                            required
                        >

                    </div>


                    <div class="form-group">

                        <label>
                            Student ID
                        </label>

                        <input
                            type="text"
                            name="student_id"
                            placeholder="Enter student ID"
                            required
                        >

                    </div>


                    <div class="form-group">

                        <label>
                            Phone Number
                        </label>

                        <input
                            type="tel"
                            name="phone"
                            placeholder="Enter phone number"
                            required
                        >

                    </div>


                    <div class="form-group">

                        <label>
                            Gender
                        </label>


                        <select
                            name="gender"
                            required
                        >

                            <option value="">
                                Select Gender
                            </option>

                            <option value="Female">
                                Female
                            </option>

                            <option value="Male">
                                Male
                            </option>

                        </select>

                    </div>


                    <div class="form-group">

                        <label>
                            Select Available Room
                        </label>


                        <select
                            name="room_no"
                            required
                        >

                            <option value="">
                                Select Room
                            </option>

                            {options}

                        </select>

                    </div>


                    <button
                        class="btn"
                        type="submit"
                    >

                        Submit Application

                    </button>


                </form>


            </div>


        </div>


        <div class="footer">

            Hostel Management System © 2026

        </div>


    </body>

    </html>

    """


# =========================================================
# APPLICATIONS PAGE
# =========================================================

@app.route("/applications")
def applications():

    conn = get_db()


    applications = conn.execute("""
        SELECT * FROM applications
        ORDER BY id DESC
    """).fetchall()


    conn.close()


    rows = ""


    for student in applications:


        if student["status"] == "Active":

            status = """
                <span class="active">
                    ACTIVE
                </span>
            """


            action = f"""

            <form
                method="POST"
                action="/vacate/{student["id"]}"

                onsubmit="
                return confirm(
                'Are you sure this student has left the hostel?'
                );
                "
            >

                <button
                    class="btn btn-danger"
                    type="submit"
                >

                    Vacate Room

                </button>

            </form>

            """

        else:

            status = """
                <span class="left">
                    LEFT HOSTEL
                </span>
            """


            action = """

                <span style="color:#777;">
                    Room Vacated
                </span>

            """


        rows += f"""

        <tr>

            <td>
                {student["name"]}
            </td>

            <td>
                {student["student_id"]}
            </td>

            <td>
                {student["phone"]}
            </td>

            <td>
                {student["gender"]}
            </td>

            <td>
                {student["room_no"]}
            </td>

            <td>
                {status}
            </td>

            <td>
                {action}
            </td>

        </tr>

        """


    return f"""

    <!DOCTYPE html>

    <html>

    <head>

        <title>
            Applications - HOSTEL MANAGEMENT SYSTEM
        </title>

        {STYLE}

    </head>


    <body>

        {navbar()}


        <div class="container">


            <h1 style="margin-bottom:25px;">

                Hostel Applications

            </h1>


            <div class="table-box">


                <table>


                    <tr>

                        <th>
                            Name
                        </th>

                        <th>
                            Student ID
                        </th>

                        <th>
                            Phone
                        </th>

                        <th>
                            Gender
                        </th>

                        <th>
                            Room
                        </th>

                        <th>
                            Status
                        </th>

                        <th>
                            Action
                        </th>

                    </tr>


                    {rows}


                </table>


            </div>


        </div>


        <div class="footer">

            Hostel Management System © 2026

        </div>


    </body>

    </html>

    """


# =========================================================
# VACATE ROOM
# =========================================================

@app.route(
    "/vacate/<int:application_id>",
    methods=["POST"]
)
def vacate(application_id):

    conn = get_db()


    student = conn.execute("""
        SELECT * FROM applications

        WHERE id = ?
    """, (application_id,)).fetchone()


    if student is None:

        conn.close()


        return """

        <script>

            alert(
                "Student application not found."
            );

            window.location.href =
                "/applications";

        </script>

        """


    # Only active students can vacate
    if student["status"] == "Active":


        # Change student status
        conn.execute("""
            UPDATE applications

            SET status = 'Left'

            WHERE id = ?
        """, (application_id,))


        # Decrease occupied beds
        conn.execute("""
            UPDATE rooms

            SET occupied =
                CASE

                    WHEN occupied > 0
                    THEN occupied - 1

                    ELSE 0

                END

            WHERE room_no = ?
        """, (student["room_no"],))


        conn.commit()


    conn.close()


    return """

    <script>

        alert(
            "Student has left the hostel. "
            + "Room vacancy updated successfully."
        );

        window.location.href =
            "/applications";

    </script>

    """


# =========================================================
# START APPLICATION
# =========================================================

create_database()


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)