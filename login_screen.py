# -*- coding: utf-8 -*-
"""
Code for creating a login screen
"""

from Tkinter import *
import tkMessageBox
import hashlib

from main_app import ExcelWoocommerceSyncApplication


class LoginForm(Frame):
    """
    class that creates a simple login screen
    """

    # credentials for logging in the application
    USERNAME = 'captain'
    PASSWORD_HASH = '64610dc7f1d1b871a5c048fae4c86d8f710791fd25b8cd1de07bca35'  # password hash using sha224

    # class variable that holds the form root
    FORM_ROOT = Tk()

    def okButtonPressed(self, event):
        """
        method for when the ok button is pressed
        :return:
        """
        # get the username and password from the textboxes
        username = self.TXT_USERNAME.get()
        pwdHash = hashlib.sha224(self.TXT_PASSWORD.get()).hexdigest()

        # open the main form, if the credentials are right
        if username == LoginForm.USERNAME and pwdHash == LoginForm.PASSWORD_HASH:  # if the credentials are right
            # when checking the username, I added \n because it is automatically added to the textfield
            LoginForm.FORM_ROOT.destroy()  # close the login form
            # open the form for updating Woocommerce
            root = Tk()
            root.title(u'Εφαρμογή ενημέρωσης τιμών e-shop')
            app = ExcelWoocommerceSyncApplication(master=root)
            app.mainloop()
        else:  # wrong credentials
            tkMessageBox.showerror(u'Πρόβλημα Σύνδεσης', u'Τα στοιχεία σύνδεσης δεν είναι σωστά')


    def cancelButtonPressed(self, event):
        """
        method for when the cancel button is pressed
        :return:
        """
        self.quit()

    def createWidgets(self):
        """
        method for creating the widgets that appear on the login screen
        :return:
        """
        self.LBL_USERNAME = Label(self, text=u'Όνομα χρήστη', width=20)
        self.TXT_USERNAME = Entry(self, width=20)
        self.LBL_PASSWORD = Label(self, text=u'Κωδικός', width=20)
        self.TXT_PASSWORD = Entry(self, show="*", width=20)

        self.BTN_OK = Button(self, text='OK', width=10)
        # self.BTN_OK['command'] = self.okButtonPressed
        self.BTN_OK.bind('<Return>', self.okButtonPressed)  # bind the Enter keyboard button to OK
        self.BTN_OK.bind('<Button-1>', self.okButtonPressed)  # bind the left mouse click to OK

        self.BTN_CANCEL = Button(self, text=u'Άκυρο', width=10)
        # self.BTN_CANCEL['command'] = self.cancelButtonPressed
        self.BTN_CANCEL.bind('<Return>', self.cancelButtonPressed)  # bind the Enter keyboard button to Cancel
        self.BTN_CANCEL.bind('<Button-1>', self.cancelButtonPressed)  # bind the left mouse click to OK

        # setup the position of the widgets
        self.LBL_USERNAME.grid(row=0, column=0)
        self.TXT_USERNAME.grid(row=0, column=1)
        self.LBL_PASSWORD.grid(row=1, column=0)
        self.TXT_PASSWORD.grid(row=1, column=1)
        self.BTN_OK.grid(row=2, column=0)
        self.BTN_CANCEL.grid(row=2, column=1)

        self.TXT_USERNAME.focus()  # set the keyboard focus on username textfield

    def __init__(self, master=None):
        """
        constructor method
        :param master:
        """
        Frame.__init__(self, master)
        self.pack()
        # create the widgets of the application
        self.createWidgets()


# create a top level widget - this is the main application window
# root = Tk()
LoginForm.FORM_ROOT.geometry("500x70")
LoginForm.FORM_ROOT.title(u'Εφαρμογή ενημέρωσης τιμών e-shop - Είσοδος')
app = LoginForm(master=LoginForm.FORM_ROOT)
app.mainloop()
LoginForm.FORM_ROOT.destroy()