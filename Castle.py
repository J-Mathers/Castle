#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Castle password manager:

"""


from multiprocessing import Process, Manager
import sqlite3
import os
import gnupg
import tkinter
from tkinter import END, StringVar, IntVar, Toplevel, GROOVE, filedialog
import xerox
import string
import random
import platform
import gc



        
#class containing window and functionality to add column to currently displayed table
class Add_Column:
 
    def __init__(self, table_view):
        
        #Save needed items into instance atributes to reference later
        self.table_view = table_view
        self.db = table_view.db
        self.table_name = table_view.table_name
        
        #Define add column window
        self.column_window = tkinter.Toplevel()
        self.column_window.geometry("420x150")
        self.column_window.title("Castle")
        self.column_window.resizable(0, 0)
        self.column_window.config(bg="white")
        
        #Event handler to detect window manually closed by user
        self.column_window.protocol(
                "WM_DELETE_WINDOW", self.__del__)
        
        #Define frames for spacers and to hold widgets
        self.button_frame = tkinter.Frame(
                self.column_window, bg="white")
        
        self.button_frame.grid(
                row=4, column=1, columnspan=3, pady=5)
        
        self.button_spacer = tkinter.Frame(
                self.button_frame, width=200, bg="white")
        
        self.button_spacer.grid(
                row=1, column=2)
        
        self.bottom_spacer = tkinter.Frame(
                self.column_window, height=15, bg="white")
        
        self.bottom_spacer.grid(
                row=3, column=1)

        #Define text entries and buttons
        self.column_label = tkinter.Label(
                self.column_window, text="Please enter the name for your new column",\
                bg="white", fg="#004aff", font=(
                "Sans-serif", 12, "bold"))
        
        self.column_label.grid(
                row=1, column=1, columnspan=3, pady=5, padx=5)
                                          
        self.column_name = tkinter.Entry(
                self.column_window, width=15, bg="white", font=(
                        "Sans-serif", 10, "bold"))
        
        self.column_name.grid(
                row=2, column=2, pady=5)
        
        self.submit_button = tkinter.Button(
                self.button_frame, text="Submit", command=lambda :self.submit(
                        ), fg="white", bg="#187bcd", activeforeground="white",\
                        activebackground="#4e97fe")
                        
        self.submit_button.grid(
                row=1, column=3, pady=5)
        
        self.cancel_button = tkinter.Button(
                self.button_frame, text="Cancel", command=self.__del__,
                fg="white", bg="#187bcd", activeforeground="white",\
                activebackground="#4e97fe")
                                            
        self.cancel_button.grid(
                row=1, column=1, pady=5)
        
        
    #function to handle creation of new column in current table
    def submit(self):

        #Safety check to prevent problematic characters in column name
        if check_forbidden_characters(self.column_name.get()) == 0:

            #Get list of column names to compare against
            self.column_headings = get_column_headings(self.db, self.table_name, 0)
            
            #Safety check to ensure a name for the new column was given and doesnt conflict with existing column
            if self.column_name.get() != "" and\
            self.column_name.get() not in self.column_headings:
            
                #attempt to add new column to table
                if self.add_column(self.column_name.get()) == 0:
            
                    #Generate display of current table the close this window
                    self.table_view.refresh()

                    #Close window
                    self.__del__()
                
                else:
                    #if an error was encountered while creating new column inform user
                    Error_Message(
                            "column already exists or name not allowed!\n"\
                            + "Try using another name")
                    
            #if no name was entered for new column display error message
            else:
                Error_Message(
                        "Please enter a column name or click 'Cancel'")        
        
    def add_column(self, column_name):
        try:
            #create cursor to issue commands to database
            self.c = self.db.cursor()
        
            #generate command based on current table and given input
            sql = "ALTER TABLE '{0}' ADD {1} VARCHAR DEFAULT '';".format(
                    self.table_name, ("'" + self.column_name.get() + "'")) 
        
            #issue command and commit changes to database so we can use another cursor elsewhere
            self.c.execute(sql)
            self.db.commit()
            return 0
        #If any errors encountered altering database return 1
        except:
            return 1
        
    
    def __del__(self):
        self.column_label.destroy()
        self.column_name.destroy()
        self.submit_button.destroy()
        self.cancel_button.destroy()
        self.button_frame.destroy()
        self.bottom_spacer.destroy()
        self.button_spacer.destroy()
        try:
            del self.c
            del self.sql
        except:
            pass
        self.column_window.destroy()




#class containing window and functionality for adding new table to database
class Add_Table:
    
    def __init__(self, sidebar):
        #Save needed items into instance atributes to reference later
        self.sidebar = sidebar
        self.db = self.sidebar.db
        self.gpg = self.sidebar.gpg

        #Define top level window and widgets
        self.table_window = tkinter.Toplevel()
        self.table_window.geometry("400x600")
        self.table_window.config(bg="white")
        self.table_window.resizable(0, 0)

        #Event handler to detect window manually closed by user
        self.table_window.protocol(
                "WM_DELETE_WINDOW", lambda:self.cancel())
        
        #Define frames to hold widgets
        self.title_frame = tkinter.LabelFrame(
                self.table_window, text="Enter the title for your new table",\
                padx=15, pady=15, borderwidth=4, relief=GROOVE, bg="white",\
                fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.title_frame.grid(
                row=1, column=1)
        
        self.top_frame = tkinter.LabelFrame(
                self.table_window, text="Select new table style", padx=60,\
                pady=5, borderwidth=4, relief=GROOVE, bg="white",\
                fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.top_frame.grid(
                row=3, column=1)
        
        self.bottom_frame = tkinter.LabelFrame(
                self.table_window, text="Create custom table", padx=5,\
                pady=10, borderwidth=4, relief=GROOVE, bg="white",\
                fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.bottom_frame.grid(
                row=5, column=1)
        
        self.button_frame = tkinter.Frame(
                self.table_window, bg="white")
        
        self.button_frame.grid(
                row=7, column=1)
        
        #Define spacer frames
        self.side_spacer = tkinter.Frame(
                self.table_window, width=40, height=10, bg="white")
        
        self.side_spacer.grid(
                row=0, column=0)
        
        self.mid_spacer1 = tkinter.Frame(
                self.table_window, height=10, bg="white")
        
        self.mid_spacer1.grid(
                row=2, column=1)
        
        self.mid_spacer2 = tkinter.Frame(
                self.table_window, height=10, bg="white")
        
        self.mid_spacer2.grid(
                row=4, column=1)
        
        self.bottom_spacer = tkinter.Frame(
                self.table_window, height=5, bg="white")
        
        self.bottom_spacer.grid(
                row=6, column=1)

        self.button_spacer = tkinter.Frame(
                self.button_frame, width=115, bg="white")        
        
        self.button_spacer.grid(
                row=1, column=2)
        
        
        #Define widget for user input
        
        self.table_title = tkinter.Entry(
                self.title_frame, width=20, bg="white", font=(
                        "Sans-serif", 10, "bold"))
        
        self.table_title.pack()
        
        
        #Define variable for radio buttons
        self.table_style = IntVar()
        self.table_style.set(5)
        
        #Define radio buttons to select table style
        self.password_radio = tkinter.Radiobutton(
                self.top_frame, text="Password table", pady=5,\
                variable=self.table_style, value=1, bg="white", fg="#004aff",\
                activebackground="white", activeforeground="#1874CD")
        
        self.password_radio.pack()
        
        self.file_radio = tkinter.Radiobutton(
                self.top_frame, text="File table", pady=5,\
                variable=self.table_style, value=2, bg="white", fg="#004aff",\
                activebackground="white", activeforeground="#1874CD")
                
        self.file_radio.pack()
        
        self.note_radio = tkinter.Radiobutton(
                self.top_frame, text="Secure note table", pady=5,\
                variable=self.table_style, value=3, bg="white", fg="#004aff",\
                activebackground="white", activeforeground="#1874CD")
                
        self.note_radio.pack()
        
        self.card_radio = tkinter.Radiobutton(
                self.top_frame, text="Credit card table", pady=5,\
                variable=self.table_style, value=4, bg="white", fg="#004aff",\
                activebackground="white", activeforeground="#1874CD")
                
        self.card_radio.pack()
        
        self.custom_radio = tkinter.Radiobutton(
                self.bottom_frame, text="custom table", pady=5,\
                variable=self.table_style, value=5, bg="white", fg="#004aff",\
                activebackground="white", activeforeground="#1874CD")
                
        self.custom_radio.pack()
        
        self.fields_label = tkinter.Label(
                self.bottom_frame, text="Please enter column names.\n"\
                + "(e.g. column1, column2, column3.....)", bg="white",\
                fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.fields_label.pack()
        
        self.table_fields = tkinter.Text(
                self.bottom_frame, width=30, height=10, bg="white", font=(
                        "Sans-serif", 10, "bold"))
        
        self.table_fields.pack()
        
        
        #Define buttons for add table window
        self.ok_button = tkinter.Button(
                self.button_frame, text="Ok", command=lambda: self.submit(
                        self.table_style.get()), fg="white",\
                        bg="#187bcd", activeforeground="white",\
                        activebackground="#4e97fe", width=8)
                        
        self.ok_button.grid(
                row=1, column=3)
        
        self.cancel_button = tkinter.Button(
                self.button_frame, text="Cancel", command=lambda: self.cancel(
                        ), fg="white", bg="#187bcd", \
                        activeforeground="white", activebackground="#4e97fe",\
                        width=8)
                
        self.cancel_button.grid(
                row=1, column=1)
        
        
        
#function to close add table window and generate new sidebar controls
    def cancel(self):
        #Generate new sidebar controls
        self.sidebar.clear_buttons()
        self.sidebar.buttons()
        
        #destroy add table window
        self.__del__()
        
        
           
    #function to add table to database based on user input
    def submit(self, table_style):
        
        #Get new table title from entry box
        self.title = self.table_title.get().strip()
        
        #Check required information was provided by user
        if self.check_for_input(table_style) == 0:
        
            #Check no problematic characters were used in table or column names
            if check_forbidden_characters(self.title) == 0 and\
            check_forbidden_characters(self.table_fields.get("1.0", END)) == 0:
                
                #Generate command to issue to database
                self.fields_command = self.generate_command(table_style)
               
                #Check there were no issues generating command
                if self.fields_command != None:
                    try:
                        #create cursor object to interact with database
                        self.c = self.db.cursor()
        
                        #Issue generated command to database
                        self.c.execute(self.fields_command)
                        self.db.commit()
            
                        #Close window and regenerate sidebar controls
                        self.cancel()
         
                    except:
                        #If column names conflict sqlite will return an exception
                        Error_Message("Column names must be unique\nPlease check and try again")
        
    def __del__(self):

        self.table_title.destroy()
        self.password_radio.destroy()
        self.file_radio.destroy()
        self.note_radio.destroy()
        self.card_radio.destroy()
        self.custom_radio.destroy()
        self.fields_label.destroy()
        self.table_fields.destroy()
        self.ok_button.destroy()
        self.cancel_button.destroy()
        self.bottom_frame.destroy()
        self.top_frame.destroy()
        self.title_frame.destroy()
        self.button_frame.destroy()
        try:
            del self.table_style
        except:
            pass
        try:
            del self.title
            del self.fields_command
            del self.c
            del self.fields
        except:
            pass
        self.table_window.destroy()
        
    def check_for_input(self, table_style):
         #Safety check to make sure we were given a title
        if self.title == "":
            Error_Message(
                    "Please enter a title for your new table!")
            return 1
        
        #Safety check to ensure column names were given
        elif self.table_fields.get(
                "1.0", END).strip() == '' and table_style == 5:
            Error_Message(
                    "Please enter columns for your new group!")
            return 1
        
        #safety check to ensure a table with that name does not already exist
        elif self.title in get_tables(self.db):
            Error_Message(
                    "Table with this title already exists\n"\
                    + "Please choose another title and try again")
            return 1
        else:
            return 0
    
    
    
    def generate_command(self, table_style):
        #select or generate new table command based on selected style
        #If table style is password
        if table_style == 1:
            fields_command = "CREATE TABLE IF NOT EXISTS '" + self.title \
                                + "' (id INTEGER PRIMARY KEY NOT NULL, "\
                                +"Title TEXT NOT NULL, Username TEXT NOT NULL,"\
                                +"Password TEXT NOT NULL, Url TEXT NOT NULL,"\
                                +"'Security question' TEXT NOT NULL, "\
                                +"'Security answer' TEXT NOT NULL);"
        
        #If table style is file
        elif table_style == 2:
            fields_command = "CREATE TABLE IF NOT EXISTS '" + self.title + \
                                  "' (id INTEGER PRIMARY KEY NOT NULL, "\
                                  +"Title TEXT NOT NULL, File BLOB NOT NULL,"\
                                  +"Filename TEXT NOT NULL, Comments TEXT NOT NULL);"
            
        #If table style is secure note
        elif table_style == 3:
            fields_command = "CREATE TABLE IF NOT EXISTS '" + self.title +\
                                  "' (id INTEGER PRIMARY KEY NOT NULL, "\
                                  +"Title TEXT NOT NULL, Note TEXT NOT NULL);"
        
        #If table style is credit card
        elif table_style == 4:
            fields_command = "CREATE TABLE IF NOT EXISTS '" + self.title +\
                                 "' ('id' INTEGER PRIMARY KEY NOT NULL, "\
                                 +"'Title' TEXT NOT NULL, 'Cardholder name'"\
                                 +"TEXT NOT NULL, 'Card type' TEXT NOT NULL,"\
                                 +"'Card number' TEXT NOT NULL, 'CVV number' "\
                                 +"TEXT NOT NULL, 'Expiry date' TEXT NOT NULL,"\
                                 +"'Valid from' TEXT NOT NULL, 'Notes' TEXT NOT NULL);"
        
        #If table style is custom
        elif table_style == 5:
            #Declare string to create command with
            fields_command = ""
       
            #Get list of field names from text box and split at commas
            self.fields = self.table_fields.get(
                    "1.0", END).split(",")
            
            #Loop over list of field names and strip any left over whitespace
            for i in range(len(self.fields)):
                self.fields[i] = self.fields[i].strip()
            
            #Generate command to be issued from title and list of fields
            for i in range(len(self.fields)):
                fields_command = fields_command + "'" + self.fields[i]\
                                      + "'" + " VARCHAR DEFAULT '', "
                                      
            #Add standard parts of SQL query to complete command to be issued
            fields_command = "CREATE TABLE IF NOT EXISTS '" + self.title + \
                                  "' (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "\
                                  + fields_command[0:-2] + ");"
       
        return fields_command



#Class containing 2 option "confirmation" popup message
class Confirmation_Message:

    def __init__(self, parent, title_text, ok_text, cancel_text, label_text):
        #Define confirmation popup window
        self.popup = tkinter.Toplevel()
        self.popup.geometry("375x150")
        self.popup.title(title_text)
        self.popup.resizable(0, 0)
        self.popup.config(bg="white")
        
        #Define frame to hold text
        self.popup_frame = tkinter.Frame(
                self.popup, padx=30, pady=15, bg="white")
        
        self.popup_frame.grid(
                row=1, column=1)
        
        #Define frame to hold buttons
        self.popup_button_frame = tkinter.Frame(
                self.popup, padx=30, pady=10, bg="white")
        
        self.popup_button_frame.grid(
                row=2, column=1)
        
        #Define spacer for between buttons
        self.popup_spacer = tkinter.Frame(
                self.popup_button_frame, width=180, bg="white")
        self.popup_spacer.grid(
                row=2, column=2)
        
        #Define warning message
        self.popup_label = tkinter.Label(
                self.popup_frame, text=label_text,wraplength=375,\
                bg="white", fg="#004aff", font=(
                "Sans-serif", 12, "bold"))
        
        self.popup_label.grid(
                row=1, column=1, columnspan=3)
        
        #Define buttons
        self.popup_cancel = tkinter.Button(
                self.popup_button_frame, text=cancel_text, fg="white",\
                bg="#187bcd", activeforeground="white",\
                activebackground="#4e97fe")
        
        self.popup_cancel.grid(
                row=2, column=1)
        
        self.popup_ok = tkinter.Button(
                self.popup_button_frame, text=ok_text, width=5, fg="white",\
                bg="#187bcd", activeforeground="white",\
                activebackground="#4e97fe")
        
        self.popup_ok.grid(
                row=2, column=3)
        
        #Event handler to detect window manually closed by user
        self.popup.protocol(
                "WM_DELETE_WINDOW", self.__del__)
        
        #Destructor to completely delete popup
    def __del__(self):
        self.popup_cancel.destroy()
        self.popup_label.destroy()
        self.popup_ok.destroy()
        try:
            self.popup.destroy()
        except:
            pass
    
               
  


#Class containing create new db window and functionality
class Create_DB:
   
    def __init__(self, gpg, selection_window):
        #Save gpg into attribute for easy referencing
        self.gpg = gpg

        #Define window to get details for new db
        self.create_window = tkinter.Toplevel()
        self.create_window.title("Castle: Create Database")
        self.create_window.geometry("850x350+200+200")
        self.create_window.resizable(0, 0)
        self.create_window.config(bg="white")
        
        #Event handler to detect window manually closed by user
        self.create_window.protocol(
                "WM_DELETE_WINDOW", self.__del__)
        
        #Define frames to hold widgets
        self.input_frame = tkinter.LabelFrame(
                self.create_window, relief=GROOVE, borderwidth=4, padx=20,\
                pady=20, text="Enter details for new database", bg="white",\
                fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.input_frame.grid(
                row=1, column=1, rowspan=3)
        
        self.create_frame = tkinter.LabelFrame(
                self.create_window, relief=GROOVE, borderwidth=4, padx=30,\
                pady=15, text="Select database style", bg="white", \
                fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.create_frame.grid(
                row=1, column=3, columnspan=2)
        
        self.cancel_frame = tkinter.LabelFrame(
                self.create_window, relief=GROOVE, borderwidth=4, padx=50,\
                pady=15, text="Close window", bg="white", fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.cancel_frame.grid(
                row=3, column=4)
        
        self.spacer_frame = tkinter.Frame(
                self.create_window, width=50, height=50, bg="white")
        self.spacer_frame.grid(
                row=0, column=0)
        
        self.mid_spacer = tkinter.Frame(
                self.create_window, width=15, bg="white")
        
        self.mid_spacer.grid(
                row=1, column=2)
        
        
        #Define text entries and buttons for create_window
        self.db_label = tkinter.Label(
                self.input_frame, text="Select folder to create new database",\
                bg="white", fg="#004aff", font=(
                "Sans-serif", 12, "bold"))
        
        self.db_label.grid(
                row=1, column=1)
                                      
        self.db_loc = tkinter.Entry(
                self.input_frame, width=40, bg="white", font=(
                        "Sans-serif", 10, "bold"))
        
        self.db_loc.grid(
                row=2, column=1)
        
        self.db_browse_button = tkinter.Button(
                self.input_frame, text="Browse", command=lambda: browse(
                        0, self.db_loc, None, None, self.create_window, None),\
                        width=12, fg="white", bg="#187bcd",\
                        activeforeground="white", activebackground="#4e97fe")
                        
        self.db_browse_button.grid(
                row=2, column=2)
        
        self.db_name_label = tkinter.Label(
                self.input_frame, text="Please enter name for new database file",\
                bg="white", fg="#004aff", font=(
                "Sans-serif", 12, "bold"))
        
        self.db_name_label.grid(
                row=3, column=1)
                                           
        self.db_name = tkinter.Entry(
                self.input_frame, width=40, bg="white", font=(
                        "Sans-serif", 10, "bold"))
        
        self.db_name.grid(
                row=4, column=1)
        
        self.enter_pass_label = tkinter.Label(
                self.input_frame, text="Please enter master password",\
                bg="white", fg="#004aff", font=(
                "Sans-serif", 12, "bold"))
        
        self.enter_pass_label.grid(
                row=5, column=1)

        self.enter_new_pass = tkinter.Entry(
                self.input_frame, width=40, show="*", bg="white", font=(
                        "Sans-serif", 10, "bold"))
        
        self.enter_new_pass.grid(
                row=6, column=1)
        
        self.enter_opt = StringVar()
        
        self.enter_show = tkinter.Checkbutton(
                self.input_frame, text="Show password", onvalue="",\
                offvalue="*", variable=self.enter_opt,\
                command=lambda:self.update_enter_box(
                        self.enter_opt.get()), bg="white", fg="#004aff",\
                        activebackground="white",\
                        activeforeground="#1874CD")
        
        self.enter_show.grid(
                row=6, column=2)
        
        self.enter_show.deselect()

        self.confirm_pass_label = tkinter.Label(
                self.input_frame, text="Please confirm master password",\
                bg="white", fg="#004aff", font=(
                "Sans-serif", 12, "bold"))
        
        self.confirm_pass_label.grid(
                row=7, column=1)

        self.confirm_pass = tkinter.Entry(
                self.input_frame, width=40, show="*", bg="white", font=(
                        "Sans-serif", 10, "bold"))
        
        self.confirm_pass.grid(
                row=8, column=1)

        self.confirm_opt = StringVar()
        
        self.confirm_show = tkinter.Checkbutton(
                self.input_frame, text="Show password", onvalue="",\
                offvalue="*", variable=self.confirm_opt,\
                command=lambda:self.update_confirm_box(
                        self.confirm_opt.get()), bg="white", fg="#004aff",\
                        activebackground="white", activeforeground="#1874CD")
        
        self.confirm_show.grid(
                row=8, column=2)
        
        self.confirm_show.deselect()
        
        
        self.db_style = IntVar()
        self.db_style.set(1)
        
        self.basic = tkinter.Radiobutton(
                self.create_frame, text="Basic", variable=self.db_style,\
                value=1, bg="white", activebackground="white",)
        
        self.basic.grid(
                row=2, column=1)
        
        self.full = tkinter.Radiobutton(
                self.create_frame, text="Full", variable=self.db_style,\
                value=2, bg="white", activebackground="white")
        
        self.full.grid(
                row=3, column=1)
        
        self.create_now = tkinter.Button(
                self.create_frame, text="Create Now",\
                command=lambda: self.create_new(
                        selection_window), fg="white",\
                        bg="#187bcd", activeforeground="white",\
                        activebackground="#4e97fe")
        
        self.create_now.grid(
                row=4, column=1)
        
        self.cancel_button = tkinter.Button(
                self.cancel_frame, text="Cancel", command=self.__del__,\
                fg="white", bg="#187bcd", activeforeground="white",\
                activebackground="#4e97fe")
        
        self.cancel_button.grid(
                row=4, column=0)
        
    #Functions to toggle password "show" state
    def update_enter_box(self, x):
        self.enter_new_pass.config(
                show=x)

    def update_confirm_box(self, x):
        self.confirm_pass.config(
                show=x)


    #function to create new DB file
    def create_new(self, selection_window):
        try:
            #Check required information was inputted by user
            if self.check_for_input() == 0:
                
                #generate full path for new file
                self.db_file_path = self.gen_db_path()
                
                #If database file didn't conflict with an existing file proceed and create file
                if self.db_file_path != None:
                    
                    #Connect to new database
                    self.conn = sqlite3.connect(
                            self.db_file_path)
                    self.c = self.conn.cursor()
                    
                    #Generate starting tables from user selection
                    create_tables(self.c, self.db_style.get())

                    #Define charset for random password generation
                    self.charset = "^*$%@#!&.=~+_-"\
                    + string.ascii_letters + string.digits\
                    + "^*$%@#!&.=~+_-"
                    
                    
                    #Create & store passwords for new database
                    self.crypt_pass, self.master_pass, self.keyfile_pass = self.generate_passwords()
                
                    #Clear password entries
                    self.enter_new_pass.delete(0, END)
                    self.confirm_pass.delete(0, END)
                    
                    #Insert keyfile password into database
                    self.c.execute(
                            "INSERT INTO keyfile_pass (pass) VALUES(?)", [
                                    str(self.keyfile_pass)])
                    
                    #Generate keyfile for new database
                    self.keyfile_name = self.generate_keyfile()
                    
                    #If keyfile was generated successfully we can proceed
                    if self.keyfile_name != None:
                        
                        #Delete plaintext copy of keyfile
                        shred(self.keyfile_name)  
                         
                        #Commit changes
                        self.conn.commit()

                        #Send relevant file paths to main window
                        self.send_to_main(selection_window)
                        
                        #Open display_DB window and close this window
                        selection_window.display = Display_DB(
                                self.conn, self.master_pass, self.crypt_pass, self.db_file_path, self.gpg, selection_window)
            
                        self.__del__()   
                    else:
                        #If encryption of keyfile failed warn user of failure and delete created database
                        Error_Message(
                                "Failed to encrypt keyfile")
                        shred(self.db_file_path)
                       
                    
        except:
            #If creation fails warn user and attempt to delete any created files
            Error_Message(
                    "Encountered an error in creation\nPlease try again")
            try:
                shred(self.db_file_path)
            except:
                pass
            try:
                shred(self.keyfile_name)
            except:
                pass
      
    
    def check_for_input(self):
        #Check entered passwords match
        if self.db_loc.get().strip() == "":
            Error_Message(
                    "Please select a location to create files")
            return 1
        
        #Check a name was entered
        elif self.db_name.get().strip() == "":
            Error_Message(
                    "Please enter a name for your database")
            return 1
        
        #Check master password wass supplied
        elif self.enter_new_pass.get() == "":
            Error_Message(
                    "Please enter a master password!")
            return 1
        
        #check master password was confirmed
        elif self.confirm_pass.get().strip() == "":
            Error_Message(
                    "Please confirm master password")
            return 1
        
        #check passwords matched
        elif self.enter_new_pass.get() != self.confirm_pass.get():
            Error_Message(
                    "Passwords did not match!")
            return 1
            
        #Check selected directory exists
        elif not os.path.isdir(self.db_loc.get().strip()):
            Error_Message(
                        "Path does not exist!")
            return 1
        #If all checks passed return 0
        else:
            return 0
                
    
    
    def gen_db_path(self):
        #Generate full file path from user inputs
        db_file_path = os.path.join(
                self.db_loc.get().strip(), (
                        self.db_name.get().strip() + ".db"))
        #If an encrypted database with that name already exists return None
        if os.path.isfile(
                db_file_path + ".gpg"):
            Error_Message(
                    "A database file with that name already exists in this folder!")
            return None
        else:
            #If no conflicts return generated file path
            return db_file_path
        
        
    def generate_passwords(self):
        #Generate random password that will be used to encrypt data stored in DB
        crypt_pass = "".join(
                random.SystemRandom().choice(
                        self.charset) for i in range (256))
        
        #Read master_pass into memory, encrypt with crypt_pass while reading
        master_pass = str(
                self.gpg.encrypt(self.enter_new_pass.get(),\
                            recipients=None, passphrase=crypt_pass,\
                            symmetric=cipher.upper(), armor=True))
    
        
        #Generate random password for keyfile encryption
        keyfile_pass = self.gpg.encrypt(
                "".join(random.SystemRandom().choice(
                        self.charset) for i in range (256)),\
                        recipients=None, passphrase=str(
                                self.gpg.decrypt(
                                        master_pass,\
                                        passphrase=crypt_pass)),\
                                symmetric=cipher.upper(), armor=True)
        #Return generated passwords                
        return crypt_pass, master_pass, keyfile_pass
    
    
    
    def generate_keyfile(self):
        #Generate full path for keyfile
        keyfile_name = os.path.join(
                self.db_loc.get(), (self.db_name.get() + "key.txt"))
        
        #If keyfile already exists inform user and return None
        if os.path.isfile(keyfile_name + ".gpg"):
            Error_Message(
                    "Keyfile with this name already exists in this folder!")
            return None
        
        #If no conflicts found create new file and insert crypt_pass
        with open(
                keyfile_name, "w") as file:
            file.write(
                    self.crypt_pass)
            
        #Encrypt key file and shred original
        if encrypt(str(
                self.gpg.decrypt(str(
                        self.keyfile_pass), passphrase=str(
                                self.gpg.decrypt(
                                        self.master_pass,\
                                        passphrase=self.crypt_pass)))),\
            keyfile_name, self.gpg) == 0:
                return keyfile_name
        else:
            #If error occured during encryption delete created file and return None
            shred(keyfile_name)
            return None
    
      
    def send_to_main(self, selection_window):
        #Send db path to main window 
        selection_window.db_path.delete(0, END)
        
        selection_window.db_path.insert(0, os.path.join(
                self.db_loc.get(), (self.db_name.get() + ".db.gpg")))
        #Send path to keyfile to main window
        selection_window.keyfile_path.delete(0, END)
        selection_window.keyfile_path.insert(0, self.keyfile_name + ".gpg")
                            
        
    def __del__(self):
        self.db_label.destroy()
        self.db_loc.destroy()
        self.db_browse_button.destroy()
        self.db_name_label.destroy()
        self.db_name.destroy()
        self.enter_pass_label.destroy()
        self.enter_new_pass.destroy()
        self.confirm_pass_label.destroy()
        self.confirm_pass.destroy()
        self.create_now.destroy()
        self.cancel_button.destroy()
        self.enter_show.destroy()
        self.confirm_show.destroy()
        self.basic.destroy()
        self.full.destroy()
        self.create_frame.destroy()
        self.cancel_frame.destroy()
        self.spacer_frame.destroy()
        self.mid_spacer.destroy()
        try:
            del self.db_style
            del self.enter_opt
            del self.confirm_opt
            del self.master_pass
            del self.folder
            del self.db_file_path
            del self.conn
            del self.c
            del self.charset
            del self.keyfile_name

            
        except:
            pass
        self.create_window.destroy()






#class containing window and functionality to delete column from currently viewed table
class Delete_Column:
    
    def __init__(self, column_headings, sidebar, table_style):
        
        #Save needed objects into attributes for easy referencing
        self.sidebar = sidebar
        self.db = self.sidebar.db
        self.gpg = self.sidebar.gpg
        self.table_view = self.sidebar.table_view
        self.table_name = self.table_view.table_name
        self.table_style = table_style
        self.column_headings = column_headings
        self.table_style = table_style
        
        
        #if the only columns in table are id and one more display error
        if len(column_headings) == 2:
            Error_Message(
                    "There is only one column left in this table.\nPlease delete the table if this is what you wish.")
            
        #if there are enough columns to proceed then continue and display window
        else:        
            #Define delete column window
            self.delete_window = tkinter.Toplevel()
            self.delete_window.geometry("200x500")
            self.delete_window.config(bg="white")
            self.delete_window.resizable(0, 0)
            self.delete_window.title("Castle")
            
            #Event handler to detect window manually closed by user
            self.delete_window.protocol(
                    "WM_DELETE_WINDOW", self.__del__)
    
            #Create scrollable frame for window
            self.scroll_frame  = Scrollable_Frame(
                    self.delete_window, False, True, 185, 500, 0, 0, 1, 1)
            self.scroll_frame.frame.config( bg="white")
            self.scroll_frame.container.config(bg="white")
            self.scroll_frame.canvas.config(bg="white")
            
            #Define labelframe surrounding column buttons
            self.column_list = tkinter.LabelFrame(
                    self.scroll_frame.frame, text="Delete column",\
                    padx=25, pady=5, borderwidth=4, relief=GROOVE,\
                    bg="white", fg="#004aff", font=(
                    "Sans-serif", 10, "bold"))
            self.column_list.grid(
                    row=1, column=0)
            
            #Generate controls for each column and store in buttons list
            self.buttons = self.generate_controls()
            
            #Define cancel button
            self.cancel_button = tkinter.Button(
                    self.scroll_frame.frame, text="Cancel",\
                    command=self.__del__, width=12, fg="white", bg="#187bcd",\
                    activeforeground="white", activebackground="#4e97fe")
                    
            self.cancel_button.grid(
                    row=2, column=0, pady=5)
            
            

    def generate_controls(self):
        #Define list to hold generated controls
        button_list = []
        
        #loop over columns and generate functions and buttons for each
        for i in range(len(self.column_headings)):
        
            #skip over id column
            if self.column_headings[i].lower() == "id":
                pass
            else:

                #generate button for each column
                self.b = tkinter.Button(
                        self.column_list, text=self.column_headings[i],\
                        wraplength=100, command = lambda x=i:\
                                        self.get_confirmation(self.column_headings[x]),\
                                                width=12, fg="white", bg="#187bcd",\
                                                activeforeground="white",\
                                                activebackground="#4e97fe")
                                                
                self.b.grid(
                        row=i, column=0, pady=5)
                
                button_list.append(self.b)
        return button_list
                
        

    def user_confirm(self, column_name):
        #Call function to delete chosen column
        self.delete(column_name)
        #close confirmation popup
        self.confirmation.__del__()
        
    
    def get_confirmation(self, column_name):
        #display confirmation popup to make sure correct column was selected
        self.confirmation = Confirmation_Message(
                self, "Delete column?", "Delete",\
                "Cancel", "Are you sure?\nAll data "\
                +"stored in this column will be lost!.")
        #Once user confirms proceed to delete column            
        self.confirmation.popup_ok.config(
                command=lambda:self.user_confirm(column_name))
        
        self.confirmation.popup_cancel.config(
                command=self.confirmation.__del__)
        
        self.confirmation.popup.protocol(
                "WM_DELETE_WINDOW", self.confirmation.__del__)           



    def check_protected_columns(self, column_name):
        #Safety checks to prevent user from deleting columns that are needed for table to function correctly
        if (self.table_style == 3 and column_name.lower() == "note") or (
                self.table_style == 1 and column_name.lower() == "password") or (
                        self.table_style == 2 and column_name.lower() == "file") or (
                                self.table_style == 2 and column_name.lower() == "filename") or (
                                        self.table_style == 4 and column_name.lower() == "card number") or (
                                                self.table_style == 4 and column_name.lower() == "cvv number"):
            Error_Message(
                    "You cannot delete this column\n"\
                    + "Please delete table instead if this is that you wish")
            return 1
        else:
            return 0

        
    def get_new_columns(self, column_name):
        #Define list to hold list of columns to be kept
        new_column_headings = []
        
        #Loop over columns and add all but the one we are deleting to new list
        for i in range(len(self.column_headings)):
            if self.column_headings[i] != column_name and self.column_headings[i] != "id":
                new_column_headings.append(self.column_headings[i])
        
        return new_column_headings

               
    def generate_create_command(self):
        #Empty string to generate command
        columns_command = ""
    
        #loop over updated column headings and append relevant part of command to string
        for i in range(len(self.new_column_headings)):
    
            #Check to see if we need to recreate a BLOB column for a file table
            if self.table_style == 2 and self.new_column_headings[i].lower() == "file":
                columns_command = columns_command + "'" + \
                                  self.new_column_headings[i] + \
                                  "'" + " BLOB DEFAULT '', "
            #If not a BLOB column create as text
            else:
                columns_command = columns_command + "'" + \
                                  self.new_column_headings[i] + \
                                  "'" + " VARCHAR DEFAULT '', "
                                       
        #generate final command by adding standard parts
        columns_command = "CREATE TABLE IF NOT EXISTS '" +\
                               self.temp_table_name + \
                               "' (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "\
                               + columns_command[0:-2] + ");"
        return columns_command
    
 
    def generate_select_command(self):
        #declare empty string to generate extraction command
        select_command = ""
        
        #loop over updated list of table headings and generate command to extract needed columns 
        for i in range(len(self.new_column_headings)):
            select_command = select_command + '"' + \
                             self.new_column_headings[i] + '", '
        
        #Generate final command
        select_command = "SELECT " + select_command[0:-2] +\
                         " FROM '" + self.table_name + "';"
        
        return select_command

    def generate_insert_command(self):
        #Generate command to insert extracted data into new table
        #Safety check to alter command depending if we are inserting one or more column of data
        if len(self.new_column_headings) != 1:
            insert_command = "INSERT INTO '{0}' {1} VALUES ({2});".format(
                    self.temp_table_name, tuple(
                            self.new_column_headings), (
                                    ", ".join('?'*(len(self.new_column_headings)))))
        else:
            insert_command = "INSERT INTO '{0}' ({1}) VALUES ({2});".format(
                    self.temp_table_name, self.new_column_headings[0], (
                            ", ".join('?'*(len(self.new_column_headings)))))
        return insert_command


    def get_data(self, command):
        #Issue command to get needed data
        data_tuple = self.c.execute(command)

        #loop over extracted entries and store in a list
        extracted_data = []
        for row in data_tuple:
            extracted_data.append(row)
            
        #Return list of gathered data
        return extracted_data


   
    #function to delete selected column from current table
    def delete(self, column_name):
        #Check user hasn't tried to delete a protected column
        if self.check_protected_columns(column_name) == 0:
        
            #create cursor
            self.c = self.db.cursor()
            
            #Generate temporary name for table
            self.temp_table_name = self.table_name + "_new"

            #Get new list of column headings
            self.new_column_headings = self.get_new_columns(column_name)
            
            try:
                #Generate command to create replacement table
                self.columns_command = self.generate_create_command()
                
                #issue generated command
                self.c.execute(self.columns_command)

                #Generate command to extract data from existing table
                self.select_command = self.generate_select_command()
                
                #Extract needed data from table
                self.extracted_data = self.get_data(self.select_command)
        
                #Generate command to insert existing entries into new table
                self.insert_command = self.generate_insert_command()
        
                #loop over list of extracted data and issue insert command for each row
                for i in range(len(self.extracted_data)):
                    self.c.execute(
                            self.insert_command, self.extracted_data[i])

                #generate command and delete old table
                self.delete_command = "DROP TABLE '" + self.table_name + "';"
                self.c.execute(self.delete_command)

                #Rename new table with original name
                self.rename_command = "ALTER TABLE '{0}' RENAME TO '{1}';".format(
                        self.temp_table_name, self.table_name)
                self.c.execute(self.rename_command)
                
                #commit changes so we can use another cursor elsewhere
                self.db.commit()
                
                #regenerate current table display
                self.table_view.refresh()
                
                #close delete column window and regenerate current table display
                self.__del__()
            
            #If an error encountered delete temp table and inform user
            except:
                try:
                    self.c.execute(
                            "DROP TABLE '" + self.temp_table_name + "';")
                except:
                    pass
                #print(e)
                Error_Message("Error adjusting table, please try again.")


    def __del__(self):
        try:
            self.cancel_button.destroy()
            for i in range(len(self.buttons)):
                self.buttons[i].destroy()
            del self.scroll_frame
            del self.buttons
            self.column_list.destroy()
        except:
            pass
        try:
            del self.c
            del self.temp_table_name
            for i in self.new_column_headings:
                del i
            del self.new_column_headings
            del self.rename_command
            del self.columns_command
            del self.select_command
            del self.extracted_data
            for i in self.extracted_entries:
                del i
            del self.extracted_entries
            del self.insert_command
            del self.delete_command
            del self.confirmation    
        except:
            pass
        try:
            self.delete_window.destroy()
        except:
            pass
          

#class containing window and functionality to select and delete table from DB
class Delete_Table:
    
    #Save needed objects into attributes for easy referencing
    def __init__(self, sidebar):
        self.sidebar = sidebar
        self.db = self.sidebar.db
        self.gpg = self.sidebar.gpg
        
        #get current list of tables
        self.tables_list = get_tables(self.db)

        #Define window containing list of available groups
        self.delete_window = tkinter.Toplevel()
        self.delete_window.geometry("200x500")
        self.delete_window.config(bg="white")
        self.delete_window.resizable(0, 0)
        self.delete_window.title("Castle")
        
        #Event handler to detect window manually closed by user
        self.delete_window.protocol(
                "WM_DELETE_WINDOW", lambda:self.cancel_delete()) 
        
        #Define scrollable frame for delete window
        self.scroll_frame = Scrollable_Frame(
                self.delete_window, False, True, 185, 500, 1, 1, 1, 1)
        self.scroll_frame.frame.config( bg="white")
        self.scroll_frame.container.config(bg="white")
        self.scroll_frame.canvas.config(bg="white")
        
        #Define labelframe surrounding table buttons
        self.column_list = tkinter.LabelFrame(
                self.scroll_frame.frame, text="Delete Table", padx=25,\
                pady=5, borderwidth=4, relief=GROOVE, bg="white",\
                fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.column_list.grid(
                row=1, column=0)
        
        #create list to store generated buttons
        self.buttons = []
        
        #Generate delete button for each table
        for i in range(len(self.tables_list)):
            self.generate_delete_button(i)
        
        #define cancel button on main delete table window
        self.cancel_del_button = tkinter.Button(
                self.scroll_frame.frame, text="Cancel", command=lambda:
                    self.cancel_delete(), width=12, fg="white",\
                            bg="#187bcd", activeforeground="white",\
                            activebackground="#4e97fe")
                            
        self.cancel_del_button.grid(
                row=(len(self.tables_list) + 1), column=0, pady=5)


    def generate_delete_button(self, i):
        #generate buttons for each table in current list and point at relevant function in dictionary
        self.b = tkinter.Button(
                self.column_list, text=self.tables_list[i], command=lambda x=i:
                    self.user_confirm(self.tables_list[x]), wraplength=100,\
                    width=12, fg="white", bg="#187bcd",\
                    activeforeground="white", activebackground="#4e97fe")
        self.b.grid(
                row=i, column=0, pady=5)
        
        #add button to list
        self.buttons.append(self.b)


        #Function to handle cancel button on main delete table window
    def cancel_delete(self):
        #generate new sidepanel controls
        self.sidebar.clear_buttons()
        self.sidebar.buttons()
        #close delete table window
        self.__del__()
    
    
    #Function to delete chosen table from database
    def delete_table(self, table_name):
        #generate sql statement for chosen table
        self.sql = "DROP TABLE IF EXISTS '" + table_name + "';"
        
        #create cursor object to issue generated command
        self.c = self.db.cursor()
        
        #issue drop command to database
        try:
            self.c.execute(self.sql)
        except:
            Error_Message("Encountered an error!")
        
        #commit changes
        self.db.commit()
        #If deleting currently viewed table clear the display
        try:    
            if self.sidebar.current_table == table_name:
                self.sidebar.table_view.clear_view()
        except:
            pass
        
        #close popup window
        self.confirmation.__del__()
        
        #Close window and generate needed controls 
        self.cancel_delete()

    #function called after button is pressed to delete a table 
    #generates a confirmation message to ensure correct column selected     
    def user_confirm(self, table_name):
        self.confirmation = Confirmation_Message(
                self, "Delete Table {}?".format(
                        table_name), "Delete", "Cancel",\
                        "Are you sure?\nThis cannot be undone.")
        
        self.confirmation.popup_ok.config(command=lambda:
            self.delete_table(table_name))
        
        self.confirmation.popup_cancel.config(
                command=self.confirmation.__del__)
        
        self.confirmation.popup.protocol(
                "WM_DELETE_WINDOW", self.confirmation.__del__)
    

    def __del__(self):
        try:
            del self.tables_list
            for i in self.delete_functions:
                del i
            del self.delete_functions
            for i in self.buttons:
                i.destroy()
            del self.buttons
            self.cancel_del_button.destroy()
            self.scroll_frame.__del__()
        except:
            pass
        try:
            del self.c
            del self.sql
        except:
            pass
        self.delete_window.destroy()
        


#Class containing window that will hold sidebar and table display
class Display_DB:
    
     
    def __init__(self, db, master_pass, crypt_key, db_path, gpg, parent):
        #Save needed objects into attributes for easy referencing
        self.db_file_path = db_path
        self.parent = parent
        self.db = db
        
        #Store crypt key in attribute so we can access it from elsewhere later
        self.crypt_key = crypt_key
        self.master_pass = master_pass
        
        #Define window to display open database file
        self.display_window = tkinter.Toplevel()
        self.display_window.title("Castle")
        self.display_window.geometry("1015x700")
        self.display_window.config(bg="white")


        #Event handler to lock database file if window closed manually 
        self.display_window.protocol(
                "WM_DELETE_WINDOW", lambda:
                    self.lock(gpg))        
        
        #Generate sidebar controls
        self.panel = Sidebar(db, self, gpg)

   
    def lock(self, gpg):
        #Commit any changes to database that might be outstanding
        try:
            self.db.commit()
        except:
            pass
        # Encrypt database file with master password
        if encrypt(
                str(gpg.decrypt(
                        str(self.master_pass), passphrase=self.crypt_key)),\
                        self.db_file_path, gpg)== 0:
                    
            try:
                #Close connection to database if possible
                self.db.close()
            except:
                pass
            #If successfully encrypted shred decrypted file
            shred(self.db_file_path)
            #Close this window
            self.__del__()
        else:
            Error_Message("Failed to lock database!")

        
    
    def __del__(self):
        try:
            del self.panel
            del self.master_pass
            del self.keyfile
            del self.crypt_key
            del self.db_file_path
        except:
            pass
        try:
            self.display_window.destroy()
        except:
            pass

    
#Class containing add entry and edit entry windows depending what values are passed
class Entry_Window:
    
    def __init__(self, column_headings, entry_data, id_ref, table_view, table_style):
        #Save needed objects into attributes for easy referencing
        self.table_view = table_view
        self.sidebar = self.table_view.sidebar
        self.db = self.sidebar.db
        self.gpg = self.sidebar.gpg
        self.table_name = table_view.table_name
        self.id_ref = id_ref 
        self.column_headings = column_headings
        self.table_style = table_style
        self.entry_data = entry_data 
        
        
        #create dictionary and lists to store generated widgets
        self.entries = {}
        self.buttons = []
        self.entry_refs = []
        self.labels = []
        
        #Declare variables to store column references
        self.file_ref = None
        self.title_ref = None
        self.note_ref = None
        self.filename_ref = None        
        
        
        #Define entry window
        self.entry_window = tkinter.Toplevel()
        self.entry_window.geometry("600x200")
        if id_ref == None:
            self.entry_window.title("Castle: Add Entry")
        else:
            self.entry_window.title("Castle: Edit Entry")
        self.entry_window.config(bg="white")
        self.entry_window.resizable(0, 0)
        
        #Event handler to detect window manually closed by user
        self.entry_window.protocol(
                "WM_DELETE_WINDOW", self.__del__)
        
        
        #Create scrollable frame for window
        self.side_scroll = Scrollable_Frame(
                self.entry_window, True, False, 600, 135, 0, 0, 1, 1)
        
        self.side_scroll.frame.config(bg="white")
        
        self.side_scroll.canvas.config(bg="white")
        
        self.button_frame = tkinter.Frame(
                self.entry_window, bg="white", padx=10)
        
        self.button_frame.grid(
                row=2, column=0)
        
        
        self.button_spacer = tkinter.Frame(
                self.button_frame, bg="white", width=400)
        
        self.button_spacer.grid(
                row=1, column=2, pady=5)
        
        #Adjust display depending on table style
        if table_style == 2:
            self.side_spacer = tkinter.Frame(
                    self.side_scroll.frame, bg="white")
        
            self.side_spacer.grid(
                    row=0, column=0)
        
            self.side_spacer.config(width=40)
        

        #Loop over columns to generate display - skip ID column
        for i in range(len(column_headings)):
            if column_headings[i].lower() == "id":
                pass
            
            #If looking at file storage column of a file table 
            #generate label entry and button for directory browser
            elif column_headings[i].lower() == "file" and table_style == 2:
                self.generate_file_widgets(i)
               
            else:
                #If not looking at a file storage column create standard widgets and insert decrypted values
                self.generate_standard_widgets(i)
                self.insert_data(i)
          
        #Define submit and cancel buttons for main edit entry window
        self.submit_button = tkinter.Button(
                self.button_frame, text="Submit", command=lambda:
                    self.submit(
                            column_headings, table_style),\
                            fg="white", bg="#187bcd", \
                            activeforeground="white",\
                            activebackground="#4e97fe")
                            
        self.submit_button.grid(
                row=1, column=3)
        
        self.cancel_button = tkinter.Button(
                self.button_frame, text="Cancel", command=self.__del__,\
                fg="white", bg="#187bcd", activeforeground="white",\
                activebackground="#4e97fe")
        
        self.cancel_button.grid(
                row=1, column=1)
    
    
    #function to add/edit row in current table based on users inputs
    def submit(self, column_headings, table_style):
                
        #Flag to check if user has selected a file to store
        self.file_uploaded = False
        
        #Check user inputted data into at least one field
        if self.check_for_input():
         
            #If this is a file table
            if table_style == 2:
                #Read in data from file
                self.fields, self.values = self.update_file_entry()
                            
            #If not looking at a file table just read in entries  
            else:
                self.fields, self.values = self.update_text_entry()
                    
            #Sefety check to make sure statement was generated
            if self.fields!= None and self.values != None:
                
                #Generate swl command to add/edit this record
                self.sql = self.generate_command()
                
                try:
                    #create cursor to issue commands to database
                    self.c = self.db.cursor()
                    
                    #issue command to database and commit changes
                    self.c.execute(self.sql, self.values)
                    self.db.commit()
                    
                #If an error encountered during database command inform user
                #and leave window open
                except:
                    self.db.commit()
                    Error_Message("Encountered an error!")
                    return
                
                #Display success message to user
                self.display_success_message()
                
                #Regenerate current table display 
                self.table_view.refresh()
                
                #call function to close edit entry window and regenerate curent table display
                self.__del__()
                
                
                
    #Display appropriate success message to user depending what type of transaction
    def display_success_message(self):
        if self.file_uploaded == True:
            if self.id_ref == None:
                Error_Message(
                        "File saved successfully")
            else:
                Error_Message(
                        "File updated successfully")
        else:
            Error_Message(
                    "Entry saved")

              
    
    def generate_command(self):                   
        #Cut last comma and space off generated statement
        self.fields = self.fields[0:-2]
        
        #Check to see if we are updating an existing record or adding a new one
        if self.id_ref == None:
            #if adding new record adjust formatting if only one value supplied
            if len(self.column_headings) == 2:
                sql = "INSERT INTO '{0}' ({1}) VALUES (?);".format(
                        self.table_name, self.column_headings[1]) 
            else:
            
                sql = "INSERT INTO '{0}' {1} VALUES ({2});".format(
                        self.table_name, tuple(self.column_headings[1:]), (
                                ", ".join('?'*(len(self.column_headings) - 1)))) 
        else:
            #If updating existing entry generate appropriate command
            sql = "UPDATE '{0}' SET {1} WHERE id = '{2}';".format(
                    self.table_name, self.fields, self.id_ref)
        return sql

    
        
    def update_text_entry(self):
        values = []
        command = ""
        #Loop over widgets and read in data to be stored
        for i in range(len(self.entries)):
            #If current table is a secure note table adjust
            #how we pick up the data from the text widget  
            if self.table_style == 3 and i == self.note_ref:
                values.append(
                        str(self.gpg.encrypt(
                                self.entries[i].get("1.0", END),\
                                recipients=None,
                                passphrase=self.sidebar.parent.crypt_key,\
                                symmetric=cipher.upper(), armor=True)))
            else:
                values.append(
                        str(self.gpg.encrypt(
                                self.entries[i].get(),\
                                recipients=None,\
                                passphrase=self.sidebar.parent.crypt_key,\
                                symmetric=cipher.upper(), armor=True)))
                
        #Generate string of fields to be updated on submission
        for i in range(len(self.column_headings) - 1):
            command = command + "'" + self.column_headings[i+1] + "'" + " = ?, "
        return command, values

        
    def read_file(self, values):
        #Encrypt file for storage
        if encrypt(
                self.sidebar.parent.crypt_key,\
                self.entries[
                        self.file_ref].get(), self.gpg) == 0:
            
            #generate filepath to encrypted file
            filepath = self.entries[
                    self.file_ref].get() + ".gpg"
            
            #Read encrypted file into memory
            with open(filepath, "rb") as file:
                values.append(file.read())
            
            #Delete encrypted copy of file and delete generated filepath
            shred(filepath)
            del filepath
            
            #Set file uploaded flag to True
            self.file_uploaded = True
            return values
        else:
            #If an error encountered while encrypting file inform user
            Error_Message(
                    "Failed to store file!\nPlease try again")
            return None

        
    def file_inputted(self):
        values = []
        command = ""
        #Loop over columns and append appropriate data to list of values
        for i in range(len(self.column_headings)):
            
            #Skip id column
            if self.column_headings[i].lower() == "id":
                pass
            
            #If looking at a file storage column read binary data from file and append to list
            elif self.column_headings[i].lower() == "file":
                
                values = self.read_file(values)
                    
            #For any other column append data from entry widget
            else:
                #Check no errors occured uploading a file
                if values == None:
                    return None, None
            
                #Encrypt and append other entered data
                values.append(
                        str(self.gpg.encrypt(
                                self.entries[i-1].get(),\
                                recipients=None,\
                                passphrase=self.sidebar.parent.crypt_key,\
                                symmetric=cipher.upper(), armor=True)))
 
        #Generate string of fields to be updated on submission
        for i in range(len(self.column_headings) - 1):
            command = command + "'"\
            + self.column_headings[i+1] + "'" + " = ?, "
        #return generated command and list of values
        return command, values
            
    
    
    def file_not_uploaded(self):    
        #Declare list to store columns we are going to be updating
        insert_columns = []
        values = []
        command = ""
        
        #loop through list of columns that had entries generated and append column heading to insert_columns
        for i in self.entry_refs:
            insert_columns.append(self.column_headings[i])
        
        #Loop over list of columns to update, generate sql and append data to values list
        for i in range(len(insert_columns)):
            command = command + "'" + insert_columns[i] + "'" + " = ?, "
            values.append(
                    str(self.gpg.encrypt(
                            self.entries[
                                    self.entry_refs[i] - 1].get(),\
                                    recipients=None, passphrase=self.sidebar.parent.crypt_key,\
                                    symmetric=cipher.upper(), armor=True)))
        return command, values

        
        
    def update_file_entry(self):
        #if no updated file was supplied just update the other fields
        if self.file_entry.get() == "":
            #Check to make sure filename was not removed as this is needed for retrieval
            if self.entries[
                    self.filename_ref].get() == "":
                Error_Message(
                        "Please enter a filename")
            else:
                command, values = self.file_not_uploaded()
                return command, values
         
        #If an updated file was supplied, overwrite currently stored file
        else:
            #Safety checks to ensure we have all the data we need to proceed
            if self.file_entry.get() == "":
                Error_Message(
                        "Please select a file to store")
            elif self.entries[
                    self.filename_ref].get() == "":
                Error_Message(
                        "Please enter a filename")
            else:
                command, values = self.file_inputted()
                return command, values




    def check_for_input(self):
        inputted = False
        #read in data from all entry/text widgets and see if any have data in them
        for i in range(len(self.entries)):
            try:
                if self.entries[i].get().strip() != "":
                    inputted = True
            except:
                if self.entries[i].get("1.0", END).strip() != "":
                    inputted = True
        if inputted == True:
            return True
        #if all fields were empty display error message and return False
        else:
            if self.id_ref == None:
                Error_Message(
                        "All fields appear to be empty.\n"\
                        +"Please enter details to be saved.")
            else:    
                Error_Message(
                        "All fields appear to be empty.\n"\
                        +"Please delete entry if this is what you wish.")
            return False


    def insert_data(self, i):                        
            #Insert data from database into generated widget
            #Safety checks to prevents issues with None values
            if self.entry_data != None and self.entry_data[i] != None: 
                    if i - 1 != self.note_ref and self.table_style != 3:
                        self.entries[i - 1].insert(
                                0, str(self.gpg.decrypt(
                                        str(self.entry_data[i]),\
                                        passphrase=self.sidebar.parent.crypt_key)))
                    else:
                        self.entries[i - 1].insert(
                                END, str(self.gpg.decrypt(
                                        str(self.entry_data[i]),\
                                        passphrase=self.sidebar.parent.crypt_key)))



    def generate_standard_widgets(self, i):
        #If looking at title column of secure note table save reference
        if self.column_headings[i].lower() == "title":
            self.title_ref = i - 1
        
        #If looking at filename table of file storage table save column reference
        if self.column_headings[i].lower() == "filename" and self.table_style == 2:
            self.filename_ref = i - 1
        
        #If looking at note column of secure note table create text widget and save column reference
        if self.column_headings[i].lower() == "note" and self.table_style == 3:
            self.note_ref = i - 1
            self.e = tkinter.Text(
                    self.side_scroll.frame, width=40, height=5,\
                    bg="white", font=(
                            "Sans-serif", 10, "bold"))
        
        else:
            #If none of the columns above, default to an entry widget
            self.e = tkinter.Entry(
                    self.side_scroll.frame, width=15,\
                    bg="white", font=(
                            "Sans-serif", 10, "bold"))
        
        #Grid and store generated widget and create column heading label
        #append entry reference to list of columns to update
        self.e.grid(
                row=1, column=i, pady=5)
        
        self.entries[i-1] = self.e
        
        self.l = tkinter.Label(
                self.side_scroll.frame, text=self.column_headings[i],\
                bg="white", fg="#004aff", font=(
                "Sans-serif", 12, "bold"))
        
        self.l.grid(
                row=0, column=i, pady=5)
        
        self.labels.append(self.l)
        
        self.entry_refs.append(i)



    def generate_file_widgets(self, i):
        self.file_ref = i - 1
        
        #If we have not been passed an entry ID we are adding a new file
        if self.id_ref == None:
            self.file_label = tkinter.LabelFrame(
                    self.side_scroll.frame, text="Please select file to store",\
                    borderwidth=4, relief=GROOVE, bg="white",\
                    fg="#004aff", font=(
                    "Sans-serif", 10, "bold"), padx=10)
        
        #If we have an entry ID we are updating a file
        else:
            self.file_label = tkinter.LabelFrame(
                    self.side_scroll.frame, text=\
                    "If you wish to update file, please select",\
                    borderwidth=4, relief=GROOVE, bg="white",\
                    fg="#004aff", font=(
                    "Sans-serif", 10, "bold"), padx=10)
        
        self.file_entry = tkinter.Entry(
                self.file_label, width=40, bg="white", font=(
                        "Sans-serif", 10, "bold"))
        
        self.file_button = tkinter.Button(
                self.file_label, text="Browse", command=lambda:
                    browse(1, self.entries[self.file_ref],\
                           "Select a file to store", ("all files", "*.*"),\
                           self.entry_window, self.entries[self.filename_ref]),\
                           fg="white", bg="#187bcd", activeforeground="white",\
                           activebackground="#4e97fe")
        
        self.file_label.grid(
                row=5, column=1, columnspan=4, pady=5)
        
        self.file_entry.grid(
                row=1, column=1, pady=5)
        
        self.file_button.grid(
                row=1, column=3, pady=5)
        
        self.labels.append(
                self.file_label)
        
        self.buttons.append(
                self.file_button)
        
        self.entries[i-1] = self.file_entry
   


    def __del__(self):
        self.submit_button.destroy()
        self.cancel_button.destroy()
        try:
            
            for i in self.entries.keys():
                self.entries[i].destroy()
            del self.entries
            for i in self.labels:
                i.destroy()
            for i in self.buttons:
                i.destroy()
            del self.side_scroll
            self.button_spacer.destroy()
            self.button_frame.destroy()
            self.bottom_spacer.destroy()
        except:
            pass
        try:
            del self.note_ref
            del self.title_ref
            del self.filename_ref
        except:
            pass
        
        try:
            del self.c
            del self.sql
            del self.fields
            for i in self.values:
                del i
            del self.values
            del self.inputted
        except:
            pass
        self.entry_window.destroy()
            
        
        

#Classs containing single button error of informational popup
class Error_Message:
      
    def __init__(self, text):
        
        #Define error popup
        self.warning = tkinter.Toplevel()
        self.warning.geometry("350x125")
        self.warning.resizable(0, 0)
        self.warning.config(bg="white")
        self.warning.title("Castle")
        
        #Define frame to hold widgets
        self.warning_frame = tkinter.Frame(
                self.warning, padx=20, pady=10, bg="white")
        
        self.warning_frame.pack()
        
        #Only insert spacer if there is just one line of text in the message
        if len(text.split("\n")) < 2 :
            #Define spacer for between text and button
            self.warning_spacer = tkinter.Frame(
                    self.warning_frame, height=10, bg="white")
            
            self.warning_spacer.grid(
                    row=2, column=2)
        
        #Define warning message
        self.warning_label = tkinter.Label(
                self.warning_frame, text=text, wraplength=300,\
                bg="white", fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
            
        self.warning_label.grid(
                row=1, column=1, columnspan=3)
        
        #Define ok button
        self.warning_ok = tkinter.Button(
                self.warning_frame, text="Ok", command=self.ok, fg="white",\
                bg="#187bcd", activeforeground="white",\
                activebackground="#4e97fe")
                
        self.warning_ok.grid(
                row=3, column=2)
        
    def ok(self):
        self.warning.destroy()


#Class containing window and functionality to generate random password strings
class Password_Generator:
           
    def __init__(self):
        #Define tkinter variables for checkboxes and dragbar
        self.length = IntVar()
        self.letters = StringVar()
        self.numbers = StringVar()
        self.special = StringVar()
        self.brackets = StringVar()
        self.space = StringVar()
        
        #Define min and max password lengths
        self.max = 128
        self.min = 8
        
        #Define main generator window
        self.generator_window = tkinter.Toplevel()
        self.generator_window.geometry("450x500")
        self.generator_window.title("Castle: Password Generator")
        self.generator_window.config(bg="white")
        self.generator_window.resizable(0, 0)
        
        #Event handler to detect window manually closed by user
        self.generator_window.protocol(
                "WM_DELETE_WINDOW", self.__del__)
        
        #Define frames to hold widgets
        self.charset_frame = tkinter.LabelFrame(
                self.generator_window,\
                text="Select character set to use for generation",\
                padx=60, pady=10, borderwidth=4,relief=GROOVE,\
                bg="white", fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.charset_frame.grid(
                row=1, column=1)
        
        self.length_frame = tkinter.LabelFrame(
                self.generator_window, \
                text="Select length of password ({0}-{1})".format(
                        self.min, self.max), padx=30, pady=10,\
                        borderwidth=4, relief=GROOVE, bg="white",\
                        fg="#004aff", font=(
                        "Sans-serif", 10, "bold"))
                
        self.length_frame.grid(
                row=3, column=1)
        
        self.button_frame = tkinter.Frame(
                self.generator_window, bg="white")
        
        self.button_frame.grid(
                row=5, column=1)
        
        self.cancel_frame = tkinter.Frame(
                self.generator_window, bg="white")
        
        self.cancel_frame.grid(
                row=7, column=1)
        
        #Define spacer frames
        self.side_spacer = tkinter.Frame(
                self.generator_window, width=50,\
                height=20, bg="white")
        
        self.side_spacer.grid(
                row=0, column=0)
        
        self.mid_spacer = tkinter.Frame(
                self.generator_window, height=20,\
                bg="white")
        
        self.mid_spacer.grid(
                row=2, column=1)
        
        self.bottom_spacer = tkinter.Frame(
                self.generator_window, height=15,\
                bg="white")
        
        self.bottom_spacer.grid(
                row=4, column=1)
        
        self.cancel_spacer = tkinter.Frame(
                self.generator_window, height=25,\
                bg="white")
        
        self.cancel_spacer.grid(
                row=6, column=1)
        

        #Define letters checkbox - selected by default
        self.alpha_check = tkinter.Checkbutton(
                self.charset_frame, text="Letters", variable=self.letters,\
                pady=5, onvalue=string.ascii_letters, offvalue="",\
                bg="white", fg="#004aff", activebackground="white",\
                activeforeground="#1874CD")
                
        self.alpha_check.grid(
                row=1, column=1)
        
        self.alpha_check.select()
        
        #Define numbers checkbox - selected by default
        self.num_check = tkinter.Checkbutton(
                self.charset_frame, text="Numbers", variable=self.numbers,\
                pady=5, onvalue=string.digits, offvalue="", bg="white",\
                fg="#004aff", activebackground="white",\
                activeforeground="#1874CD")
        
        self.num_check.grid(
                row=2, column=1)
        
        self.num_check.select()
        
        #Define special characters checkbox - selected by default
        self.special_check = tkinter.Checkbutton(
                self.charset_frame, text="^*$%@#!&.=~+-_",\
                variable=self.special, pady=5, onvalue="^*$%@#!&.=~+", \
                offvalue="", bg="white", fg="#004aff",\
                activebackground="white", activeforeground="#1874CD")
        
        self.special_check.grid(
                row=3, column=1)
        
        self.special_check.select()        
        
        #Define brackets characters checkbox 
        self.bracket_check = tkinter.Checkbutton(
                self.charset_frame, text="{}[]()<>", variable=self.brackets,\
                pady=5, onvalue="{}[]()<>", offvalue="", bg="white",\
                fg="#004aff", activebackground="white",\
                activeforeground="#1874CD")
        
        self.bracket_check.grid(
                row=4, column=1)
        
        #Define space characters checkbox 
        self.space_check = tkinter.Checkbutton(
                self.charset_frame, text="Space", variable=self.space,\
                pady=5, onvalue=" ", offvalue="", bg="white", fg="#004aff",\
                activebackground="white", activeforeground="#1874CD")
        
        self.space_check.grid(
                row=5, column=1)


        #Define length text entry
        self.length_box = tkinter.Entry(
                self.length_frame, width=30, bg="white", font=(
                        "Sans-serif", 10, "bold"))
        
        self.length_box.grid(
                row=1, column=1)
        
        #Define length scale/dragbgar
        self.length_scale = tkinter.Scale(
                self.length_frame, variable=self.length, from_=self.min,\
                to=self.max, orient="horizontal", \
                command=self.update_length_box, length=230, bg="#187bcd", \
                activebackground="#4e97fe", fg="white", troughcolor="white")
        
        self.length_scale.grid(
                row=2, column=1)

        #Define password entry box for generated output
        self.password_box = tkinter.Entry(
                self.button_frame, width=30, bg="white", font=(
                        "Sans-serif", 10, "bold"))
        
        self.password_box.grid(
                row=1, column=1, columnspan=3, pady=5)
    
        #Define copy password button
        self.copy_button = tkinter.Button(
                self.button_frame, text="Copy Password", command=self.copy,\
                fg="white", bg="#187bcd", activeforeground="white", \
                activebackground="#4e97fe")
        
        self.copy_button.grid(
                row=2, column=1)
        
        #Define generate button
        self.generate_button = tkinter.Button(
                self.button_frame, text="Generate", command=lambda:
                    self.generate(
                            self.length.get()), fg="white", bg="#187bcd",\
                            activeforeground="white", activebackground="#4e97fe")
        
        self.generate_button.grid(
                row=2, column=3)
        
        
        #Define cancel button
        self.cancel_button = tkinter.Button(
                self.cancel_frame, text="Cancel", command=self.__del__,\
                fg="white", bg="#187bcd", activeforeground="white",\
                activebackground="#4e97fe")
        
        self.cancel_button.grid(
                row=1, column=1)
        
        #Insert starting value from dragbar into length entry box
        self.length_box.insert(
                0, self.length.get())
    
        #Create event listener for length_box to listen for user changes
        self.length_box.bind(
                "<KeyRelease>", self.update_length_scale)
        
        
        
        
    #Function to copy generated password to clipboard
    def copy(self):
        xerox.copy(
                self.password_box.get(), xsel=True)
        
        
        
    #Function to update the slider bar to the value in the entry box
    #provided it is within bounds. triggered on key release
    def update_length_scale(self, event):
        try:
            if int(self.length_box.get()) >= self.min and \
            int(self.length_box.get()) <= self.max: 
                self.length_scale.set(self.length_box.get())
        except:
            pass
        
        
        
    #function to update the length box with new value if the drag bar is moved
    def update_length_box(self, length):
        self.length_box.delete(
                0, END)

        self.length_box.insert(
                0, self.length.get())
    
    
    
    #Function to generate password from chosen inputs
    def generate(self, length):
        #Define characterset to use
        #Special has been added multiple times to increase the odds of special characters being chosen
        charset = self.letters.get() + self.numbers.get() + self.special.get()\
                        + self.brackets.get() + self.space.get() + self.special.get()
        #Put in a try block to avoid errors if nothing is selected
        try:
            #Generate string from given inputs
            self.password = "".join(
                    random.SystemRandom().choice(
                            charset) for i in range (length))
            
            #Clear password entry box
            self.password_box.delete(
                    0, END)
            
            #Insert generated password into entry box
            self.password_box.insert(
                    0, self.password)
        except:
            pass
        
    def __del__(self):
        self.length_box.destroy()
        self.cancel_button.destroy()
        self.generate_button.destroy()
        self.password_box.destroy()
        self.length_scale.destroy()
        self.length_box.destroy()
        self.space_check.destroy()
        self.bracket_check.destroy()
        self.special_check.destroy()
        self.num_check.destroy()
        self.alpha_check.destroy()
        self.cancel_spacer.destroy()
        self.mid_spacer.destroy()
        self.bottom_spacer.destroy()
        self.side_spacer.destroy()
        self.cancel_frame.destroy()
        self.button_frame.destroy()
        self.length_frame.destroy()
        self.charset_frame.destroy()
        try:
            del self.password
            del self.charset
        except:
            pass
        try:
            del self.length
            del self.letters
            del self.numbers
            del self.special
            del self.brackets
            del self.space
            del self.max
            del self.min
        except:
            pass
        self.generator_window.destroy()
        

#Class containing window and functionality to extract stored file
class Retrieve_File:
     
    def __init__(self, entry_data, column_headings, sidebar):
        #Save needed objects into attributes for easy referencing
        self.sidebar = sidebar
        self.gpg = self.sidebar.gpg
        self.entry_data = entry_data
        
        #Parse column headings and find the ones we need
        for i in range(len(column_headings)):
            if column_headings[i].lower() == "filename":
                self.filename_ref = i
            elif column_headings[i].lower() == "file":
                self.file_ref = i

        
        #Define file retrieval window
        self.retrieve_window = tkinter.Toplevel()
        self.retrieve_window.geometry("500x150")
        self.retrieve_window.title("Castle")
        self.retrieve_window.resizable(0, 0)
        self.retrieve_window.config(bg="white")
        
        #Event handler to detect window manually closed by user
        self.retrieve_window.protocol(
                "WM_DELETE_WINDOW", self.__del__)
        
        self.button_frame = tkinter.Frame(
                self.retrieve_window, bg="white")
        
        self.button_frame.grid(
                row=4, column=1, columnspan=2, pady=5)
        
        self.button_spacer = tkinter.Frame(
                self.button_frame, width=250, bg="white")
        
        self.button_spacer.grid(
                row=1, column=2, pady=5)
        
        self.bottom_spacer = tkinter.Frame(
                self.retrieve_window, height=15, bg="white")
        
        self.bottom_spacer.grid(
                row=3, column=1, pady=5)
        
        self.side_spacer = tkinter.Frame(
                self.retrieve_window, width=20, bg="white")
        
        self.side_spacer.grid(
                row=0, column=0)
        
        #Define label, entry box and buttons
        self.heading_label = tkinter.Label(
                self.retrieve_window, text=\
                "Please select a folder to download file to",\
                bg="white", fg="#004aff", font=(
                "Sans-serif", 12, "bold"))
        
        self.heading_label.grid(
                row=1, column=1, columnspan=2, pady=5)
        
        self.path_entry = tkinter.Entry(
                self.retrieve_window, width=40, bg="white", font=(
                        "Sans-serif", 10, "bold"))
        
        self.path_entry.grid(
                row=2, column=1, pady=5)
        
        self.browse_button = tkinter.Button(
                self.retrieve_window, text="Browse", command=lambda: browse(
                        0, self.path_entry, None, None, self.retrieve_window, None),\
                        fg="white", bg="#187bcd", activeforeground="white",\
                        activebackground="#4e97fe")
        
        self.browse_button.grid(
                row=2, column=2, pady=5)
        
        self.download_button = tkinter.Button(
                self.button_frame, text="Download", command=lambda:
                    self.download(
                            entry_data),\
                            fg="white", bg="#187bcd",activeforeground="white",\
                            activebackground="#4e97fe")
        
        self.download_button.grid(
                row=1, column=3, pady=5)
        
        self.cancel_button = tkinter.Button(
                self.button_frame, text="Cancel", command=self.__del__,\
                fg="white", bg="#187bcd", activeforeground="white",\
                activebackground="#4e97fe")
        
        self.cancel_button.grid(
                row=1, column=1, pady=5)
        
        
    def generate_full_path(self):
        #Read in download directory from user input
        filepath = self.path_entry.get() 
        
        #Decrypt filename from saved info
        filename = str(
                self.gpg.decrypt(self.entry_data[self.filename_ref],\
                passphrase=self.sidebar.parent.crypt_key))
        
        #Combine given path and stored filename into full path for destination file
        filepath = os.path.join(
                filepath, filename)
        return filepath

        
    
    #Function to write file from database into chosen destination
    def download(self, entry_data):
        #Check required information was entered by user
        if self.check_for_input() == 0:
            
            #Create full path from download directory and stored filename
            self.filepath = self.generate_full_path()
            
            #Safety check to make sure a file with this name does not already exist
            if os.path.isfile(self.filepath):
            
                Error_Message(
                        "A file with this name already exists")
            else:
                #Write encrypted entry to file
                with open(self.filepath, "wb") as file:
                    file.write(
                            entry_data[self.file_ref])
                
                #Decrypt file
                decrypt(self.sidebar.parent.crypt_key, self.filepath, self.gpg)
                
                #Delete encrypted copy of file
                shred(self.filepath)
                
                #Popup to confirm file retrieved
                Error_Message(
                        "File retrieved successfully!")    
                    
            #Close file retrieval window
            self.__del__()
 
    def check_for_input(self):
        #Safety checks to make sure we have all the information to proceed
        if self.path_entry.get() == "":
            Error_Message(
                    "Please select a download location")
            return 1
        elif self.entry_data[self.filename_ref] == "":
            Error_Message(
                    "Cannot download file without filename\nPlease edit entry")
            return 1
        elif self.entry_data[self.file_ref] == "":
            Error_Message(
                    "Error: No file to download!")
            return 1
        #If all check passed return 0
        else:
            return 0
    
    
    def __del__(self):
        self.heading_label.destroy()
        self.path_entry.destroy()
        self.browse_button.destroy()
        self.download_button.destroy()
        self.cancel_button.destroy()
        self.button_frame.destroy()
        self.side_spacer.destroy()
        self.bottom_spacer.destroy()
        self.button_spacer.destroy()
        try:
            del self.file_ref
            del self.filename_ref
        except:
            pass
        try:
            del self.filename
            del self.filepath
        except:
            pass
        self.retrieve_window.destroy()



#Portable class to create a scrollable frame
class Scrollable_Frame:
    
    def __init__(self, parent, x, y, width, height, row, column, rowspan, columnspan):
        #Define frame and canvas to construct scroll frame
        self.container = tkinter.Frame(parent)
        
        self.canvas = tkinter.Canvas(
                self.container, width=width, height=height) 
        
        #Define scrollbars
        if y == True:
            self.scrollbary = tkinter.Scrollbar(
                    self.container, orient="vertical",\
                    command=self.canvas.yview, bg="#187bcd",\
                    activebackground="#4e97fe", troughcolor="white")
        
        if x == True:
            self.scrollbarx = tkinter.Scrollbar(
                    self.container, orient="horizontal",\
                    command=self.canvas.xview, bg="#187bcd",\
                    activebackground="#4e97fe", troughcolor="white")

        #Create the top frame to hold widgets
        self.frame = tkinter.Frame(
                self.canvas)
        
        
        #Define scrollable region of canvas
        self.frame.bind(
                "<Configure>", lambda e:
                    self.canvas.configure(
                            scrollregion=self.canvas.bbox(
                                    "all")))

        self.canvas.create_window(
                (0, 0), window=self.frame, anchor="nw")
        
        #Configure the commands for interacting with scrollbars
        if y == True:
            self.canvas.configure(
                    yscrollcommand=self.scrollbary.set)
        
        if x == True:
            self.canvas.configure(
                    xscrollcommand=self.scrollbarx.set)
        
        #attach container to parent
        self.container.grid(
                row=row, column=column, rowspan=rowspan,\
                columnspan=columnspan)
        
        #Define positioning of scrollbars
        if y == True:
            self.scrollbary.grid(
                    row=1, column=2, sticky="ns")
        
        if x == True:
            self.scrollbarx.grid(
                    row=2, column=1, columnspan=2, sticky="ew")
        
        #pack canvas into container and span full area
        self.canvas.grid(
                row=1, column=1, sticky="nsew")
     
    def __del__(self):
        try:
            self.scrollbarx.destroy()
        except:
            pass
        try:
            self.scrollbary.destroy()
        except:
            pass
        try:
            self.frame.destroy()
        except:
            pass
        try:
            self.canvas.destroy()
        except:
            pass
        try:
            self.container.destroy()
        except:
            pass
        
        
        
#Class containing display for database selection
class Selection_Window:
    
    def __init__(self, root, gpg):
      
        #define frames to hold main window widgets
        self.unlock_frame = tkinter.LabelFrame(
                root, padx=30, pady=30, text=\
                "Select existing database to unlock",borderwidth=4,\
                relief=GROOVE, bg="white", fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        self.unlock_frame.grid(
                row=1, column=1)
        
        self.create_frame = tkinter.LabelFrame(
                root, borderwidth=4, relief=GROOVE, pady=15, padx=45,\
                text="Create new database", bg="white", fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        self.create_frame.grid(
                row=1, column=3)
        
        self.side_padding = tkinter.Frame(
                root, width=30, height=60, bg="white")
        self.side_padding.grid(
                row=0, column=0)
        
        self.mid_padding = tkinter.Frame(
                root, width=25, bg="white")
        self.mid_padding.grid(
                row=1, column=2)
         
        self.unlock_spacer = tkinter.Frame(
                self.unlock_frame, height=15, bg="white")
        self.unlock_spacer.grid(
                row=6, column=1)
        
        #Define Initial window layout
        self.db_label = tkinter.Label(
                self.unlock_frame, text="Select database file", bg="white",\
                                 fg="#004aff", font=(
                                 "Sans-serif", 12, "bold"))
        self.db_label.grid(
                row=0, column=0)
        
        self.db_path = tkinter.Entry(
                self.unlock_frame, width=40, bg="white", font=(
                        "Sans-serif", 10, "bold"))
        self.db_path.grid(
                row=1, column=0)
        
        self.unlock_browse_button = tkinter.Button(
                self.unlock_frame, text="Browse", command=lambda: browse(
                        1, self.db_path, "Select a database file to unlock",(
                                "Encrypted database", "*.db.gpg*"),\
                                root, None), fg="white", bg="#187bcd",\
                            activeforeground="white", activebackground="#4e97fe")
        
        self.unlock_browse_button.grid(
                row=1, column=1)
        
        self.keyfile_label = tkinter.Label(
                self.unlock_frame, text="Select keyfile", bg="white",\
                                      fg="#004aff", font=(
                                      "Sans-serif", 12, "bold"))
        self.keyfile_label.grid(
                row=2, column=0)
        
        self.keyfile_path = tkinter.Entry(
                self.unlock_frame, width=40, bg="white", font=(
                        "Sans-serif", 10, "bold"))
        self.keyfile_path.grid(
                row=3, column=0)
        
        self.keyfile_browse = tkinter.Button(
                self.unlock_frame, text="Browse", command=lambda: browse(
                        1, self.keyfile_path, "Please select a keyfile for database", (
                                "Encrypted key", "*.txt.gpg*"), root, None),\
                        fg="white", bg="#187bcd", activeforeground="white",\
                        activebackground="#4e97fe")
                        
        self.keyfile_browse.grid(
                row=3, column=1)
        
        self.enter_pass_label = tkinter.Label(
                self.unlock_frame, text="Enter master password", bg="white",\
                fg="#004aff", font=(
                "Sans-serif", 12, "bold"))
        
        self.enter_pass_label.grid(
                row=4, column=0)
        
        self.enter_pass = tkinter.Entry(
                self.unlock_frame, width=40, show="*", bg="white", font=(
                        "Sans-serif", 10, "bold"))
        self.enter_pass.grid(
                row=5, column=0)
            
        #Define variable and widget for show password checkbutton
        self.show_opt = StringVar()
        self.show_pass = tkinter.Checkbutton(
                self.unlock_frame, text="Show password", onvalue="", offvalue="*",\
                variable=self.show_opt, command=lambda: update_pass_box(
                        self.enter_pass, self.show_opt), bg="white", fg="#004aff",\
                        activebackground="white", activeforeground="#1874CD")
                                            
        self.show_pass.grid(
                row=5, column=1)
        
        self.show_pass.deselect()
        
        self.unlock_button = tkinter.Button(
                self.unlock_frame, text="Unlock", command=lambda: unlock(gpg, self),\
                        fg="white", bg="#187bcd", activeforeground="white",\
                        activebackground="#4e97fe")
                        
        self.unlock_button.grid(
                row=7, column=1)
        
        self.create_button = tkinter.Button(
                self.create_frame, text="Create", command=lambda: Create_DB(gpg, self),\
                        fg="white", bg="#187bcd", activeforeground="white",\
                        activebackground="#4e97fe")
                        
        self.create_button.grid(
                row=2, column=0)
    
         
        


#Class to generate sidebar navigation panel
class Sidebar:
        
    def __init__(self, db, parent, gpg):
        #Define variables to hold tables and displays
        self.table_view = None
        self.current_table = None
        
        #Save attributesd we will need for easy referencing
        self.keyfile_path = parent.parent.keyfile_path
        self.parent = parent
        self.db = db
        self.gpg = gpg


        #Create scrollable frame to use for sidepanel controls
        self.side_scroll = Scrollable_Frame(
                parent.display_window, False, True, 180, 700, 0, 0, 2, 1)
        
        self.side_scroll.canvas.config(
                bg="white")
        
        self.side_scroll.frame.config(
                padx=20, bg="white")

        #Define labelframes to hold buttons
        self.control_bar = tkinter.LabelFrame(
                self.side_scroll.frame, width=170, height=700, padx=20,\
                pady=5, text="Database", bg="white", fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.control_bar.grid(
                row=0, column=0)

        self.nav_bar = tkinter.LabelFrame(
                self.side_scroll.frame, width=170, height=700, padx=20,\
                pady=5, text="Navigation", bg="white", fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.nav_bar.grid(
                row=1, column=0)
        
        self.buttons()
        
    #Function to generate buttons for side control panel
    def buttons(self): 
        
        #Get list of current database tables
        self.tables_list = get_tables(self.db)
        
        #add table button
        self.add_table_button = tkinter.Button(
                self.control_bar, text="Add table", command=lambda:
                    Add_Table(self), width=10, fg="white",\
                    bg="#187bcd", activeforeground="white", activebackground="#4e97fe")
        
        self.add_table_button.grid(
                row=1, column=0, pady=5)
        
        #Delete group button
        self.delete_group_button = tkinter.Button(
                self.control_bar, text="Delete table", command=lambda:
                    Delete_Table(self), width=10,\
                    fg="white", bg="#187bcd", activeforeground="white",\
                    activebackground="#4e97fe")
        
        self.delete_group_button.grid(
                row=2, column=0, pady=5)
        
        #Password generator button
        self.password_generator_button = tkinter.Button(
                self.control_bar, text="Password\nGenerator", command=lambda:
                    Password_Generator(), width=10, fg="white",\
                    bg="#187bcd", activeforeground="white",\
                    activebackground="#4e97fe")
        
        self.password_generator_button.grid(
                row=3, column=0, pady=5)
        
        #Define update password button
        self.update_pass_button = tkinter.Button(
                self.control_bar, text="Change\nMaster Pass", command=lambda:
                    Update_Password(
                            self),\
                            width=10, fg="white", bg="#187bcd",\
                            activeforeground="white", activebackground="#4e97fe")
        
        self.update_pass_button.grid(
                row=4, column=0, pady=5)
        
        #Define lock button
        self.lock_button = tkinter.Button(
                self.control_bar, text="Lock", command=lambda:
                    self.parent.lock(self.gpg), width=10, fg="white",\
                    bg="#187bcd", activeforeground="white",\
                    activebackground="#4e97fe")
        
        self.lock_button.grid(
                row=5, column=0, pady=5)
        
        
        #Define lists to store controls and functions
        self.table_controls = []
        self.window_functions = []
        
        #Generate buttons and functions for each table
        self.generate_table_buttons()
        
        
        
    def generate_function(self):
        #Define function to handle this table's button
        def f(db, table, x, gpg):
            #Store currently viewed table for refreshing elsewhere
            self.current_table = table    
            try:
                #Clear current display, point at selected table and refresh display
                self.table_view.clear_view()    
                self.table_view.table_name = table
                self.table_view.refresh()
            except:
                #If no table display exists yet generate new display with selected table
                self.table_view = Table_Display(
                        table, self)
            
            #clear sidepanel buttons 
            self.clear_buttons()
            
            #generate updated sidepanel buttons
            self.buttons()
            
        #append generated function to list
        self.window_functions.append(f)
        

    def generate_table_buttons(self):
        #Loop over list of tables and generate function and button for each
        for i in range(len(self.tables_list)):
            #generate function to handle button for this table
            self.generate_function()

            #generate buttons for each table
            self.table_button = tkinter.Button(
                    self.nav_bar, text=self.tables_list[i], command=lambda x=i:
                        self.window_functions[x](
                                self.db, self.tables_list[x], x, self.gpg),\
                                width=10, fg="white", bg="#187bcd",\
                                activeforeground="white",\
                                activebackground="#4e97fe", wraplength=100)
                                
            self.table_button.grid(
                    row=i, column=0, pady=5)
            
            #Invert button colours for currently viewed table
            if self.current_table != None:
                if self.current_table == self.tables_list[i]:
                    self.table_button.config(bg="white", fg="#187bcd",\
                                activebackground="white",\
                                activeforeground="#4e97fe")
            
            #Store each button in list
            self.table_controls.append(
                    self.table_button)
        
        
        
    #Function to destroy sidebar controls so we can create new ones 
    def clear_buttons(self):
        del self.tables_list
        for i in range(len(self.table_controls)):
            self.table_controls[i].destroy()
        del self.table_controls
        self.add_table_button.destroy()
        self.delete_group_button.destroy()
        self.password_generator_button.destroy()
        self.lock_button.destroy()
        self.update_pass_button.destroy()
        for i in self.window_functions:
            del i
        del self.window_functions
        try:
            self.table_view.__del__()
            del self.current_table
        except:
            pass


#Class containing code to generate display table of current database table contents       
class Table_Display:
    
    def __init__(self, table_name, sidebar): 
        #Save attributes we need for easy referencing
        self.table_name = table_name
        self.sidebar = sidebar
        self.gpg = sidebar.gpg
        self.db = sidebar.db
        
        #Event handler to detect window manually closed by user
        sidebar.parent.display_window.protocol(
                "WM_DELETE_WINDOW", self.clear_view())

        #Define scrollable frame for top display window
        self.frame = Scrollable_Frame(
                sidebar.parent.display_window, True, True, 800, 500, 0, 1, 1, 1)        
        self.frame.frame.config(bg="white")
        self.frame.canvas.config(bg="white")

        #define frames used for bottom control panel
        self.bottom_bar = tkinter.Frame(
                sidebar.parent.display_window, width=500,\
                height=200, bg="white")
        
        self.bottom_bar.grid(
                row=1, column=1)
        
        #If any unhandled errors encountered during display generation lock database for safety
        try:
            self.generate_display()
        except:
            Error_Message(
                            "Encountered a fatal error!\nLocking database")        
            self.sidebar.parent.lock()




    def generate_display(self):
        
        #Define lists, dicts to hold widgets and functions
        self.table_headings = []
        self.password_entries = {}
        self.grid_display = {}
        self.cvv_entries = {}   
        self.card_entries = {}
               
        
        #Create detection variables to determine table style
        self.username_ref = None
        self.password_ref = None
        self.note_ref = None
        self.card_num_ref = None
        self.cvv_ref = None
        self.note_ref = None
        self.file_table = False
        self.table_style = None
        
        #Create labelframes to hold controls
        self.table_buttons = tkinter.LabelFrame(
                self.bottom_bar, text="Table Controls", padx=30,\
                pady=12, borderwidth=4, relief=GROOVE, bg="white",\
                fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.table_buttons.grid(
                row=1, column=1)
        
        self.entry_buttons = tkinter.LabelFrame(
                self.bottom_bar, text="Entry Controls", padx=30, pady=10,\
                borderwidth=4, relief=GROOVE, bg="white", fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.entry_buttons.grid(
                row=2, column=1)

        #Query database for table headings, 
        self.columns, self.column_headings = get_column_headings(self.db, self.table_name, 1)

        #if unsuccessful lock database for safety
        if self.column_headings == None or self.column_headings == None:
            Error_Message(
                    "Encountered a fatal error!\nLocking database")
            self.sidebar.parent.lock()

        else:                      
            #Extract data from table & check for success
            self.table_data, self.id_refs = self.get_table_data()
            
            #If unsuccessful lock database for safety
            if self.table_data == None or self.id_refs == None:
                    Error_Message(
                            "Encountered a fatal error!\nLocking database")        
                    self.sidebar.parent.lock()
            else:
                #Detect table style    
                self.table_style = self.detect_table_style()
        
                #Generate controls based on table style         
                self.generate_standard_controls()
                if self.table_style == 3:
                    self.generate_secure_note_controls()
                elif self.table_style == 4:
                    self.generate_credit_card_controls()
                elif self.table_style == 1:
                    self.generate_pass_table_controls()
        
                #Generate radio buttons to select each entry in table
                self.select_buttons = self.generate_selection_controls()
                
                #Generate main table display
                self.generate_table()
        
                #Declare manager dict for updating display with decrypted values
                self.grid_values = Manager().dict()
                
                #Spawn processes to decrypt each entry and store in manager dict
                self.decrypt_entries()
                
                #Insert decrypted values into table display
                self.insert_entries()
                
                #Delete decrypted entries from memory
                self.delete_entries()


    def get_table_data(self):
        #Define lists to store extracted data and db entry ids
        table_data = {}
        id_refs = [] 
        
        #Create cursor to issue commands to database
        c = self.db.cursor()
        
        try:
            #Issue command to extract all data for current table
            self.data = c.execute(
                    "SELECT * FROM '{}';".format(self.table_name))
            #Commit queries to database
            self.db.commit()
        #If we cannot communicate with database inform user and lock for safety
        except:
            return None, None
        
        #loop over returned data append each row and it's id to appropriate list
        for row in self.data:
            table_data[row[0]] = row
            id_refs.append(row[0])
            
        #Return extracted data
        return table_data, id_refs



    def delete_entries(self):
        #Delete all decrypted entries held in memory
        for key in self.grid_values.keys():
            del self.grid_values[key]



    def insert_entries(self):
        #Insert data from decrypted values into grid display
        for key, value in self.grid_values.items():
            try:
                self.grid_display[
                        key].insert(
                        0, value)
            #Adjust insert command for text entry
            except:
                self.grid_display[
                        key].insert(
                        END, value)

        

    def decrypt_entries(self):
        procs = []
        #Loop over grid and spawn a process to decrypt each entry
        for i in range(len(self.column_headings)):
            #Skip Id column
            if i == 0:
                pass
            #Skip file data column for file storage tables
            elif self.table_style == 2 and self.column_headings[i].lower() == "file":
                pass
            
            else:
                #For each other cell in table spawn process to decrypt content
                for key in self.table_data.keys():
                    self.grid_values[
                            "{0},{1}".format(key, i)] = ""
        
                    try:
                        #Spawn process for this entry and add to list
                        p = Process(
                                target=decrypt_item, args=(
                                        bytes(self.table_data[key][i]),\
                                        i, key, self.grid_values,\
                                        self.sidebar.parent.crypt_key, self.gpg))
                        p.start()
                        procs.append(p)
                    except:
                        try:
                            #Adjust process command for text entries
                            p = Process(
                                    target=decrypt_item, args=(
                                            bytes(self.table_data[key][i], "utf-8"),\
                                            i, key, self.grid_values,\
                                            self.sidebar.parent.crypt_key, self.gpg))
                            p.start()
                            procs.append(p)
                        except:
                            pass
            
        #Call garbage collector to avoid it being triggered by spawned thread.            
        gc.collect()
        
        #Wait for all processes to complete before proceding
        for proc in procs:
            proc.join()
    

    def generate_pass_table(self, j):
        e = tkinter.Entry(
                self.frame.frame, width=18, show="*",\
                bg="white", font=(
                        "Sans-serif", 10, "bold"),\
                        highlightbackground="#187bcd",\
                        highlightcolor="#187bcd")
                        
        self.password_entries[self.table_data[j][0]] = e
        return e
    
    def generate_cc_table(self, i, j):
        e = tkinter.Entry(
                self.frame.frame, width=18, show="*",\
                bg="white", font=(
                        "Sans-serif", 10, "bold"),\
                        highlightbackground="#187bcd",\
                        highlightcolor="#187bcd")
                        
        #Append entries to appropriate lists so we can generate show functions
        if self.column_headings[i].lower() == "cvv number":
            self.cvv_entries[
                    self.table_data[j][0]] = e
        
        else:
            self.card_entries[
                    self.table_data[j][0]] = e
        return e
    
    def generate_note_table(self):
        e = tkinter.Text(
            self.frame.frame, height=10, width=40,\
            bg="white", font=(
                    "Sans-serif", 10, "bold"),\
                    highlightbackground="#187bcd",\
                    highlightcolor="#187bcd")
        return e
    
    def generate_file_table(self, j):
        e = tkinter.Button(
                        self.frame.frame, text="Retrieve file",\
                        command=lambda x=j:Retrieve_File(
                                self.table_data[x],\
                                self.column_headings, self.sidebar),\
                                fg="white", bg="#187bcd",\
                                activeforeground="white",\
                                activebackground="#4e97fe")
        return e
        

    
    def generate_table(self):
        #Loop over column_headings and create a label widget to mark each column, skipping id
        for i in range(len(self.column_headings)):
            if self.column_headings[i] == "id":
                pass
            else:
                l = tkinter.Label(
                        self.frame.frame, text=self.column_headings[i],\
                        bg="white", fg="#004aff", font=(
                        "Sans-serif", 10, "bold"))
                
                l.grid(row=0, column=i)
                
                l.config(padx=10, pady=5)
                
                #Store generated labels in a list
                self.table_headings.append(l)
            #Loop over entries in table & generate display table
                for j in self.table_data.keys():
                    #Generate entries, if looking at a password column use starred out entry instead
                    if self.column_headings[i].lower() == "password" and self.table_style == 1:
                        e = self.generate_pass_table(j)
 
                    #Define table layout for credit card column    
                    elif (self.table_style == 4 and self.column_headings[i].lower() == "card number")\
                    or (self.table_style == 4 and self.column_headings[i].lower() == "cvv number"):
                        e = self.generate_cc_table(i, j)

                    #Define table layout for secure note column
                    elif self.table_style == 3 and self.column_headings[i] == "Note":
                        e = self.generate_note_table()
                            
                    #Define table layout for file table column
                    elif self.table_style == 2 and self.column_headings[i].lower() == "file":
                        e = self.generate_file_table(j)
                    #Define standard layout for all other columns
                    else:
                        e = tkinter.Entry(
                                self.frame.frame, width=18, bg="white", font=(
                                        "Sans-serif", 10, "bold"),\
                                        highlightbackground="#187bcd",\
                                        highlightcolor="#187bcd")

                    #Insert generated widget into display and add to dictionary
                    #with grid reference as key so we can insert values once decrypted
                    e.grid(
                            row=j + 1, column=i)
                    
                    self.grid_display[
                            "{0},{1}".format(
                                    self.table_data[j][0], i)] = e


    def generate_selection_controls(self):
        #Generate a radio button for each entry & store in list
        select_buttons = []
        
        #Variable to hold selected entry id and blank out any "show" boxes on new entry selection
        self.entry_check = IntVar()
        self.entry_ref = IntVar()
        
        #Loop over table entries and create radio button to select each one
        for i in range(len(self.table_data)):
            select = tkinter.Radiobutton(
                    self.frame.frame, variable=self.entry_ref,\
                    value=self.id_refs[i], command=self.hide_entry,\
                    bg="white", activebackground="white",\
                    highlightbackground="#187bcd",\
                    highlightcolor="#187bcd")
                    
            select.grid(
                    row=self.table_data[self.id_refs[i]][0] + 1, column=0)
            
            select_buttons.append(select)
        #Set first entry i table to selected (provided there are entries in current table)
        try:
            select_buttons[0].select()
        except:
            pass
        
        #Set entry check to starting value of entry ref
        self.entry_check.set(
                self.entry_ref.get())
        return select_buttons


    def generate_pass_table_controls(self):
                   
        #Function to copy selected entry's password
        def copy_password():
            try: 
                xerox.copy(
                        str(self.gpg.decrypt(
                                self.table_data[
                                        self.entry_ref.get()][
                                                self.password_ref],\
                                        passphrase=self.sidebar.parent.crypt_key)).strip(),\
                                xsel=True)
            except:
                pass


        #function to listen for change in show password checkboxes
        def show_password():
            self.password_entries[
                    self.entry_ref.get()].config(
                    show=self.show_var.get())


        #declare variable for show password box
        self.show_var = StringVar()


        #Generate controls and stick to bottom panel
        self.copy = tkinter.Button(
                self.entry_buttons, text="Copy Password",\
                command=copy_password, anchor="n", fg="white",\
                bg="#187bcd", activeforeground="white",\
                activebackground="#4e97fe", width=12)
        
        self.copy.grid(
                row=1, column=2)
        
        self.show = tkinter.Checkbutton(
                self.entry_buttons, text="Show password",\
                variable=self.show_var, onvalue="", offvalue="*",\
                command=show_password, bg="white", fg="#004aff",\
                activebackground="white", activeforeground="#1874CD")
        
        self.show.deselect()
        
        self.show.grid(
                row=2, column=2)  


    def generate_credit_card_controls(self):
        
        #functions to copy card and cvv number
        def card():
            try:
                xerox.copy(
                        str(self.gpg.decrypt(
                                self.table_data[
                                        self.entry_ref.get()][
                                                self.card_num_ref],\
                                        passphrase=self.sidebar.parent.crypt_key)).strip(),\
                                xsel=True)
            except:
                pass
 
        def cvv():
            try:
                xerox.copy(
                        str(self.gpg.decrypt(
                                self.table_data[
                                        self.entry_ref.get()][
                                                self.cvv_ref],\
                                        passphrase=self.sidebar.parent.crypt_key)).strip(),\
                                xsel=True)
            except:
                pass

        #Functions to listen for changes in show card/cvv boxes
        def show_card():
            self.card_entries[
                    self.entry_ref.get()].config(
                    show=self.show_card_var.get())

        
        def show_cvv():
            self.cvv_entries[
                    self.entry_ref.get()].config(
                    show=self.show_cvv_var.get())

        #Declare variables for show card/cvv boxes
        self.show_card_var = StringVar()            
        self.show_cvv_var = StringVar()

        #Generate controls and stick to bottom panel        
        self.copy_card = tkinter.Button(
                self.entry_buttons, text="Copy Card #", command=card,\
                anchor="n", fg="white", bg="#187bcd",\
                activeforeground="white", activebackground="#4e97fe",\
                width=12)
        
        self.copy_card.grid(
                row=1, column=2)
        
        
        self.copy_cvv = tkinter.Button(
                self.entry_buttons, text="Copy CVV #", command=cvv,\
                anchor="n", fg="white", bg="#187bcd",\
                activeforeground="white", activebackground="#4e97fe",\
                width=12)
        
        self.copy_cvv.grid(
                row=1, column=3)
        
        self.show_card = tkinter.Checkbutton(
                self.entry_buttons, text="Show card number",\
                variable=self.show_card_var, onvalue="", offvalue="*",\
                command=show_card, bg="white", fg="#004aff", 
                activebackground="white", activeforeground="#1874CD")
        
        self.show_card.grid(
                row=2, column=2)
        
        self.show_card.deselect()
                                       
        self.show_cvv = tkinter.Checkbutton(
                self.entry_buttons, text="Show cvv Number",\
                variable=self.show_cvv_var, onvalue="", offvalue="*",\
                command=show_cvv, bg="white", fg="#004aff",\
                activebackground="white", activeforeground="#1874CD")
        
        self.show_cvv.grid(
                row=2, column=3)
        
        self.show_cvv.deselect()


    def generate_secure_note_controls(self):
        #function for copy password button

        def copy_note():
            try:
                xerox.copy(
                        str(self.gpg.decrypt(
                                self.table_data[
                                        self.entry_ref.get()][
                                                self.note_ref],\
                                        passphrase=self.sidebar.parent.crypt_key)).strip(),\
                                xsel=True)
            except:
                pass

        
        #Generate copy note button for each entry
        self.copy = tkinter.Button(
                self.entry_buttons, text="Copy Note", command=copy_note,\
                anchor="n", fg="white", bg="#187bcd",\
                activeforeground="white", activebackground="#4e97fe",\
                width=12)
        
        self.copy.grid(
                row=1, column=2)


    def generate_standard_controls(self):
                #Define add entry button
        self.add_button = tkinter.Button(
                self.table_buttons, text="Add entry", command=lambda:
                    Entry_Window(
                            self.column_headings, None, \
                            None, self, self.table_style),\
                            anchor="n", fg="white", bg="#187bcd",\
                            activeforeground="white",\
                            activebackground="#4e97fe", width=12)
                            
        self.add_button.grid(
                row=0, column=0)

        #Define add column button
        self.add_column_button = tkinter.Button(
                self.table_buttons, text="New column", command=lambda: Add_Column\
                                                (self),\
                                                anchor="n", fg="white",\
                                                bg="#187bcd", activeforeground="white",\
                                                activebackground="#4e97fe", width=12)
        
        self.add_column_button.grid(
                row=0, column=1)
        
        #Define delete column button
        self.delete_column_button = tkinter.Button(
                self.table_buttons, text="Delete column", command=lambda :
                    Delete_Column(
                            self.column_headings, self.sidebar, self.table_style),anchor="n",\
                            fg="white", bg="#187bcd", activeforeground="white",\
                            activebackground="#4e97fe", width=12)
        
        self.delete_column_button.grid(
                row=0, column=2)
         
        #Refresh display
        self.refresh_button = tkinter.Button(
                self.table_buttons, text="Refresh", command=lambda:
                    self.refresh(),\
                            anchor="n", fg="white",\
                            bg="#187bcd", activeforeground="white",\
                            activebackground="#4e97fe", width=12)
        
        self.refresh_button.grid(
                row=0, column=3)

        #Define delete entry button
        self.delete_button = tkinter.Button(
                self.entry_buttons, text="Delete entry", command=lambda:
                    self.delete_entry(self.entry_ref.get()),\
                            anchor="n", fg="white", bg="#187bcd",\
                            activeforeground="white",\
                            activebackground="#4e97fe", width=12)
        
        self.delete_button.grid(
                row=1, column=0)
        
        #Define edit entry button
        self.edit = tkinter.Button(
                self.entry_buttons, text="Edit entry", command=lambda:
                    self.edit_e(
                            self.sidebar),\
                            anchor="n", fg="white", bg="#187bcd",\
                            activeforeground="white",\
                            activebackground="#4e97fe", width=12)
        
        self.edit.grid(
                row=1, column=1)
            

    def detect_table_style(self):
        #Loop over column headings and detect what style of table we are looking at
        table_style = None
        for i in range(len(self.columns)):
            if self.columns[i][2] == 'BLOB':
                self.file_table = True
            elif self.column_headings[i].lower() == "note":
                self.note_ref = i
            elif self.column_headings[i].lower() == "card number":
                self.card_num_ref = i
            elif self.column_headings[i].lower() == "cvv number" or\
                        self.column_headings[i].lower() == "cvv":
                self.cvv_ref = i
            elif self.column_headings[i].lower().strip() == "username":
                self.username_ref = i
            elif self.column_headings[i].lower().strip() == "password":
                self.password_ref = i

        #Check what we've found in the headers and determine table type
        if self.file_table == True:
            table_style = 2
        elif self.card_num_ref != None and self.cvv_ref != None: 
            table_style = 4
        elif self.username_ref != None and self.password_ref != None:
            table_style = 1
        elif self.note_ref != None and self.cvv_ref == None and\
                    self.file_table == False and\
                    self.username_ref == None and self.password_ref == None:
            table_style = 3
        else:
            table_style = 5
        return table_style
            

    #Function to call edit entry window
    def edit_e(self, sidebar):
        #try block in case we are looking at an empty table
        try:
            Entry_Window(
                    self.column_headings, self.table_data[
                            self.entry_ref.get()],\
                            self.entry_ref.get(), self,\
                            self.table_style)
        except:
            Error_Message("No entries in this table to edit.")
            

    #Function to return password/card entry to show="*" state if new entry selected
    def hide_entry(self):
        try:
            self.card_entries[
                    self.entry_check.get()].config(show="*")
            
            self.cvv_entries[
                    self.entry_check.get()].config(show="*")
            
            self.show_card.deselect()
            
            self.show_cvv.deselect()
        except:
            pass
        try:
            self.password_entries[
                    self.entry_check.get()].config(show="*")
            
            self.show.deselect()
        except:
            pass
        self.entry_check.set(
                self.entry_ref.get())
        
        
     
    #Function to delete selected entry from current table once user has given confirmation
    def delete(self, table_name, id_ref):
        #Create cursor to issue commands to database
        c = self.db.cursor()
        try:
            #Issue command to delete selected entry
            c.execute(
                    "DELETE FROM '{0}' WHERE id = {1};".format(
                            table_name, id_ref))
            
            #Commit changes to database to  we can use another cursor elsewhere
            self.db.commit()
            
            #Close popup and refresh display
            self.refresh()
            
            self.confirmation.__del__()
        except:
            self.db.commit()
            
            Error_Message(
                    "Error deleting entry, please try again.")
        
        
    #function to ask user for confirmation then delete a selected entry from the curent table
    def delete_entry(self, id_ref):

        #Check to ensure there is an entry to delete
        if id_ref == 0:
            Error_Message("No entry to delete!")
        else:
            #Create confirmation popup to ensure correct entry weas selected
            self.confirmation = Confirmation_Message(
                    self,"Delete entry?", "Ok", "Cancel",\
                    "Are you sure?\nOnce deleted details cannot be retrieved.")
            
            self.confirmation.popup_ok.config(
                    command=lambda: self.delete(
                            self.table_name, id_ref))
            
            self.confirmation.popup_cancel.config(
                    command=self.confirmation.__del__)


    #Function to refresh current display
    def refresh(self):
        #Clear current widgets from display
        self.clear_view()
        #Generate new display
        self.generate_display()
    
    #Function to destroy the contents of the current display
    def clear_view(self):
        try:
            for widget in self.frame.frame.winfo_children():
                widget.destroy()
            for widget in self.bottom_bar.winfo_children():
                widget.destroy()
        except:
            pass

        #Delete variables to bew recreated on generation of new display 
        try:
            del self.table_headings
            del self.password_entries 
            del self.grid_display
            del self.cvv_entries 
            del self.card_entries
            del self.username_ref
            del self.password_ref
            del self.note_ref
            del self.card_num_ref
            del self.cvv_ref
            del self.note_ref
            del self.file_table
            del self.table_style
        except:
            pass

#Class containing window and functionality to update master pasword and keyfile    
class Update_Password:
    
    def __init__(self, sidebar):
        #Save attributes for easy referencing
        self.sidebar = sidebar
        self.db = self.sidebar.db
        self.gpg = self.sidebar.gpg
        self.selec_keyfile = self.sidebar.parent.parent.keyfile_path
        
        #Define window
        self.update_window = tkinter.Toplevel()
        self.update_window.geometry("600x540")
        self.update_window.config(bg="white")
        self.update_window.title("Castle: Update Password")
        self.update_window.resizable=(0, 0)
        
        #Event handler to detect window manually closed by user
        self.update_window.protocol(
                "WM_DELETE_WINDOW", self.__del__)
        
        #Define frames to hold widgets
        self.password_frame = tkinter.LabelFrame(
                self.update_window, text="Update Password", padx=15,
                pady=20, borderwidth=4, relief=GROOVE, bg="white",\
                fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.password_frame.grid(
                row=1, column=1)
        
        self.keyfile_frame = tkinter.LabelFrame(
                self.update_window, text="Update Keyfile", padx=35,
                pady=20, borderwidth=4, relief=GROOVE, bg="white",\
                fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.keyfile_frame.grid(
                row=3, column=1)
        
        self.button_frame = tkinter.Frame(
                self.update_window, bg="white")
        
        self.button_frame.grid(
                row=5, column=1)
        
        self.side_spacer = tkinter.Frame(
                self.update_window, width=12, height=20, bg="white")
        
        self.side_spacer.grid(
                row=0, column=0)
        
        self.mid_spacer = tkinter.Frame(
                self.update_window, height=20, bg="white")
        
        self.mid_spacer.grid(
                row=2, column=1)
        
        self.bottom_spacer = tkinter.Frame(
                self.update_window, height=20, bg="white")
        
        self.bottom_spacer.grid(
                row=4, column=1)
        
        self.button_spacer = tkinter.Frame(
                self.button_frame, width=350, bg="white")
        
        self.button_spacer.grid(
                row=1, column=2)

        self.password_warning = tkinter.Label(
                self.password_frame, text=\
                "Warning: Password update will ONLY apply to this copy of database",\
                pady=5, bg="white", fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.password_warning.grid(
                row=1, column=1, columnspan=2)
        
        #Define heading labels
        self.enter_label = tkinter.Label(
                self.password_frame, text=\
                "Please enter your new master password",\
                pady=5, bg="white", fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.enter_label.grid(
                row=2, column=1)
        
        #Define password and comfirmation entries
        self.enter_password = tkinter.Entry(
                self.password_frame, width=40, show="*", bg="white", font=(
                        "Sans-serif", 10, "bold"))
        
        self.enter_password.grid(
                row=3, column=1)
        
        #Define show password checkbuttons
        self.pass_var = StringVar()
        
        self.show_password = tkinter.Checkbutton(
                self.password_frame, text="Show password", onvalue="",\
                offvalue="*", variable=self.pass_var,\
                command=self.update_pass_box, bg="white", fg="#004aff",\
                activebackground="white", activeforeground="#1874CD")
        
        self.show_password.grid(
                row=3, column=2)
        
        self.show_password.deselect()
        
        self.confirm_label = tkinter.Label(
                self.password_frame, text=\
                "Please confirm your new master password",\
                pady=5, bg="white", fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.confirm_label.grid(
                row=4, column=1)
        
        self.confirm_password = tkinter.Entry(
                self.password_frame, width=40, show="*", bg="white", font=(
                        "Sans-serif", 10, "bold"))
        
        self.confirm_password.grid(
                row=5, column=1)
                
        self.confirm_var = StringVar()
        
        self.show_confirm = tkinter.Checkbutton(
                self.password_frame, text="Show password", onvalue="",\
                offvalue="*", variable=self.confirm_var,\
                command=self.update_confirm_box, bg="white", fg="#004aff",\
                activebackground="white", activeforeground="#1874CD")
        
        self.show_confirm.grid(
                row=5, column=2)
        
        self.show_confirm.deselect()
        
        #Define selection button for keyfile update
        self.update_select = IntVar()
        
        self.update_key = tkinter.Checkbutton(
                self.keyfile_frame, text="Regenerate keyfile",\
                onvalue=1, offvalue=0, variable=self.update_select,\
                pady=5, bg="white", fg="#004aff", activebackground="white",\
                activeforeground="#1874CD")
        
        self.update_key.deselect()
        
        self.update_key.grid(
                row=1, column=1)
        
        #Define warning labels
        self.update_warning = tkinter.Label(
                self.keyfile_frame, text=\
                "Warning: This will render any backups of your keyfile useless",\
                pady=5, bg="white", fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.update_warning.grid(
                row=2, column=1, columnspan=3)
        
        #Define entry and button for browser and entry for new keyfile name
        self.browse_label = tkinter.Label(
                self.keyfile_frame, text=\
                "Please select location to create your new keyfile",\
                pady=5, bg="white", fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.browse_label.grid(
                row=3, column=1, columnspan=2)
        
        
        self.keyfile_path = tkinter.Entry(
                self.keyfile_frame, width=40, bg="white", font=(
                        "Sans-serif", 10, "bold"))
        
        self.keyfile_path.grid(
                row=4, column=1, columnspan=2)
        
        self.browse_button= tkinter.Button(
                self.keyfile_frame, text="Browse", command=lambda: browse(
                        0, self.keyfile_path, None, None, self.update_window, None),\
                        width=10, fg="white", bg="#187bcd",\
                        activeforeground="white", activebackground="#4e97fe")
        
        self.browse_button.grid(
                row=4, column=3)
        
        self.name_label = tkinter.Label(
                self.keyfile_frame, text=\
                "Please enter a name for your new keyfile",\
                pady=5, bg="white", fg="#004aff", font=(
                "Sans-serif", 10, "bold"))
        
        self.name_label.grid(
                row=5, column=1, columnspan=2)
        
        self.keyfile_name = tkinter.Entry(
                self.keyfile_frame, width=40, bg="white", font=(
                        "Sans-serif", 10, "bold"))
        
        self.keyfile_name.grid(
                row=6, column=1, columnspan=2)
        
        
        #Define ok and cancel buttons
        self.cancel_button = tkinter.Button(
                self.button_frame, text="Cancel", command=self.__del__,\
                width=10, fg="white", bg="#187bcd",\
                activeforeground="white", activebackground="#4e97fe")
        
        self.cancel_button.grid(
                row=1, column=1)

        
        self.ok_button = tkinter.Button(
                self.button_frame, text="Ok", command=lambda: self.update(), width=10,\
                        fg="white", bg="#187bcd",\
                        activeforeground="white",\
                        activebackground="#4e97fe")
        
        self.ok_button.grid(
                row=1, column=3)
    
       
    #Function to update password box if show password button is clicked
    def update_pass_box(self):
        self.enter_password.config(
                show=self.pass_var.get())

    #Function to update confirm password box if show password button is clicked
    def update_confirm_box(self):
        self.confirm_password.config(
                show=self.confirm_var.get())

    #Function to update master password with given inputs
    def update(self):
        
        #Safety checks to ensure password was entered and passwords in both boxes match
        if self.enter_password.get() != self.confirm_password.get():
            Error_Message(
                    "Entered passwords did not match!")
        
        elif self.enter_password.get().strip() == "":
            Error_Message(
                    "Please enter a new master password!")
        
        #If all ok proceed and update password
        else:
            #Create cursor to communicate with database
            self.c = self.db.cursor()
            
            #Check to see if user selected option to generate new keyfile
            if self.update_select.get() == 0:
                
                #update master pasword held in memory and encrypt keyfile password with new master pass
                extracted_key = get_keypass(
                        self.c, str(
                                self.gpg.decrypt(
                                        str(self.sidebar.parent.master_pass),\
                                        passphrase=self.sidebar.parent.crypt_key))\
                                , self.gpg)
                
                #Encrypt stored password with new master pass and update database
                self.update_keyfile_pass(extracted_key)
                
                #Present success message to user
                Error_Message(
                        "Password changed successfully!")    
                
                #Close window
                self.__del__()
            
            #if new keyfile to be generated
            else:
                if self.generate_new_keyfile() == 0:
                    #Present success message to user
                    Error_Message(
                            "Password changed successfully!")
     
                    #Close window
                    self.__del__()
  
    
    def generate_new_keyfile(self):
        #Generate path for new file
        keypath = os.path.join(
                self.keyfile_path.get(), self.keyfile_name.get()) + ".txt"
            
        #Safety checks to ensure we have all the information to proceed
        if self.keyfile_path.get().strip() == "":
            Error_Message(
                    "Please select a location to create new keyfile")
            return 1
        
        elif os.path.isfile(keypath + ".gpg"):
            Error_Message(
                    "Chosen file already exists!\nPlease change name or location")
            return 1
        
        elif self.keyfile_name.get().strip() == "":
            Error_Message(
                    "Please enter a name for your new keyfile")
            return 1
        else:
            
            #If all checks passed successfully generate
            #characterset for new keyfile pass
            self.charset = "^*$%@#!&.=~+_-"\
            + string.ascii_letters + string.digits
            
            #Generate new random password to store
            keypass = "".join(random.SystemRandom().choice(self.charset)for i in range (256))
            
            #Update stored keyfile password in database
            self.update_keyfile_pass(keypass)
            
            if self.update_keyfile(keypath, keypass) == 0:
                return 0
            else:
                return 1
            
            
    def update_keyfile(self, keypath, password):
        #create new keyfile and write crypt_pass
        with open(keypath, "w") as file:
            file.write(
                    self.sidebar.parent.crypt_key)
        
        #Encrypt new keyfile and check for success
        if encrypt(password, keypath, self.gpg) == 1:
            Error_Message(
                    "Failed to create keyfile")
            return 1
        else:
            #delete plaintext copy of new keyfile
            shred(keypath)
            #Once keyfile generated successfully update main window
            #keyfile_path entry box with new file
            keypath = keypath + ".gpg"
            self.selec_keyfile.delete(
                    0, END)
            
            self.selec_keyfile.insert(
                    0, keypath)

            return 0

    
    
    def update_keyfile_pass(self, keypass):
        #Update master password held in memory
        self.sidebar.parent.master_pass = str(self.gpg.encrypt(
                self.enter_password.get(), recipients=None,\
                passphrase=self.sidebar.parent.crypt_key,\
                symmetric=cipher.upper(), armor=True))
        
        #Encrypt keyfile_pass with new master_password
        updated_key = str(self.gpg.encrypt(
                keypass, recipients=None,\
                symmetric=cipher.upper(), armor=True,\
                passphrase=self.enter_password.get()))
        
        #Insert re-encrypted keyfile password into table
        self.c.execute(
                "UPDATE 'keyfile_pass' SET 'pass' = ? WHERE id = 1", (
                        updated_key,))
        #Commit changes to database
        self.db.commit()

     
    def __del__(self):
        try:
            del self.charset
            del self.keyfile_pass
            del self.keypath
            del self.c
        except:
            pass
        try:
            del self.extracted_key
        except:
            pass
        
        try:
            self.password_warning.destroy()
            self.update_warning.destroy()
            self.enter_label.destroy()
            self.enter_password.destroy()
            self.show_password.destroy()
            self.confirm_label.destroy()
            self.confirm_password.destroy()
            self.show_confirm.destroy()
            self.ok_button.destroy()
            self.cancel_button.destroy()
            self.update_key.destroy()
            self.browse_label.destroy()
            self.keyfile_path.destroy()
            self.browse_button.destroy()
            self.name_label.destroy()
            self.keyfile_name.destroy()
            self.button_frame.destroy()
            self.keyfile_frame.destroy()
            self.password_frame.destroy()
        except:
            pass
        try:
            del self.update_select
            del self.pass_var
            del self.confirm_var
            self.update_window.destroy()
        except:
            pass
        
        

#Portable file/directory browser function
def browse(style, output_entry, title, filetype, parent, extra_entry):
    #If style == 1 open a file dialog
    if style == 1:
        file = tkinter.filedialog.askopenfilename(
                title=title, filetypes=[
                        filetype], parent=parent)
        #Send selected file location to output entry box, clear entry first
        try:
            output_entry.delete(
                    0, END)
            output_entry.insert(
                    0, file)
            if extra_entry != None:
                extra_entry.delete(
                        0, END)
                extra_entry.insert(
                        0, os.path.split(file)[-1])
        except:
            pass
    #If style == 0 open a folder dialog
    else:
        file = tkinter.filedialog.askdirectory(
                parent=parent)
        #Send selected file location to output entry box, clear entry first
        output_entry.delete(
                0, END)
        try:
            output_entry.insert(
                    0, file)
        except:
            pass

#Function to decrypt database file with given master password
def decrypt(master_pass, filepath, gpg):
    #Open file
    file = open(
            filepath, "rb")
   
    #generate path for decrypted file
    savefile = filepath[0:-4]
    decrypted_data = gpg.decrypt_file(
            file, passphrase=master_pass, output=savefile)
    
    file.close()
    
    #Delete password from memory
    del master_pass
    
#Check file was decrypted successfully
    if decrypted_data.ok != True:
        return 1
    else:
        return 0

#Function called to decrypt a single entry from returned table data
def decrypt_item(data, i, j, dictionary, crypt_key, gpg):
    dictionary[
            "{0},{1}".format(j, i)] += str(
            gpg.decrypt(
                    data, passphrase=crypt_key))

#Function to encrypt database with provided master password
def encrypt(master_pass, filepath, gpg):
    #Check passed file paths and adjust as needed
    if filepath[-4:] == ".gpg.":
        filepath = filepath[0:-4]

    #Generate path for new file
    savefile = filepath + ".gpg"

    #Open file & encrypt
    file = open(filepath, "rb")        
    encrypted_data = gpg.encrypt_file(
            file, None, passphrase=master_pass,\
            symmetric=cipher.upper(),\
            output=savefile, armor=False)
    file.close()

    #Delete master password from memory
    del master_pass

    #Check encryption was successful
    if encrypted_data.ok != True:
        return 1
    
    else:
        return 0

#Function to return list of table headings
def get_tables(db):
    #create cursor to issue commands to database
    c = db.cursor()
    
    #Extract info on what tables are stored
    tables = c.execute(
            "SELECT name FROM SQLITE_MASTER WHERE type='table';")
    
    #create list, loop over returned data and append to list for use
    tables_list = []
    for row in tables:
        #Skip over "sqlite_sequence" and "keyfile_pass"
        if row[0] != 'sqlite_sequence' and row[0] != "keyfile_pass":
            tables_list.append(row[0]) 
    
    #Commit changes so we can use another cursor elsewhere
    db.commit()
    
    #Delete data from used variables
    del tables
    del c
    
    #Sort resulting list in alphabetical order, ignoring case
    tables_list.sort(
            key=str.casefold)
    
    #return resulting list
    return tables_list


def check_selection_input(selection_window):
    #Error checks to make sure required paths were given, and refers to actual file
    if selection_window.db_path.get().strip() == "":
        Error_Message(
                "Please select database")
        return 1
    
    elif selection_window.db_path.get().strip()[-7:] != ".db.gpg":
        Error_Message(
                "Selected database does not appear to be valid\nPlease check and try again")
        return 1
        
    elif selection_window.keyfile_path.get().strip() == "":
        Error_Message(
                "Please select keyfile")
        return 1
        
    elif selection_window.keyfile_path.get().strip()[-8:] != ".txt.gpg":
        Error_Message(
                "Selected keyfile does not appear to be valid\nPlease check and try again")    
        return 1
        
    elif not os.path.isfile(selection_window.db_path.get()):
        Error_Message(
                "Specified database does not exist!")
        return 1

    elif not os.path.isfile(selection_window.keyfile_path.get()):
        Error_Message(
                "Specified keyfile does not exist!")
        return 1
    
    elif selection_window.enter_pass.get().strip() == "":
        Error_Message(
                "Please enter password")
        return 1
    else:
        return 0


#Function to delete files & overwrite any decrypted files
def shred(filepath):
    if filepath[-4:] != ".gpg" and platform.system() == "Linux":
        os.system(
                "shred '" + filepath + "'")
        
    os.unlink(filepath)

#Popup message if main window is closed by user
def close_warning(root, main_window, gpg):
    def cancel():
        close_warning.__del__()
    def ok(main_window, gpg):
        #Call lock function in case a database is currently open
        try:
            main_window.display.lock(gpg)
        except:
            pass
        root.destroy()
    #Create confirmation popup on root window close
    close_warning = Confirmation_Message(
            root, "Are you sure?", "Ok", "Cancel",\
            "Are you sure?\n Closing this window with"\
            +" DB open\n could result in data loss.")
    
    close_warning.popup_ok.config(
            command=lambda: ok(main_window, gpg))
    
    close_warning.popup_cancel.config(
            command=cancel)
    
    close_warning.popup.protocol(
            "WM_DELETE_WINDOW", cancel)

#Function to decrypt an encrypted db file and pass the path to the new file along to the display window
def unlock(gpg, selection_window):
    
    #If checks passed successfully proceed and connect to database
    if check_selection_input(selection_window) == 0:
        #Read in path to database file
        dbPath = selection_window.db_path.get()
        
        #Decrypt database file
        if decrypt(
                selection_window.enter_pass.get(), dbPath, gpg) == 0:
            
            #Connect to database
            db = sqlite3.connect(
                    dbPath[0:-4])
            c = db.cursor()
            
            try:
                #Extract keyfile password from DB
                extracted_key = get_keypass(c, selection_window.enter_pass.get(), gpg)
                
                #Read in location of keyfile
                keyfile = selection_window.keyfile_path.get()
                
                #Attempt to extract crypt_key from keyfile
                crypt_key = extract_crypt_pass(extracted_key, keyfile, gpg, dbPath)
                
                #Read master_pass into memory, encrypt while reading
                master_pass = gpg.encrypt(
                    selection_window.enter_pass.get(), recipients=None, passphrase=crypt_key,\
                    symmetric=cipher.upper(), armor=True)
                
                #If successful delete stored keyfile password and open display window
                if crypt_key != None:
                    
                    #Delete variable storing password to keyfile
                    del extracted_key
                    
                    #Create new instance of display_db class and pass through connection to it's window method
                    selection_window.display = Display_DB(
                        db, master_pass, crypt_key, selection_window.db_path.get()[0:-4], gpg, selection_window)
            except:
                #If we failed to unlock successfully re-encrypt db with
                #master pass so it's not stuck open
                encrypt(
                        selection_window.enter_pass.get(), dbPath, gpg)
                Error_Message(
                        "Failed to extract keyfile\ndatabase may be corrupted!")
            
        else:
            Error_Message(
                    "Failed to decrypt database")



def get_column_headings(db, table_name, return_data):
    #Extract column headings for table & store in variable
    try:
        c = db.cursor()
        column_headings = c.execute(
                "PRAGMA table_info('{}');".format(
                        table_name))
     
    #If we cannot communicate with database inform user and lock for safety
    except:
        return None
        
    #move returned column data into a list to work with 
    columns = []
    for row in column_headings:
        columns.append(row)
    
    #Declare new list to store column headings
    column_headings = []
    
    #Loop over returned columns data and store column headings in a list
    for i in range(len(columns)):
        column_headings.append(
                columns[i][1])
    db.commit()
    
    #If requested return column headings and list containing column styles
    if return_data == 1:
        return columns, column_headings
    #If not requested to return data just return column headings
    else:
        return column_headings


def get_keypass(c, master_pass, gpg):
    keypass = c.execute(
            "SELECT pass FROM 'keyfile_pass' WHERE id = 1;")
  
    #Append returned tuple to list
    extracted_key = []                
    for row in keypass:
        extracted_key.append(row)
    #change variable to point at password string in returned tuple
    #and decrypt keyfile pass with master pass from entry widget
    extracted_key = str(
            gpg.decrypt(extracted_key[0][0],\
                        passphrase=master_pass))
    
    #Delete variable that held extracted password & decrypted master password
    del keypass
    del master_pass
    return extracted_key


def extract_crypt_pass(extracted_key, keyfile, gpg, dbPath):
    #Extract key from file using password extracted from DB
    #Safety check to ensure keyfile decrypted successfully
    if decrypt(
            extracted_key, keyfile, gpg) == 0:
        with open(
                keyfile[0:-4], "r") as file:
            
            crypt_key = file.read()

        #re-encrypt keyfile
        if encrypt(
                extracted_key, keyfile[0:-4], gpg) == 0:
            
            #shred encrypted copy of database file and decrypted keyfile
            shred(dbPath)                       
            shred(keyfile[0:-4])
            return crypt_key
            

        else:
            Error_Message(
                    "Failed to re-encrypt keyfile,\nplease regenerate keyfile before closing")
            return crypt_key
    
    else:
        #If we failed to decrypt keyfile shred decrypted copy of database
        shred(dbPath[0:-4])
        Error_Message(
                "Failed to decrypt keyfile")
        return None




def create_tables(c, db_style):
    #Create starting tables depending on which option was chosen
    c.execute(
            "CREATE TABLE IF NOT EXISTS 'keyfile_pass'"\
            +"('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"\
            +"'pass' TEXT NOT NULL);")
    c.execute(
            "CREATE TABLE IF NOT EXISTS 'Logins' "\
            +"('id' INTEGER PRIMARY KEY NOT NULL, "\
            +"'Title' TEXT NOT NULL, 'Username' TEXT NOT NULL,"\
            +"'Password' TEXT NOT NULL, 'Url' TEXT NOT NULL,"\
            +"'Security question' TEXT NOT NULL, "\
            +"'Security answer' TEXT NOT NULL);")
    c.execute(
            "CREATE TABLE IF NOT EXISTS 'Files' "\
            +"('id' INTEGER PRIMARY KEY NOT NULL, "\
            +"'Title' TEXT NOT NULL, 'File' BLOB NOT NULL, "\
            +"'Filename' TEXT NOT NULL, 'Comments' TEXT NOT NULL);")
    c.execute(
            "CREATE TABLE IF NOT EXISTS 'Secure Notes' "\
            +"('id' INTEGER PRIMARY KEY NOT NULL, "\
            +"'Title' TEXT NOT NULL, 'Note' TEXT NOT NULL);")
    c.execute(
            "CREATE TABLE IF NOT EXISTS 'Credit Cards' "\
            +"('id' INTEGER PRIMARY KEY NOT NULL, "\
            +"'Title' TEXT NOT NULL, 'Cardholder name' "\
            +"TEXT NOT NULL, 'Card type' TEXT NOT NULL, "\
            +"'Card number' TEXT NOT NULL, 'CVV number' "\
            +"TEXT NOT NULL, 'Expiry date' TEXT NOT NULL,"\
            +"'Valid from' TEXT NOT NULL, 'Notes' TEXT NOT NULL);")
    if db_style == 2:
        c.execute(
                "CREATE TABLE IF NOT EXISTS 'Work Logins' "\
                +"('id' INTEGER PRIMARY KEY NOT NULL, "\
                +"'Title' TEXT NOT NULL, 'Username' "\
                +"TEXT NOT NULL, 'Password' TEXT NOT NULL, "\
                +"'Url' TEXT NOT NULL, 'Security question' "\
                +"TEXT NOT NULL, 'Security answer' TEXT NOT NULL);")
        c.execute(
                "CREATE TABLE IF NOT EXISTS 'Identity' "\
                +"('id' INTEGER PRIMARY KEY NOT NULL, "\
                +"'First Name' TEXT NOT NULL, 'Last Name' "\
                +"TEXT NOT NULL, 'Initial' TEXT NOT NULL, "\
                +"'Sex' TEXT NOT NULL, 'DOB' TEXT NOT NULL, "\
                +"'Occupation' TEXT NOT NULL, 'Address Line1' "\
                +"TEXT NOT NULL, 'Address Line2' TEXT NOT NULL, "\
                +"'Postcode' TEXT NOT NULL);")
        c.execute(
                "CREATE TABLE IF NOT EXISTS 'Licences' "\
                +"(id INTEGER PRIMARY KEY NOT NULL, "\
                +"'Full Name' TEXT NOT NULL, 'Sex' "\
                +"TEXT NOT NULL, 'Height' TEXT NOT NULL, "\
                +"'Licence Class' TEXT NOT NULL, 'Restrictions' "\
                +"TEXT NOT NULL, 'Expiry Date' TEXT NOT NULL, "\
                +"'Country' TEXT NOT NULL, 'State' TEXT NOT NULL);")
        c.execute(
                "CREATE TABLE IF NOT EXISTS 'Bank Account' "\
                +"(id INTEGER PRIMARY KEY NOT NULL, "\
                +"'Bank Name' TEXT NOT NULL, 'Account Name' "\
                +"TEXT NOT NULL, 'Type' TEXT NOT NULL, "\
                +"'Account Number' TEXT NOT NULL, "\
                +"'Sort Code' TEXT NOT NULL, 'PIN' "\
                +"TEXT NOT NULL, 'Address Line1' TEXT NOT NULL, "\
                +"'Address Line2' TEXT NOT NULL, "\
                +"'Branch Phone' TEXT NOT NULL);")
        c.execute(
                "CREATE TABLE IF NOT EXISTS 'Passport' "\
                +"(id INTEGER PRIMARY KEY NOT NULL, 'Type' "\
                +"TEXT NOT NULL, 'Authority' TEXT NOT NULL, "\
                +"'Number' TEXT NOT NULL, 'Full Name' "\
                +"TEXT NOT NULL, 'DOB' TEXT NOT NULL, "\
                +"'Sex' TEXT NOT NULL, 'Nationality' "\
                +"TEXT NOT NULL, 'Place of Birth' "\
                +"TEXT NOT NULL, 'Issued on' TEXT NOT NULL, "\
                +"'Expiry Date' TEXT NOT NULL);")



def check_forbidden_characters(title):
    #Safety check to prevent problematic characters in column name
        if "'" in title\
        or '"' in title\
        or "-" in title:
            Error_Message(
                    """The following characters\n"""\
                    + """are not permitted in table or column names\n" ' - """)
            return 1
        else:
            return 0




#Function to update "show=" status of main window password box
def update_pass_box(enter_pass, show_opt):
    enter_pass.config(
            show=show_opt.get())

def main():    
    #Detect gpg configuration of different systems
    if os.path.isdir(
            os.path.expanduser("~") + "/.gnupg"):
        gpg_home = os.path.expanduser("~") + "/.gnupg"
        gpg = gnupg.GPG(
                gnupghome=gpg_home)
    else:
        gpg = gnupg.GPG()

    #Define root window
    root = tkinter.Tk()
        
    #Configure first window
    root.title("Castle")
    root.geometry("815x400")
    root.resizable(0, 0)
    root.config(bg="white")

    #Call instance of class to populate root window    
    main_window = Selection_Window(root, gpg)

    #Event handler to lock database file if window closed manually 
    root.protocol(
            "WM_DELETE_WINDOW", lambda:
                close_warning(root, main_window, gpg))


    #Root window mainloop()
    root.mainloop()
    


if __name__ == "__main__":
    #Cipher to use for encryption
    cipher="AES256"
    
    main()