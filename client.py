#!/usr/bin/env python3
from enc_dec_des import des
import socket
import sys
import rsa

# Establish remote connection with a server (vs)

key = "des_key_"

def cl_connect(server_ip, server_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rv = s.connect_ex((server_ip, server_port))
    return (s, rv)


def cl_disconnect(s):
    s.close()


def cl_register(s):
    # Ask user for username and password
    print("\nRegister New Client\n")
    in_uname = str(input("Username: ")).encode('ascii')
    in_pwd = str(input("Password: ")).encode('ascii')
    s.send(in_uname)
    # ----
    s.recv(1024)
    # ----
    s.send(in_pwd)

    # Check server response
    res = s.recv(1024).decode('ascii')
    if res == '1':
        print("Email address already registered.")
    else:
        print("Registration Complete.")
    return None


def cl_login(conn):

    # ---
    conn.send(b'0')
    # ---

    # Recieve the login prompt
    prompt = conn.recv(1024).decode('ascii')

    # Display Welcome Message
    print(prompt)

    # Authenticate user
    print("\nClient Login\n")
    uname = str(input("Username: ")).encode('ascii')
    pwd = str(input("Password: ")).encode('ascii')

    # Send credentials to server
    conn.send(uname)
    # ----
    conn.recv(1024)
    # ----
    conn.send(pwd)

    # Check response
    rv = conn.recv(1024).decode('ascii')
    if rv == '1':
        print("Wrong mail address.")
        return None
    elif rv == '2':
        print("Wrong password.")
        return None

    # rv == 0
    print("Successfully Logged In")

    # Go to Logged in Menu
    logged_in_menu(conn)



def cl_send_email(conn):
    # Begin with Send
    conn.send(b'0')

    # Begin Email Loop
    in_email = True

   
    s_reply = conn.recv(1024).decode('ascii')
    print("S:", s_reply)

    if "220" in s_reply:
        while(in_email):
            # Sending 
            cl_cmd = str(input("C: ")).encode('ascii')
            conn.send(cl_cmd)

            # Response
            s_reply = conn.recv(1024).decode('ascii')
            if "Enter Data" not in s_reply:
                print("S:", s_reply)
            
            if "221 Connection Closed" in s_reply:
                print("Session Closed")
                return None


def cl_get_email(conn):

    # Begin with Send
    conn.send(b'0')
    d = des()
    mail = conn.recv(1024)
    printdata = mail.decode('UTF-8')
    if(printdata != "No Mail in the Mail-Box"):
        plain = d.decrypt(key,printdata,padding=True)
        print(plain)
    else :
        print(printdata)
    
    return None


def logged_in_menu(conn):

    while True:
        # After login menu
        print("\n1. Send Mail\n2. Read Mail\n3. Logout")
        choice = int(input("Enter your Choice: "))

        # Send to server
        ch = str(choice).encode('ascii')
        conn.send(ch)

        # Validation
        valid = conn.recv(1024)
        valid = int(valid.decode('ascii'))
        if valid == 0:
            print("Unrecognized Input")
            continue

        # Client after login choice
        if choice == 1:
            cl_send_email(conn)
        elif choice == 2:
            cl_get_email(conn)
        elif choice == 3:
            return None


def cl_close(conn):
    conn.send(b'0')
    # Response from server
    stats = conn.recv(1024).decode('ascii')
    print(stats)


if __name__ == '__main__':

    # Server IP and Port
    server_ip = '127.0.0.1'
    server_port = int(sys.argv[1])

    # Connect to server
    sd, status = cl_connect(server_ip, server_port)

    # print("DES Key : secret_k     (known already)")
    print("\nRSA Key Generation\n")
    p = int(input("Enter a prime number : "))
    q = int(input("Enter another prime number : "))
    public, private = rsa.generate_keypair(p, q)
    print ("\nGenerating public/private keypairs . . .")
    print ("Public key : ", public, "\nPrivate key : ", private)
    pK = str(public).encode('ascii')
    sd.send(pK)
    print("\nPublic key sent to server.\n")
    print("\nDES Key : " , key , "    (Known already) \n")
    
    
    while True:

        # CLIENT MENU
        print("\n\tCLIENT MENU\n1. Register\n2. Login\n3. Quit")
        choice = int(input("Enter your Choice: "))

        # Send choice to server
        ch = str(choice).encode('ascii')
        sd.send(ch)
        
        # Quitting the client module
       

        # Validation
        valid = sd.recv(1024)
        valid = int(valid.decode('ascii'))
        if valid == 0:
            print("Unrecognized Input")
            continue

        # Client choice redirection
        if choice == 1:
            cl_register(sd)
        elif choice == 2:
            cl_login(sd)
        elif choice == 3:
            print("Quitting the mail server ... ")
            break
        else:
            cl_close(sd)
            break

    sd.close()
