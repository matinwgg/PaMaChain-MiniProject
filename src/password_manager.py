# GUI Python Password Manager by matinwgg
# License: [Yet-to-be]
# Author: Odoom Abdul-Matin


import tkinter
import pyperclip
import csv
import hashlib
from PIL import Image
from CTkTableRowSelector import *
import tkinter as tk
import customtkinter as ctk
from customtkinter import *
from CTkTable import *


LABEL_FONT = ("Sans-Serif", 17)
BUTTON_FONT = ("Roboto", 16, "bold")
ENTRY_FONT = ("Sans-Serif", 23)
SMALL_LABEL_FONT = ("Sans-Serif", 15, "bold")

value = []


def display_username():
    try:
        with open(app.file1, "r", newline="") as csvfile:
            lines = csv.DictReader(csvfile, fieldnames=[
                "username", "password"])
            if lines:
                for row in lines:
                    username = row['username']
                    value.append([username])
                return value
            else:
                return []
    except FileNotFoundError():
        print("File not found")


class AddPasswordPage(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.geometry("700x600")
        self.resizable(False, False)
        self.title("Add a password")

        self.back = ctk.CTkButton(
            master=self, font=BUTTON_FONT, text="back",  fg_color='#242424', hover_color='#383838')
        self.back.place(relx=2, rely=2)

        self.label = ctk.CTkLabel(self, text="Add Password")
        self.label.pack(padx=10, pady=0)

        self.wallpaper = ctk.CTkImage(
            dark_image=Image.open("pattern.png"), size=(800, 800))
        self.wall_pic = ctk.CTkLabel(
            master=self, image=self.wallpaper, text='')
        self.wall_pic.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        self.frame1 = ctk.CTkFrame(
            master=self.wall_pic, corner_radius=15, width=500, height=300)
        self.frame1.place(relx=0.5, rely=0.5, relwidth=0.6,
                          relheight=0.4, anchor=ctk.CENTER)

        # Username label & Entry
        self.label_site = ctk.CTkLabel(
            master=self.frame1, text="Site", font=LABEL_FONT, width=30)
        self.label_site.pack(padx=50, pady=(40, 0), anchor=W)

        # Site entry
        self.placeholder_text = "\t\t\texample@mail.com"
        self.site = ctk.CTkEntry(
            master=self.frame1, corner_radius=10, height=35, font=LABEL_FONT, placeholder_text=self.placeholder_text, justify="left")
        self.site.focus()
        self.site.pack(padx=(50, 80), pady=(5, 10), fill=BOTH)

        # Password label & Entry
        self.label_password = ctk.CTkLabel(
            master=self.frame1, text="Password", font=LABEL_FONT, width=30)
        self.label_password.pack(padx=50, pady=(10, 0), anchor=W)
        self.password = ctk.CTkEntry(
            master=self.frame1, corner_radius=10, show='•', height=35, font=LABEL_FONT)
        self.password.pack(padx=(50, 80), pady=(5, 20), fill=BOTH)

        self.save_password = ctk.CTkButton(
            master=self.frame1, font=BUTTON_FONT, text="Save password", command=self.set_data)
        self.save_password.pack(
            padx=(50, 80), pady=(20, 30), ipady=4, fill=BOTH)

        self.file_1 = app.file1

    def get_row_of_site(self):
        self.idx = 0
        self.this_site = self.site.get()[0][0]

        with open(self.file_1, "r",) as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=[
                "username", "password"])
            for row in reader:
                if row['username'] == self.this_site.strip():
                    return self.idx
                self.idx += 1
        return None

    def is_site_present(self):
        with open(self.file_1, "r", newline="") as csvfile:
            reader = csv.DictReader(
                csvfile, fieldnames=["username", "password"])
            for row in reader:
                if row['username'] == self.site.get()[0][0]:
                    return self.get_row_of_site()
            return None

    def set_data(self):
        if self.site.get() and self.password.get():
            f = open(self.file_1, "r", newline="")
            reader = csv.DictReader(
                f, fieldnames=["username", "password"])

            with open(self.file_1, "a", newline="") as csvfile:
                writer = csv.DictWriter(
                    csvfile, fieldnames=["username", "password"])

                for self.row in reader:
                    if self.row == self.is_site_present():
                        self.row['password'] = self.password.get()

                        writer.writerow(
                            {"site": self.site.get().rstrip(), "password": self.password.get()})
                        break
                writer.writerow(
                    {"username": self.site.get().rstrip(), "password": self.password.get()})
            self.clear_frame()
        else:
            error_message = "Entry cannot be blank"
            self.err = ctk.CTkLabel(
                master=self.self.frame1, height=15, text=error_message, font=("Sans-Serif", 15, "bold"), text_color='#af1717')
            self.err.place(relx=0.4, rely=0.45)

    def clear_frame(self):
        # Get the list of child widgets in the frame
        self.widgets = self.frame1.winfo_children()

        # Destroy each child widget
        for widget in self.widgets:
            widget.destroy()

        # Update the GUI
        self.frame1.update()

        self.saved_msg()

    def saved_msg(self):
        self.msg = "Your password has been saved successfully"

        self.some_text = ctk.CTkLabel(
            master=self.frame1, font=("Adobe Garamond Pro", 20, "bold"), text=self.msg, wraplength=250)
        self.some_text.pack(
            padx=(50, 80), pady=(40, 30), fill=BOTH)
        self.exit_btn = ctk.CTkButton(
            master=self.frame1, font=BUTTON_FONT, text="Exit", command=self.exit_window)
        self.exit_btn.pack(
            padx=(60), pady=(30), fill=BOTH)

        display_username()

    def exit_window(self):
        self.destroy()


class App(ctk.CTk, AddPasswordPage):
    def __init__(self):
        super().__init__()
        self.title("Password Manager")
        self.geometry("1000x900")
        self.resizable(False, False)
        self.initial_page()

    def initial_page(self):
        self.wallpaper = ctk.CTkImage(
            dark_image=Image.open("pattern.png"), size=(1000, 1000))
        self.wall_pic = ctk.CTkLabel(
            master=self, image=self.wallpaper, text='')
        self.wall_pic.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        # Create a custom frame
        self.initial_frame = ctk.CTkFrame(
            master=self.wall_pic, corner_radius=15)
        self.initial_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER,
                                 relheight=0.55, relwidth=0.5)

        # Set profile picture
        self.profile_pic = ctk.CTkImage(Image.open(
            "padlock.png"),  size=(80, 80))
        self.pic = ctk.CTkLabel(
            master=self.initial_frame, image=self.profile_pic, text='')
        self.pic.place(relx=0.5, rely=0.15, anchor=ctk.CENTER)

        username = "User name"
        password = "Password"

        # Username label
        self.label_username = ctk.CTkLabel(
            master=self.initial_frame, text=username, font=LABEL_FONT, width=30)
        self.label_username.pack(padx=70, pady=(150, 0), anchor=W)

        # Username field
        self.initial_entry_username = ctk.CTkEntry(
            master=self.initial_frame,  height=31, width=370, font=ENTRY_FONT)
        self.initial_entry_username.pack(
            padx=25, pady=(8, 0))  # pady= 120, 10
        self.initial_entry_username.focus()

        # Password label
        self.label_password = ctk.CTkLabel(
            master=self.initial_frame, text=password, font=LABEL_FONT, width=30)
        self.label_password.pack(padx=70, pady=(15, 0), anchor=W)

        # Password field with eye button
        self.initial_entry_password = ctk.CTkEntry(
            master=self.initial_frame, show='•', height=31, width=370, font=ENTRY_FONT)
        self.initial_entry_password.pack(padx=25, pady=0)

        # Login Button
        self.button_login = ctk.CTkButton(
            self.initial_frame, text="Login", command=self.check_pwd, width=350, height=30, font=BUTTON_FONT)
        self.button_login.pack(padx=25, pady=(50, 0))

        # Add account Button
        self.button_create_account = ctk.CTkButton(
            master=self.initial_frame, text="Add Account", command=self.create_account, width=350, height=30, font=BUTTON_FONT)
        self.button_create_account.pack(
            padx=25, pady=(0, 100), side="bottom")

        self.label_base_msg = ctk.CTkLabel(
            self, text="Powered by matinwgg corp.", font=('Helvetica', 20))
        self.label_base_msg.pack(pady=(0, 10), side="bottom")

    def check_pwd(self):
        try:
            flag = False
            if self.initial_entry_username.get() or self.initial_entry_password.get():
                self.file1 = self.initial_entry_username.get(
                )[-3:] + "vault.csv"
                self.chk_pwd = hashlib.sha256(
                    self.initial_entry_password.get().encode()).hexdigest()
                with open("password.csv", "r") as csvfile:
                    reader = csv.DictReader(csvfile, fieldnames=[
                                            "username", "password"])
                    for row in reader:
                        if row['username'] == self.initial_entry_username.get():
                            if self.chk_pwd == row['password']:
                                self.login()
                                flag = True
                    if flag == False:
                        self.error_message = "Provide valid username and password"
                        self.err = ctk.CTkLabel(
                            master=self.initial_frame, height=15, text=self.error_message, font=SMALL_LABEL_FONT, text_color='#af1717')
                        self.err.place(relx=0.4, rely=0.45)
            else:
                self.error_message = "Provide valid username and password"
                self.err = ctk.CTkLabel(
                    master=self.initial_frame, height=15, text=self.error_message, font=SMALL_LABEL_FONT, text_color='#af1717')
                self.err.place(relx=0.4, rely=0.43)
        except FileNotFoundError as e:
            self.error_message = "Make sure that you have an account"
            self.err = ctk.CTkLabel(
                master=self.initial_frame, height=15, text=self.error_message, font=SMALL_LABEL_FONT, text_color='#af1717')
            self.err.place(relx=0.4, rely=0.28)

    def create_account(self):
        self.initial_frame.pack_forget()

        self.label_base_msg.pack_forget()

        # Set a new initial_frame
        self.create_account_frame = ctk.CTkFrame(
            master=self, corner_radius=15)
        self.create_account_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
        self.create_account_frame.pack(
            padx=(50, 50), pady=(60, 60), fill="both", expand=True)

        # Navigate to previous page
        self.back_button = ctk.CTkButton(
            master=self.create_account_frame, text="Back", width=60, height=50, corner_radius=12, command=self.exit_window, font=BUTTON_FONT)
        self.back_button.place(relx=0.07, rely=0.05)

        # Make create account label
        self.label_create_account = ctk.CTkLabel(
            master=self.create_account_frame, text="Create a new account", font=("Nanum Gothic", 30, "bold"), width=30)
        self.label_create_account.pack(pady=(130, 10))

        # Make a confirmation message to user his account has been created
        self.label_font = ctk.CTkFont(
            family="Sans-Serif", size=14)

        self.entry_font = ctk.CTkFont(
            family="Sans-Serif", size=14)

        self.password_entry = ctk.CTkFont(
            family="Sans-Serif", size=20)

        # email
        self.lbl_email = ctk.CTkLabel(
            master=self.create_account_frame, text="Email", font=LABEL_FONT)
        self.lbl_email.pack(padx=280, pady=(20, 0), anchor=ctk.W)
        self.entry_email = ctk.CTkEntry(
            master=self.create_account_frame, placeholder_text="", height=35, width=370, font=ENTRY_FONT)
        self.entry_email.pack(padx=(280, 240), pady=(0, 5), anchor=ctk.W)

        # username
        self.lbl_username = ctk.CTkLabel(
            master=self.create_account_frame, text="Username", font=LABEL_FONT)
        self.lbl_username.pack(padx=280, pady=(10, 0), anchor=ctk.W)
        self.entry_username = ctk.CTkEntry(
            master=self.create_account_frame, height=35, width=370, font=ENTRY_FONT)
        self.entry_username.pack(padx=(280, 240), pady=(0, 5), anchor=ctk.W)

        # Password
        self.lbl_pwd = ctk.CTkLabel(
            master=self.create_account_frame, text="Password", font=LABEL_FONT)
        self.lbl_pwd.pack(padx=280, pady=(5, 0), anchor=ctk.W)
        self.entry_password = ctk.CTkEntry(
            master=self.create_account_frame, height=35, show='•', width=370,  font=ENTRY_FONT)
        self.entry_password.pack(padx=(280, 240), pady=(0, 5), anchor=ctk.W)

        # Confirm password
        self.lbl_confirm = ctk.CTkLabel(
            master=self.create_account_frame, text="Confirm password", font=LABEL_FONT)
        self.lbl_confirm.pack(padx=280, pady=(5, 0), anchor=ctk.W)
        self.entry_confirm_password = ctk.CTkEntry(
            master=self.create_account_frame, height=35, show='•', width=370,  font=ENTRY_FONT)
        self.entry_confirm_password.pack(
            padx=(280, 240), pady=(0, 0), anchor=ctk.W)

        # Make a DONE button to exit the application
        self.create_button = ctk.CTkButton(
            master=self.create_account_frame, text="Create account", font=LABEL_FONT, height=35, width=370, command=lambda: self.register())
        self.create_button.pack(padx=(280, 240), pady=(60, 0))
       # Check csv file for already existing user details

    def is_user_present(self, username, password):
        with open("password.csv", "r") as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=[
                                    "username", "password"])
            for row in reader:
                if row['username'] == username or row['password'] == password:
                    return True
        return False

    def get_file(self):
        self.filename = self.entry_username.get()[-3:] + "vault.csv"
        with open(self.filename, 'w') as f:
            pass

        return self.filename

    def register(self):
        self.initial_frame.pack_forget()
        self.get_file()
        if self.entry_username.get() == "" or self.entry_password.get() == "":
            self.error_msg = "Required"
            for i in range(3):
                self.error = ctk.CTkLabel(
                    master=self.create_account_frame, height=15, text=self.error_msg, font=LABEL_FONT, text_color='#af1717')
                self.error.place_configure(relx=0.6, rely=0.33)
                if i == 1:
                    self.error.place_configure(relx=0.6, rely=0.48)
                if i == 2:
                    self.error.place_configure(relx=0.6, rely=0.62)
            # Destroy error label when username and password entries are focused
            if self.entry_username.focus() or self.entry_password.focus() or self.entry_confirm_password.focus():
                self.error.destroy()

        elif self.entry_password.get() == self.entry_confirm_password.get():
            self.hashed_password = hashlib.sha256(
                self.entry_password.get().encode()).hexdigest()
            # Save the hashed password in a .csv file
            with open("password.csv", "a", newline="") as file:
                writer = csv.DictWriter(
                    file, fieldnames=["username", "password"])
                writer.writerow(
                    {"username": self.entry_username.get().rstrip(), "password": self.hashed_password})
            self.clear_register_frame()

        # Is username and password already set?
        elif self.is_user_present(self.entry_username.get(), self.entry_password.get()):
            self.error_msg = "Username already exists!"
            self.error = ctk.CTkLabel(
                master=self.create_account_frame, text=self.error_msg, font=LABEL_FONT, text_color='#af1717')
            self.error.place(relx=0.5, rely=0.30)

        elif self.entry_password.get() != self.entry_confirm_password.get():
            self.error_msg = "Passwords do not match!"
            self.error = ctk.CTkLabel(
                master=self.create_account_frame, text=self.error_msg, font=LABEL_FONT, text_color='#af1717')
            self.error.place(relx=0.5, rely=0.5)

    def clear_register_frame(self):
        # Get the list of child widgets in the frame
        self.widgets = self.create_account_frame.winfo_children()

        # Destroy each child widget
        for widget in self.widgets:
            widget.destroy()

        # Update the GUI
        self.create_account_frame.update()

        self.saved_msg_()

    def saved_msg_(self):
        self.msg = "You have successfully created a new account"

        self.some_text = ctk.CTkLabel(
            master=self.create_account_frame, font=("Sans-Serif", 30, "bold"), text=self.msg, wraplength=400)
        self.some_text.pack(
            padx=(50, 80), pady=(200, 30), fill=BOTH)
        self.exit_btn = ctk.CTkButton(
            master=self.create_account_frame, font=BUTTON_FONT, text="Exit", command=self.exit_window)
        self.exit_btn.pack(
            padx=200, pady=(30), fill=BOTH)

    def exit_window(self):
        self.create_account_frame.pack_forget()
        self.initial_page()

    def callbacks(self, choice):
        self.filename_ = self.file1
        if choice == "Copy":
            self.copy()
        if choice == "Delete":
            self.delete()

    def index(self):
        self.idx = 0
        self.url = self.row_selector.get()[0][0]

        with open(self.filename_, "r",) as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=[
                "username", "password"])
            for row in reader:
                if row['username'] == self.url.strip():
                    return self.idx
                self.idx += 1
        return None

    def delete(self):
        self.index_to_delete = self.index()
        if self.index_to_delete is None:
            return

        with open(self.filename_, "r",) as csvfile:
            lines = csvfile.readlines()

        with open(self.filename_, "w",) as csvfile:
            for i, row in enumerate(lines):
                if i != self.index_to_delete:
                    csvfile.write(row)

        self.table.delete_row(self.index_to_delete)

        self.delete_msg = ctk.CTkLabel(
            master=self, text="Deleted!", text_color="#15e60a", font=("sans-serif", 20, "bold"))
        self.delete_msg.place(relx=0.16, rely=0.05)

    def copy(self):
        self.delete_msg = None
        with open(self.filename_, "r", newline="") as csvfile:
            lines = csv.DictReader(csvfile, fieldnames=[
                "username", "password"])
            for self.row in lines:
                self.url = self.row_selector.get()[0][0]
                if self.row['username'].strip() == self.url.strip():
                    pyperclip.copy(self.row['password'])
                    break
                else:
                    ...

        self.copied_msg = ctk.CTkLabel(
            master=self, text="Copied!", text_color="#15e60a", font=("sans-serif", 20, "bold"))
        if self.delete_msg:
            self.delete_msg.place_forget()
            self.copied_msg.place(relx=0.16, rely=0.05)
        else:
            self.copied_msg.place(relx=0.16, rely=0.05)

    def login(self):
        self.initial_frame.place_forget()
        self.add_password_page = None

        self.title("Saved Passwords")

        # Navigate to previous page
        self.back_button = ctk.CTkButton(
            master=self, text="Back", width=70, height=40, font=BUTTON_FONT, corner_radius=12, command=self.exit_win)
        self.back_button.place(relx=0.03, rely=0.04)

        self.guide_text = ctk.CTkLabel(
            master=self, text="Create, save and manage your passwords\n that you can easily sign in\n to sites and apps.", text_color="#7d7a7a", font=("sans-serif", 15))
        self.guide_text.place(relx=0.3, rely=0.03)

        self.add_password_button = ctk.CTkButton(
            master=self, text="Add Password", font=BUTTON_FONT, height=35, width=160, command=self.add_to_passwords)
        self.add_password_button.place(relx=0.82, rely=0.07)

        self.option = ctk.StringVar(value="Options")
        self.option_menu = ctk.CTkOptionMenu(master=self, values=[
            "Copy", "Delete"],
            height=35, width=160, command=self.callbacks, variable=self.option, font=BUTTON_FONT)
        self.option_menu.place(relx=0.62, rely=0.07)

        # # Make a scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(
            master=self, width=950, height=800)
        self.scrollable_frame.pack(padx=10, pady=(130, 0))

        self.table = CTkTable(master=self.scrollable_frame,
                              row=50, column=1, values=display_username(), font=LABEL_FONT, anchor='w', corner_radius=0)
        self.table.pack(expand=True, fill="both", padx=10, pady=10)

        # Add the selector
        self.row_selector = CTkTableRowSelector(
            self.table, can_select_headers=True)

        self.text = self.row_selector.get()

        self.label_base_msg.pack_forget()

    def clear_frame(self):
        # Get the list of child widgets in the frame
        self.widgets = self.scrollable_frame.winfo_children()

        # Destroy each child widget
        for widget in self.widgets:
            widget.destroy()

        # Update the GUI
        self.create_account_frame.update()

        self.exit_win()

    def exit_win(self):
        self.scrollable_frame.pack_forget()
        self.initial_page()

    def add_to_passwords(self):
        if self.add_password_page is None or not self.add_password_page.winfo_exists():
            # create window if its None or destroyed
            self.add_password_page = AddPasswordPage()
        else:
            self.add_password_page.set_data()


if __name__ == '__main__':
    # Create an instance of the App class
    app = App()

    # Start the main event loop
    app.mainloop()
