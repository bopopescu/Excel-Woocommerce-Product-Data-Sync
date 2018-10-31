# -*- coding: utf-8 -*-

# for the creation of the executable, follow the instructions below (package installed):
# https://medium.com/dreamcatcher-its-blog/making-an-stand-alone-executable-from-a-python-script-using-pyinstaller-d1df9170e263


from Tkinter import *
import tkMessageBox
import tkFileDialog
import ttk

from utilities.woocommerce_updater import WooCommerceUpdater


class ExcelWoocommerceSyncApplication(Frame):
    """
    class for creating the user interface of our application
    """

    def openFileDialogWindow(self):
        """
        Method called when pressing the OPEN_FILE button
        :return:
        """
        # enable editing
        self.TXT_FILE_PATH['state'] = 'normal'
        self.filePath = tkFileDialog.askopenfilename(initialdir="/",
                                                     title=u"Επιλογή αρχείου με τιμές",
                                                     filetypes=(("Excel", "*.xlsx"), ("Excel 1997-2003", "*.xls")))
        # first delete the existing contents of the textbox (if there are any)
        self.TXT_FILE_PATH.delete("%d.%d" % (1, 0), END)
        # insert the path in the textbox
        self.TXT_FILE_PATH.insert("%d.%d" % (1, 0), self.filePath)
        # disable editing
        self.TXT_FILE_PATH['state'] = 'disabled'

    def updateWoocommerceProductData(self):
        """
        Method called when pressing the UPDATE_WOOCOMMERCE button
        :return:
        """
        # start the process of importing the data
        updateResult, errorMessage = \
            WooCommerceUpdater.importDataInWoocommerce(
                self.filePath, self.PGB_UPDATE_PROGRESS_BAR, self.LBL_STATUS
            )
        # inform the user about the result of the operation
        if updateResult == False:
            tkMessageBox.showerror(u'Πρόβλημα', u'Πρόβλημα! '+errorMessage)
        else:
            tkMessageBox.showinfo(u'Επιτυχία', u'Η ενημέρωση των τιμών έγινε με επιτυχία')

    def cancelOperation(self):
        """
        Method for cancelling the operation and closing the program
        :return:
        """
        self.quit()

    def createWidgets(self):
        """
        method for creating the widgets of the application
        :return:
        """

        # object variable for storing the file path of the excel file
        self.filePath = ''

        # initialization of the text element that will display the file path
        self.TXT_FILE_PATH = Text(self, background='grey', height=1)

        # button for opening a file to import
        self.BTN_OPEN_FILE = Button(self)
        self.BTN_OPEN_FILE['text'] = u'Άνοιγμα αρχείου'
        self.BTN_OPEN_FILE['command'] = self.openFileDialogWindow
        self.BTN_OPEN_FILE.pack(side=LEFT)

        # pack the file path textbox

        self.TXT_FILE_PATH.pack(side=LEFT, padx=10)

        # button for starting the process of updating woocommerce product data
        self.BTN_UPDATE_WOOCOMMERCE = Button(self)
        self.BTN_UPDATE_WOOCOMMERCE['text'] = u'Ενημέρωση στοιχείων προϊόντων Eshop'
        self.BTN_UPDATE_WOOCOMMERCE['command'] = self.updateWoocommerceProductData
        self.BTN_UPDATE_WOOCOMMERCE.pack(side=LEFT)

        # button for the cancel button
        self.BTN_CANCEL = Button(self)
        self.BTN_CANCEL['text'] = u'Άκυρο'
        self.BTN_CANCEL['command'] = self.cancelOperation
        self.BTN_CANCEL.pack(padx=6, side=LEFT)

        # progress bar
        self.PGB_UPDATE_PROGRESS_BAR = ttk.Progressbar(self, orient='horizontal', length=200, mode='determinate')
        self.PGB_UPDATE_PROGRESS_BAR.pack(padx=6, side=LEFT)

        # status label
        self.LBL_STATUS = Label(self, width=20)
        self.LBL_STATUS.pack(padx=6)

    def __init__(self, master=None):
        """
        Constructor method
        :param master:
        """

        Frame.__init__(self, master)
        self.pack()
        # create the widgets of the application
        self.createWidgets()


# create a top level widget - this is the main application window
"""
root = Tk()
root.title(u'Εφαρμογή ενημέρωσης τιμών e-shop')
app = ExcelWoocommerceSyncApplication(master=root)
app.mainloop()
root.destroy()
"""
