#!/user/bin/python

##########################
#written with python 3.8
#turn off Gmail security for less secure email apps for emails
#Created By: Quan Tieu
############################
import sys, getopt, os
import smtplib
import signal
import socket

#global setting
server_setting = ()
email_setting = ()

#recipients, add email addresses here.
email_recipients = ['qtieu@hotmail.com']

#helper functions
    
##################################
#Gmail 


#turn off Gmail security for account
def sendEmail(subject, message):
    try:
        TO = email_recipients[0]
        SUBJECT = subject
        TEXT = message

        # Gmail Sign In
        gmail_sender = email_setting[0]
        gmail_passwd = email_setting[1]

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        #server = smtplib.SMTP('smtp.gmail.com', 587) #587, 465
        server.ehlo()
        #server.starttls()
        server.login(gmail_sender, gmail_passwd)

        BODY = '\r\n'.join(['To: %s' % TO,'From: %s' % gmail_sender,'Subject: %s' % SUBJECT,'', TEXT])

        try:
            server.sendmail(gmail_sender, [TO], BODY)
            print ('email sent')
        except:
            print ('error sending mail')

        server.quit()
        
    except:
        print("problem with sendEmail")      
    

def validateUTCDate(dateStr):
    try:
        print("validateUTCDate")
        
    except:
        print("problem with validateUTCDate")      
    

####################################
def sendToServer(cmd):
    try:
        if(cmd[1] != "--reset"):
            srv_message = cmd[1] + ' ' + cmd[2]
        else:
            srv_message = cmd[1]
    except:
        print("Not enough parameters")
        sys.exit(1)
    
    try:
        
        
        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((server_setting[0], server_setting[1]))
            sock.sendall(bytes(srv_message, "utf-8"))

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")
            print(received)
        
    except:
        print("problem with sendToServer") 
        sendEmail("Socket Failed", "Error With sendToServer")       

def sendToServerTicker(cmd):
    try:
        
        srv_message = cmd[1] + ' ' + cmd[2]
    except:
        print("Not enough parameters")
        sys.exit(1)
        
    try:
        
        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((server_setting[0], server_setting[1]))
            sock.sendall(bytes(srv_message, "utf-8"))

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")
            print(received)
        
    except:
        print("problem with sendToServerTicker") 
        sendEmail("Socket Failed", "Error With sendToServerTicker")   
        return 1 

#sets the new port
def setServerAddress(cmd):
    try:
        global server_setting
        
        newConfig = cmd[2].split(':')
        server_setting = (newConfig[0], int(newConfig[1]))
        print(server_setting)
        
    except:
        print("problem with setServerAddress")

  
#get settings for the text file        
def getSettings(filename):
    try:
        
        with open(filename, "r") as f:
            read_data = f.read()
            #print(fp.readline())
        
        f.closed
        
        return read_data
        
    except:
        print("problem with getSettings")
    

def saveSettings(cmd):
    try:
        print("saveSettings")
        
    except:
        print("problem with saveSettings")
    
####################################


def processClientCmd(cmd):
    try:
        if(cmd[1] == '--price'):
            sendToServer(cmd)
        elif(cmd[1] == '--signal'):
            sendToServer(cmd)
        elif(cmd[1] == '--server_address'):
            setServerAddress(cmd)
        elif(cmd[1] == '--del_ticker'):
            sendToServerTicker(cmd)
        elif(cmd[1] == '--add_ticker'):
            sendToServerTicker(cmd)
        elif(cmd[1] == '--reset'):
            sendToServer(cmd)
        else:
            print("Command Not Found")
    except:
        print("problem with processClientCmd")

#run as API
def client_app():
    try:
        input_txt = ''

        print("Client App Started : Ctr C to close.  Use 'client --cmd param' ")
        while(True):
            
            input_txt = input("> ")
            
            cmd = input_txt.split(' ')
            
            ####
            #print(cmd)
            if (cmd[0] == "client" and len(cmd) > 1):
                #input needs to be client and a parameter
                processClientCmd(cmd)
            else:
                print("Invalid command")
        
    except:
        print("problem with client_app")


#run as API
def client_api(argv, argc):
    try:
        cmd = argv
        #print(cmd)
        
        processClientCmd(cmd)
        
    except:
        print("problem with client_api")

####################################

#main function
def main(argv, argc):
    try:
        #if there is client --something something, use it as api for individual features
        #otherwise create a prompt, better in Windows
        if (argc > 1):
            client_api(argv, argc)
        else:
            client_app()
    except:
        print("Error has occurred starting client, in main")



if __name__== "__main__":
    #defaults for client
    cdefaults = ("127.0.0.1", 8000)
    
    #get path to the settings file.
    #assumes the app is run in the same directory as settings file
    config_file = os.path.dirname(__file__) + os.path.sep + "settings.txt"
    
    #read from the file specified for email settings etc.
    file_settings = getSettings(config_file).split('\n')
    
    not_missing_parameter = True
    
    #get email setting
    try:
        user_password = file_settings[0].split(':')
        email_setting = (user_password[0], user_password[1])
        
        #sends an email to the default reciever.
        email_recipients.append(user_password[0])
    except:
        not_missing_parameter = False

    #get server setting or set to default
    #saved user server settings
    try:
        ssettings = file_settings[1].split(':')
        server_setting = (ssettings[0], int(ssettings[1]) )
    except:
        server_setting = cdefaults
    
    
    
    
    ####check right parameters and path
    print("***Checking Inputs*******")
    print(sys.argv[1:])
    print(len(sys.argv))
    print(file_settings)
    
    print(server_setting)
    print(email_setting)
    print(email_recipients)
    print("***Done*******")
    #####
    
    ##email test
    #sendEmail("My Email","Hello Everyone")

    if(not_missing_parameter):
        main(sys.argv, len(sys.argv))
    else :
        print("Input Settings Are Not Correct, Check Email Settings")