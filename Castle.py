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
from tkinter.scrolledtext import ScrolledText
import xerox
import string
import random
import platform
import gc
import logging
from logging.handlers import RotatingFileHandler
import time


        
#class containing window and functionality to add column to currently displayed table
class Add_Column:
 
    def __init__(self, table_view):
        
        #Save needed items into instance atributes to reference later
        self.table_view = table_view
        self.db = table_view.db
        self.table_name = table_view.table_name
        
        #Define add column window
        self.column_window = tkinter.Toplevel()
        #Compensate for rendering differences in windows
        if platform.system() == "Windows":
            self.column_window.geometry("350x150")
        else:
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
                self.column_window, text=\
                "Please enter the name for your new column",\
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
            
            #Check a name for the new column was given
            if self.column_name.get() == "":
                Error_Message(
                        "Please enter a column name or click 'Cancel'")
            
            #Check name doesn't conflict with an existing column
            elif self.column_name.get() in self.column_headings:
                Error_Message(
                        "Column names must be unique!")
            
            else:
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

                        
        
    def add_column(self, column_name):
        #generate command based on current table and given input
        self.sql = "ALTER TABLE '{0}' ADD {1} VARCHAR DEFAULT '';".format(
                self.table_name, ("'" + self.column_name.get() + "'"))
        
        #Attempt to issue command to database, return exit value
        return issue_command(self.db, self.sql, None)
            
        
    
    def __del__(self):
        try:
            del self.sql
            for i in self.column_headings:
                del i
            del self.column_headings
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
        #Compensate for rendering differences in windows
        if platform.system() == "Windows":
            self.table_window.geometry("350x600")
        else:
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
                    #Issue command to database and check for success
                    if issue_command(self.db, self.fields_command, None) == 0:
                        
                        # If successful close window and regenerate sidebar controls
                        self.cancel()

                    else:
                        #If column names conflict sqlite will return an exception
                        Error_Message("Column names must be unique\nPlease check and try again")
        
    def __del__(self):
        try:
            del self.table_style
        except:
            pass
        try:
            del self.title
            del self.fields_command
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
                                + "' (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "\
                                +"Title TEXT, Username TEXT,"\
                                +"Password TEXT, Url TEXT,"\
                                +"'Security question' TEXT, "\
                                +"'Security answer' TEXT);"
        
        #If table style is file
        elif table_style == 2:
            fields_command = "CREATE TABLE IF NOT EXISTS '" + self.title + \
                                  "' (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "\
                                  +"Title TEXT, File BLOB,"\
                                  +"Filename TEXT, Comments TEXT);"
            
        #If table style is secure note
        elif table_style == 3:
            fields_command = "CREATE TABLE IF NOT EXISTS '" + self.title +\
                                  "' (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "\
                                  +"Title TEXT, Note TEXT);"
        
        #If table style is credit card
        elif table_style == 4:
            fields_command = "CREATE TABLE IF NOT EXISTS '" + self.title +\
                                 "' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "\
                                 +"'Title' TEXT, 'Cardholder name'"\
                                 +"TEXT, 'Card type' TEXT,"\
                                 +"'Card number' TEXT, 'CVV number' "\
                                 +"TEXT, 'Expiry date' TEXT,"\
                                 +"'Valid from' TEXT, 'Notes' TEXT);"
        
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
        #Compensate for rendering differences in windows
        if platform.system() == "Windows":
            self.popup.geometry("340x150")
        else:
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
        
        #Compensate for rendering differences in windows
        if platform.system() == "Windows":
            #Define warning message
            self.popup_label = tkinter.Label(
                    self.popup_frame, text=label_text,wraplength=300,\
                    bg="white", fg="#004aff", font=(
                    "Sans-serif", 12, "bold"))
        
        else:
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
    



class Control_Panel:
    
    def __init__(self, display_window, display):
        self.display = display
        self.table_style = display.table_style
        self.db = display.db
        
         #define frames used for bottom control panel
        self.bottom_bar = tkinter.Frame(
                display_window, width=500,\
                height=200, bg="white")
        
        self.bottom_bar.grid(
                row=1, column=1)
        
        
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
        
        #Generate controls based on table style         
        self.generate_standard_controls()
        if self.table_style == 3:
            self.generate_secure_note_controls()
        elif self.table_style == 4:
            self.generate_credit_card_controls()
        elif self.table_style == 1:
            self.generate_pass_table_controls()



    def generate_pass_table_controls(self):
                   
        #Function to copy selected entry's password
        def copy_password():
            try: 
                xerox.copy(
                        str(self.display.gpg.decrypt(
                                self.display.table_data[
                                        self.display.entry_ref.get()][
                                                self.display.password_ref],\
                                        passphrase=self.display.sidebar.parent.crypt_key)).strip(),\
                                xsel=True)
            except Exception as e:
                logger.exception(e)
            
            
        #function to listen for change in show password checkboxes
        def show_password():
            self.display.password_entries[
                    self.display.entry_ref.get()].config(
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
                        str(self.display.gpg.decrypt(
                                self.display.table_data[
                                        self.display.entry_ref.get()][
                                                self.display.card_num_ref],\
                                        passphrase=self.display.sidebar.parent.crypt_key)).strip(),\
                                xsel=True)
            except Exception as e:
                logger.exception(e)
        def cvv():
            try:
                xerox.copy(
                        str(self.display.gpg.decrypt(
                                self.display.table_data[
                                        self.display.entry_ref.get()][
                                                self.display.cvv_ref],\
                                        passphrase=self.display.sidebar.parent.crypt_key)).strip(),\
                                xsel=True)
            except Exception as e:
                logger.exception(e)

        #Functions to listen for changes in show card/cvv boxes
        def show_card():
            self.display.card_entries[
                    self.display.entry_ref.get()].config(
                    show=self.show_card_var.get())

        
        def show_cvv():
            self.display.cvv_entries[
                    self.display.entry_ref.get()].config(
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
                        str(self.display.gpg.decrypt(
                                self.display.table_data[
                                        self.display.entry_ref.get()][
                                                self.display.note_ref],\
                                        passphrase=self.display.sidebar.parent.crypt_key)).strip(),\
                                xsel=True)
            except Exception as e:
                logger.exception(e)

        
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
                            self.display.column_headings, None, \
                            None, self.display, self.display.table_style),\
                            anchor="n", fg="white", bg="#187bcd",\
                            activeforeground="white",\
                            activebackground="#4e97fe", width=12)
                            
        self.add_button.grid(
                row=0, column=0)

        #Define add column button
        self.add_column_button = tkinter.Button(
                self.table_buttons, text="New column", command=lambda: Add_Column\
                                                (self.display),\
                                                anchor="n", fg="white",\
                                                bg="#187bcd", activeforeground="white",\
                                                activebackground="#4e97fe", width=12)
        
        self.add_column_button.grid(
                row=0, column=1)
        
        #Define delete column button
        self.delete_column_button = tkinter.Button(
                self.table_buttons, text="Delete column", command=lambda :
                    Delete_Column(
                            self.display.column_headings, self.display.sidebar,\
                            self.display.table_style),anchor="n",fg="white",\
                            bg="#187bcd", activeforeground="white",\
                            activebackground="#4e97fe", width=12)
        
        self.delete_column_button.grid(
                row=0, column=2)
         
        #Refresh display
        self.refresh_button = tkinter.Button(
                self.table_buttons, text="Refresh", command=lambda:
                    self.display.refresh(),\
                            anchor="n", fg="white",\
                            bg="#187bcd", activeforeground="white",\
                            activebackground="#4e97fe", width=12)
        
        self.refresh_button.grid(
                row=0, column=3)

        #Define delete entry button
        self.delete_button = tkinter.Button(
                self.entry_buttons, text="Delete entry", command=lambda:
                    self.delete_entry(self.display.entry_ref.get()),\
                            anchor="n", fg="white", bg="#187bcd",\
                            activeforeground="white",\
                            activebackground="#4e97fe", width=12)
        
        self.delete_button.grid(
                row=1, column=0)
        
        #Define edit entry button
        self.edit = tkinter.Button(
                self.entry_buttons, text="Edit entry", command=lambda:
                    self.edit_e(
                            self.display.sidebar),\
                            anchor="n", fg="white", bg="#187bcd",\
                            activeforeground="white",\
                            activebackground="#4e97fe", width=12)
        
        self.edit.grid(
                row=1, column=1)
            
        
    #Function to call edit entry window
    def edit_e(self, sidebar):
        #try block in case we are looking at an empty table
        try:
            Entry_Window(
                    self.display.column_headings, self.display.table_data[
                            self.display.entry_ref.get()],\
                            self.display.entry_ref.get(), self.display,\
                            self.display.table_style)
        except:
            Error_Message("No entries in this table to edit.")
            
            
          
    #Function to delete selected entry from current table once user has given confirmation
    def delete(self, table_name, id_ref):
        if issue_command(self.db,\
                    "DELETE FROM '{0}' WHERE id = {1};".format(
                            table_name, id_ref), None) == 0:
            
            #Close popup and refresh display
            self.display.refresh()
            
            self.confirmation.__del__()
        else:
            
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
                            self.display.table_name, id_ref))
            
            self.confirmation.popup_cancel.config(
                    command=self.confirmation.__del__)

    def destroy(self):
        for widget in self.bottom_bar.winfo_children():
                widget.destroy()
        self.bottom_bar.destroy()



               
  


#Class containing create new db window and functionality
class Create_DB:
   
    def __init__(self, gpg, selection_window):
        #Save gpg into attribute for easy referencing
        self.gpg = gpg

        #Define window to get details for new db
        self.create_window = tkinter.Toplevel()
        self.create_window.title("Castle: Create Database")
        
        #Compensate for rendering differences in windows
        if platform.system() == "Windows":
            self.create_window.geometry("740x350")
        else:
            self.create_window.geometry("850x350")
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

                    #Try to create new database file
                    self.conn = sqlite3.connect(self.db_file_path)
                
                    #Generate starting tables from user selection
                    create_tables(self.conn, self.db_style.get())

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
                    issue_command(self.conn,\
                            "INSERT INTO keyfile_pass (pass) VALUES(?)", [
                                    str(self.keyfile_pass)])
                    
                    #Generate keyfile for new database
                    self.keyfile_name = self.generate_keyfile()
                    
                    #If keyfile was generated successfully we can proceed
                    if self.keyfile_name != None:
                        
                        #Delete plaintext copy of keyfile
                        shred(self.keyfile_name)  

                        #Send relevant file paths to main window
                        self.send_to_main(selection_window)
                        
                        #Open display_DB window and close this window
                        selection_window.display = Display_DB(
                                self.conn, self.master_pass, self.crypt_pass,\
                                self.db_file_path, self.gpg, selection_window)
            
                        self.__del__()   
                    else:
                        #If encryption of keyfile failed warn user of failure and delete created database
                        Error_Message(
                                "Failed to encrypt keyfile")
                        shred(self.db_file_path)
            
                    
        except Exception as e:
            logger.exception(e)
            #If creation fails warn user and attempt to delete any created files
            Error_Message(
                    "Encountered an error in creation\nCheck permissions and try again")
            try:
                shred(self.db_file_path)
            except:
                pass
            try:
                shred(self.keyfile_name)
            except:
                pass
            try:
                shred(self.keyfile_name + ".gpg")
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
        if encrypt(
                str(self.gpg.decrypt(
                        str(self.keyfile_pass), passphrase=str(self.gpg.decrypt(
                                self.master_pass, passphrase=self.crypt_pass)))),\
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
        try:
            del self.db_style
            del self.enter_opt
            del self.confirm_opt
            del self.master_pass
            del self.folder
            del self.db_file_path
            del self.conn
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
                    "There is only one column left in this table.\n"\
                    +"Please delete the table if this is what you wish.")
            
        #if there are enough columns to proceed then continue and display window
        else:        
            #Define delete column window
            self.delete_window = tkinter.Toplevel()
            #Compensate for rendering differences in windows
            if platform.system() == "Windows":
                self.delete_window.geometry("173x500")
            else:
                self.delete_window.geometry("200x500")
            self.delete_window.config(bg="white")
            self.delete_window.resizable(0, 0)
            self.delete_window.title("Castle")
            
            #Event handler to detect window manually closed by user
            self.delete_window.protocol(
                    "WM_DELETE_WINDOW", self.__del__)
    
            #Create scrollable frame for window
            #Compensate for rendering differences in windows
            if platform.system() == "Windows":
                self.scroll_frame  = Scrollable_Frame(
                        self.delete_window, False, True, 150, 500, 0, 0, 1, 1)
            else:
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
            except Exception as e:
                logger.exception(e)
                try:
                    self.c.execute(
                            "DROP TABLE '" + self.temp_table_name + "';")
                except:
                    pass
                Error_Message("Error adjusting table, please try again.")


    def __del__(self):
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
        self.delete_window.destroy()
          

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
        #Compensate for rendering differences in windows
        if platform.system() == "Windows":
            self.delete_window.geometry("170x500")
        else:
            self.delete_window.geometry("200x500")
        self.delete_window.config(bg="white")
        self.delete_window.resizable(0, 0)
        self.delete_window.title("Castle")
        
        #Event handler to detect window manually closed by user
        self.delete_window.protocol(
                "WM_DELETE_WINDOW", lambda:self.cancel_delete()) 
        
        #Define scrollable frame for delete window
        #Compensate for rendering differences in windows
        if platform.system() == "Windows":
            self.scroll_frame = Scrollable_Frame(
                    self.delete_window, False, True, 150, 500, 1, 1, 1, 1)
        else:
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
                
        #issue drop command to database
        if  issue_command(self.db, self.sql, None) != 0:
            Error_Message("Encountered an error!")
        
        #If deleting currently viewed table clear the display
        try:    
            if self.sidebar.current_table == table_name:
                self.sidebar.table_view.clear_view()
        except Exception as e:
            logger.exception(e)
        
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
            del self.buttons
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
        #Set flag to indicate database is currently open
        self.locked = False
        
        #Save needed objects into attributes for easy referencing
        self.db_file_path = db_path
        self.parent = parent
        self.db = db
        self.gpg = gpg
        
        #Store crypt key in attribute so we can access it from elsewhere later
        self.crypt_key = crypt_key
        self.master_pass = master_pass
        
        #Define window to display open database file
        self.display_window = tkinter.Toplevel()
        self.display_window.title("Castle")
        self.display_window.geometry("1015x700")
        self.display_window.config(bg="white")
        self.display_window.resizable(0, 0)


        #Event handler to lock database file if window closed manually 
        self.display_window.protocol(
                "WM_DELETE_WINDOW", lambda:
                    self.lock())        
        
        #Generate sidebar controls
        self.panel = Sidebar(db, self, gpg)

   
    def lock(self):
        #Check database isn't already locked
        if self.locked == False:
            #Commit any changes to database that might be outstanding
            try:
                self.db.commit()
            except Exception as e:
                logger.exception(e)

            # Encrypt database file with master password
            if encrypt(
                    str(self.gpg.decrypt(
                            str(self.master_pass), passphrase=self.crypt_key)),\
                            self.db_file_path, self.gpg)== 0:
                        
                try:
                    #Close connection to database if possible
                    self.db.close()
                except Exception as e:
                    logger.exception(e)

                #Toggle locked flag
                self.locked = True
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
        self.display_window.destroy()
        
    
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
        self.file_uploaded = False
        
        
        #create dictionary and lists to store generated widgets
        self.entries = {}
        self.labels = []
        
     
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
                #Otherwise create standard widgets and insert decrypted values
                self.generate_standard_widgets(i)
                
            #Insert any passed data into generateds widgets
            if self.entry_data != None and self.entry_data[i] != None:
                #Skip decrypting file storage column
                if self.column_headings[i] != "File" or self.table_style != 2:
                    self.insert_data(i)
          
        #Define submit and cancel buttons for main edit entry window
        self.submit_button = tkinter.Button(
                self.button_frame, text="Submit", command=lambda:
                    self.submit(
                            column_headings),\
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
    
        
    def submit(self, column_headings):
        
        #Scan all entries for user input, build lists as we go
        self.fields, self.values, self.insert_columns = self.scan_for_input()
        
        #As long as user inputted at least one field generate command to insert
        #or update entry
        if self.fields != "" and self.values != []:
            self.sql = self.generate_command(self.fields)    
        
            #issue command and check for success
            if issue_command(self.db, self.sql, self.values) == 0:
                #Display success message to user
                self.display_success_message()
                
                #Regenerate current table display ond close window
                self.table_view.refresh()
                self.__del__()
            #If an error occured issuing command inform user and close
            #any remaining cursor
            else:
                #Display error message
                self.db.commit()
                Error_Message("Encountered an error!")
    
        
    def scan_for_input(self):
        #Declare lists and string to build sql
        fields = ""
        insert_columns = []
        values = []
        
        #Bool flag to check for user input
        user_input = False
        
        #loop over entries and check for input
        for i in range(len(self.column_headings)):
            #Skip ID column
            if self.column_headings[i].lower() == "id": 
                pass
            
            #if secure note table and note column heading call read note input function
            elif self.table_style == 3 and self.column_headings[i] == "Note":
                if self.entries["Note"].get("1.0", END) != "" or self.id_ref != None:
                    user_input = True
                    fields, values, insert_columns = self.read_note_input(
                            i, fields, values, insert_columns)
                    
                        
            #if filename column of file table
            elif self.column_headings[i] == "Filename" and self.table_style == 2:
                if self.entries["Filename"].get() != "":
                    
                    #if updating existing record read in data from entry
                    if self.id_ref != None:
                        user_input = True
                        fields, values, insert_columns = self.read_standard_input(
                                i, fields, values, insert_columns)
                    
                    #if adding new record check if file was supplied
                    else:
                       
                        #if file entry is blank return empty lists to halt processing
                        if self.entries["File"].get() == "":
                            Error_Message("Please select a file to store!")
                            return "", [], []
                
                        #if file entry not blank read data with standard function 
                        elif self.entries["File"].get() != "":
                            user_input = True
                            fields, values, insert_columns = self.read_standard_input(
                                    i, fields, values, insert_columns)
                            
                        
                    
            
            #if file column  of file table
            elif self.column_headings[i] == "File" and self.table_style == 2:
                if self.entries["File"].get() != "":
                    
                    ##if user has removed filename and we are creating a new entry
                    #present warning and halt processing
                    if self.entries["Filename"].get() == "" and self.id_ref == None:
                        Error_Message("Please enter a filename!")
                        return "", [], []
                    
                    #Toggle bool flag and read data from file
                    user_input = True
                    fields, values, insert_columns = self.read_file_input(
                            i, fields, values, insert_columns)
                    
                    #Check reading file was successful
                    if fields == "" and values == [] and insert_columns == []:
                        #If reading file failed return empty lists to halt processing
                        return "", [], []
                    
                    

                    
            #if any other column read in data
            else:
                #If adding new entry only read in filled entries, if editing entry read all
                if self.entries[self.column_headings[i]].get() != "" or self.id_ref != None:
                    user_input = True
                    fields, values, insert_columns = self.read_standard_input(
                            i, fields, values, insert_columns)
            
        #If no errors and there was input in at least one field return gathered data
        if user_input == True:
            return fields, values, insert_columns
        
        else:
            #If any errors encountered in collecting input
            #return empty lists to halt processing
            Error_Message(
                    "Encountered an error\nPlease check input and try again.")
            return "", [], []
         
            
            
    def read_note_input(self, i, fields, values, insert_columns):
        #Add this column's heading to fields command
        fields = fields +"'" + self.column_headings[i] + "'" + " = ?, "
        #Read in and encrypt value from relevant entry widget
        if self.entries[self.column_headings[i]].get("1.0", END) != "":
            values.append(
                str(self.gpg.encrypt(
                        self.entries["Note"].get("1.0", END),\
                        recipients=None,
                        passphrase=self.sidebar.parent.crypt_key,\
                        symmetric=cipher.upper(), armor=True)))
        #If entry is blank
        else:
            values.append(None)
        #Add ccolumn heading to list of columns to update
        insert_columns.append("Note")
        #Return collected data
        return fields, values, insert_columns
    
    
    
    
    def read_file_input(self, i, fields, values, insert_columns):
        #Encrypt and read in file data
        file_data = self.read_file(self.entries["File"].get())
        
        #If error encountered while reading file data return
        #empty lists to halt processing and inform user
        if file_data == None:
            Error_Message(
                    "Failed to store file!\nPlease try again")
            
            return "", [], []

        #Add file column to fields command
        fields = fields + "'File' = ?, "
        #Append encrypted file data to values
        values.append(file_data)
        #Add column heading to list of columns to update
        insert_columns.append("File")
        
        #Toggle flag to indicate file has been
        #updated and return gathered data
        self.file_uploaded = True
        return fields, values, insert_columns
        
        
        
        
    def read_standard_input(self, i, fields, values, insert_columns):
        #Add this column's heading to fields command
        fields = fields +"'" + self.column_headings[i] + "'" + " = ?, "
        #Read in and encrypt value from relevant entry widget
        if self.entries[self.column_headings[i]].get() != "":            
            values.append(
                str(self.gpg.encrypt(
                        self.entries[self.column_headings[i]].get(),\
                        recipients=None,\
                        passphrase=self.sidebar.parent.crypt_key,\
                        symmetric=cipher.upper(), armor=True)))
        #If entry is blank
        else:
            values.append(None)
        
        #Add ccolumn heading to list of columns to update
        insert_columns.append(self.column_headings[i])
        #Return collected data
        return fields, values, insert_columns
            
    
    
    
    def generate_command(self, fields):                   
            #Cut last comma and space off generated statement
            fields = fields[0:-2]
            
            #Check to see if we are updating an
            #existing record or adding a new one
            if self.id_ref == None:
                #if adding new record adjust formatting if only one value supplied
                if len(self.insert_columns) == 1:
                    sql = "INSERT INTO '{0}' ('{1}') VALUES (?);".format(
                            self.table_name, self.insert_columns[0]) 
                else:
                
                    sql = "INSERT INTO '{0}' {1} VALUES ({2});".format(
                            self.table_name, tuple(self.insert_columns), (
                                    ", ".join('?'*(len(self.insert_columns))))) 
            else:
                #If updating existing entry generate appropriate command
                sql = "UPDATE '{0}' SET {1} WHERE id = '{2}';".format(
                        self.table_name, fields, self.id_ref)
            return sql
    
            
    
                
        
    #Display appropriate success message to user
    #depending what type of transaction
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
            
            
            
    def read_file(self, filename):
        #Encrypt file for storage
        if encrypt(
                self.sidebar.parent.crypt_key,\
                filename, self.gpg) == 0:
            
            #generate filepath to encrypted file
            filepath = filename + ".gpg"
            
            #Read encrypted file into memory
            with open(filepath, "rb") as file:
                data = file.read()
            
            #Delete encrypted copy of file and delete generated filepath
            shred(filepath)
            del filepath
            
            #Set file uploaded flag to True
            self.file_uploaded = True
            return data
        #If error during encryption return None
        else:
            return None

    def insert_data(self, i):                        
            #Skip id column
            if self.column_headings[i].lower() == "id":
                pass
            else: 
                #decrypt and insert data for current widget, adjusting if text widget
                if self.column_headings[i].lower() != "note" and self.table_style != 3:
                    self.entries[self.column_headings[i]].insert(
                            0, str(self.gpg.decrypt(
                                    str(self.entry_data[i]),\
                                    passphrase=self.sidebar.parent.crypt_key)))
                else:
                    self.entries[self.column_headings[i]].insert(
                            END, str(self.gpg.decrypt(
                                    str(self.entry_data[i]),\
                                    passphrase=self.sidebar.parent.crypt_key)))



    def generate_standard_widgets(self, i):
        #If looking at note column of secure note table
        #create text widget and save column reference
        if self.column_headings[i].lower() == "note" and self.table_style == 3:    
            self.e = ScrolledText(
                    self.side_scroll.frame, width=40, height=5,\
                    bg="white", font=(
                            "Sans-serif", 10, "bold"))
            self.e.vbar.config(bg="#187bcd",\
                    activebackground="#4e97fe", troughcolor="white")
        
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
        
        self.entries[self.column_headings[i]] = self.e
        
        self.l = tkinter.Label(
                self.side_scroll.frame, text=self.column_headings[i],\
                bg="white", fg="#004aff", font=(
                "Sans-serif", 12, "bold"))
        
        self.l.grid(
                row=0, column=i, pady=5)
        
        self.labels.append(self.l)
        


    def generate_file_widgets(self, i):
        
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
                    browse(1, self.entries["File"],\
                           "Select a file to store", ("all files", "*.*"),\
                           self.entry_window, self.entries["Filename"]),\
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

        #Save this widget into dictionary to reference while building input
        self.entries[self.column_headings[i]] = self.file_entry
   


    def __del__(self):

        try:
            del self.entries
            del self.side_scroll
        except:
            pass
        try:
            del self.note_ref
            del self.title_ref
            del self.filename_ref
        except:
            pass        
        try:
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
        for widget in self.warning.winfo_children():
                widget.destroy()
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
        
        #Compensate for rendering differences in windows
        if platform.system() == "Windows":
            self.generator_window.geometry("410x500")
        else:
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
        except Exception as e:
            logger.exception(e)
            
        
        
        
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
        except Exception as e:
            logger.exception(e)
            
            
    def __del__(self):

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
                passphrase=self.sidebar.parent.crypt_key))+ ".gpg"
        
        
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
                try:
                    with open(self.filepath, "wb") as file:
                        file.write(
                                entry_data[self.file_ref])
                except PermissionError:
                    Error_Message("Permission Denied!")
                
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

        #Compensate for rendering differences in windows
        if platform.system() == "Windows":
            #Create scrollable frame to use for sidepanel controls
            self.side_scroll = Scrollable_Frame(
                    parent.display_window, False, True, 168, 700, 0, 0, 2, 1)
            
        else:
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
                    bg="#187bcd", activeforeground="white",\
                    activebackground="#4e97fe")
        
        self.add_table_button.grid(
                row=1, column=0, pady=5)
        
        #Delete group button
        self.delete_group_button = tkinter.Button(
                self.control_bar, text="Delete table", command=lambda:
                    Delete_Table(self), width=10, fg="white", bg="#187bcd",\
                    activeforeground="white",\
                    activebackground="#4e97fe")
        
        self.delete_group_button.grid(
                row=2, column=0, pady=5)
        
        #Password generator button
        self.password_generator_button = tkinter.Button(
                self.control_bar, text="Password\nGenerator", command=lambda:
                    Password_Generator(), width=10, fg="white", bg="#187bcd",\
                    activeforeground="white",\
                    activebackground="#4e97fe")
        
        self.password_generator_button.grid(
                row=3, column=0, pady=5)
        
        #Define update password button
        self.update_pass_button = tkinter.Button(
                self.control_bar, text="Change\nMaster Pass", command=lambda:
                    Update_Password(self), width=10, fg="white",\
                    bg="#187bcd", activeforeground="white",\
                    activebackground="#4e97fe")
        
        self.update_pass_button.grid(
                row=4, column=0, pady=5)
        
        #Define lock button
        self.lock_button = tkinter.Button(
                self.control_bar, text="Lock", command=lambda:
                    self.parent.lock(), width=10, fg="white",\
                    bg="#187bcd", activeforeground="white",\
                    activebackground="#4e97fe")
        
        self.lock_button.grid(
                row=5, column=0, pady=5)
        
        
        #Define lists to store controls and functions
        self.table_controls = {}
        self.window_functions = []
        
        #Generate buttons and functions for each table
        self.generate_table_buttons()
        
        
        
    def generate_function(self):
        #Define function to handle this table's button
        def f(db, table, x, gpg):
            #Store currently viewed table for refreshing elsewhere
            self.current_table = table    
            
            #If table_view hasnt been created yet
            if self.table_view == None:
                #create new table view
                self.table_view = Table_Display(
                        table, self)
                
            #if table_view already exists point display at 
            #selected table and refresh display
            else:
                self.table_view.table_name = table
                self.table_view.refresh()
                
            #Update button colours to indicate currently
            #viewed table
            self.update_button_colours()
            
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
            self.table_controls[self.tables_list[i]] = self.table_button
        
        
        
    def update_button_colours(self):
        #Loop over current buttons and update colours to indicate currently viewed table
        for key in self.table_controls:
            if key == self.current_table:
                #invert colours
                self.table_controls[key].config(bg="white", fg="#187bcd",\
                                activebackground="white",\
                                activeforeground="#4e97fe")
            else:
                #standard colours
                self.table_controls[key].config(fg="white", bg="#187bcd",\
                                activeforeground="white",\
                                activebackground="#4e97fe")
        
        
        
        
    #Function to destroy sidebar controls so we can create new ones 
    def clear_buttons(self):
        del self.tables_list
        for key in self.table_controls:
            self.table_controls[key].destroy()
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

       
        #If any unhandled errors encountered during display generation lock database for safety
        try:
            self.generate_display()
        except Exception as e:
            logger.error("Fatal error - database locked for safety!")
            logger.exception(e)
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
        
        
        #Query database for table headings, 
        self.columns, self.column_headings = get_column_headings(self.db, self.table_name, 1)

        #if unsuccessful lock database for safety
        if self.column_headings == None or self.column_headings == None:
            Error_Message(
                    "Encountered a fatal error!\nLocking database")
            self.sidebar.parent.lock()

        else:                      
            #Extract data from table & check for success
            self.table_data, self.id_refs = self.get_table_data(self.db)
            
            #If unsuccessful lock database for safety
            if self.table_data == None or self.id_refs == None:
                Error_Message(
                        "Encountered a fatal error!\nLocking database")        
                self.sidebar.parent.lock()
            else:
                #Detect table style    
                self.table_style = self.detect_table_style()
        
                #Generate control panel
                self.control_panel = Control_Panel(self.sidebar.parent.display_window, self)
                
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
                self.delete_decrypted()


    def get_table_data(self, db):
        #Define lists to store extracted data and db entry ids
        table_data = {}
        id_refs = [] 
        
        try:
            #Create cursor to issue commands to the database
            c = db.cursor()
            
            #Issue command to extract all data for current table
            self.data = c.execute(
                    "SELECT * FROM '{}';".format(self.table_name))
            
            #Commit changes so we can open another cursor elsewhere
            db.commit()
            
        #If we cannot communicate with database inform user and lock for safety
        except Exception as e:
            logger.exception(e)
            return None, None
        
        #loop over returned data append each row and it's id to appropriate list
        for row in self.data:
            table_data[row[0]] = row
            id_refs.append(row[0])
            
        #Return extracted data
        return table_data, id_refs



    def delete_decrypted(self):
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
                    #Provided there is something to decrypt for this entry
                    if self.table_data[key][i] != None and self.table_data[key][i] != "":
            
                        try:
                            #Spawn process for this entry and add to list
                            p = Process(
                                    target=decrypt_item, args=(
                                            bytes(self.table_data[key][i], "utf-8"),\
                                            i, key, self.grid_values,\
                                            self.sidebar.parent.crypt_key, self.gpg))
                            p.start()
                            procs.append(p)
                        except:
                            try:
                                #Adjust process command for text entries
                                p = Process(
                                        target=decrypt_item, args=(
                                                bytes(self.table_data[key][i]),\
                                                i, key, self.grid_values,\
                                                self.sidebar.parent.crypt_key, self.gpg))
                                p.start()
                                procs.append(p)
                            except Exception as e:
                                logger.exception(e)
                                
            
        #Call garbage collector to avoid it being triggered by spawned thread.            
        gc.collect()
        
        #Wait for all processes to complete before proceding
        for proc in procs:
            proc.join()
    
    #Generate widgets for password column
    def generate_pass_table(self, j):
        e = tkinter.Entry(
                self.frame.frame, width=18, show="*",\
                bg="white", font=(
                        "Sans-serif", 10, "bold"),\
                        highlightbackground="#187bcd",\
                        highlightcolor="#187bcd")
                        
        self.password_entries[self.table_data[j][0]] = e
        return e
    
    #Generate widgets for credit card columns
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
    
    #Generate widgets for secure note column
    def generate_note_table(self):
        e = ScrolledText(
            self.frame.frame, height=10, width=40,\
            bg="white", font=(
                    "Sans-serif", 10, "bold"),\
                    highlightbackground="#187bcd",\
                    highlightcolor="#187bcd")
        e.vbar.config(bg="#187bcd",\
                    activebackground="#4e97fe", troughcolor="white")
        return e
    
    #Generate widgets for file column
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
                    
                    #if looking at a password column use starred out entry instead
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
                    #Define default layout for all other columns
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
        
        #If any BLOB columns it's a file table
        if self.file_table == True:
            table_style = 2
        
        #If columns for card number and CVV number it's a credit card table
        elif self.card_num_ref != None and self.cvv_ref != None: 
            table_style = 4
        
        #If columns for username and password it's a login table
        elif self.username_ref != None and self.password_ref != None:
            table_style = 1
        
        #If there's a note column and no other expected columns it's a secure note table
        elif self.note_ref != None and self.cvv_ref == None and\
                    self.file_table == False and\
                    self.username_ref == None and self.password_ref == None:
            table_style = 3
        
        #Otherwise treat as a custom table and use defaults
        else:
            table_style = 5
        return table_style
            


            

    #Function to return password/card entry to show="*" state if new entry selected
    def hide_entry(self):
        try:
            self.card_entries[
                    self.entry_check.get()].config(show="*")
            
            self.cvv_entries[
                    self.entry_check.get()].config(show="*")
            
            self.control_panel.show_card.deselect()
            
            self.control_panel.show_cvv.deselect()
        except:
            pass
        try:
            self.password_entries[
                    self.entry_check.get()].config(show="*")
            
            self.control_panel.show.deselect()
        except:
            pass
        self.entry_check.set(
                self.entry_ref.get())
        
        
   

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
            self.control_panel.destroy()
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
        #Compensate for rendering differences in windows
        if platform.system() == "Windows":
            self.update_window.geometry("540x540")
        else:
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

    def check_password(self):
        #Check entered passwords match    
        if self.enter_password.get() != self.confirm_password.get():
            Error_Message(
                    "Entered passwords did not match!")
            return 1
        #Check at least one password was supplied
        elif self.enter_password.get().strip() == "":
            Error_Message(
                    "Please enter a new master password!")
            return 1
        return 0


    def check_keyfile_path(self):
        #Safety checks to ensure we have all the information to proceed
        if self.keyfile_path.get().strip() == "":
            Error_Message(
                    "Please select a location to create new keyfile")
            return ""
        
        elif self.keyfile_name.get().strip() == "":
            Error_Message(
                    "Please enter a name for your new keyfile")
            return ""
        
        #Generate full path to selected file
        keypath = os.path.join(
                self.keyfile_path.get(), self.keyfile_name.get()) + ".txt"
        
        #Check file exists
        if os.path.isfile(keypath + ".gpg"):
            Error_Message(
                    "Chosen file already exists!\nPlease change name or location")
            return ""
        
        #Check we have access to file
        try:
            file = open(keypath, "a")
            file.close()
        except PermissionError:
            Error_Message("Permission denied!")
            return ""
        
        #If all checks passed successfully return path to keyfile
        return keypath
        
        
        
        


    def password_only(self):
        #get current keyfile password
        extracted_key = get_keypass(
                self.db, str(
                        self.gpg.decrypt(
                                str(self.sidebar.parent.master_pass),\
                                passphrase=self.sidebar.parent.crypt_key))\
                        , self.gpg)

        #Encrypt keyfile_pass with new master_password
        updated_key = str(self.gpg.encrypt(
                extracted_key, recipients=None,\
                symmetric=cipher.upper(), armor=True,\
                passphrase=self.enter_password.get()))
        
        #Insert re-encrypted keyfile password into table
        if issue_command(self.db,\
                "UPDATE 'keyfile_pass' SET 'pass' = ? WHERE id = 1", (
                        updated_key,)) == 0:
            
            #If successful update master password held in memory
            self.sidebar.parent.master_pass = str(self.gpg.encrypt(
                    self.enter_password.get(), recipients=None,\
                    passphrase=self.sidebar.parent.crypt_key,\
                    symmetric=cipher.upper(), armor=True))
            return 0
        else:
            return 1



    def pass_and_keyfile(self):
        #Generate path for new file
        keypath = self.check_keyfile_path()
        #if any errors with keyfile location halt processing
        if keypath == "":
            return
        else:
            #If all checks passed successfully generate
            #characterset for new keyfile pass
            self.charset = "^*$%@#!&.=~+_-"\
            + string.ascii_letters + string.digits

            #Generate new random password to store
            keypass = "".join(random.SystemRandom().choice(self.charset)for i in range (256))
            
            ##create and encrypt new keyfile with keypass
            if self.update_keyfile(keypath, keypass) == 0:

                #encrypt keypass for storage in table
                keypass = str(self.gpg.encrypt(
                    keypass, recipients=None,\
                    passphrase=self.enter_password.get(),\
                    symmetric=cipher.upper(), armor=True))
                
                ##update keypass stored in table
                if issue_command(self.db,\
                        "UPDATE 'keyfile_pass' SET 'pass' = ? WHERE id = 1", (
                               keypass ,)) == 0:

                    #if all succsessful update master password held in memory
                    self.sidebar.parent.master_pass = str(self.gpg.encrypt(
                            self.enter_password.get(), recipients=None,\
                            passphrase=self.sidebar.parent.crypt_key,\
                            symmetric=cipher.upper(), armor=True))
                    return 0
                
                #If updating keypass in database failed halt proceessing
                else:
                    return 1
            
            #If generating new keyfile failed attempt to delete created file
            #And halt processing
            else:
                try:
                    shred(keypath + ".gpg")
                except:
                    pass
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
        
        


    #Function to update master password with given inputs
    def update(self):
        
        #Check password was entered and passwords in both boxes match
        if self.check_password() == 1:
            #If no password or didnt match halt processing
            return
        
        #If all ok proceed and update password
        else:
            
            #If user is only updating password
            if self.update_select.get() == 0:
                
                #Attempt to update password and inform user of result and close window
                if self.password_only() == 0:
                    Error_Message("Password updated successfully")
                    self.__del__()
                    
                else:
                    Error_Message("Error updating password!")
            #If user is updating keyfile as well
            else:
                if self.pass_and_keyfile() == 0:
                    Error_Message("Password updated successfully")
                    self.__del__()
                    
                else:
                    Error_Message("Error updating password!")
                
    
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
            del self.update_select
            del self.pass_var
            del self.confirm_var
            self.update_window.destroy()
        except:
            pass

#Portable function to issue and commit commands to database
def issue_command(db, statement, values):
    #if passed a list of values issue statement and values
    if values != None:
        try:
            c = db.cursor()
            c.execute(statement, values)
            db.commit
            return 0
        except Exception as e:
            logger.exception(e)
            return 1
    #if only passed a statement issue the statement
    else:
        try:
            c = db.cursor()
            c.execute(statement)
            db.commit
            return 0
        except Exception as e:
            logger.exception(e)
            return 1  

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
    try:
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
            logger.error("Failed to decrypt file {}".format(filepath))
            return 1
        else:
            return 0
    except PermissionError:
        Error_Message("Permission denied!")
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
    try:
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
            logger.error("Failed to encrypt file {}".format(filepath))
            return 1
        
        else:
            return 0
    except PermissionError:
        Error_Message("Permission denied!")
        return 1

#Function to return list of table headings
def get_tables(db):
    try:
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
    except Exception as e:
        logger.error("Failet to retrieve table information!")
        logger.exception(e)


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
    try:
        if filepath[-4:] != ".gpg" and platform.system() == "Linux":
            os.system(
                    "shred '" + filepath + "'")
            
        os.unlink(filepath)
    except Exception as e:
        logger.error("Failed to delete file {}".format(filepath))
        logger.exception(e)

#Popup message if main window is closed by user
def close_warning(root, main_window, gpg):
    def cancel():
        close_warning.__del__()
        
    def ok(main_window, gpg):
        #Call lock function in case a database is currently open
        try:
            main_window.display.lock()
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
    
    #Star out password entry in selection window
    #And deselect "show password" checkbox
    selection_window.enter_pass.config(show="*")
    selection_window.show_pass.deselect()
    
    #If checks passed successfully proceed and connect to database
    if check_selection_input(selection_window) == 0:
        #Read in path to database file
        dbPath = selection_window.db_path.get()
        
        try:
            #Decrypt database file
            if decrypt(
                    selection_window.enter_pass.get(), dbPath, gpg) != 0:
                Error_Message(
                        "Failed to decrypt database")
            else:
                #Connect to database
                db = sqlite3.connect(
                        dbPath[0:-4])
                
                try:
                    #Extract keyfile password from DB
                    extracted_key = get_keypass(db, selection_window.enter_pass.get(), gpg)
                    
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
                except Exception as e:
                    logger.error("Failed to unlock database")
                    logger.exception(e)
                    #If we failed to unlock successfully re-encrypt db with
                    #master pass so it's not stuck open
                    encrypt(
                            selection_window.enter_pass.get(), dbPath, gpg)
                    Error_Message(
                            "Failed to extract keyfile\ndatabase may be corrupted!")
                
    
        except PermissionError:
            Error_Message("Permission denied!")
    

def get_column_headings(db, table_name, return_data):
    #Extract column headings for table & store in variable
    try:
        c = db.cursor()
        column_headings = c.execute(
                "PRAGMA table_info('{}');".format(
                        table_name))
     
    #If we cannot communicate with database inform user and lock for safety
    except Exception as e:
        logger.exception(e)
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


def get_keypass(db, master_pass, gpg):
    try:    
        #Create cursor and issue command to database
        c = db.cursor()
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
        #Close cursor
        db.commit()
        #Delete variable that held extracted password & decrypted master password
        del keypass
        del master_pass
        return extracted_key
    except Exception as e:
        logger.error("Failed to extract keypass!")
        logger.exception(e)

def extract_crypt_pass(extracted_key, keyfile, gpg, dbPath):
    #Extract key from file using password extracted from DB
    #Safety check to ensure keyfile decrypted successfully
    try:
        if decrypt(
                extracted_key, keyfile, gpg) != 0:
            #If failed to decrypt keyfile shred decrypted copy of database
            shred(dbPath[0:-4])
            Error_Message(
                    "Failed to decrypt keyfile")
            logger.error("Failed to decrypt keyfile")
            return None
        
        #If decryption was successful read key from file
        else:
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
                
            #If re-encryption of keyfile failed inform user
            else:
                Error_Message(
                        "Failed to re-encrypt keyfile,\nplease regenerate keyfile before closing")
                logger.error("Failed to re-encrypt keyfile!")
                return crypt_key
            
    except PermissionError:
        Error_Message("Permission Denied!")



def create_tables(db, db_style):
    try:
        #Create cursor to issue commands to database
        c = db.cursor()
        #Create starting tables depending on which option was chosen
        c.execute(
                "CREATE TABLE IF NOT EXISTS 'keyfile_pass'"\
                +"('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"\
                +"'pass' TEXT);")
        c.execute(
                "CREATE TABLE IF NOT EXISTS 'Logins' "\
                +"('id' INTEGER PRIMARY KEY NOT NULL, "\
                +"'Title' TEXT, 'Username' TEXT,"\
                +"'Password' TEXT, 'Url' TEXT,"\
                +"'Security question' TEXT, "\
                +"'Security answer' TEXT);")
        c.execute(
                "CREATE TABLE IF NOT EXISTS 'Files' "\
                +"('id' INTEGER PRIMARY KEY NOT NULL, "\
                +"'Title' TEXT, 'File' BLOB, "\
                +"'Filename' TEXT, 'Comments' TEXT);")
        c.execute(
                "CREATE TABLE IF NOT EXISTS 'Secure Notes' "\
                +"('id' INTEGER PRIMARY KEY NOT NULL, "\
                +"'Title' TEXT, 'Note' TEXT);")
        c.execute(
                "CREATE TABLE IF NOT EXISTS 'Credit Cards' "\
                +"('id' INTEGER PRIMARY KEY NOT NULL, "\
                +"'Title' TEXT, 'Cardholder name' "\
                +"TEXT, 'Card type' TEXT, "\
                +"'Card number' TEXT, 'CVV number' "\
                +"TEXT, 'Expiry date' TEXT,"\
                +"'Valid from' TEXT, 'Notes' TEXT);")
        if db_style == 2:
            c.execute(
                    "CREATE TABLE IF NOT EXISTS 'Work Logins' "\
                    +"('id' INTEGER PRIMARY KEY NOT NULL, "\
                    +"'Title' TEXT, 'Username' "\
                    +"TEXT, 'Password' TEXT, "\
                    +"'Url' TEXT, 'Security question' "\
                    +"TEXT, 'Security answer' TEXT);")
            c.execute(
                    "CREATE TABLE IF NOT EXISTS 'Identity' "\
                    +"('id' INTEGER PRIMARY KEY NOT NULL, "\
                    +"'First Name' TEXT, 'Last Name' "\
                    +"TEXT, 'Initial' TEXT, "\
                    +"'Sex' TEXT, 'DOB' TEXT, "\
                    +"'Occupation' TEXT, 'Address Line1' "\
                    +"TEXT, 'Address Line2' TEXT, "\
                    +"'Postcode' TEXT);")
            c.execute(
                    "CREATE TABLE IF NOT EXISTS 'Licences' "\
                    +"(id INTEGER PRIMARY KEY NOT NULL, "\
                    +"'Full Name' TEXT, 'Sex' "\
                    +"TEXT, 'Height' TEXT, "\
                    +"'Licence Class' TEXT, 'Restrictions' "\
                    +"TEXT, 'Expiry Date' TEXT, "\
                    +"'Country' TEXT, 'State' TEXT);")
            c.execute(
                    "CREATE TABLE IF NOT EXISTS 'Bank Account' "\
                    +"(id INTEGER PRIMARY KEY NOT NULL, "\
                    +"'Bank Name' TEXT, 'Account Name' "\
                    +"TEXT, 'Type' TEXT, "\
                    +"'Account Number' TEXT, "\
                    +"'Sort Code' TEXT, 'PIN' "\
                    +"TEXT, 'Address Line1' TEXT, "\
                    +"'Address Line2' TEXT, "\
                    +"'Branch Phone' TEXT);")
            c.execute(
                    "CREATE TABLE IF NOT EXISTS 'Passport' "\
                    +"(id INTEGER PRIMARY KEY NOT NULL, 'Type' "\
                    +"TEXT, 'Authority' TEXT, "\
                    +"'Number' TEXT, 'Full Name' "\
                    +"TEXT, 'DOB' TEXT, "\
                    +"'Sex' TEXT, 'Nationality' "\
                    +"TEXT, 'Place of Birth' "\
                    +"TEXT, 'Issued on' TEXT, "\
                    +"'Expiry Date' TEXT);")
            #Commit changes to database
            db.commit()
    except Exception as e:
        logger.error("Failed to create starting tables!")
        logger.exception(e)



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
    
    #Compensate for rendering differences in windows
    if platform.system() == "Windows":
        root.geometry("720x370")
    else:
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
    
    
    #Set and configure logger
    logger = logging.getLogger()
    

    
    handler = RotatingFileHandler(
            'Castle.log', maxBytes=200000, backupCount=10)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(asctime)s %(message)s')
    formatter.converter = time.gmtime
    handler.setFormatter(formatter)
    
    main()