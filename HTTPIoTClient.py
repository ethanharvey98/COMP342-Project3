import socket
import json
import time
import threading
import email, smtplib, ssl
from datetime import datetime

def sendEmail():
    mailer = smtplib.SMTP_SSL('smtp.gmail.com',465)

    mailer.ehlo()
    mailer.login('homesafecomp342@gmail.com','Security342')

    From = 'Data Comm Protect'
    To = 'Homeowner'
    Subject = 'House Alarm!'
    Body = 'Your house is being broken into!'

    msg = 'From: ' + From + '\r\nTo: ' + To + '\r\nSubject: ' + Subject + '\r\n\r\n' + Body + '\r\n'

    mailFrom = 'homesafecomp342@gmail.com'
    mailTo = 'joworley131@gmail.com'
    mailer.sendmail(mailFrom,mailTo,msg)

    mailer.close()


def alarm():
    # This function works as long as nothing is printed in it
    global alarmOn
    fireLevel = int(input("Enter maximum house temp: "))
    while(alarmOn):
        # print('alarm running...')
        s.send(b'GET /sensors/proximity HTTP/1.1\r\n\r\n')
        reply = s.recv(1024)
        # print(reply)
        reply = s.recv(1024)
        # print(reply)
        if (reply == b'HTTP/1.1 200 OK'):
            reply = s.recv(1024)
            # print(reply)

        # set onFire variable
        s.send(b'GET /sensors/temperature HTTP/1.1\r\n\r\n')
        temp = s.recv(1024)
        temp = s.recv(1024)
        try:
            temp = str(temp).split(" ")[4]
            if (float(temp) > float(fireLevel)):
                onFire = True
            else:
                onFire = False
        except:
            onFire = False
        
        # the alarm goes off here
        if (reply == b'\r\nContent-type:text/html\r\nConnection: close\r\n\r\nDigital proximity sensor indicates object is NOT PRESENT\r\n\r\n'
            or onFire):
            alarmOn = False
            alarmRinging = True
            sendEmail()
            for i in range(10):
                s.send(b'PUT /buzz/beeps HTTP/1.1\r\n\r\n')
                s.send(b'PUT /led/toggle HTTP/1.1\r\n\r\n')
                time.sleep(1)
        else:
            # wait 15 seconds
            time.sleep(15)

def logger():
    global logging
    global log
    while(logging):
        # datetime object containing current date and time
        now = datetime.now()
        date_string = now.strftime("%m/%d/%Y %H:%M:%S") + " >> "
        
        s.send(b'GET /sensors/proximity HTTP/1.1\r\n\r\n')
        reply = s.recv(1024)
        reply = s.recv(1024)
        if(reply == b'\r\nContent-type:text/html\r\nConnection: close\r\n\r\nDigital proximity sensor indicates object is PRESENT\r\n\r\n'):
            logFile.write(date_string + "An Object is PRESENT" + "\n")
        else:
            logFile.write(date_string + "An Object is NOT PRESENT" + "\n")
        s.send(b'GET /sensors/temperature HTTP/1.1\r\n\r\n')
        reply = s.recv(1024)
        reply = s.recv(1024)
        
        logFile.write(date_string + "Temperature: " + str(reply).split(" ")[4] + "\n")

        time.sleep(2)

# global alarmOn tells whether alarm is on or not
global alarmOn
alarmOn = False
global logging
logging = False
global log
log = ["Sensor Data"]
logFile = open("MyLog.txt","a")

# thread for alarm
t1 = threading.Thread(target=alarm, args=())
# thread for logging
t2 = threading.Thread(target=logger, args=())

# port number
port = 80
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# password
password = "password"
# authentication status
authenticated = False

# get IP Address
# ipAddress = "10.24.110.246"
ipAddress = input("Enter the IP address of the IoT device: ")

try:
    # attempt to connect
    s.connect((ipAddress, int(port)))
    x = "0"

    # Start while loop
    while (x != "12"):

        # list the valid actions available to the user
        print("Menu: ")
        print("1. List all hardware")
        print("2. Query all sensors values")
        print("3. Query the Temperature sensor")
        print("4. Query the Proximity sensor")
        print("5. Toggle white LED light")
        print("6. Toggle red LED light")
        print("7. Toggle buzzer")
        print("8. Turn alarm on")
        print("9. Turn alarm off")
        print("10. Start logging sensor data")
        print("11. Stop logging sensor data")
        print("12. To quit")    
        x = input("")

        if (x=="1"):
            print("Proximity sensor, temperature sensor, red LED light, and buzzer are used in this device.")
            
        elif (x=="2"):
            s.send(b'GET /sensors HTTP/1.1\r\n\r\n')
            reply = s.recv(1024)
            reply = s.recv(1024)

            # Ethan, will this if statement work when all sensor values are queried?
            if(b'\r\nContent-type:text/html\r\nConnection: close\r\n\r\nDigital proximity sensor indicates object is PRESENT\r\n\r\n' in reply):
                print("An Object is PRESENT")
            else:
                print("An Object is NOT PRESENT")

            # Print temperature
            print("Temperature: " + (str(reply).split(" ")[14])[:-1])
        elif (x=="3"):
            s.send(b'GET /sensors/temperature HTTP/1.1\r\n\r\n')
            reply = s.recv(1024)
            reply = s.recv(1024)
            print("Temperature: " + str(reply).split(" ")[4])
        elif (x=="4"):
            s.send(b'GET /sensors/proximity HTTP/1.1\r\n\r\n')
            reply = s.recv(1024)
            reply = s.recv(1024)
            if(reply == b'\r\nContent-type:text/html\r\nConnection: close\r\n\r\nDigital proximity sensor indicates object is PRESENT\r\n\r\n'):
                print("An Object is PRESENT")
            else:
                print("An Object is NOT PRESENT")            
        elif (x=="5" or x=="6"):
            while (authenticated==False):
                guess = input("Please enter the password('m' for menu): ")
                if (guess == password):
                    authenticated = True
                elif (guess == "m"):
                    break
                else:
                    print("Password was incorrect.")
            if (authenticated):
                # Get temperature value
                s.send(b'PUT /led/toggle HTTP/1.1\r\n\r\n')
                reply = s.recv(1024)
                reply = s.recv(1024)
                print(reply)
        #elif (x=="6"):
        elif (x=="7"):
            while (authenticated==False):
                guess = input("Please enter the password('m' for menu): ")
                if (guess == password):
                    authenticated = True
                elif (guess == "m"):
                    break
                else:
                    print("Password was incorrect.")
            if (authenticated):
                # get temperature value
                s.send(b'PUT /buzz/beeps HTTP/1.1\r\n\r\n')
                reply = s.recv(1024)
                print(reply)
                reply = s.recv(1024)
                print(reply)
        # when the alarm is turned on the system should
        # query the sensors on its own every 15 seconds
        elif (x=="8"):
            # start the alarm thread
            if(alarmOn):
                print("The alarm is already on")
            else:
                print("The alarm is on")
                # TODO: if you turn the alarm on, off, and back on again it fails
                try:
                    alarmOn = True
                    t1.start()
                except:
                    # Ignore starting thread
                    alarmOn = True
        elif (x=="9"):
            if(not alarmOn):
                print("The alarm is already off")
            else:
                alarmOn = False
                print("The alarm is off")
        elif (x=="10"):
            # this may need to be tweaked/tested before it's good
            if(logging):
                print("Already logging sensor data")
            else:
                logging = True
                t2.start()
        elif (x=="11"):
            # this may need to be tested too
            if(not logging):
                print("Logging is already turned off")
            else:
                logging = False
                print("Logging off. Please wait a couple seconds before logging again")
                logFile.close()
        elif (x=="12"):
            s.close()
            logFile.close()
        else:
            x="0"
            print("Invalid menu option.")

        print("")

except:
    # failed to connect
    print("Failed to connect")
