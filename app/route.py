from flask import Blueprint, render_template, request, redirect, url_for,session, jsonify
from app import db, get_db_connection

app = Blueprint('main', __name__)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    user_type = request.form.get('user_type')
    if user_type == 'admin':
        return redirect(url_for('main.admin'))
    else:
        return redirect(url_for('main.index'))

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students ;')
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        for student in students:
            if student[1]==username and password == '123456':
                session['username'] = username
                return redirect(url_for('main.curriculum'))
        return render_template('index.html')

@app.route('/curriculum', methods=['GET', 'POST'])
def curriculum():
    username = session.get('username')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM courses;')
        courses = cursor.fetchall()

        cursor.execute('SELECT sid FROM students WHERE sname = %s;', (username,))
        sid_result = cursor.fetchone()
        if sid_result:
            sid=sid_result[0]
        else:
            sid = None

        if sid:
            cursor.execute('SELECT cid FROM choices WHERE sid = %s;', (sid,))
            selected_cids = [row[0] for row in cursor.fetchall()]
            if selected_cids:
                cursor.execute('SELECT * FROM courses WHERE cid IN %s;', (tuple(selected_cids),))
                selected_courses = cursor.fetchall()
            else:
                selected_courses = []
        else:
            selected_courses = []
    except Exception as e:
        print(f"Error fetching data: {e}")
        courses = []
        selected_courses = []
    finally:
        cursor.close()
        conn.close()

    return render_template('curriculumn.html', courses=courses, selected_courses=selected_courses, username=username)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'admin' and password == '123456':
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM students;')
            students = cursor.fetchall()

            cursor.execute('SELECT * FROM courses;')
            courses = cursor.fetchall()

            cursor.execute('SELECT * FROM choices;')
            choices = cursor.fetchall()

            cursor.close()
            conn.close()

            return render_template('database.html', students=students, courses=courses, choices=choices)
        else:
            return render_template('admin.html')
    return render_template('admin.html')

@app.route('/add_choice', methods=['POST'])
def add_choice():
    data = request.get_json()
    cid = data.get('cid')
    username=data.get('username')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT sid FROM students WHERE sname = %s;', (username,))
        sid=cursor.fetchone()[0]
        # Get the current count of rows in the choices table
        cursor.execute('SELECT * FROM choices WHERE sid=%s AND cid=%s', (sid,cid))
        existing_choice = cursor.fetchone()
        if existing_choice:
            success=False
            message='Course already selected'
        else:
            cursor.execute('INSERT INTO choices (sid, cid) VALUES ( %s, %s)', ( sid, cid))
            conn.commit()
            success = True
            message='Course added successfully'
    except Exception as e:
        print(f"Error adding choice: {e}")
        success = False
        message='Error adding choice'
    finally:
        cursor.close()
        conn.close()

    return jsonify({'success': success,'message':message})

@app.route('/get_choices', methods=['GET'])
def get_choices():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM choices;')
        choices = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching choices: {e}")
        choices = []
    finally:
        cursor.close()
        conn.close()

    return jsonify({'choices': choices})

@app.route('/delete_choice', methods=['POST'])
def delete_choice():
    data = request.get_json()
    cid = data.get('cid')
    username = data.get('username')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT sid FROM students WHERE sname = %s;', (username,))
        sid_result = cursor.fetchone()
        if not sid_result:
            return jsonify({'success': False, 'message': 'Student not found'})
        sid=sid_result[0]

        cursor.execute('DELETE FROM choices WHERE sid = %s AND cid = %s;', (sid, cid))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Choice not found'})
        success = True
        message = 'Course deleted successfully'
    except Exception as e:
        print(f"Error deleting choice: {e}")
        success = False
        message = 'Error deleting choice'
    finally:
        cursor.close()
        conn.close()

    return jsonify({'success': success, 'message': message})

@app.route('/update_student', methods=['POST'])
def update_student():
    current_sid = request.form.get('current_sid')
    new_sid = request.form.get('sid')
    new_sname = request.form.get('sname')
    new_grade = request.form.get('grade')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('UPDATE students SET sid=%s, sname = %s, grade = %s WHERE sid = %s;', (new_sid,new_sname, new_grade, current_sid))
        conn.commit()

    except Exception as e:
        print(f"Error updating student: {e}")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('main.admin'))

@app.route('/get_students', methods=['GET'])
def get_students():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM students;')
        students = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching students: {e}")
        students = []
    finally:
        cursor.close()
        conn.close()

    return jsonify({'students': [{'sid': student[0], 'sname': student[1], 'grade': student[2]} for student in students]})

@app.route('/delete_student', methods=['POST'])
def delete_student():
    sid = request.form.get('sid')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM students WHERE sid = %s;', (sid,))
        conn.commit()
        success = cursor.rowcount > 0
        message = 'Student deleted successfully' if success else 'Student not found'
    except Exception as e:
        print(f"Error deleting student: {e}")
        success = False
        message = 'Error deleting student'
    finally:
        cursor.close()
        conn.close()

    return jsonify({'success': success, 'message': message})

@app.route('/add_student', methods=['POST'])
def add_student():
    sid = request.form.get('sid')
    sname = request.form.get('sname')
    grade = request.form.get('grade')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO students (sid, sname, grade) VALUES (%s, %s, %s);', (sid, sname, grade))
        conn.commit()
        success = True
        message = 'Student added successfully'
    except Exception as e:
        print(f"Error adding student: {e}")
        success = False
        message = 'Error adding student'
    finally:
        cursor.close()
        conn.close()

    return jsonify({'success': success, 'message': message})


@app.route('/update_course', methods=['POST'])
def update_course():
    current_cid = request.form.get('current_cid')
    new_cid = request.form.get('cid')
    new_cname = request.form.get('cname')
    new_credit = request.form.get('credit')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('UPDATE courses SET cid=%s, cname = %s, credit = %s WHERE cid = %s;', (new_cid,new_cname, new_credit, current_cid))
        conn.commit()

    except Exception as e:
        print(f"Error updating course: {e}")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('main.admin'))

@app.route('/delete_course', methods=['POST'])
def delete_course():
    cid = request.form.get('cid')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM courses WHERE cid = %s;', (cid,))
        conn.commit()
        success = cursor.rowcount > 0
        message = 'Course deleted successfully' if success else 'Course not found'
    except Exception as e:
        print(f"Error deleting course: {e}")
        success = False
        message = 'Error deleting course'
    finally:
        cursor.close()
        conn.close()

    return jsonify({'success': success, 'message': message})

@app.route('/add_course', methods=['POST'])
def add_course():
    cid = request.form.get('cid')
    cname = request.form.get('cname')
    credit = request.form.get('credit')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO courses (cid, cname, credit) VALUES (%s, %s, %s);', (cid, cname, credit))
        conn.commit()
        success = True
        message = 'Course added successfully'
    except Exception as e:
        print(f"Error adding student: {e}")
        success = False
        message = 'Error adding student'
    finally:
        cursor.close()
        conn.close()

    return jsonify({'success': success, 'message': message})

@app.route('/delete_ch', methods=['POST'])
def delete_ch():
    no = request.form.get('no')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM choices WHERE no = %s;', (no,))
        conn.commit()
        success = cursor.rowcount > 0
        message = 'Choice deleted successfully' if success else 'Choice not found'
    except Exception as e:
        print(f"Error deleting choice: {e}")
        success = False
        message = 'Error deleting chocie'
    finally:
        cursor.close()
        conn.close()

    return jsonify({'success': success, 'message': message})