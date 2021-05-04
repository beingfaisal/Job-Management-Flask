from flask import Flask , render_template, request, redirect, url_for, flash,session
from flask_mysqldb import MySQL



app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'practicedb'
app.secret_key = 'abc'


mysql = MySQL(app)

@app.route('/', methods= ['GET','POST'])
@app.route('/login', methods= ['GET','POST'])
def login():
    if request.method == 'POST':
        log_email = request.form['log_email']
        log_pin = request.form['log_password']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE EMAIL = %s AND PIN = %s', ([log_email], [log_pin]))
        account = cur.fetchone()

        flash("HELOOO")
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
    if request.method == 'POST':
        reg_email = request.form['reg_email']
        reg_name = request.form['reg_name']
        reg_pin = request.form['reg_pin']
        reg_type = request.form.get('reg_type')
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO users(EMAIL,NAME,PIN,TYPE) VALUES(%s,%s,%s,%s)', ([reg_email], [reg_name],[reg_pin],[reg_type]))
        mysql.connection.commit()
        return "Success"

    return render_template('register.html')


@app.route('/student', methods=['GET','SET'])
def student():
    user_id = session.get('user_id', None)
    cur = mysql.connection.cursor()
    
    cur.execute('Select jobs.JOB_TITLE, jobs.JOB_DESCRIPTION FROM jobs INNER JOIN jobs_creation ON jobs.JOB_ID = jobs_creation.JOB_ID INNER join users on jobs_creation.CREATOR_ID = users.EMAIL WHERE users.EMAIL = %s', [user_id])
    data = cur.fetchall()
    return render_template('student.html', data = data)



@app.route('/technican', methods=['GET','SET'])
def technican():
    cur = mysql.connection.cursor()
    cur.execute('Select users.name, jobs.job_title, jobs.job_description, jobs.status, jobs.job_id from users inner join jobs_creation on users.email= jobs_creation.CREATOR_ID inner join jobs on jobs.job_id = jobs_creation.job_id where jobs.status = "Active"')
    data = cur.fetchall()
    

    user_id = session.get('user_id', None)
    return render_template('technican.html', data = data)



@app.route('/admin', methods=['GET','SET'])
def admin():
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
    
    return render_template('admin.html', tech_count = tech_count, tech_names = tech_names, student_names = student_names, student_count = student_count )



@app.route('/problem-creation', methods=['GET','POST'])
def problem_creation():
    user_id = session.get('user_id',None)
    if request.method == "POST":
        
        prob_title = request.form['problem_title']
        prob_desc = request.form['problem_description']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO JOBS(JOB_TITLE,JOB_DESCRIPTION) VALUES(%s,%s)',([prob_title],[prob_desc]))
        
        cur.execute('SELECT MAX(JOB_ID) FROM JOBS')
        latest_id = cur.fetchone()

        cur.execute('INSERT INTO JOBS_CREATION(CREATOR_ID,JOB_ID) VALUES(%s,%s)',([user_id],latest_id))
        cur.execute("UPDATE users set users.job_created = users.job_created+1 where users.EMAIL =%s", [user_id])

        mysql.connection.commit()

        return redirect(url_for('student'))

    return render_template('problem-creation.html', user = user_id)




@app.route('/resolvejob/<string:id>', methods=['GET','POST'])
def resolvejob(id):
    job_id = id
    cur = mysql.connection.cursor()
    user_id = session.get('user_id', None) 
    cur.execute("Update jobs set jobs.STATUS = 'Resolved' where jobs.JOB_ID = %s", [job_id])
    cur.execute("UPDATE users set users.job_count = users.job_count+1 where users.EMAIL = %s", [user_id])
    cur.execute("INSERT INTO jobs_resolved(RESOLVER_ID,JOB_ID) VALUES(%s,%s)", ([user_id],[job_id]))
    mysql.connection.commit()
    return redirect(url_for('technican'))
    


if __name__ == "__main__":
    app.run(debug=True)