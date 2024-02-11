import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import subprocess
import pkg_resources
from Cryptodome.Random import get_random_bytes
from cryptography.fernet import Fernet
from tkhtmlview import HTMLLabel
import json
import base64
import os
import time

# Check if each required package is installed
required_packages = ['pycryptodomex', 'cryptography']
for package in required_packages:
    try:
        pkg_resources.get_distribution(package)
    except pkg_resources.DistributionNotFound:
        print(f"{package} is not installed. Installing...")
        subprocess.check_call(['pip', 'install', package])

time_limit = 0  # Initialize the time_limit variable

def browse_file(filepath_entry):
    file_path = filedialog.askopenfilename()
    filepath_entry.delete(0, tk.END)
    filepath_entry.insert(0, file_path)

def send_mail(sender_email, receiver_email, subject, message, smtp_password):
    # Set up SMTP server configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = sender_email

    # Create a multipart message object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Add a text message to the email
    msg.attach(MIMEText(message, 'plain'))

    # Connect to the SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()

    try:
        # Log in to the SMTP server
        server.login(smtp_username, smtp_password)

        # Send the message
        server.send_message(msg)
        messagebox.showinfo("Info", "Email sent successfully.")

    except smtplib.SMTPAuthenticationError:
        messagebox.showerror("Error", "Wrong SMTP Password")

    finally:
        # Quit the server
        server.quit()

import time  # Import the time module

import time

def encrypt_file(filepath, sender_email, receiver_email, smtp_password, time_limit, window):
    key = Fernet.generate_key()
    fernet = Fernet(key)

    with open(filepath, 'rb') as file:
        data = file.read()

    encrypted_data = fernet.encrypt(data)

    with open(filepath, 'wb') as file:
        file.write(encrypted_data)

    # Convert the key to a string before saving it to JSON
    key_str = base64.urlsafe_b64encode(key).decode('utf-8')

    if float(time_limit) > 0:  # Check if time_limit is greater than 0
        # Save the key and expiration time to a file
        key_info = {'key': key_str, 'expiration_time': time.time() + float(time_limit) * 60}
    else:
        # Save the key without expiration time when time_limit is 0
        key_info = {'key': key_str}

    key_info_file = filepath + "_key_info.json"
    with open(key_info_file, 'w') as key_file:
        json.dump(key_info, key_file)

    subject = 'The Key for Encrypted file'
    message = f'The Key for Encrypted file is:\n{key_str}'

    send_mail(sender_email, receiver_email, subject, message, smtp_password)

    messagebox.showinfo("Info", "File encrypted successfully.")
    window.destroy()

def decrypt_file(filepath, password):
    # Get file path and password from the respective entries
    if not filepath:
        messagebox.showerror("Error", "Please select a file to decrypt.")
        return

    if not os.path.exists(filepath):
        messagebox.showerror("Error", "Invalid file path.")
        return

    if not password:
        messagebox.showerror("Error", "Please enter a password.")
        return

    try:
        # Convert password to bytes and extract key
        key_info_file = filepath + "_key_info.json"
        with open(key_info_file, 'r') as key_file:
            key_info = json.load(key_file)

        # Retrieve key and expiration time
        key = base64.urlsafe_b64decode(key_info['key'])
        expiration_time = key_info.get('expiration_time')

        # Check if expiration time is present and not expired
        if expiration_time is None or time.time() <= expiration_time:
            # Read encrypted data from file
            with open(filepath, 'rb') as encrypted_file:
                encrypted_data = encrypted_file.read()

            # Decrypt the data
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)

            # Write decrypted data to output file
            with open(filepath, 'wb') as decrypted_file:
                decrypted_file.write(decrypted_data)
                messagebox.showinfo("Success", "Decryption successful.")
        else:
            messagebox.showerror("Error", "Key has expired. Decryption failed.")
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during decryption or it has already been decrypted: {str(e)}")



def open_time_limit_window(callback):
    time_limit_window = tk.Toplevel(root)
    time_limit_window.geometry("300x150")
    time_limit_window.title("Set Time Limit")

    time_limit_label = tk.Label(time_limit_window, text="Enter Time Limit (minutes):")
    time_limit_entry = tk.Entry(time_limit_window)
    set_button = tk.Button(time_limit_window, text="Encrypt", command=lambda: callback(time_limit_entry.get(), time_limit_window))

    time_limit_label.pack(pady=10)
    time_limit_entry.pack(pady=10)
    set_button.pack(pady=10)

def open_file_window():
    global time_limit  # Use the global time_limit variable
    file_window = tk.Toplevel(root)
    file_window.geometry("560x200")
    file_window.title("Select File")

    filepath_label = tk.Label(file_window, text="File Path")
    email_label = tk.Label(file_window, text="Sender Email")
    smtp_label = tk.Label(file_window, text="SMTP Password")
    receiver_label = tk.Label(file_window, text="Receiver Email")

    filepath_entry = tk.Entry(file_window, width=60)
    email_entry = tk.Entry(file_window, width=60)
    smtp_entry = tk.Entry(file_window, width=60, show="*")
    receiver_entry = tk.Entry(file_window, width=60)

    browse_button = tk.Button(file_window, text="Browse Files", command=lambda: browse_file(filepath_entry))

    # Create the Encrypt File button in the file window
    encrypt_button = tk.Button(file_window, text="Encrypt File", font=("Arial", 14, "bold"), bg="red", fg="white", command=lambda: encrypt_file(filepath_entry.get(), email_entry.get(), receiver_entry.get(), smtp_entry.get(), time_limit, file_window))

    time_limit_button = tk.Button(file_window, text="Set Time Limit", command=lambda: open_time_limit_window(lambda time_limit, window: encrypt_file(filepath_entry.get(), email_entry.get(), receiver_entry.get(), smtp_entry.get(), time_limit, window)))

    filepath_label.grid(row=0, column=0, sticky=tk.E)
    filepath_entry.grid(row=0, column=1)
    email_label.grid(row=1, column=0)
    email_entry.grid(row=1, column=1)
    smtp_label.grid(row=2, column=0)
    smtp_entry.grid(row=2, column=1)
    receiver_label.grid(row=3, column=0)
    receiver_entry.grid(row=3, column=1)

    browse_button.grid(row=0, column=2)
    encrypt_button.grid(row=5, column=0, columnspan=2, pady=10)
    time_limit_button.grid(row=6, column=0, columnspan=2, pady=10)

def decrypting():
    file_window = tk.Toplevel(root)
    file_window.geometry("560x200")
    file_window.title("Decrypt File")

    filepath_label = tk.Label(file_window, text="File Path")
    filepath_entry = tk.Entry(file_window, width=60)
    password_label = tk.Label(file_window, text="Password")
    password_entry = tk.Entry(file_window, width=60, show="*")

    filepath_label.grid(row=0, column=0, sticky=tk.E)
    filepath_entry.grid(row=0, column=1)
    password_label.grid(row=1, column=0)
    password_entry.grid(row=1, column=1)

    browse_button = tk.Button(file_window, text="Browse Files", command=lambda: browse_file(filepath_entry))
    decrypt_button = tk.Button(file_window, text="Decrypt File", font=("Arial", 14, "bold"), bg="red", fg="white",
                               command=lambda: decrypt_file(filepath_entry.get(), password_entry.get()))

    decrypt_button.grid(row=6, column=0, columnspan=2, pady=10)
    browse_button.grid(row=0, column=2)

# ... (rest of the code remains the same)
def display_html():
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <title></title>
       
      
    </head>
    <body>
        <div class="container">
            <h2>Project Information</h2>
            <table>
                <tr>
                    Project done by<br>
                    Uday Teja <br>
                
                </tr>
                <tr>
                    Email for queries:
                    <td>q124441@gmail.com</td>
                </tr>
            </table>
        </div>
    </body>
    </html>
    """

    html_window = tk.Toplevel(root)
    html_window.title("HTML Viewer")
    html_window.geometry("800x600")

    html_label = HTMLLabel(html_window, html=html_code)
    html_label.pack(expand=True, fill="both")

root = tk.Tk()

# Create the main window and buttons

root.title("File Encrypt Decrypt")
root.geometry("600x500")

window_width = 600
window_height = 500

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = int((screen_width/2) - (window_width / 2))
y = int((screen_height/2) - (window_height / 2))

root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.configure(bg='black')

button_frame = tk.Frame(root, bg="grey")

info_button = tk.Button(root, text="Project Info", font=("Arial", 14, "bold"), bg="red", fg="white", command=lambda: display_html())
info_button.pack(pady=20)

project_label = tk.Label(root, text="File Encrypt And Decrypt!!!", font=("Arial", 18, "bold"), bg="black")
project_label.pack(pady=25)

# Set base64 string image as the background
button_frame = tk.Frame(root, bg="grey")
button1 = tk.Button(button_frame, text="Encrypt files", font=("Arial", 14, "bold"), padx=10, pady=5, command=lambda: open_file_window())
button2 = tk.Button(button_frame, text="Decrypt files", font=("Arial", 14, "bold"), padx=10, pady=5, command=lambda: decrypting())
button1.pack(side="top", fill="x", padx=50, pady=10)
button2.pack(side="bottom", fill="x", padx=50, pady=10)
button_frame.pack(expand=True)

root.mainloop()
