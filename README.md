<h1>Castle - A Python password manager</h1>

Castle is a simple password manager written entirely in python.

It makes use of sqlite3 databases to store your data and gpg encryption on both the files themcselves and all data stored within the database file.

When a new database is created it also generates a "keyfile" - a text file containing a 256 character password required to decrypt any passwords etc stored in database tables.
This file is only opened to read the key into memory and then encrypted again.

The password to open this file is stored in a table of it's own in the database, which is hidden from the user interface, and cannot be retrieved without the master password.

The outcome is a "handshake" style operation needed in order to unlock the database fully. i.e. the master password is needed to unlock the overall database and retrieve the password to the keyfile.
The keyfile is then opened and if read successfully can then decrypt your stored data.

This creates an opportunity to treat this "keyfile" like a multifactor authentication token. the intention is for the keyfile to be stored separately from the database file (for example on a usb pen).

If for any reason you think your keyfile may have been compromised there is an option to generate a new keyfile when you change your master password.

Note this will not change the password stored in this file, but it will change the password his file is encrypted with so the original will no longer be usable with the program.

Beyond this it functions much like any other password manager.

The interface is a simple dashboard style and fairly self explanatory.

You can generate passwords from a selection of character sets and easily copy these back and forth between the manager and your applications.

The program itself is capable of storing standard password style data, secure notes for longer messages and will also store files - all fully encrypted for peace of mind.






<h2>Installation</h2>

<h2>Linux</h2>

<h3>Debian:-</h3>


Ensure you have python 3.8 and pip3 installed on your system, if not install with
'''bash
sudo apt-get install python3 pip
'''

Clone the repository
'''bash
git clone https://github.com/J-Mathers/Castle.git
'''

Move into the downloaded directory
'''bash
cd ./Castle
'''

Install tkinter if not present
'''bash
sudo apt install python3-tk
'''

Install xclip and xsel to handle copying passwords to clipboard
'''bash
sudo apt install xclip xsel
'''

Install neeed python packages
'''bash
pip3 install -r requirements.txt
'''

Then simply run the script "castle.py"
'''bash
./castle.py
'''



<h3>Fedora:</h3>


Ensure you have python 3.8 and pip3 installed on your system, if not install with
'''bash
sudo dnf install python3 pip
'''

Clone the repository
'''bash
git clone https://github.com/J-Mathers/Castle.git
'''

Move into the downloaded directory
'''bash
cd ./Castle
'''

Install tkinter if not present
'''bash
sudo dnf install python3-tkinter
''

Install xclip and xsel to handle copying passwords to clipboard
'''bash
sudo dnf install xclip xsel
'''

Install neeed python packages
'''bash
pip install -r requirements.txt
'''

Then simply run the script "castle.py"
'''bash
./castle.py
'''




<h2>Windows</h2>

Install python 3.8 from the Microsoft Store

Make sure this installation included pip by opening a command prompt window and executing
'''bash
pip --version
'''

If this gives a program version pip is installed on your system and you may proceed

Install the latest version of gpg4win from https://www.gpg4win.org/

Install needed python packages - from a command prompt window execute
'''bash
pip install -r win-requirements.txt
'''

Now simply right click the script, select "open with" and chooose python 3.8


Licensing

This software is released under the GNU GPLv3 licence



