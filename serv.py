@app.get('/register/<name>/<email>/<mobile_no>/<device_type>')
def register(name, email, mobile_no, device_type):
    # name = request.forms.get('name')
    # email = request.forms.get('email')
    # mobile_no = request.forms.get('mobile_no')
    # device_type = request.forms.get('device_type')

    cur = db.users.find({'mobile_no': mobile_no})
    cur_data = json.loads(dumps(cur))

    if len(cur_data) != 0:
        return {'status': 'User exists'}
    else:
        cur = db.users.insert({'name': name, 'email': email, 'mobile_no': mobile_no, 'tickets': [], 'discount_code_log': [], 'access': [{'access_key':'','status':'','time_created':'','time_status_changed':'','device_type':'android'},{'access_key':'','status':'','time_created':'','time_status_changed':'','device_type':'ios'},{'access_key':'','status':'','time_created':'','time_status_changed':'','device_type':'web'},{'access_key':'','status':'','time_created':'','time_status_changed':'','device_type':'bot'}]})
        otp = randint(1000, 9999)

        cur = db.otp.find({'mobile_no': mobile_no})
        cur_data = json.loads(dumps(cur))

        if len(cur_data) == 0:
            cur = db.otp.insert({'mobile_no': mobile_no, 'otp': otp, 'time_created': time.time(), 'flag': 0})
            #notify.send_otp_sms(mobile_no, str(otp))
            console.log("sentotp");
        else:
            cur = db.otp.update({'mobile_no': mobile_no}, {'$set': {'otp': otp, 'flag': 0, 'time_created': time.time()}})
            #notify.send_otp_sms(mobile_no, str(otp))
            console.log("sentotp");

        return {'status': 'OTP sent to your mobile no'}

@app.get('/verify_otp/<mobile_no>/<otp>/<device_type>')
def verify_otp(mobile_no, otp, device_type):

    cur = db.users.find({'mobile_no': mobile_no})
    cur_data = json.loads(dumps(cur))

    if len(cur_data) == 0:
        return {'status': "User dosen't exists"}
    else:
        cur = db.otp.find({'mobile_no': mobile_no})
        cur_data = json.loads(dumps(cur))

        print cur_data

        if(len(cur_data)) == 0:
            return {'status': "OTP dosen't exist"}
        else:
            if(abs(cur_data[0]['time_created'] - time.time()) <= 300 and cur_data[0]['flag'] == 0):
                if cur_data[0]['otp'] == int(otp):
                    access_key = hl.sha256(b'' + mobile_no + 'otp' + str(time.time())).hexdigest()
                    print access_key
                    res = access_obj.access_key(mobile_no, access_key, device_type)
                    if res == 'DONE':
                        cur = db.otp.update({'mobile_no': mobile_no}, {'$set': {'flag': 1}})
                        return {'status': 'User validated', 'access_key': access_key}
                    else:
                        return {'status': 'Server Error'}
                else:
                    return {'status': 'OTP entered is wrong'}
            else:
                return {'status': 'OTP expired'}

@app.get('/resendOTP/<mobile_no>')
def resendOTP(mobile_no):
    cur = db.otp.find({'mobile_no': mobile_no})
    cur_data = json.loads(dumps(cur))
    print cur_data
    if len(cur_data) != 0:
        if(abs(cur_data[0]['time_created'] - time.time()) <= 300 and cur_data[0]['flag'] == 0):
            notify.send_otp_sms(mobile_no, str(cur_data[0]['otp']))
            # print 'OLD OTP :', str(cur_data[0]['otp'])
        else:
            otp = randint(1000, 9999)
            cur = db.otp.update({'mobile_no': mobile_no}, {'$set': {'otp': otp, 'flag': 0, 'time_created': time.time()}})
            notify.send_otp_sms(mobile_no, str(otp))
            # print 'New OTP :', str(otp)
        return {'status': 'OTP sent again'}
    else:
        return {'status': "User dosen't exist"}

@app.get('/login/<mobile_no>')
def login(mobile_no):
    cur = db.users.find({'mobile_no': mobile_no})
    cur_data = json.loads(dumps(cur))

    if len(cur_data) != 0:
        otp = randint(1000, 9999)
        cur = db.otp.update({'mobile_no': mobile_no}, {'$set': {'otp': otp, 'flag': 0, 'time_created': time.time()}})
        notify.send_otp_sms(mobile_no, str(otp))
        # print 'New OTP :', str(otp)
        return {'status': 'OTP sent to your mobile no'}
    else:
        return {'status': "User dosen't exist"}

@app.get('/logout/<mobile_no>/<device_type>')
def logout(mobile_no, device_type):
    device_types = ['android', 'ios', 'web', 'bot']

    cur = db.users.find({'mobile_no': mobile_no})
    cur_data = json.loads(dumps(cur))

    if len(cur_data) != 0:
        for i in range(0,4):
            if device_types[i] == device_type:
                cur = db.users.update({'mobile_no': mobile_no}, {'$set': {'access.'+str(i)+'.status': 0}})
                return {'status': 'Logged out'}
    else:
        return {'status': "User dosen't exist"}
