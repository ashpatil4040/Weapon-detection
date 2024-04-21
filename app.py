import os
import sqlite3
import time

import cv2
from flask import Flask, render_template, Response, request, send_file

import deploy_model
from create_database import create_database_here

picFolder = os.path.join('static')
app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = picFolder
urll = ""

current_email=''
otp=''
create_database_here()


@app.route('/')
def index():
    close_video()
    return render_template("index.html")


@app.route('/addnewcam')
def addnewcam():
    close_video()
    return render_template("addnewcam.html")


@app.route('/addnewcam2', methods=['POST'])
def addnewcam2():
    close_video()
    protocol = request.form.get('protocol')
    ip_address = request.form.get('ip_address')
    username = request.form.get('username')
    cam_name = request.form.get('cam_name')
    password = request.form.get('password')
    conn=sqlite3.connect('WeaponDetection.db')
    cursor=conn.cursor()
    sql_command = "INSERT INTO camera VALUES(?,?,?,?,?,?)"
    rec = (current_email,protocol,ip_address,username,cam_name,password)
    cursor.execute(sql_command,rec)
    conn.commit()
    conn.close()
    return render_template("addnewcam.html")


#cap = cv2.VideoCapture(0)
obj = deploy_model.ObjectDetection('video.mp4')
cap = ''


def get_video_stream():
    global urll
    #cap = cv2.VideoCapture(urll)
    global cap
    previous_time=time.time()-30
    while cap.isOpened():
        ret, frames = cap.read()

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
        frames, previous_time = obj.ex(frames,previous_time,current_email,current_camera_username)
        ret, buffer = cv2.imencode('.jpg', frames)
        frames = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frames + b'\r\n')


def close_video():
    global cap
    if cap:
        cap.release()
        cv2.destroyAllWindows()


@app.route("/video_feed")
def video_feed():
    return Response(get_video_stream(),mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/video_feed2")
def video_feed2():
    return Response(get_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/Adminlogin")
def Adminlogin():
    close_video()
    return render_template('Adminlogin.html')


@app.route("/Adminhistory")
def Adminhistory():
    close_video()
    conn = sqlite3.connect('WeaponDetection.db')
    cursor = conn.cursor()
    sqlcommand = "SELECT client_email,date ,time,camera_username, pic_path FROM history"
    cursor.execute(sqlcommand)
    res = cursor.fetchall()
    conn.commit()
    conn.close()
    return render_template('Adminhistory.html',data=res)


@app.route("/video_cam_list")
def video_cam_list():
    close_video()
    global current_email
    conn = sqlite3.connect('WeaponDetection.db')
    cursor = conn.cursor()
    sql_command = f"SELECT camera_name,camera_username FROM camera WHERE client_email=\'"+current_email+"\';"
    cursor.execute(sql_command)
    res = cursor.fetchall()
    conn.commit()
    conn.close()
    return render_template('video_cam_list.html', cam_daata=res)


def video_go_to(cam_username=None):
    print('video_go_to')
    return render_template('video.html', cam_u=cam_username)


@app.route("/clientHistory")
def clientHistory():
    close_video()
    conn = sqlite3.connect('WeaponDetection.db')
    cursor = conn.cursor()
    sqlcommand = "SELECT date ,time,camera_username, pic_path FROM history WHERE client_email=\'"+current_email+"\';"
    cursor.execute(sqlcommand)
    res = cursor.fetchall()
    conn.commit()
    conn.close()
    return render_template('clientHistory.html', data=res)


def client_login():
    print("hi")


@app.route("/login")
def login():
    close_video()
    global current_email
    current_email = ''
    return render_template("login.html", vake='client')


@app.route("/index")
def index2():
    close_video()
    return render_template("index.html")


@app.route("/SignUp")
def SignUp():
    close_video()
    return render_template("SignUp.html",vake='client')


@app.route("/client_newpass" , methods=['POST'])
def client_newpass():
    close_video()
    otp_enter = request.form.get('otp')
    if not otp_enter:
        return render_template("otp.html", vake='client')
    global otp
    if otp==otp_enter:
        return render_template("newpass.html",vake='client')
    else:
        return render_template("otp.html", vake='client')


@app.route("/client_dashboard")
def client_dashboard1():
    close_video()
    return render_template("client_dashboard.html")


@app.route("/client_forgotpass")
def client_forgotpass():
    close_video()
    return render_template("forgotpass.html",vake='client')


@app.route('/client_dashboard', methods=['POST'])
def client_dashboard():
    close_video()
    text = request.form.get('email')
    password = request.form.get('password')
    conn = sqlite3.connect('WeaponDetection.db')
    cursor = conn.cursor()
    sql_command = f"SELECT client_password FROM client WHERE client_email= \'" + text + "\';"
    cursor.execute(sql_command)
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    global current_email
    current_email = text
    if not password:
        return render_template('login.html', vake='client')
    if result[0] == password:
        return render_template('client_dashboard.html')
    else:
        return render_template('login.html',vake='client')


@app.route('/admin_dashboard', methods=['POST'])
def admin_dashboard():
    close_video()
    text = request.form.get('email')
    password = request.form.get('password')
    conn = sqlite3.connect('WeaponDetection.db')
    cursor = conn.cursor()
    sql_command = f"SELECT server_password FROM server WHERE server_email= \'" + text + "\';"
    cursor.execute(sql_command)
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    global current_email
    current_email = text
    if not password:
        return render_template('Adminlogin.html', vake='admin')
    if result[0] == password:
        return render_template('admin_dashboard.html')
    else:
        return render_template('Adminlogin.html', vake='admin')


@app.route('/video', methods=['POST'])
def video():
    close_video()
    set_up_video(request.form['button1'])
    return render_template('video.html',val=request.form['button1'])


current_camera_username = ""
def set_up_video(user_name):
    global urll
    global current_camera_username
    if user_name=='0':
        urll = 0
        current_camera_username = '0'
    else:
        conn = sqlite3.connect('WeaponDetection.db')
        cursor = conn.cursor()
        sql = f"SELECT camera_username,password,camera_ip,camera_protocol FROM camera WHERE camera_username=\'"+user_name+"\';"
        cursor.execute(sql)
        res = cursor.fetchall()
        conn.commit()
        conn.close()
        urll = f'{res[0][3]}://{res[0][0]}:{res[0][1]}@{res[0][2]}'
        current_camera_username = res[0][3]
    global cap
    cap = cv2.VideoCapture(urll)


@app.route('/login', methods=['POST'])
def register():
    close_video()
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    if password2 == password:
        conn = sqlite3.connect('WeaponDetection.db')
        cursor = conn.cursor()
        sql_command = " INSERT INTO client (client_name,client_email,client_password) VALUES (?,?,?)"
        record = (name,email,password)
        cursor.execute(sql_command,record)
        conn.commit()
        conn.close()
        return render_template('login.html')
    else:
        return render_template('SignUp.html')


@app.route('/client_otp', methods=['POST'])
def client_otp():
    close_video()
    email = request.form.get('email')
    if not email:
        return render_template('forgotpass.html', vake='client')
    global current_email
    current_email = email
    import smtplib
    import random
    gmail_user = 'weapondetection4@gmail.com'
    gmail_password = 'omvystwbziwxxtmx'
    global otp
    otp = str(random.randint(1000, 9999))
    sent_from = gmail_user
    to = [str(current_email)]
    subject = 'OTP For Password Reset'
    body = f'Your otp for the password reset is {otp}'

    email_text = """\
        From: %s
        To: %s
        Subject: %s

        %s
        """ % (sent_from, ", ".join(to), subject, body)


    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.ehlo()
    smtp_server.login(gmail_user, gmail_password)
    smtp_server.sendmail(sent_from, to, email_text)
    smtp_server.close()

    return render_template('otp.html',vake='client')



@app.route("/client_otp")
def client_otp2():
    close_video()
    return render_template("otp.html",vake='client')


@app.route("/admin_dashboard")
def admin_dash2():
    close_video()
    return render_template("admin_dashboard.html")


@app.route('/client_passReset', methods=['POST'])
def client_reg():
    close_video()
    pass1 = request.form.get('pass1')
    pass2 = request.form.get('pass2')
    if not pass1 or not pass2:
        return render_template('newpass.html', vake='client')
    if pass1==pass2:
        conn = sqlite3.connect('WeaponDetection.db')
        cursor = conn.cursor()
        sql_command = f"UPDATE client SET client_password =\'"+str(pass1)+"\' WHERE client_email = \'"+current_email+"\';"
        cursor.execute(sql_command)
        conn.commit()
        conn.close()
        return render_template('passReset.html',vake='client')
    else:
        return render_template('newpass.html', vake='client')


@app.route('/admin_otp', methods=['POST'])
def admin_otp():
    close_video()
    email = request.form.get('email')
    if not email:
        return render_template('forgotpass.html', vake='admin')
    global current_email
    current_email = email
    import smtplib
    import random
    gmail_user = 'weapondetection4@gmail.com'
    gmail_password = 'omvystwbziwxxtmx'
    global otp
    otp = str(random.randint(1000, 9999))
    sent_from = gmail_user
    to = [str(current_email)]
    subject = 'OTP For Password Reset'
    body = f'Your otp for the password reset is {otp}'

    email_text = """\
            From: %s
            To: %s
            Subject: %s

            %s
            """ % (sent_from, ", ".join(to), subject, body)

    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.ehlo()
    smtp_server.login(gmail_user, gmail_password)
    smtp_server.sendmail(sent_from, to, email_text)
    smtp_server.close()

    return render_template('otp.html', vake='admin')


@app.route("/admin_otp")
def adminotp2():
    close_video()
    return render_template("otp.html", vake='admin')


@app.route("/see_pic", methods=['POST'])
def see_pic():
    close_video()
    path = request.form.get('button1')
    print(path)
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], str(path))
    return render_template("see_pic.html", user_image=pic1)


@app.route("/see_video")
def see_video():
    close_video()
    return send_file('saved_frames/ashpatil4040@gmail.com10.jpg', mimetype='image/gif')



@app.route('/admin_passReset', methods=['POST'])
def admin_reg():
    close_video()
    pass1 = request.form.get('pass1')
    pass2 = request.form.get('pass2')
    if not pass1 or not pass2:
        return render_template('newpass.html', vake='admin')
    if pass1 == pass2:
        conn = sqlite3.connect('WeaponDetection.db')
        cursor = conn.cursor()
        sql_command = f"UPDATE server SET server_password =\'" + str(
            pass1) + "\' WHERE server_email = \'" + current_email + "\';"
        cursor.execute(sql_command)
        conn.commit()
        conn.close()
        return render_template('passReset.html', vake='admin')
    else:
        return render_template('newpass.html', vake='admin')


@app.route("/admin_newpass", methods=['POST'])
def admin_newpass():
    close_video()
    otp_enter = request.form.get('otp')
    if not otp_enter:
        return render_template("otp.html", vake='admin')
    global otp
    if otp == otp_enter:
        return render_template("newpass.html", vake='admin')
    else:
        return render_template("otp.html", vake='admin')



@app.route("/admin_forgotpass")
def admin_forgotpass():
    close_video()
    return render_template("forgotpass.html",vake='admin')


@app.route("/Adminlogin")
def Adminlogin2():
    close_video()
    return render_template('Adminlogin.html')


@app.route("/clientLists")
def clientLists():
    close_video()
    conn = sqlite3.connect('WeaponDetection.db')
    cursor = conn.cursor()
    sql_commad = """SELECT DISTINCT client_email,
                            client_name, 
                            (SELECT COUNT(P.camera_username)
                                             FROM [camera] P
                                            WHERE P.client_email = S.client_email),
                            (SELECT COUNT(h.pic_path)
                                             FROM [history] h
                                            WHERE h.client_email = S.client_email)
                            FROM client S WHERE s.client_email <> ''

                            """
    cursor.execute(sql_commad)
    conn.commit()
    ress = cursor.fetchall()
    conn.close()
    return render_template("clientLists.html", data=ress)



if __name__=='__main__':
    app.run(debug=True)
