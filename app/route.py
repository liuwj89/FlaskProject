from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app import db, get_db_connection

# 创建一个名为 'main' 的 Blueprint
app = Blueprint('main', __name__)

@app.route('/')
def home():
    """
    渲染登录页面。
    """
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """
    处理登录表单提交。
    如果用户是管理员，则重定向到管理员页面，否则重定向到首页。
    """
    user_type = request.form.get('user_type')
    if user_type == 'admin':
        return redirect(url_for('main.admin'))
    else:
        return redirect(url_for('main.index'))

@app.route('/index', methods=['GET', 'POST'])
def index():
    """
    渲染首页。
    处理登录表单提交并验证用户凭据。
    """
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
            if student[1] == username and password == '123456':
                session['username'] = username
                return redirect(url_for('main.curriculum'))
        return render_template('index.html')

@app.route('/curriculum', methods=['GET', 'POST'])
def curriculum():
    """
    渲染课程页面。
    获取并显示登录用户的课程和已选课程。
    """
    username = session.get('username')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM courses;')
        courses = cursor.fetchall()

        cursor.execute('SELECT sid FROM students WHERE sname = %s;', (username,))
        sid_result = cursor.fetchone()
        if sid_result:
            sid = sid_result[0]
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
        print(f"获取数据时出错: {e}")
        courses = []
        selected_courses = []
    finally:
        cursor.close()
        conn.close()

    return render_template('curriculumn.html', courses=courses, selected_courses=selected_courses, username=username)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """
    渲染管理员页面。
    处理管理员登录并在凭据有效时显示数据库信息。
    """
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
    """
    为学生添加课程选择。
    """
    data = request.get_json()
    cid = data.get('cid')
    username = data.get('username')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT sid FROM students WHERE sname = %s;', (username,))
        sid = cursor.fetchone()[0]

        cursor.execute('SELECT * FROM choices WHERE sid=%s AND cid=%s', (sid, cid))
        existing_choice = cursor.fetchone()
        if existing_choice:
            success = False
            message = '课程已选'
        else:
            cursor.execute('INSERT INTO choices (sid, cid) VALUES ( %s, %s)', (sid, cid))
            conn.commit()
            success = True
            message = '课程添加成功'
    except Exception as e:
        print(f"添加选择时出错: {e}")
        success = False
        message = '添加选择时出错'
    finally:
        cursor.close()
        conn.close()

    return jsonify({'success': success, 'message': message})

@app.route('/get_choices', methods=['GET'])
def get_choices():
    """
    获取并返回所有课程选择。
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM choices;')
        choices = cursor.fetchall()
    except Exception as e:
        print(f"获取选择时出错: {e}")
        choices = []
    finally:
        cursor.close()
        conn.close()

    return jsonify({'choices': choices})

@app.route('/delete_choice', methods=['POST'])
def delete_choice():
    """
    删除学生的课程选择。
    """
    data = request.get_json()
    cid = data.get('cid')
    username = data.get('username')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT sid FROM students WHERE sname = %s;', (username,))
        sid_result = cursor.fetchone()
        if not sid_result:
            return jsonify({'success': False, 'message': '未找到学生'})
        sid = sid_result[0]

        cursor.execute('DELETE FROM choices WHERE sid = %s AND cid = %s;', (sid, cid))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': '未找到选择'})
        success = True
        message = '课程删除成功'
    except Exception as e:
        print(f"删除选择时出错: {e}")
        success = False
        message = '删除选择时出错'
    finally:
        cursor.close()
        conn.close()

    return jsonify({'success': success, 'message': message})

@app.route('/update_student', methods=['POST'])
def update_student():
    """
    更新学生信息。
    """
    current_sid = request.form.get('current_sid')
    new_sid = request.form.get('sid')
    new_sname = request.form.get('sname')
    new_grade = request.form.get('grade')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('UPDATE students SET sid=%s, sname = %s, grade = %s WHERE sid = %s;', (new_sid, new_sname, new_grade, current_sid))
        conn.commit()
    except Exception as e:
        print(f"更新学生信息时出错: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('main.admin'))

@app.route('/get_students', methods=['GET'])
def get_students():
    """
    获取并返回所有学生。
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM students;')
        students = cursor.fetchall()
    except Exception as e:
        print(f"获取学生时出错: {e}")
        students = []
    finally:
        cursor.close()
        conn.close()

    return jsonify({'students': [{'sid': student[0], 'sname': student[1], 'grade': student[2]} for student in students]})

@app.route('/delete_student', methods=['POST'])
def delete_student():
    """
    删除学生。
    """
    sid = request.form.get('sid')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM students WHERE sid = %s;', (sid,))
        conn.commit()
        success = cursor.rowcount > 0
        message = '学生删除成功' if success else '未找到学生'
    except Exception as e:
        print(f"删除学生时出错: {e}")
        success = False
        message = '删除学生时出错'
    finally:
        cursor.close()
        conn.close()

    return jsonify({'success': success, 'message': message})

@app.route('/add_student', methods=['POST'])
def add_student():
    """
    添加新学生。
    """
    sid = request.form.get('sid')
    sname = request.form.get('sname')
    grade = request.form.get('grade')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO students (sid, sname, grade) VALUES (%s, %s, %s);', (sid, sname, grade))
        conn.commit()
        success = True
        message = '学生添加成功'
    except Exception as e:
        print(f"添加学生时出错: {e}")
        success = False
        message = '添加学生时出错'
    finally:
        cursor.close()
        conn.close()

    return jsonify({'success': success, 'message': message})

@app.route('/update_course', methods=['POST'])
def update_course():
    """
    更新课程信息。
    """
    current_cid = request.form.get('current_cid')
    new_cid = request.form.get('cid')
    new_cname = request.form.get('cname')
    new_credit = request.form.get('credit')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('UPDATE courses SET cid=%s, cname = %s, credit = %s WHERE cid = %s;', (new_cid, new_cname, new_credit, current_cid))
        conn.commit()
    except Exception as e:
        print(f"更新课程信息时出错: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('main.admin'))

@app.route('/delete_course', methods=['POST'])
def delete_course():
    """
    删除课程。
    """
    cid = request.form.get('cid')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM courses WHERE cid = %s;', (cid,))
        conn.commit()
        success = cursor.rowcount > 0
        message = '课程删除成功' if success else '未找到课程'
    except Exception as e:
        print(f"删除课程时出错: {e}")
        success = False
        message = '删除课程时出错'
    finally:
        cursor.close()
        conn.close()

    return jsonify({'success': success, 'message': message})

@app.route('/add_course', methods=['POST'])
def add_course():
    """
    添加新课程。
    """
    cid = request.form.get('cid')
    cname = request.form.get('cname')
    credit = request.form.get('credit')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO courses (cid, cname, credit) VALUES (%s, %s, %s);', (cid, cname, credit))
        conn.commit()
        success = True
        message = '课程添加成功'
    except Exception as e:
        print(f"添加课程时出错: {e}")
        success = False
        message = '添加课程时出错'
    finally:
        cursor.close()
        conn.close()

    return jsonify({'success': success, 'message': message})

@app.route('/delete_ch', methods=['POST'])
def delete_ch():
    """
    按编号删除选择。
    """
    no = request.form.get('no')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM choices WHERE no = %s;', (no,))
        conn.commit()
        success = cursor.rowcount > 0
        message = '选择删除成功' if success else '未找到选择'
    except Exception as e:
        print(f"删除选择时出错: {e}")
        success = False
        message = '删除选择时出错'
    finally:
        cursor.close()
        conn.close()

    return jsonify({'success': success, 'message': message})