from flask import Flask , render_template, request, redirect, url_for, flash,session
from flask_mysqldb import MySQL



app = Flask(__name__)


# app.config['MYSQL_HOST'] = 'ysjcs.net'
# app.config['MYSQL_USER'] = 'noman.rafique'
# app.config['MYSQL_PASSWORD'] = 'KPKT8GWX'
# app.config['MYSQL_DB'] = 'nomanrafique_flaskApp'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'practicedb'
app.secret_key = 'abc'


mysql = MySQL(app)

@app.route('/', methods= ['GET','POST'])
@app.route('/login', methods= ['GET','POST'])
def login():
    session.pop('_flashes', None)
    session.pop('user_id',None)
    if request.method == 'POST':
        log_email = request.form['log_email']
        log_pin = request.form['log_password']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE EMAIL = %s AND PIN = %s', ([log_email], [log_pin]))
        account = cur.fetchone()

        if account:
            session['user_id'] = log_email
            if account[3] == 'Technician':
                return redirect(url_for('technican'))
            elif account[3] == 'Student':          
                return redirect(url_for('student'))
            elif account[3] == 'Admin':
                return redirect(url_for('admin'))
            else:
                return "Incorrect"


    return render_template('login.html')



@app.route('/register', methods= ['GET','POST'])
def signup():
    if session.get('user_id', None) != None and userStatus(session.get('user_id',None)) == 'Admin':
        if request.method == 'POST':
            reg_email = request.form['reg_email']
            reg_name = request.form['reg_name']
            reg_pin = request.form['reg_pin']
            reg_type = request.form.get('reg_type')
            cur = mysql.connection.cursor()
            try:
                cur.execute('INSERT INTO users(EMAIL,NAME,PIN,TYPE) VALUES(%s,%s,%s,%s)', ([reg_email], [reg_name],[reg_pin],[reg_type]))
            except Exception:
                flash('Invalid Input')
            else:
                mysql.connection.commit()
                flash('Successfully Registered')
        return render_template('register.html')
    else:
        return "Acces Denied"


@app.route('/student', methods=['GET','SET'])
def student():
    if session.get('user_id', None) != None and userStatus(session.get('user_id',None)) == 'Student':
        user_id = session.get('user_id', None)
        cur = mysql.connection.cursor()
        cur.execute('Select users.name, jobs.job_title, jobs.job_description, jobs.status, ' 
        + 'jobs_creation.event_time, jobs.job_id from users inner join jobs_creation on users.email= jobs_creation.CREATOR_ID '
        + 'inner join jobs on jobs.job_id = jobs_creation.job_id where users.EMAIL = %s and jobs.STATUS = "Active"', [user_id])
        active_data = cur.fetchall()
        cur.execute('SELECT userR.name, jobs_resolved.event_time, jobs.JOB_TITLE, jobs.job_description, jobs.status, '
        + 'userR.email FROM users userC  INNER JOIN jobs_creation ON userC.EMAIL = jobs_creation.CREATOR_ID inner JOIN '
        + 'jobs on jobs_creation.JOB_ID = jobs.JOB_ID INNER JOIN jobs_resolved on jobs.JOB_ID = jobs_resolved.JOB_ID '
        + 'INNER JOIN users userR on jobs_resolved.RESOLVER_ID = userR.EMAIL where userC.EMAIL = %s and jobs.STATUS = "Resolved"', [user_id])
        resolved_data = cur.fetchall()
        
        return render_template('student.html', active_data = active_data, resolved_data = resolved_data)
    else:
        return "Access Denied"



@app.route('/technican', methods=['GET','SET'])
def technican():
    if session.get('user_id', None) != None and userStatus(session.get('user_id',None)) == 'Technician':
        user_id = session.get('user_id', None)
        cur = mysql.connection.cursor()
        cur.execute('Select users.name, jobs.job_title, jobs.job_description, jobs.status, jobs.job_id, jobs_creation.event_time, '
        + 'users.email from users inner join jobs_creation on users.email= jobs_creation.CREATOR_ID '
        + 'inner join jobs on jobs.job_id = jobs_creation.job_id where jobs.status = "Active"')
        active_data = cur.fetchall()
        cur.execute('SELECT userC.name, jobs_creation.event_time, jobs.JOB_TITLE, jobs.job_description, jobs.status,' 
        + 'userC.email FROM users userC  INNER JOIN jobs_creation ON userC.EMAIL = jobs_creation.CREATOR_ID inner '
        + 'JOIN jobs on jobs_creation.JOB_ID = jobs.JOB_ID INNER JOIN jobs_resolved on jobs.JOB_ID = jobs_resolved.JOB_ID ' 
        + 'INNER JOIN users userR on jobs_resolved.RESOLVER_ID = userR.EMAIL where userR.EMAIL = %s and jobs.STATUS = "Resolved"', [user_id])
        resolved_data = cur.fetchall()
        
        return render_template('technican.html', active_data = active_data, resolved_data = resolved_data)
    else:
        return "Access Denied"



@app.route('/admin', methods=['GET','SET'])
def admin():
    if session.get('user_id', None) != None and userStatus(session.get('user_id',None)) == 'Admin':
        user_id = session.get('user_id', None)
        cur = mysql.connection.cursor()
        cur.execute('SELECT users.NAME, users.job_count from users WHERE users.TYPE = "Technician"')
        tech_data = cur.fetchall()
        tech_count = [row[1] for row in tech_data]
        tech_names = [row[0] for row in tech_data]
        
        cur.execute('SELECT users.NAME, users.job_created from users WHERE users.TYPE = "Student"')
        student_data = cur.fetchall()
        student_count = [row[1] for row in student_data]
        student_names = [row[0] for row in student_data]

        cur.execute('SELECT WEEK(event_time), count(*) From jobs_resolved GROUP BY WEEK(event_time)')
        
        weekly_resolved_data = cur.fetchall()
        weekly_resolve_count = [row[1] for row in weekly_resolved_data]
        resolve_week_num = [row[0] for row in weekly_resolved_data]


        cur.execute('SELECT WEEK(event_time), count(*) From jobs_creation GROUP BY WEEK(event_time)')
        weekly_created_data = cur.fetchall()
        weekly_create_count = [row[1] for row in weekly_created_data]
        creation_week_num = [row[0] for row in weekly_created_data]

        
        return render_template('admin.html', tech_count = tech_count, tech_names = tech_names, 
        student_names = student_names, student_count = student_count,
        weekly_resolve_count = weekly_resolve_count, resolve_week_num = resolve_week_num,
        weekly_create_count = weekly_create_count, creation_week_num = creation_week_num,)
    else:
        return "Access Denied"





@app.route('/problem-creation', methods=['GET','POST'])
def problem_creation():
    if session.get('user_id', None) != None and userStatus(session.get('user_id',None)) == 'Student':
        user_id = session.get('user_id',None)
        if request.method == "POST":
            
            prob_title = request.form['problem_title']
            prob_desc = request.form['problem_description']
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO jobs(JOB_TITLE,JOB_DESCRIPTION) VALUES(%s,%s)',([prob_title],[prob_desc]))
            
            cur.execute('SELECT MAX(JOB_ID) FROM jobs')
            latest_id = cur.fetchone()
            print(latest_id, user_id)

            cur.execute('INSERT INTO jobs_creation(CREATOR_ID,JOB_ID, event_time) VALUES(%s,%s, curdate())',([user_id],latest_id))
            cur.execute("UPDATE users set users.job_created = users.job_created+1 where users.EMAIL =%s", [user_id])

            mysql.connection.commit()

            return redirect(url_for('student'))

        return render_template('problem-creation.html', user = user_id)
    else:
        return "Access Denied"




@app.route('/resolvejob/<string:id>', methods=['GET','POST'])
def resolvejob(id):
    job_id = id
    cur = mysql.connection.cursor()
    user_id = session.get('user_id', None) 
    cur.execute("Update jobs set jobs.STATUS = 'Resolved' where jobs.JOB_ID = %s", [job_id])
    cur.execute("UPDATE users set users.job_count = users.job_count+1 where users.EMAIL = %s", [user_id])
    cur.execute("INSERT INTO jobs_resolved(RESOLVER_ID,JOB_ID, event_time) VALUES(%s,%s,curdate())", ([user_id],[job_id]))
    mysql.connection.commit()
    return redirect(url_for('technican'))

@app.route('/logout', methods = ['GET','POST'])
def logout():
    session.pop('user_id',None)
    return redirect(url_for('login'))
    


def userStatus(id):
    cur = mysql.connection.cursor()
    cur.execute("Select users.TYPE from users where users.email =  %s", [id])
    status = cur.fetchone()
    return status[0]


if __name__ == "__main__":
    app.run(debug=True)