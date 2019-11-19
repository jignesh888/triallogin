from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import urllib.request

app = Flask(__name__)
app.secret_key = '_sbDdEOVwmMzzbn7eROWxg'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'newdb'
mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def login():
        if 'type' in session:
            type = session['type']
            if session['type'] != "Admin":
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT COUNT(*) FROM devices WHERE user_id=%s", (session['id'],))
                property_count = cursor.fetchall()
                cursor.execute("SELECT COUNT(*) FROM `rd_list` WHERE user_id=%s", (session['id'],))
                property_count1 = cursor.fetchall()
                cursor.execute("SELECT COUNT(*) FROM `bt_list` WHERE user_id=%s", (session['id'],))
                property_count2 = cursor.fetchall()
                return render_template("index.html", count=property_count, count1=property_count1, count2 = property_count2, title1 = session['title'])
            else:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT COUNT(*) FROM users")
                property_count = cursor.fetchall()
                return render_template("index11.html", count=property_count, title1 = session['title'])
        elif request.method == 'POST' and 'username' in request.form and 'password' in request.form:
                username1 = request.form['username']
                password1 = request.form['password']
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (username1, password1))
                account = cursor.fetchone()
                if account:
                    if account['type']=="Admin":
                        session['loggedin'] = True
                        session['id'] = account['id']
                        session['username'] = account['email']
                        session['title'] = account['username']
                        session['type'] = account['type']
                        cursor.execute("SELECT COUNT(*) FROM users")
                        property_count = cursor.fetchall()
                        return render_template("index11.html", count=property_count, title1 = session['title'])
                    elif account['type'] == "User":
                        session['loggedin'] = True
                        session['id'] = account['id']
                        session['username'] = account['email']
                        session['title'] = account['username']
                        session['type'] = account['type']
                        cursor.execute("SELECT COUNT(*) FROM devices WHERE user_id=%s", (account['id'],))
                        property_count = cursor.fetchall()
                        cursor.execute("SELECT COUNT(*) FROM `rd_list` WHERE user_id=%s", (session['id'],))
                        property_count1 = cursor.fetchall()
                        cursor.execute("SELECT COUNT(*) FROM `bt_list` WHERE user_id=%s", (session['id'],))
                        property_count2 = cursor.fetchall()
                        return render_template("index.html", user=session['username'], count=property_count, count1 = property_count1,count2 = property_count2, title1 = session['title'])
                else:
                    msg = "Please enter correct E-mail and Password"
                    return render_template("page-login.html", msg  = msg)
        else:
            return render_template("page-login.html")

@app.route("/insertredir")
def ins1():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM home_devices WHERE user_id=%s", (session['id'],))
    result = cursor.fetchall()
    return render_template("add_device.html", len = len(result), string = result, title1 = session['title'])

@app.route('/addrules')
def hdform():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM devices WHERE user_id=%s",(session['id'],))
    result = cursor.fetchall()
    cursor.execute("SELECT * FROM home_devices WHERE user_id=%s", (session['id'],))
    result1 = cursor.fetchall()
    cursor.execute("SELECT * FROM bt_devices WHERE user_id=%s", (session['id'],))
    result2 = cursor.fetchall()
    return render_template("add_rules.html", string2=result, len=len(result),  string3=result1, len1=len(result1),string4=result2, len2 = len(result2), title1 = session['title'])

@app.route('/addrulestodb1', methods = ['GET','POST'])
def artdb1():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    fvariable = request.form['device']
    svariable = request.form['appl']
    con = request.form['con']
    cursor.execute("SELECT * FROM bt_devices WHERE name=%s",(fvariable,))
    r1 = cursor.fetchall()
    cursor.execute("SELECT * FROM home_devices WHERE dname=%s",(svariable,))
    r2 = cursor.fetchall()
    r11 = r1[0]['id']
    r22 = r2[0]['id']
    cursor.execute("INSERT INTO conditions(`user_id`, `btid`, `amid`, `condition`, `type`) VALUES(%s, %s, %s, %s, %s)", (session['id'], r11, r22, con, 'Bluetooth'))
    mysql.connection.commit()
    return redirect(url_for('viewr'))

@app.route('/addrulestodb', methods = ['GET','POST'])
def artdb():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    fvariable = request.form['device']
    svariable = request.form['appl']
    con = request.form['con']
    cursor.execute("SELECT * FROM devices WHERE device=%s",(fvariable,))
    r1 = cursor.fetchall()
    cursor.execute("SELECT * FROM home_devices WHERE dname=%s",(svariable,))
    r2 = cursor.fetchall()
    r11 = r1[0]['id']
    r22 = r2[0]['id']
    cursor.execute("INSERT INTO conditions(`user_id`, `imid`, `amid`, `condition`, `type`) VALUES(%s, %s, %s, %s, %s)", (session['id'], r11, r22, con, 'Wi-Fi'))
    mysql.connection.commit()
    return redirect(url_for('viewr'))

@app.route('/homedevice', methods = ['GET','POST'])
def ahd():
    if request.method == 'POST' and 'hdevice' in request.form:
        hdevice = request.form['hdevice']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO `home_devices`(`user_id`, `dname`) VALUES (%s, %s)", (session['id'], hdevice))
        return redirect(url_for('viewd'))

@app.route('/bluedel/<int:delid>')
def bdel(delid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM `bt_devices` WHERE id=%s" %delid)
    cursor.execute("DELETE FROM `conditions` WHERE btid=%s" %delid)
    return redirect(url_for('viewd'))

@app.route('/blueupdate/<int:upid>', methods = ['GET', 'POST'])
def blueupdate(upid):
    name = request.form['name']
    mac = request.form['mac']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE  `bt_devices`  SET  `name` = %s, `mac` = %s  WHERE  `id` = %s",(name, mac, upid))
    mysql.connection.commit()
    return redirect(url_for('viewd'))

@app.route('/blueedit/<int:editid>')
def blueedit(editid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM `bt_devices` WHERE `id`=%s" %editid,)
    resultedit = cursor.fetchall()
    return render_template("blueedit.html", newvalue=resultedit)

@app.route("/view")
def viewd():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM devices WHERE user_id=%s", (session['id'],))
    result = cursor.fetchall()
    cursor.execute("SELECT * FROM bt_devices WHERE user_id=%s", (session['id'],))
    result1 = cursor.fetchall()
    cursor.execute("SELECT * FROM `rem_data` WHERE user_id=%s", (session['id'],))
    result2 = cursor.fetchall()
    return render_template("view_device.html", len=len(result), string1=result, string2=result1, len1=len(result1), title1 = session['title'], string3 = result2, len2 = len(result2))

@app.route('/insert', methods = ['GET','POST'])
def ins():
    if request.method == 'POST' and 'device' in request.form and 'ip' in request.form:
        device = request.form['device']
        ip = request.form['ip']
        mac = request.form['mac']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO `devices`(`user_id`, `device`, `mac`, `ip`) VALUES (%s, %s, %s, %s)", (session['id'], device, mac, ip))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('viewd'))
    else:
        return str(session['id'])

@app.route('/edit/<int:editid>')
def ed(editid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM `devices` WHERE `id`=%s" %editid,)
    resultedit = cursor.fetchall()
    return render_template("edit.html", newvalue=resultedit)

@app.route('/update/<int:editid1>', methods = ['GET','POST'])
def up(editid1):
    device = request.form['device']
    ip = request.form['ip']
    mac  = request.form['mac']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE  `devices`  SET  `device` = %s, `mac` = %s, `ip` = %s  WHERE  `id` = %s", (device, mac, ip, editid1))
    mysql.connection.commit()
    return redirect(url_for('viewd'))

@app.route('/delete/<int:delid>')
def delete(delid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM `devices` WHERE id=%s" %delid)
    cursor.execute("DELETE FROM `conditions` WHERE imid=%s" %delid)
    return redirect(url_for('viewd'))

@app.route('/viewrules')
def viewr():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT conditions.id, devices.device, home_devices.dname, conditions.condition, conditions.type "
                   "FROM conditions INNER JOIN devices ON conditions.imid = devices.id INNER JOIN home_devices ON "
                   "conditions.amid = home_devices.id WHERE devices.user_id=%s;", (session['id'],))
    result = cursor.fetchall()
    cursor.execute("SELECT conditions.id, bt_devices.name, home_devices.dname, conditions.condition, conditions.type "
                   "FROM conditions INNER JOIN bt_devices ON conditions.btid = bt_devices.id INNER JOIN home_devices ON "
                   "conditions.amid = home_devices.id WHERE bt_devices.user_id=%s;", (session['id'],))
    result1 = cursor.fetchall()
    return render_template("view_rules.html", result = result, len = len(result), result1 = result1, len1 = len(result1), title1 = session['title'])

@app.route('/ruleupview/<int:editid>', methods = ['GET','POST'])
def ruleup(editid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM devices WHERE user_id=%s", (session['id'],))
    result = cursor.fetchall()
    cursor.execute("SELECT * FROM home_devices WHERE user_id=%s", (session['id'],))
    result1 = cursor.fetchall()
    cursor.execute("SELECT * FROM conditions WHERE id=%s" %editid)
    result2 = cursor.fetchall()
    return render_template("edit_rules.html", result=result, len=len(result), result1=result1, len1=len(result1), result2=result2, len2=len(result2))

@app.route('/ruleupview1/<int:editid>', methods = ['GET','POST'])
def ruleup1(editid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM bt_devices WHERE user_id=%s", (session['id'],))
    result = cursor.fetchall()
    cursor.execute("SELECT * FROM home_devices WHERE user_id=%s", (session['id'],))
    result1 = cursor.fetchall()
    cursor.execute("SELECT * FROM conditions WHERE id=%s" %editid)
    result2 = cursor.fetchall()
    return render_template("edit_rules_bt.html", result=result, len=len(result), result1=result1, len1=len(result1), result2=result2, len2=len(result2))

@app.route('/updaterules/<int:editid1>', methods = ['GET','POST'])
def uprules(editid1):
    device = request.form['device']
    appl = request.form['appl']
    con = request.form['con']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM devices WHERE device=%s", (device,))
    r1 = cursor.fetchall()
    cursor.execute("SELECT * FROM home_devices WHERE dname=%s", (appl,))
    r2 = cursor.fetchall()
    r11 = r1[0]['id']
    r22 = r2[0]['id']
    cursor.execute("UPDATE  `conditions`  SET  `user_id` = %s, `imid` = %s, `amid` = %s, `condition` = %s  WHERE  `id` = %s", (session['id'], r11, r22, con, editid1))
    mysql.connection.commit()
    return redirect(url_for('viewr'))

@app.route('/updaterules1/<int:editid1>', methods = ['GET','POST'])
def uprules1(editid1):
    device = request.form['device']
    appl = request.form['appl']
    con = request.form['con']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM bt_devices WHERE name=%s", (device,))
    r1 = cursor.fetchall()
    cursor.execute("SELECT * FROM home_devices WHERE dname=%s", (appl,))
    r2 = cursor.fetchall()
    r11 = r1[0]['id']
    r22 = r2[0]['id']
    cursor.execute("UPDATE  `conditions`  SET  `user_id` = %s, `btid` = %s, `amid` = %s, `condition` = %s  WHERE  `id` = %s", (session['id'], r11, r22, con, editid1))
    mysql.connection.commit()
    return redirect(url_for('viewr'))

@app.route('/delrule/<int:delid>')
def delr(delid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM `conditions` WHERE id=%s" % delid)
    return redirect(url_for('viewr'))

@app.route('/login/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('type', None)
   return redirect(url_for('login'))

@app.route('/insertbt', methods = ['GET','POST'])
def insertbt():
    name = request.form['btdevice']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO `bt_devices`(`user_id`,`name`) VALUES(%s, %s)",(session['id'], name))
    return redirect(url_for('viewd'))

@app.route('/insertir', methods = ['GET','POST'])
def insertir():
    name = request.form['irdevice']
    amid = request.form['amid']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM home_devices WHERE dname=%s", (amid,))
    r2 = cursor.fetchall()
    r22 = r2[0]['id']
    cursor.execute("INSERT INTO `rem_data`(`user_id`,`amid`,`name`) VALUES(%s, %s, %s)",(session['id'], r22, name))
    mysql.connection.commit()
    return redirect(url_for('viewd'))

@app.route('/iredit/<int:editid>')
def iredit(editid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM `rem_data` WHERE id=%s" % editid)
    result1 = cursor.fetchall()
    return render_template('iredit.html', result1 = result1, len1 = len(result1), msg = request.args.get('msg'))

@app.route('/irdel/<int:delid>')
def irdelete(delid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM `rem_data` WHERE id=%s" % delid)
    return redirect(url_for('viewd'))

@app.route('/startbt/<int:reid>')
def startbt(reid):
    urllib.request.urlopen("http://sailasercom.ipage.com/home_auto/startbt.php?uid="+ str(session['id']) +"&rid=" + str(reid))
    msg = 'Receiving Signal'
    return redirect(url_for('iredit', editid = reid, msg = msg))

@app.route('/stopbt/<int:reid1>')
def stopbt(reid1):
    urllib.request.urlopen("http://sailasercom.ipage.com/home_auto/stopbt.php?uid=" + str(session['id']))
    return redirect(url_for('iredit', editid = reid1))

@app.route('/fetchdata')
def fetchdata():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM `rd_list` WHERE user_id=%s",(session['id'],))
    x = cursor.fetchall()
    return render_template("router_device.html", result = x, len = len(x))

@app.route('/fetchdatabt')
def fetchdatabt():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM `bt_list` WHERE user_id=%s",(session['id'],))
    x = cursor.fetchall()
    return render_template("bluetooth_device.html", result = x, len = len(x))

@app.route('/adddevice2db/<int:id1>')
def adddev2db(id1):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM `rd_list` WHERE id=%s" % id1)
    result = cursor.fetchone()
    cursor.execute("INSERT INTO `devices`(`user_id`, `device`, `mac`, `ip`) VALUES(%s, %s, %s, %s)", (session['id'], result['name'], result['mac'], result['ip']))
    mysql.connection.commit()
    return redirect(url_for('viewd'))

@app.route('/addbtdevice2db/<int:id1>')
def addbtdev2db(id1):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM `bt_list` WHERE id=%s" % id1)
    result = cursor.fetchone()
    cursor.execute("INSERT INTO `bt_devices`(`user_id`, `name`, `mac`) VALUES(%s, %s, %s)",(session['id'], result['name'], result['mac'],))
    mysql.connection.commit()
    return redirect(url_for('viewd'))

@app.route('/irupdate/<int:id1>', methods = ['GET','POST'])
def irupdate(id1):
    name1 = request.form['name1']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE `rem_data` SET name = %s WHERE id=%s",(name1, id1))
    return redirect(url_for('viewd'))

###############################################################admin panel###############################################################################################################################
@app.route('/manageusers')
def viewu():
    if session['type'] == "Admin":
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users")
        result1 = cursor.fetchall()
        return render_template("view_users.html", result1 = result1, len=len(result1), title1 = session['title'])
    else:
        return render_template("page-error-403.html")

@app.route('/adminedit/<int:editid>')
def aedit(editid):
    if session['type'] == "Admin":
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM `users` WHERE `id`=%s" % editid, )
        resultedit = cursor.fetchall()
        return render_template("admin_edit.html", newvalue=resultedit, msg = request.args.get('msg'), msg1 = request.args.get('msg1'), msg2 = request.args.get('msg2'))
    else:
        return render_template("page-error-403.html")

@app.route('/adminupdate/<int:editid>', methods = ['GET','POST'])
def aupdate(editid):
    if session['type'] == "Admin":
        if 'username' in request.form and 'email' in request.form and 'password' in request.form and 'birthdate' in request.form and 'gender' in request.form and 'device_id' in request.form and 'type' in request.form:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            birthdate = request.form['birthdate']
            gender = request.form['gender']
            device_id = request.form['device_id']
            type = request.form['type']
            edit_id = editid
            if re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
            # match
                if re.search('^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email):
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute("UPDATE  `users`  SET  `type` = %s, `username` = %s, `email` = %s, `password` = %s,  `birthdate` = %s, `gender` = %s, `device_id` = %s WHERE  `id` = %s",(type, username, email, password, birthdate, gender, device_id, editid))
                    mysql.connection.commit()
                    return redirect(url_for('viewu'))
                else:
                    msg2 = "Enter valid email"
                    return redirect(url_for('aedit',msg2 = msg2, editid=edit_id))
            else:
                if re.search('^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email):
                    msg = "At least 8 Character, 1 Upper case, 1 lower case, 1 Number, 1 Special Character required"
                    return redirect(url_for('aedit', msg=msg, editid=edit_id))
                else:
                    msg2 = "Enter valid mail"
                    msg = "At least 8 Character, 1 Upper case, 1 lower case, 1 Number, 1 Special Character required"
                    return redirect(url_for('aedit', msg=msg, msg2=msg2, editid=edit_id))
        else:
            msg1 = "Please fill the form"
            return redirect(url_for('adadd1',msg1=msg1))
    else:
        return render_template("page-error-403.html")

@app.route('/adminadduser1', methods=['GET', 'POST'])
def adadd1():
    if session['type'] == "Admin":
        return render_template("admin_add_user.html",msg = request.args.get('msg'),msg1 = request.args.get('msg1'),msg2 = request.args.get('msg2'),msg3 = request.args.get('msg3'), title1 = session['title'])
    else:
        return render_template("page-error-403.html")

@app.route('/adminadduser2', methods = ['GET','POST'])
def adadd2():
    if session['type'] == 'Admin':
        if 'username' in request.form and 'email' in request.form and 'password' in request.form and 'birthdate' in request.form and 'gender' in request.form and 'device_id' in request.form and 'type' in request.form:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            birthdate = request.form['birthdate']
            gender = request.form['gender']
            device_id = request.form['device_id']
            type = request.form['type']
            if re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
            # match
                if re.search('^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email):
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute("SELECT * FROM `users` WHERE email=%s", (email,))
                    ert = cursor.fetchall()
                    cursor.execute("SELECT * FROM `users` WHERE device_id=%s", (device_id,))
                    ert1 = cursor.fetchall()
                    if ert or ert1:
                        msg3 = "User or Hardware Device already exist!"
                        return redirect(url_for('adadd1', msg3 = msg3))
                    else:
                        cursor.execute("INSERT INTO `users`(`type`, `username`, `email`, `password`, `birthdate`, `gender`, `device_id`) VALUES (%s, %s, %s, %s, %s, %s, %s)", (type, username, email, password, birthdate, gender, device_id,))
                        mysql.connection.commit()
                        return redirect(url_for('viewu'))
                else:
                    msg2 = "Enter valid email"
                    return redirect(url_for('adadd1',msg2 = msg2))
            else:
                if re.search('^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email):
                    msg = "At least 8 Character, 1 Upper case, 1 lower case, 1 Number, 1 Special Character required"
                    return redirect(url_for('adadd1', msg=msg))
                else:
                    msg2 = "Enter valid mail"
                    msg = "At least 8 Character, 1 Upper case, 1 Lower case, 1 Number, 1 Special Character required"
                    return redirect(url_for('adadd1', msg=msg, msg2=msg2))
        else:
            msg1 = "Please fill the form"
            return redirect(url_for('adadd1',msg1=msg1))
    else:
        return render_template("page-error-403.html")

@app.route('/admindelete/<int:delid>')
def adelete(delid):
    if session['type'] == "Admin":
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DELETE FROM `users` WHERE id=%s" % delid)
        cursor.execute("DELETE FROM `home_devices` WHERE user_id=%s" % delid)
        cursor.execute("DELETE FROM `devices` WHERE user_id=%s" % delid)
        cursor.execute("DELETE FROM `bt_devices` WHERE user_id=%s" % delid)
        cursor.execute("DELETE FROM `conditions` WHERE user_id=%s" % delid)
        cursor.execute("DELETE FROM `current_condition` WHERE user_id=%s" % delid)
        cursor.execute("DELETE FROM `p_mac` WHERE user_id=%s" % delid)
        cursor.execute("DELETE FROM `rd_list` WHERE user_id=%s" % delid)
        cursor.execute("DELETE FROM `bt_list` WHERE user_id=%s" % delid)
        cursor.execute("DELETE FROM `rem_data` WHERE user_id=%s" % delid)
        return redirect(url_for('viewu'))
    else:
        return render_template("page-error-403.html")
#################################################################admin panel over#################################################################

if __name__ == '__main__':
    app.run(debug="True")

