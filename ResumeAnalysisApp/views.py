from django.shortcuts import render,redirect
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse , JsonResponse
from django.core.files.storage import FileSystemStorage
import datetime
import os
from datetime import date,datetime
import numpy as np
import matplotlib.pyplot as plt
from pyresparser import ResumeParser
import io , json , base64 , re

global uname, job_id
global admin_login_status
user_job_list = []
all_jobs_list = []

def checkUserLogin():
    global uname
    try:
        if not uname:  # Check if uname is empty or not set
            print("Not logged in - Please login first")
            return False  # Indicate login failure
    except NameError:  # Handle case where uname is not defined
        return False  
    return True  # Indicate login success

def checkadminloginstatus():
    global admin_login_status
    try:
        if not admin_login_status:  # Check if uname is empty or not set
            print("Not logged in - Please login first")
            return False  # Indicate login failure
    except NameError:  # Handle case where uname is not defined
        return False  
    return True  # Indicate login success

def AdminLogin(request):
    if request.method == 'GET':
       return render(request, 'AdminLogin.html', {})

def UserLogin(request):
    if request.method == 'GET':
       return render(request, 'UserLogin.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Signup(request):
    if request.method == 'GET':
       return render(request, 'Signup.html', {})

def Aboutus(request):
    if request.method == 'GET':
       return render(request, 'Aboutus.html', {})

def Feedback(request):
    if request.method == 'GET':
       return render(request, 'Feedback.html', {})
    

def EditJobs(request, job_id):

    global all_jobs_list
    all_jobs_list = []
    update_all_jobs_list()

    job_to_edit = None
    for job in all_jobs_list:
        if job['job_id'] == job_id:
            job_to_edit = job
            break

    if job_to_edit is None:
        return render(request, 'AdminScreen.html', {
            'Admin_name': "Administrator",
            'edit_job_status': False,
            'edit_job_status_message': "Job not found" + ' - Invalid request method',
            'Admin_jobs_List': all_jobs_list
        })
    
    all_skills = ["Access","C","C++","Cloud","CSS","Data analysis","Database","HTML","Java","JavaScript","Microsoft Word","OpenCV","Oracle","PHP","Python","Scrum","Shell","SQL","Technical"]


    return render(request, 'EditJobs.html', {
            'jobid': job_id,
            'job_title': job_to_edit['title'],
            'job_details': job_to_edit['description'],
            'company': job_to_edit['company'],
            'salary': job_to_edit['salary'],
            'skills': job_to_edit['skills_required'],
            'all_skills' : all_skills
        })

def SignupAction(request):
    Signup_status = False
    Signup_status_message = ''

    if request.method == 'POST':
        username = request.POST.get('t1', '').strip()
        password = request.POST.get('t2', '').strip()
        contact = request.POST.get('t3', '').strip()
        email = request.POST.get('t4', '').strip()
        address = request.POST.get('t5', '').strip()

        try:
            # Database connection
            with pymysql.connect(
                host='127.0.0.1', port=3306, user='root', password='root',
                database='resumeanalysis', charset='utf8'
            ) as con:
                with con.cursor() as cur:
                    # Check if username already exists
                    cur.execute("SELECT username FROM signup WHERE username = %s", (username,))
                    existing_user = cur.fetchone()

                    if existing_user:
                        Signup_status_message = "Given Username already exists."
                    else:
                        # Insert new user
                        signup_query = """
                            INSERT INTO signup (username, password, contact_no, email_id, address) 
                            VALUES (%s, %s, %s, %s, %s)
                        """
                        cur.execute(signup_query, (username, password, contact, email, address))
                        con.commit()

                        if cur.rowcount == 1:
                            Signup_status = True
                            Signup_status_message = "Your account has been created successfully."

        except pymysql.MySQLError as e:
            Signup_status_message = "There was an error creating your account. Please try again later." + f"Database Error: {e}"

        except Exception as e:
            Signup_status_message = "An unexpected error occurred. Please try again later." + f"Unexpected Error: {e}"

    context = {
        'Signup_status': Signup_status,
        'Signup_status_message': Signup_status_message
    }
    return render(request, 'Signup.html', context)

def UserLoginAction(request):
    if request.method == 'POST':
        global uname
        option = 0
        username = request.POST.get('username', False).strip()
        password = request.POST.get('password', False)
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'resumeanalysis',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM signup")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and row[1] == password:
                    uname = username
                    option = 1
                    break
        if option == 1:
            return redirect('UserDashboard')
        else:
            context= {'data':'Invalid login details'}
            return render(request, 'UserLogin.html', context)

def AdminLoginAction(request):
    if request.method == 'POST':
        global uname , admin_login_status
        username = request.POST.get('username', False).strip()
        password = request.POST.get('password', False).strip()
        if username == "admin" and password == "admin":
            admin_login_status = True
            return redirect('AdminDashboard')
        else:
            context= {'data':'Invalid login details'}
            return render(request, 'AdminLogin.html', context)          


def PostJobs(request):
    if not checkadminloginstatus():
        return redirect('AdminLogin')
    if request.method == 'GET':
       return render(request, 'PostJobs.html', {})

def Feedback(request):
    if request.method == 'GET':
        return render(request, 'Feedback.html', {})

def Aboutus(request):
    if request.method == 'GET':
        return render(request, 'Aboutus.html', {})     

def FeedbackAction(request):
    Feedback_status = False
    Feedback_status_message = ''

    global uname
    if request.method == 'POST':
        try:

            if not checkUserLogin():
                uname = "Anonymous"
                
            Feedback_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            feedback = request.POST.get('t1', '').strip()
            rank = request.POST.get('t2', '').strip()

            # Database Connection
            with pymysql.connect(
                host='127.0.0.1', port=3306, user='root', password='root',
                database='resumeanalysis', charset='utf8'
            ) as db_connection:
                with db_connection.cursor() as db_cursor:
                    # student_sql_query = """
                    #     INSERT INTO feedback (username, feedback, feedback_date, feedback_rank)
                    #     VALUES (%s, %s, %s, %s)
                    # """
                    student_sql_query = f"INSERT INTO feedback (username, feedback, feedback_date, feedback_rank) VALUES ('{uname}', '{feedback}', '{Feedback_date}', {rank})"
                    db_cursor.execute(student_sql_query)
                    db_connection.commit()

                    if db_cursor.rowcount == 1:
                        Feedback_status = True
                        Feedback_status_message = 'Your feedback has been accepted. The admin will review and get back to you.'

        except pymysql.MySQLError as e:
            print(f"Database Error: {e}")
            Feedback_status_message = 'There was an error posting your feedback. Please try again later.'

        except Exception as e:
            print(f"Unexpected Error: {e}")
            Feedback_status_message = 'An unexpected error occurred. Please try again later.'

    context = {
        'Feedback_status': Feedback_status,
        'Feedback_status_message': Feedback_status_message
    }
    return render(request, 'Feedback.html', context) 

def PostJobsAction(request):
    error_message = "There was an error posting your job. Please try again later."
    
    if not checkadminloginstatus():
        return redirect('AdminLogin')

    PostJobs_status = False
    PostJobs_status_message = error_message

    if request.method == 'POST':
        try:
            job = request.POST.get('t1', '').strip()
            details = request.POST.get('t2', '').strip()
            company = request.POST.get('t3', '').strip()
            salary = request.POST.get('t4', '').strip()
            skills = request.POST.getlist('t5')
            skills = ','.join(skills)
            today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            job_id = 0

            # Database Connection
            con = pymysql.connect(
                host='127.0.0.1', port=3306, user='root', password='root',
                database='resumeanalysis', charset='utf8'
            )
            with con.cursor() as cur:
                cur.execute("SELECT COUNT(job_id) FROM postjob")
                job_id = cur.fetchone()[0] + 1

            # Insert Job Posting
            with pymysql.connect(
                host='127.0.0.1', port=3306, user='root', password='root',
                database='resumeanalysis', charset='utf8'
            ) as db_connection:
                with db_connection.cursor() as db_cursor:
                    student_sql_query = """
                        INSERT INTO postjob (job_id, job_name, job_details, skills, post_date, company_name, salary)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    db_cursor.execute(student_sql_query, (job_id, job, details, skills, today, company, salary))
                    db_connection.commit()

                    if db_cursor.rowcount == 1:
                        PostJobs_status = True
                        PostJobs_status_message = f'Your job was posted successfully... You can see your {job} job in the dashboard.'

        except pymysql.MySQLError as e:
            PostJobs_status_message = error_message + f"Database Error: {e}"
        except Exception as e:
            PostJobs_status_message = error_message + f"Unexpected Error: {e}"

    context = {
        'PostJobs_status': PostJobs_status,
        'PostJobs_status_message': PostJobs_status_message
    }
    return render(request, 'PostJobs.html', context)      

def EditJobsAction(request, job_id):

    global all_jobs_list
    if not checkadminloginstatus():
        return redirect('AdminLogin')

    EditJobs_status = False
    EditJobs_status_message = ""
    job_data = None

    if request.method == 'POST':
        try:
            job = request.POST.get('t1', '').strip()
            details = request.POST.get('t2', '').strip()
            company = request.POST.get('t3', '').strip()
            salary = request.POST.get('t4', '').strip()
            skills = request.POST.getlist('t5')
            skills = ','.join(skills)
            today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with pymysql.connect(
                host='127.0.0.1', port=3306, user='root', password='root',
                database='resumeanalysis', charset='utf8'
            ) as db_connection:
                with db_connection.cursor() as db_cursor:
                    student_sql_query = """
                        UPDATE postjob
                        SET job_name = %s, job_details = %s, skills = %s, post_date = %s, company_name = %s, salary = %s
                        WHERE job_id = %s
                    """
                    db_cursor.execute(student_sql_query, (job, details, skills, today, company, salary, job_id))
                    db_connection.commit()

                    if db_cursor.rowcount == 1:
                        EditJobs_status = True
                        EditJobs_status_message = f'Your job was updated successfully... You can see the updated {job} job in the dashboard.'
                    elif db_cursor.rowcount == 0:
                        EditJobs_status_message = "No job was updated. Please check the job ID."
                    else:
                        EditJobs_status_message = "Multiple jobs were updated. This should not happen."

        except pymysql.MySQLError as e:
            EditJobs_status_message = f"Database Error: {e}"
        except Exception as e:
            EditJobs_status_message = f"Unexpected Error: {e}"

        if EditJobs_status:
            all_jobs_list = []
            update_all_jobs_list()
            return render(request, 'AdminScreen.html', {'Admin_name': "Administrator", 'Admin_jobs_List': all_jobs_list, 'EditJobs_status': True, 'EditJobs_status_message': EditJobs_status_message})

    # GET request or POST with errors: Fetch job data and render form
    try:
        with pymysql.connect(
            host='127.0.0.1', port=3306, user='root', password='root',
            database='resumeanalysis', charset='utf8'
        ) as db_connection:
            with db_connection.cursor(pymysql.cursors.DictCursor) as db_cursor:
                db_cursor.execute("SELECT * FROM postjob WHERE job_id = %s", (job_id,))
                job_data = db_cursor.fetchone()

                if not job_data:
                    EditJobs_status_message = "Job not found."
                    return render(request, 'AdminScreen.html', {'Admin_name': "Administrator", 'Admin_jobs_List': all_jobs_list, 'EditJobs_status': False, 'EditJobs_status_message': EditJobs_status_message})

                if job_data['skills']:
                    job_data['skills'] = job_data['skills'].split(',')
                else:
                    job_data['skills'] = []

    except pymysql.MySQLError as e:
        EditJobs_status_message = f"Database Error: {e}"
        job_data = None
    except Exception as e:
        EditJobs_status_message = f"Unexpected Error: {e}"
        job_data = None

    context = {
        'Admin_name': "Administrator",
        'Admin_jobs_List': all_jobs_list,
        'EditJobs_status': EditJobs_status,
        'EditJobs_status_message': EditJobs_status_message,
        'job_data': job_data,
    }

    return render(request, 'AdminScreen.html', context)

def ViewFeedback(request):
    if request.method == 'GET':
        Feedback_list = []
        rank = []
        con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='resumeanalysis', charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username,feedback,feedback_rank,feedback_date FROM feedback ORDER BY feedback_rank DESC")
            rows = cur.fetchall()
            for row in rows:
                Feedback_list.append({
                'username': row[0],
                'feedback_text': row[1],
                'feedback_rank': row[2],
                'feedback_date' : row[3]
                })
                rank.append(row[2])

        unique, count = np.unique(np.asarray(rank), return_counts=True)
        plt.figure(figsize=(6, 6))  # Create a new figure
        plt.pie(count, labels=unique, autopct='%1.1f%%')
        plt.title('Feedback Ranking Graph')
        plt.axis('equal')

        # Save the plot to a BytesIO object
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        # Encode the image to base64
        graphic = base64.b64encode(image_png).decode('utf-8')
        img_data = f'data:image/png;base64,{graphic}'

        context = {'Feedback_list': Feedback_list, 'chart': img_data}
        return render(request, 'ViewFeedback.html', context)
    
def UserDashboard(request):

    if not checkUserLogin():
        return redirect('UserLogin')
    
    global uname, user_job_list
    
    update_all_jobs_list()
    update_user_job_list()  # Update user_job_list whenever UserDashboard is accessed
    return render(request, 'UserScreen.html', {'C_username': uname, 'User_jobs': user_job_list})    

def AdminDashboard(request):

    if not checkadminloginstatus():
        return redirect('AdminLogin')
    
    global all_jobs_list
    update_all_jobs_list()

    return render(request, 'AdminScreen.html', {'Admin_name': "Administrator", 'Admin_jobs_List': all_jobs_list})    
              
def update_user_job_list():
    """Function to refresh the global user_job_list. Called whenever UserDashboard is accessed"""
    global user_job_list, uname
    user_job_list = [] # Clear previous job_list

    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'resumeanalysis',charset='utf8')
    with con:
        cur = con.cursor()
        job_query = f"SELECT p.job_name, p.job_details, p.company_name, p.skills , u.resume_score  , p.job_id , p.salary , u.selected , u.upload_date FROM postjob p JOIN upload_resume u ON p.job_id = u.job_id WHERE u.username = \"{uname}\" ORDER BY u.upload_date DESC"
        cur.execute(job_query)
        applied_jobs = cur.fetchall()
        for job in applied_jobs:
            skills_string = job[3]
            skills_list = [skill.strip() for skill in skills_string.split(',')] if skills_string else []
            job_logo_name = skills_list[0] if skills_list else "default"
            job_logo_name = job_logo_name + ".png"
            user_job_list.append({
                'title': job[0],
                'description': job[1],
                'company': job[2],
                'skills_required': job[3],
                'resume_score' : job[4],
                'job_id': job[5],
                'salary' : job[6],
                'job_logo_name': job_logo_name,
                'selected': job[7] if job[7] is not None else -1,
                'applied_date': job[8]
                })
        print(user_job_list)
            
def update_all_jobs_list():
    """Function to refresh the global all_jobs_list posted """
    global all_jobs_list
    all_jobs_list = [] # Clear previous job_list

    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'resumeanalysis',charset='utf8')
    with con:
        cur = con.cursor()
        query = "SELECT p.job_id, p.job_name, p.job_details, p.company_name, p.skills, p.post_date, p.salary, COALESCE(u.resume_count, 0) AS resume_count FROM postjob p LEFT JOIN ( SELECT job_id, COUNT(job_id) AS resume_count FROM upload_resume GROUP BY job_id ) u ON p.job_id = u.job_id ORDER BY resume_count DESC, p.post_date DESC"
        cur.execute(query)
        applied_jobs = cur.fetchall()
        for job in applied_jobs:

            skills_string = job[4]
            skills_list = [skill.strip() for skill in skills_string.split(',')] if skills_string else []

            cur.execute(f"SELECT COUNT(*) FROM upload_resume WHERE job_id = {job[0]} AND selected = 1")
            NumberOfSelected = cur.fetchone()[0]

            cur.execute(f"SELECT COUNT(*) FROM upload_resume WHERE job_id = {job[0]} AND selected = 0")
            NumberOfRejected = cur.fetchone()[0]

            job_logo_name = skills_list[0] if skills_list else "default"
            job_logo_name = job_logo_name + ".png"
            all_jobs_list.append({
                'job_id': job[0],
                'title': job[1],
                'description': job[2],
                'company' : job[3],
                'skills_required': job[4],
                'post_date' : job[5],
                'salary' : job[6],
                'NumberOfApplied': job[7],
                'NumberOfNew': job[7]-NumberOfSelected-NumberOfRejected,
                'NumberOfSelected': NumberOfSelected,
                'NumberOfRejected': NumberOfRejected,
                'job_logo_name': job_logo_name
                })

def getScore(job_id, skills):
    require_skills = None
    score = 0
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'resumeanalysis',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select skills FROM postjob where job_id='"+job_id+"'")
        rows = cur.fetchall()
        for row in rows:
            require_skills = row[0]
    require_skills = require_skills.strip().split(",")
    for i in range(len(skills)):
        skills[i] = skills[i].lower().strip()
    for i in range(len(require_skills)):
        require_skills[i] = require_skills[i].lower()
    print(require_skills)    
    found_skills = [x for x in skills if x in require_skills]
    if len(found_skills) > 0:
        if len(found_skills) >= len(require_skills):
            score = 100
        else:
            score = len(found_skills) / len(require_skills)
            score = score * 100
    return round(score)
    

    

def UploadResumeAction(request):
    error_message = "There was an error uploading your resume. Please try again later."
    if request.method != 'POST':
        return render(request, 'UploadResume.html', {'resume_upload_status': False, 'resume_upload_status_message': error_message +' - Invalid request method'})
    
    if not checkUserLogin():
        return redirect('UserLogin')
    
    global uname
    resume_upload_status = False

    try:
        job_id = request.POST.get('t1', False)
        myfile = request.FILES['t2']
        if not job_id:
            return render(request, 'UploadResume.html', {'resume_upload_status': False, 'resume_upload_status_message': error_message + ' - Job ID is missing'})

        if not myfile:
            return render(request, 'UploadResume.html', {'resume_upload_status': False, 'resume_upload_status_message': error_message + ' - Resume file is missing'})

        fname = request.FILES['t2'].name
        upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        fs = FileSystemStorage()
        filename = fs.save('ResumeAnalysisApp/static/resumes/'+fname, myfile)

        try: 
            data = ResumeParser('ResumeAnalysisApp/static/resumes/'+fname).get_extracted_data()
            if not data or 'skills' not in data:
                return render(request, 'UploadResume.html', {'resume_upload_status': False, 'resume_upload_status_message': error_message + ' - Failed to extract data from resume'})
        except Exception as e:
            return render(request, 'UploadResume.html', {'resume_upload_status': False, 'resume_upload_status_message': error_message + f' - Resume parsing error: {str(e)}'})
        
        skills = data['skills']
        score = getScore(job_id, skills)
         # Convert data to JSON string
        # json_data = json.dumps(data)
        try:
            json_data = json.dumps(data)
            json_data = re.sub(r'[\x00-\x1F\x7F]', '', json_data)  # Remove all control characters
            json_data = json_data.replace("\u2022", "- ")  # Bullet points
            json_data = json_data.replace("\u2019", "'")   # Curly apostrophe
            json_data = json_data.replace("\n", " ")       # Remove unexpected newlines

        except Exception as e:
            print(f"Error in json_data processing: {e}")
            json_data = "{}"  # Return empty JSON in case of an error

        # Database connection
        try:
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'resumeanalysis',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO upload_resume(job_id,username,resume_name,upload_date,resume_json,resume_score) VALUES('"+str(job_id)+"','"+uname+"','"+fname+"','"+str(upload_date)+"','"+str(json_data)+"','"+str(score)+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
        except pymysql.Error as db_err:
            return render(request, 'UploadResume.html', {'resume_upload_status': False, 'resume_upload_status_message': error_message + f' - Database error: {str(db_err)}'})

        print(db_cursor.rowcount, "Record Inserted")

        if db_cursor.rowcount == 1:
            status_message = "Your resume has been uploaded, and we will get in touch with you."
            resume_upload_status = True
        else:
            return render(request, 'UploadResume.html', {'resume_upload_status': False, 'resume_upload_status_message': error_message + ' - Database insertion failed'})
    except Exception as e:
        return render(request, 'UploadResume.html', {'resume_upload_status': False, 'resume_upload_status_message': error_message + f' - Unexpected error: {str(e)}'})

    context = {'user_resume_score': score, 'resume_upload_status': resume_upload_status, 'resume_upload_status_message': status_message}
    return render(request, 'UploadResume.html', context)
        
def DeleteJobAction(request):
    error_message = "There was an error deleting the job. Please try again later."
    # Check if the admin is logged in
    if not checkadminloginstatus():
        return redirect('AdminLogin')
    global all_jobs_list
    if request.method != 'GET':
        return render(request, 'AdminScreen.html', {
            'Admin_name': "Administrator",
            'delete_job_status': False,
            'delete_job_status_message': error_message + ' - Invalid request method',
            'Admin_jobs_List': all_jobs_list
        })
    delete_job_status = False

    try:
    
        job_id = request.GET.get('jobid')
        job_name = request.GET.get('jobTitle')
    
        if not job_id:
        
            return render(request, 'AdminScreen.html', {
                'Admin_name': "Administrator",
                'delete_job_status': False,
                'delete_job_status_message': error_message + ' - Job ID is missing',
                'Admin_jobs_List': all_jobs_list
            })
    
        # Database connection
        try:
        
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='resumeanalysis', charset='utf8')
            cur = con.cursor()
        
            # Use a parameterized query to prevent SQL injection
            cur.execute(f"DELETE FROM postjob WHERE job_id = {job_id}")
            con.commit()

            if cur.rowcount == 1:
                delete_job_status = True
                status_message = f"the job {job_name} has been deleted successfully."
            
            else:
                all_jobs_list = []         
                update_all_jobs_list()   

                return render(request, 'AdminScreen.html', {
                    'Admin_name': "Administrator",
                    'delete_job_status': False,
                    'delete_job_status_message': error_message + ' - Job not found or already deleted',
                    'Admin_jobs_List': all_jobs_list
                })
        
        except pymysql.Error as db_err:       
            return render(request, 'AdminScreen.html', {
                'Admin_name': "Administrator",
                'delete_job_status': False,
                'delete_job_status_message': error_message + f' - Database error: {str(db_err)}',
                'Admin_jobs_List': all_jobs_list
            })
        finally:       
            con.close()
        
        # Update job lists    
        all_jobs_list = []
        update_all_jobs_list()
    
    except Exception as e:
        return render(request, 'AdminScreen.html', {
            'Admin_name': "Administrator",
            'delete_job_status': False,
            'delete_job_status_message': error_message + f' - Unexpected error: {str(e)}',
            'Admin_jobs_List': all_jobs_list
        })

    return render(request, 'AdminScreen.html', {
        'Admin_name': "Administrator",
        'delete_job_status': delete_job_status,
        'delete_job_status_message': status_message,
        'Admin_jobs_List': all_jobs_list
    })



def UploadResume(request):
    global all_jobs_list
    all_jobs_list = []
    update_all_jobs_list()

    if request.method == 'GET':
        job_id = request.GET.get('t1', False)
        print(job_id)
        job_Name = request.GET.get('title', False)
        job_description = next(
            (job['description'] for job in all_jobs_list if str(job['job_id']) == job_id), 
            "Description not available"
        )
        output = '<tr><td><font size="" color="black">Job&nbsp;ID</b></td><td><input type="text" name="t1" style="font-family: Comic Sans MS" size="30" value="'+job_id+'" readonly/></td></tr>'
        print("hit: "+job_description)
        context= {'data':output, 'job_title':job_Name ,'job_description': job_description }
        return render(request, 'UploadResume.html', context)

def ViewJobs(request):
    if not checkUserLogin():
        return redirect('UserLogin')
    global all_jobs_list , user_job_list
    all_jobs_list = []
    user_job_list = []
    update_all_jobs_list() 
    update_user_job_list()
    applied_job_ids = {job['job_id'] for job in user_job_list}  # Set for faster lookup
    user_available_jobs = [job for job in all_jobs_list if job['job_id'] not in applied_job_ids]
    if request.method == 'GET':
        context= { 'Available_jobs':user_available_jobs}
        return render(request, 'UserScreen.html', context)
    
# def ViewScore(request): 
#     if not checkadminloginstatus():
#         return redirect('AdminLogin')
#     if request.method == 'GET':

#         output = '<table border=1><tr><th><font size="" color=black>Job ID</font></th>'
#         output+='<td><font size="" color="black">Username</td>'
#         output+='<td><font size="" color="black">Resume Name</td>'
#         output+='<td><font size="" color="black">Upload Date</td>'
#         output+='<td><font size="" color="black">Resume JSON Data</td>'
#         output+='<td><font size="" color="black">Resume Score</td></tr>'
#         rank = []
#         con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'resumeanalysis',charset='utf8')
#         with con:
#             cur = con.cursor()
#             cur.execute("select * FROM upload_resume")
#             rows = cur.fetchall()
#             for row in rows:
#                 output+='<tr><td><font size="" color="black">'+str(row[0])+'</td>'
#                 output+='<td><font size="" color="black">'+str(row[1])+'</td>'
#                 output+='<td><font size="" color="black">'+str(row[2])+'</td>'
#                 output+='<td><font size="" color="black">'+str(row[3])+'</td>'
#                 output+='<td><font size="" color="black">'+str(row[4])+'</td>'
#                 output+='<td><font size="" color="black">'+str(row[5])+'</td></tr>'                
#         output += "</table><br/><br/><br/>"
#         context= {'data': output}
#         return render(request, 'ViewScore.html', context)


def ViewScore(request):
    if not checkadminloginstatus():
        return redirect('AdminLogin')

    applicants = []
    message = ""
    success_message = ""
    text = ""
    selectednumber = None
    count_selected_null = 0  # Count where selected is NULL
    count_selected_0 = 0  # Count where selected is 0
    count_selected_1 = 0  # Count where selected is 1

    try:
        # Get query parameters
        job_id = request.GET.get('jobid', None)
        job_title = request.GET.get('jobTitle', None)
        selected = request.GET.get('selected', None)

        # Establish database connection
        con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', 
                              database='resumeanalysis', charset='utf8')
        with con.cursor() as cur:
            # Construct base query with JOIN
            query = """
                SELECT r.job_id, r.username, s.contact_no, s.email_id, r.resume_name, 
                       r.upload_date, r.selected, r.resume_json, r.resume_score 
                FROM upload_resume r 
                LEFT JOIN signup s ON r.username = s.username
            """
            params = []
            
            # Apply filters
            if job_id is not None:
                query += " WHERE r.job_id = %s"
                params.append(job_id)

                if selected is not None:
                    if selected == 'None':
                        text = "New"
                        selectednumber = None
                        query += " AND r.selected IS NULL"
                    elif selected in ['0', '1']:
                        selectednumber = int(selected)
                        print("hit: ",selectednumber)
                        text = "Selected" if selected == '1' else "Rejected"
                        query += " AND r.selected = %s"
                        params.append(selected)

            query += " ORDER BY r.upload_date ASC"  # Sorting by earliest application first

            # Execute the query
            cur.execute(query, params)
            rows = cur.fetchall()

            # Process results
            if rows:
                for row in rows:
                    selected_status = "Under Review"
                    selectednumber_res = -1;
                    resume_json = json.loads(row[7])
                    # print("hit: ",resume_json)

                    if row[6] is not None:
                        selectednumber_res = row[6] 
                        selected_status = "Selected" if row[6] == 1 else "Rejected"
                    applicants.append({
                        "job_id": row[0],
                        "job_name":job_title,
                        "username": row[1],
                        "contact_no": row[2] if row[2] else "N/A",
                        "email_id": row[3] if row[3] else "N/A",
                        "resume_name": row[4],
                        "upload_date": row[5],
                        "selected": selected_status,
                        "selected_number": selectednumber_res,
                        "resume_json": resume_json,
                        "resume_score": row[8]
                    })
                success_message = f"Successfully retrieved {len(applicants)} applications for  {job_title} job."
            else:
                message = f"No {text} applications found for {job_title} job."

            # Count applicants based on selected status for the given job_id
            if job_id:
                count_query = """
                    SELECT 
                        SUM(CASE WHEN selected IS NULL THEN 1 ELSE 0 END) AS count_null,
                        SUM(CASE WHEN selected = 0 THEN 1 ELSE 0 END) AS count_0,
                        SUM(CASE WHEN selected = 1 THEN 1 ELSE 0 END) AS count_1
                    FROM upload_resume WHERE job_id = %s
                """
                cur.execute(count_query, (job_id,))
                result = cur.fetchone()
                count_selected_null, count_selected_0, count_selected_1 = result

    except Exception as e:
        message = f"An error occurred: {str(e)}"

    finally:
        if con:
            con.close()

    # Context data for rendering
    context = {
        'job_id': job_id,
        'job_title': job_title,
        'applicants': applicants,
        'message': message,
        'success_message': success_message,
        'selected': selectednumber,
        'count_selected_null': count_selected_null,
        'count_selected_0': count_selected_0,
        'count_selected_1': count_selected_1
    }
    return render(request, 'ViewScore.html', context)

def AllViewScore(request):
    if not checkadminloginstatus():
        return redirect('AdminLogin')

    applicants = []
    message = ""
    success_message = ""
    selectednumber = None

    try:
        selected = request.GET.get('selected', None)

        con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root',
                              database='resumeanalysis', charset='utf8')
        with con.cursor() as cur:
            query = """
                SELECT r.job_id, r.username, s.contact_no, s.email_id, r.resume_name, 
                       r.upload_date, r.selected, r.resume_json, r.resume_score, p.job_name 
                FROM upload_resume r 
                LEFT JOIN signup s ON r.username = s.username
                LEFT JOIN postjob p ON r.job_id = p.job_id
            """
            params = []
            where_clause = []

            if selected is not None:
                if selected == 'None':
                    text = "New"
                    selectednumber = None
                    where_clause.append("r.selected IS NULL")
                elif selected in ['0', '1']:
                    selectednumber = int(selected)
                    text = "Selected" if selected == '1' else "Rejected"
                    where_clause.append("r.selected = %s")
                    params.append(selected)

            if where_clause:
                query += " WHERE " + " AND ".join(where_clause)

            query += " ORDER BY r.upload_date ASC"

            cur.execute(query, params)
            rows = cur.fetchall()

            if rows:
                for row in rows:
                    selected_status = "Under Review"
                    selectednumber_res = -1
                    
                    resume_json = json.loads(row[7])
                    if row[6] is not None:
                        selectednumber_res = row[6]
                        selected_status = "Selected" if row[6] == 1 else "Rejected"

                    applicants.append({
                        "job_id": row[0],
                        "job_name": row[9],
                        "username": row[1],
                        "contact_no": row[2] if row[2] else "N/A",
                        "email_id": row[3] if row[3] else "N/A",
                        "resume_name": row[4],
                        "upload_date": row[5],
                        "selected": selected_status,
                        "selected_number": selectednumber_res,
                        "resume_json": resume_json,
                        "resume_score": row[8]
                    })

                if selected is not None:
                    if selected == 'None':
                        success_message = f"Successfully retrieved {len(applicants)} new applications."
                    elif selected == '0':
                        success_message = f"Successfully retrieved {len(applicants)} rejected applications."
                    elif selected == '1':
                        success_message = f"Successfully retrieved {len(applicants)} selected applications."
                else:
                    success_message = f"Successfully retrieved All {len(applicants)} applications."
            else:
                if selected is not None:
                    if selected == 'None':
                        message = f"No new applications found."
                    elif selected == '0':
                        message = f"No rejected applications found."
                    elif selected == '1':
                        message = f"No selected applications found."
                else:
                    message = f"No applications found."

    except Exception as e:
        message = f"An error occurred: {str(e)}"

    finally:
        if con:
            con.close()

    context = {
        'type': 'All',
        'applicants': applicants,
        'message': message,
        'success_message': success_message,
        'selected': selectednumber,
    }
    return render(request, 'ViewScore.html', context)

def MakeSelected(request):
    if not checkadminloginstatus():
        return redirect('AdminLogin')
    
    username = request.GET.get('username', None)
    job_id = request.GET.get('job_id', None)
    MakeSelected_statues = False

    if username and job_id:
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', 
                                  database='resumeanalysis', charset='utf8')
            with con.cursor() as cur:
                cur.execute("UPDATE upload_resume SET selected = 1 WHERE username = %s AND job_id = %s", (username, job_id))
                con.commit()
                makeSelected_statues = True
                message = f"Successfully selected {username} for {job_id} job."

        except Exception as e:
            message = f"An error occurred: {str(e)}"
        finally:
            if con:
                con.close()
    else:
        message = "Invalid username or job_id provided."

    return JsonResponse({ 'action': 'Selected', 'makeSelected_statues': makeSelected_statues, 'message': message})


def MakeRejected(request):
    if not checkadminloginstatus():
        return redirect('AdminLogin')
    
    username = request.GET.get('username', None)
    job_id = request.GET.get('job_id', None)
    MakeRejected_statues = False

    if username and job_id:
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', 
                                  database='resumeanalysis', charset='utf8')
            with con.cursor() as cur:
                cur.execute("UPDATE upload_resume SET selected = 0 WHERE username = %s AND job_id = %s", (username, job_id))
                con.commit()
                MakeRejected_statues = True
                message = f"Successfully rejected {username} for {job_id} job."

        except Exception as e:
            message = f"An error occurred: {str(e)}"
        finally:
            if con:
                con.close()
    else:
        message = "Invalid username or job_id provided."

    return JsonResponse({ 'action': 'Rejected', 'MakeRejected_statues': MakeRejected_statues, 'message': message})
