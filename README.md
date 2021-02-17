<h1>Castle - A Python password manager</h1>

Castle is a simple password manager written entirely in python.



<h2>How it works</h2>

Castle makes use of sqlite3 databases to store your data and gpg symmetric encryption on both the files themcselves and all data stored within the database.

When a new database is created it also generates a "keyfile" - a text file containing a 256 character password required to decrypt any passwords etc stored in database tables.
This file is only opened to read the key into memory and then encrypted again.

The password to open this file is stored in a table of it's own in the database, which is hidden from the user interface, and cannot be retrieved without the master password.

The outcome is a "handshake" style operation needed in order to unlock the database fully. i.e. the master password is needed to unlock the overall database and retrieve the password to the keyfile.
The keyfile is then opened and if read successfully can then decrypt your stored data.

This creates an opportunity to treat this "keyfile" like a multifactor authentication token. the intention is for the keyfile to be stored separately from the database file (for example on a usb pen).

If for any reason you think your keyfile may have been compromised there is an option to generate a new keyfile when you change your master password.

Note this will not change the password stored in this file, but it will change the password this file is encrypted with so the original will no longer be usable with the program. This means any backups
you have made of the database or keyfile will no longer be useable with your main files.

The interface is a simple and intuitive dashboard style.

A password genarator is included with selectable charactersets to quickly generate strong passwords and copy them straight to your clipboard.

The program itself is capable of storing standard password style data, secure notes for longer messages and will also store files - all fully encrypted for peace of mind.


<h2>How to use</h2>

1. On first running the program you will see the login screen, with options to open an existing database or create a new one, click "Create" to start a new database"
This will generate 2 files. One is your database file, this stores all your information and should be backed up in case of data corruption or hardware failure.<br>
The second is a "keyfile", an encrypted text file that is required to open your database. This file should also be backed up but for best security should NOT be stored in the same place
as the database file. Remember, if someone ever gets your master password it would be useless to them unless they have both of these files.
<img src="images/selection_window.png"; alt="Home screen"; align="center"; width="750px"/>

2. You will now be asked to select where you want to create your new files, and to create a strong master password for your database.<br>
At this stage you can also select the database style you wish. Select "Basic" for a simpler database consisting of "Credit card", "Files", "Logins", and "Secure note" tables or 
"Full" for a more elaborate database structure. Keep in mind you can add or remove tables as you wish so there's no need to restrict yourself to these starting templates.<br>
Once you have everything set how you wish click "Create now".
<img src="images/creation_window.png"; alt="Home screen"; align="center"; width="800px"/>

4. You will now be logged into your new database, and can navigate between tables using the nav bar at the left side of the display, and control the contents of tables 
using the control panel which appears at the bottom of the display when viewing a table.
<img src="images/main_display.png"; alt="Home screen"; align="center"; width="600px"/>

5. Should you wish to add custom tables to your database simply select the entry in the navbar on the left and the add table window will open.<br>
Give your new table a name and select one of the predefined table templates or just enter your desired column headings (separated by commas) in the appropriate text box and click "Ok".<br>
Whether created from a template or custom you can add or remove columns from tables as you wish to tailor your database to your needs.
<img src="images/create_table.png"; alt="Home screen"; align="center"; width="400px"/>

6. To generate a strong password for an account again simply select the password genarator from the nav bar on the left and the generator window will open.<br>
Select the character sets you wish to use then choose the length of passord you want, either by moving the dragbar or typing in the appropriate box, then click "Generate". A
random password will be created using your selection, click the "Copy password" button to copy this to your clipboard for use.
<img src="images/password_genarator.png"; alt="Home screen"; align="center"; width="450px"/>

7. To save a new entry to a table select the table from the navbar and select "Add entry" from the control panel. This will open a new erntry window, enter your desired information and click "Submit"

8. To update the password for your database file select the "Change master pass" option from the navbar on the left and the appropriate window will open.<br>
Enter and confirm your new password. You will also have the option to generate a new keyfile at this point, keep in mind you will need to replace any backups with the new files.<br>
Once you are satisfied everything has been entered correctly click "Ok" and your details will be updated.
<img src="images/update_password.png"; alt="Home screen"; align="center"; width="600px"/>




<h2>Installation</h2>

<h2>Linux</h2>

<h3>Debian:-</h3>


Ensure you have python 3.8 and pip3 installed on your system, if not install with

    sudo apt-get install python3 pip


Clone the repository

    git clone https://github.com/J-Mathers/Castle.git


Move into the downloaded directory

    cd ./Castle


Install tkinter if not present

    sudo apt install python3-tk


Install xclip and xsel to handle copying passwords to clipboard

    sudo apt install xclip xsel


Install neeed python packages

    pip3 install -r requirements.txt


Then simply run the script "castle.py"

    ./castle.py




<h3>Fedora:</h3>


Ensure you have python 3.8 and pip3 installed on your system, if not install with

    sudo dnf install python3 pip


Clone the repository

    git clone https://github.com/J-Mathers/Castle.git


Move into the downloaded directory

    cd ./Castle


Install tkinter if not present

    sudo dnf install python3-tkinter


Install xclip and xsel to handle copying passwords to clipboard

    sudo dnf install xclip xsel


Install neeed python packages

    pip install -r requirements.txt


Then simply run the script "castle.py"

    ./castle.py





<h2>Windows</h2>

Install python 3.8 from the Microsoft Store

Make sure this installation included pip by opening a command prompt window and executing

    pip --version


If this gives a program version pip is installed on your system and you may proceed

Install the latest version of gpg4win from https://www.gpg4win.org/

Install needed python packages - from a command prompt window execute

    pip install -r win-requirements.txt


Now simply right click the script, select "open with" and chooose python 3.8




<h2>Licensing</h2>

This software is released under the GNU GPLv3 licence



