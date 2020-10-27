#dependencies
#subprocess, os, smtplib
#host: pwgen

#simple script for user creation and deletion
#remote openvpn script:/usr/local/openvpn_as/scripts/sacli
#pwgen: apt install pwgen -y

import os, subprocess
import smtplib
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def Add_user_and_send_email(user_to_add, group_to_add = 'Default'):
    try:
        password_generator = subprocess.Popen(['pwgen', '30', '1'], stdout = subprocess.PIPE)
        password = password_generator.stdout.read(). decode(). rstrip()
        print("User password for {} will be {}". format(user_to_add, password))
    except:
        print("The password for the user could not be generated")
        print("You must have pwgen installed: apt/yum/pacman pwgen")

    #email using SES. with and without html
    BODY = """Hi.
        Your credentials to access our services through VPN are:
        User: {}
        Password: {}
        URL: https://your-access-server.com
        OTP: Google Authenticator
        Best regards.
        """.format(user_to_add, password)
    BODYHTML = """Hi.
        <br>
        <br>
        Your credentials to access our services via VPN are: <br>
        <br>
        User: {}
        <br>
        Password: {}
        <br>
        URL: https://your-access-server.com
        <br>
        OTP: Google Authenticator
        <br>
        <br>
        Best regards.
        <br>
        """.format(user_to_add, password)

    ### Commands
    add_user = """sudo sh/usr/local/openvpn_as/scripts/sacli --user {} --key" type "--value" user_connect "UserPropPut""". format(user_to_add)
    add_to_group = """sudo sh/usr/local/openvpn_as/scripts/sacli --user {} --key" conn_group "--value" {} "UserPropPut""". format(user_to_add, group_to_add)
    add_local_password = """sudo sh/usr/local/openvpn_as/scripts/sacli --user {} --new_pass {} SetLocalPassword""". format(user_to_add, password)
    enable_auto_login_profile = """sudo sh/usr/local/openvpn_as/scripts/sacli --user {} --key" prop_autologin "--value" true "UserPropPut""". format(user_to_add)

    #add user
    print("Creating User:")
    try:
        print("Running" + add_user)
        subprocess.run(add_user, timeout = 10, shell = True)
        print("User {} created" .format(user_to_add))
    except:
        print("The user could not be created {}". format(user_to_add))
        exit()

    #add user to group
    try:
        subprocess.run(add_to_group, timeout = 10, shell = True)
        print("User {} added to group {}" .format(user_to_add, group_to_add))
    except:
        print("Could not add user {} to group {}". format(user_to_add, group_to_add))
        exit()
    #set password
    try:
        subprocess.run(add_local_password, timeout = 10, shell = True)
        print("Password for user {} created" .format(user_to_add))
    except:
        print("Could not create password for user {}". format(user_to_add))
        exit()
    #enable autologin: client.ovpn file without OTP
    try:
        subprocess.run(enable_auto_login_profile, timeout = 10, shell = True)
        print("Autologin created for user {}". format(user_to_add))
    except:
        print("Could not create Autologin for user {}". format(user_to_add))
        exit()

    #send mail
    SENDER = 'noreply@yourdomain.com'
    SENDERNAME = 'Your  name'
    MAILTO = user_to_add
    USERNAME_SMTP = "your username"
    PASSWORD_SMTP = "your password"
    HOST = "email-smtp.us-west-2.amazonaws.com"
    PORT = 587
    SUBJECT = 'VPN ACCESS'

    # clients without html.
    BODY_TEXT =(BODY)
    # clients with html.
    BODY_HTML = BODYHTML

    msg = MIMEMultipart('alternative')
    msg ['Subject'] = SUBJECT
    msg ['From'] = email.utils.formataddr((SENDERNAME, SENDER))
    msg ['To'] = MAILTO

    part1 = MIMEText(BODY_TEXT, 'plain')
    part2 = MIMEText(BODY_HTML, 'html')

    msg.attach(part1)
    msg.attach(part2)

    #send mail
    try:
        server = smtplib.SMTP(HOST, PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(USERNAME_SMTP, PASSWORD_SMTP)
        server.sendmail(SENDER, MAILTO, msg.as_string())
        server.close()

    #if something goes wrong print error.
    except Exception as e:
        print("Error:", e)
    else:
        print("########## Email sent ##########")


    #Delete user

def Delete_user(user_to_delete):
    disconnect_user = """sudo sh/usr/local/openvpn_as/scripts/sacli --user {} DisconnectUser""". format(user_to_delete)
    delete_user = """sudo sh/usr/local/openvpn_as/scripts/sacli --user {} UserPropDelAll""". format(user_to_delete)
    try:
        print("Deleting user ...")
        print("Clients connected from user {}:". format(user_to_delete))
        subprocess.run(disconnect_user, timeout = 10, shell = True)
        subprocess.run(delete_user, timeout = 10, shell = True)
        print("########## User {} DELETED ##########". format(user_to_delete))
    except:
        print("Could not delete user {}". format(user_to_delete))

def New_token_GA(user_new_ga):
    reset_google_authenticator = """sudo sh/usr/local/openvpn_as/scripts/sacli --user {} GoogleAuthRegen""". format(user_new_ga)
    try:
        print("Generating new token ...")
        subprocess.run(reset_google_authenticator, timeout = 10, shell = True)
        print("########## New Generated Token ##########". format(user_new_ga))
    except:
        print("Could not generate token for user {}". format(user_new_ga))

#interactive
while True:
    print("""
########## OPENVPN  ##########
    """)
    print("""Simple user manager for OPENVPN ACCESS SERVER EMAIL INVITE
    """)
    print("""Enter an option:

    1 - Add 1 user.
    2 - Add user using users_to_add.txt
    3 - Deletion of 1 user.
    4 - Deleting users with users_to_delete.txt
    5 - Generate new token for Google Authenticator
    6 - List Users.
    7 - Exit.
    """)
    option = str(input("Enter your option and press enter:"))

    #Actions
    if option == '1':
        user_to_add = str(input("enter mail for the new user and press enter:"))
        group_to_add = str(input("""enter the group for the new user and press enter(By default "Default"):"""))
        while True:
            validation = str(input("An email will be sent to {}, sure ?? Press enter to send ...". format(user_to_add)))
            Add_user_and_send_email(user_to_add)
            break

    if option == '2':
        directory = os.path.dirname(os.path.abspath(__file__))
        users_to_add = open(directory + "/users_to_add.txt", "r"). readlines()
        group_to_add = str(input("""enter the group for the new user and press enter(By default  "Default"):"""))
        while True:
            print("Mail will be sent to:")
            for user_to_add in users_to_add:
                print(user_to_add.rstrip())
            validation = str(input("Is the list correct ?, press enter to continue."))
            for user_to_add in users_to_add:
                Add_user_and_send_email(user_to_add.rstrip())
            break

    if option == '3':
        user_to_delete = str(input("enter user's mail to DELETE and press enter:"))
        while True:
            validation = str(input("This DELETES the user {} and removes her access to the server, sure ?? Press enter to DELETE ...". format(user_to_delete)))
            Delete_user(user_to_delete)
            break

    if option == '4':
        directory = os.path.dirname(os.path.abspath(__file__))
        users_to_delete = open(directory + "/users_to_delete.txt", "r"). readlines()
        while True:
            print("User accounts WILL be DELETED:")
            for user_to_delete in users_to_delete:
                print(user_to_delete.rstrip())
            validation = str(input("Is the list correct ?, press enter to DELETE THE ACCOUNTS."))
            for user_to_delete in users_to_delete:
                Delete_user(user_to_delete.rstrip())
            break

    if option == '5':
        user_new_ga = str(input("enter user's mail to generate new token and press enter:"))
        while True:
            validation = str(input("This generates a new token to user {}, sure ?? Press enter to GENERATE ...". format(user_new_ga)))
            New_token_GA(user_new_ga)
            break

    if option == '6':
        while True:
            list_users = """sudo sh/usr/local/openvpn_as/scripts/sacli EnumClients"""
            subprocess.run(list_users, timeout = 10, shell = True)
            break

    if option == '7':
        print("""
Goodbye.
        """)
        exit()