# Import libraries
import sys
from termcolor import cprint

# Get user email and password
email = input("Type your email address: ")
password = input("Password: ")

# Function to verify password
def confirm_password(password):
    cur_password = input("Re-type password to confirm: ")
    if password == cur_password:
        cprint("Congratulations! You've signed up successfully.", 'green')
        return
    else: 
        cprint("X", 'red', end=' ')
        print("Passwords do not match.")
        confirm_password(password)    

# Function caller
confirm_password(password)
