#!/usr/bin/env python3
from enc_dec_des import des
import sys
import socket
from _thread import start_new_thread, allocate_lock
import rsa

registered = {}
database = {}

key = "des_key_"

def ser_init(ip, port):
    # Initialize a TCP socket to recieve connections
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, port))
    s.listen(5)
    return s


def ser_close(conn):

    conn.recv(1024)
    results = ""
    clist = list(registered)
    for i in range(0, len(clist)):
        s = "%d. %s -- %d votes\n" % (i+1, clist[i], registered[clist[i]])
        results = results + s

    conn.send(results.encode('ascii'))


def ser_register(conn, lock):

    # Recieve username and password from user
    cl_uname = conn.recv(1024).decode('ascii')
    # ---- #
    conn.send(b'0')
    # ---- #
    cl_pwd = conn.recv(1024).decode('ascii')

    # Check if username exists
    if cl_uname in registered:
        conn.send(b'1')
    else:
        # Store user registered
        lock.acquire()
        registered[cl_uname] = cl_pwd
        lock.release()
        conn.send(b'0')

    print(registered)
    return None


def ser_login(conn, lock):

    # List of registered
    clist = list(registered)

    # Send the login menu
    conn.recv(1024)
    conn.send("\n\tMAIL-BOX\n".encode('ascii'))

    # Check registered
    cl_uname = conn.recv(1024).decode('ascii')
    conn.send(b'0')
    cl_pwd = conn.recv(1024).decode('ascii')

    # Send back 1 if user not registered
    if cl_uname not in registered:
        conn.send(b'1')
        return None

    # Send back 2 if user provides invalid password
    if registered[cl_uname] != cl_pwd:
        conn.send(b'2')
        return None

    # Send 0 if login successful
    conn.send(b'0')

    logged_in = cl_uname

    # Go to Logged in Menu
    logged_in_menu(conn, lock, logged_in)

    logged_in = ''
    return None
    # Go to email section
    # ser_send_email(conn, lock, logged_in)


def ser_send_email(conn, lock, logged_in):
    # Begin with recv
    conn.recv(1024)

    # Begin Email Loop
    in_send_email = True

    # Temp Storage
    from_email = ''
    email_list = []
    messages = []
    order = 0
    data_flag = False

    # Send Initialization Message
    conn.send("220 Service Ready".encode('ascii'))

    while(in_send_email):
        # Start Receiving Commands
        cl_cmd = conn.recv(1024).decode('ascii')

        if "HELLO" in cl_cmd:
            conn.send("250 OK".encode('ascii'))
        
        elif "MAIL FROM:" in cl_cmd:
            if order == 0:
                from_email = cl_cmd.replace('MAIL FROM: ', '')
                
                if from_email in registered and from_email == logged_in:
                    conn.send("250 OK".encode('ascii'))
                    order = 1

                else:
                    conn.send("550 No such user here".encode('ascii'))

            else:
                conn.send("Wrong Order of Input [MAIL To , RCPT TO, DATA]".encode('ascii'))
                order = 0
            
        elif "RCPT TO:" in cl_cmd:
            if order == (1 + len(email_list)):
                rcpt_email = cl_cmd.replace('RCPT TO: ', '')
                # print(rcpt_email)
                
                if rcpt_email in registered:
                    conn.send("250 OK".encode('ascii'))
                    email_list.append(rcpt_email)
                    order += 1

                else:
                    conn.send("550 No such user here".encode('ascii'))

            else:
                conn.send("Unrecognized Input".encode('ascii'))
                order = 0
        
        elif "DATA" in cl_cmd:
            if order == (1 + len(email_list)):
                conn.send("354 Start mail input; end with <CRLF>.<CRLF>".encode('ascii'))
                order += 1
                data_flag = True

            else:
                conn.send("Unrecognized Input".encode('ascii'))
                order = 0

        elif "." in cl_cmd:
            if data_flag is True:
                conn.send("250 OK".encode('ascii'))
                data_flag = False
                email_to_db(conn, lock, logged_in, email_list, messages)
                email_list = []
                messages = []

            else:
                conn.send("Unrecognized Input".encode('ascii'))
                order = 0

        elif "QUIT" in cl_cmd:
            conn.send("221 Connection Closed".encode('ascii'))
            order = 0
            in_send_email = False
            return None

        elif data_flag is True:
            messages.append(cl_cmd)
            conn.send("Enter Data".encode('ascii'))

        else:
            conn.send("Invalid Request".encode('ascii'))


def ser_get_email(conn, lock, logged_in):
    # Begin with recv
    conn.recv(1024)

    if logged_in not in database:
        conn.send("No Mails in the Mail-Box.".encode('ascii'))
        return None

    elif len(database[logged_in]) != 0:

        inbox = ""

        # Get Mail
        for mail in database[logged_in]:
            sender = mail[0]
            # print(sender)
            message = ""

            for msg in mail[1]:
                message += msg + '\n'

            # Create Header
            header  = ( "\n***************************************\n"
                        "From: %s\n"
                        "To: %s\n"
                        "MIME-Version: 1.0\n"
                        "Content-Type: text\n"
                        "***************************************\n") % (sender, logged_in)
                        
            footer = ("------------End of Message-------------\n")
            
            # Ready to send content
            content = header + '\n' + message + '\n' + footer
            # print(content)
            inbox += content + '\n'
            d = des()
            ciphered = d.encrypt(key,inbox,padding=True)
            messg = bytes(ciphered, 'UTF-8')
            conn.send(messg)
            print("-------------------ENCRYPTED MAIL------------------------\n")
            print(messg)
            print("-------------------END OF MAIL------------------------\n")
            database[logged_in].clear()
        return None

    else:
        # No Mail
        conn.send("No Mail in the Mail-Box".encode('ascii'))
        return None


def logged_in_menu(conn, lock, logged_in):
    # Request-Response Loop
    while True:
        # Wait for choice
        choice = conn.recv(1024)
        choice = int(choice.decode('ascii'))

        # Check validity of choice
        if choice < 1 or choice > 3:
            conn.send(str(0).encode('ascii'))
            continue
        else:
            conn.send(str(1).encode('ascii'))

        # Transfer control to specific module based on request
        if choice == 1:
            ser_send_email(conn, lock, logged_in)
        elif choice == 2:
            ser_get_email(conn, lock, logged_in)
        elif choice == 3:
            return None


def email_to_db(conn, lock, logged_in, email_list, messages):
    for email in email_list:
        database[email] = [[logged_in, messages]]
    
    print(database)

    return None


def child(conn, lock):

    # Request-Response Loop
    while True:

        # Wait for choice
        choice = conn.recv(1024)
        choice = int(choice.decode('ascii'))

        # Check validity of choice
        if choice < 1 or choice > 3:
            conn.send(str(0).encode('ascii'))
            continue
        else:
            conn.send(str(1).encode('ascii'))

        # Transfer control to specific module based on request
        if choice == 1:
            ser_register(conn, lock)
        elif choice == 2:
            ser_login(conn, lock)
        elif choice == 3:
            print(cl_addr, "Disconnected")
            break
        else:
            ser_close(conn)
            break

    conn.close()
#[list(i) for i in level]
publicKeys = []
if __name__ == '__main__':

    print("\n ----------------------------------------------------\n")
    print("                      SERVER SIDE                       \n")
    print(" ----------------------------------------------------\n")
    
    
    print("\nDES Key: ", key, "   (known already)")

    s = ser_init('127.0.0.1', int(sys.argv[1]))

    # Wait for a connection
    while True:
        conn, cl_addr = s.accept()
        print("\n",cl_addr, "Connected")
        publicK = conn.recv(1024)
        publicK = publicK.decode('ascii')
        #publicKeys = publicKeys + dict(publicK)
        print("Public-Key from ", cl_addr, " : ", publicK,"\n")
        #print(publicKeys)
        lock = allocate_lock()
        start_new_thread(child, (conn, lock, ))
