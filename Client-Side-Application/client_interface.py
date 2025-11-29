import os

import customtkinter as ctk
import tkinter as tk
import subprocess
from threading import Thread
import ast
import time
from customtkinter import filedialog

class ClientCmd:
    def __init__(self):
        #initiation for the client communication
        self.p = None
        self.current_dir = ''

    def login(self, username, password):
        #open the client application and attempt to login
        self.p = subprocess.Popen(["python", "clientApplication.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT , text=True)
        if not "OK@Welcome" in self.p.stdout.readline():
            self.p.kill()
            self.p = None
            return False

        self.p.stdin.write(f"{username}\n")
        self.p.stdin.flush()
        self.p.stdin.write(f"{password}\n")
        self.p.stdin.flush()

        if "AUTH_OK" in self.p.stdout.readline():
            self.p.stdout.readline()
            self.p.stdout.readline()
            return True
        else:
            return False

    def current_dir_name(self):
        #return the dir name of the dir we are in
        return self.current_dir
    
    def delete_file(self, filename):
        #delete file instruction, and result takes in filename string and returns bool of success
        self.p.stdin.write(f"Delete {filename}\n")
        self.p.stdin.flush()

        self.p.stdout.readline()
        self.p.stdout.readline()
        self.p.stdout.readline()
        result = self.p.stdout.readline()
        self.p.stdout.readline()

        return result != "File Deleted"

    def download_file(self, filename):
        #download files takes fileanme, returns bool, takes filename
        self.p.stdin.write(f"Download {filename}\n")
        self.p.stdin.flush()
        self.p.stdout.readline()
        while self.p.stdout.readline().startswith("Receiving..."):
            continue
        bot =self.p.stdout.readline()
        self.p.stdout.readline()
        self.p.stdout.readline()
        self.p.stdout.readline()

        if bot.startswith("received: OK"):
            return True
        else:
            return False

    def delete_dir(self, name):
        #takes dir name and then attempts to delete it, returns bool of success
        self.p.stdin.write(f"DirDelete {name}\n")
        self.p.stdin.flush()

        self.p.stdout.readline()
        self.p.stdout.readline()
        self.p.stdout.readline()
        result = self.p.stdout.readline()
        self.p.stdout.readline()

        if result.startswith("Directory Deleted"):
            return True
        else:
            return False

    def create_dir(self, name):
        #returns bool of success, takes name for dir, attempts to create the dir
        self.p.stdin.write(f"DirCreate {name}\n")
        self.p.stdin.flush()

        self.p.stdout.readline()
        self.p.stdout.readline()
        self.p.stdout.readline()
        result = self.p.stdout.readline()
        self.p.stdout.readline()

        if result.startswith("Directory /"):
            return True
        else:
            return False

    def change_dir(self, dir):
        #change dir to dir can move up or down, needs name of dir, .. to move up
        if dir == '..':
            if len(self.current_dir) > 0:
                i = self.current_dir.rindex('/')
                self.current_dir = self.current_dir[0:i]
            else:
                #already at highest dir possible
                pass
        else:
            self.current_dir +=f"/{dir}"

        self.p.stdin.write(f"ChangeDir {self.current_dir}\n")
        self.p.stdin.flush()

        self.p.stdout.readline()
        if not "OK" in self.p.stdout.readline():
            print("something is wrong in change_dir")

        self.p.stdout.readline()
        self.p.stdout.readline()
        self.p.stdout.readline()

    def get_current_dir(self):
        #reutns contents of current dir
        self.p.stdin.write(f"Dir\n")
        self.p.stdin.flush()

        output = self.p.stdout.readline()
        if not "Dir" in output :
            print("something is wrong in get_current_dir")
            print(output)
            pass

        output = self.p.stdout.readline()
        if not "OK" in output :
            print("something is wrong in get_current_dir")
            print(output)
            pass

        #no point checking client output
        self.p.stdout.readline()

        dir = self.p.stdout.readline()
        dir_set = ast.literal_eval(dir)
        self.p.stdout.readline()
        return dir_set

    def start_upload_file(self, filePath):
        #File path to upload path, returns a bool to say wheter overwrite is needed
        self.p.stdin.write(f"Upload {filePath}\n")
        self.p.stdin.flush()

        self.p.stdout.readline()
        self.p.stdout.readline()

        data = self.p.stdout.readline()
        return data.startswith('File already exists')

    def cancel_upload_file(self):
        #cancel the upload of a file
        self.p.stdin.write(f"n\n")
        self.p.stdin.flush()

        self.p.stdout.readline()
        self.p.stdout.readline()
        self.p.stdout.readline()
        self.p.stdout.readline()

    def finish_upload_file(self, overwrite = False):
        # overwrite a file
        if overwrite:
            self.p.stdin.write(f"y\n")
            self.p.stdin.flush()

        data = self.p.stdout.readline()
        while not data.startswith("File sent"):
            data = self.p.stdout.readline()

        self.p.stdout.readline()
        self.p.stdout.readline()
        self.p.stdout.readline()
        self.p.stdout.readline()

    def logout(self):
        #function to logout
        self.p.stdin.write(f"LOGOUT\n")
        self.p.stdin.flush()
        return True

class client_ui:
    #class to contain the client ui and make calls to the clien cmd class
    def __init__(self):
        #initiatino, instance varibales 
        self.client_cmd = None
        self.window = None
        self.user = None
        self.password = None
        ctk.set_appearance_mode("Dark")


    def login(self, failed = False):
        #Window that has two text entry one for user one for login, a button to submit
        self.window.configure(fg_color="#070F2B")
        self.window.title("CNT3004 File Server Login")
        self.window.geometry("400x300")

        self.window.frame = ctk.CTkFrame(master=self.window)
        self.window.frame.configure(fg_color="#070F2B")
        self.window.frame.pack(expand=True)

        self.user = ctk.CTkEntry(master=self.window.frame, placeholder_text="Username", fg_color="#1B1A55")
        self.password = ctk.CTkEntry(master=self.window.frame, placeholder_text="Password", show="*", fg_color="#1B1A55")
        login_button = ctk.CTkButton(master=self.window.frame, text="Login", command=self.send_login, fg_color="#3C3D37")

        warning = "Login Failed! Invalid username or password."
        self.window.frame.warning_label = ctk.CTkLabel(master=self.window.frame, text=warning, text_color="#070F2B")
        self.window.frame.warning_label.pack(pady=(10, 10))

        self.user.pack(pady=10)
        self.password.pack(pady=10)
        login_button.pack(pady=20)

    def send_login(self):
        #attempt login go to main window id the login works else go back to login with warning label
        if self.client_cmd.login(self.user.get(), self.password.get()):
            self.main_window()
        else:
            self.login_failed()

    def login_failed(self):
        #set the label to inform the user that the login has failed
        self.window.frame.warning_label.configure(True, text_color="#FF3333")
        #self.window.destroy()
        #self.login(True)

    def main_window(self):
        #The main window that holds the dir, and file oprions
        #click on files and options to see more options
        self.window.title("CNT3004 File Server")
        self.window.geometry("800x600")
        self.window.configure(fg_color="#070F2B")
        self.window.frame.destroy()

        #current dir
        current_dir = self.client_cmd.get_current_dir()

        self.window.frame = ctk.CTkFrame(master=self.window)
        self.window.frame.configure(fg_color="#FFFFFF")

        self.window.frame.warning_label = ctk.CTkLabel(master=self.window.frame, text="", text_color="#070F2B")
        self.window.frame.warning_label.pack(pady=(10, 10))

        self.window.frame1 = self.display_dir(self.window.frame, current_dir)
        self.window.frame2 = self.file_system_options(self.window.frame)

        self.window.frame1.pack(fill ="x", padx=10)
        self.window.frame2.pack()


        self.window.frame.pack(expand=True, fill="x", padx=10, pady=10)
        #self.window.mainloop()

    def display_dir(self, frame_master, dir_set):
        # creates a frame to show the current dir
        frame = ctk.CTkScrollableFrame(master=frame_master)
        frame.configure(fg_color="#DDDDDD")
        frame.configure(width=600)

        dir_name = self.client_cmd.current_dir_name()
        if dir_name == "":
            dir_name = "downloadable-storage/"
        else:
            dir_name = "downloadable-storage" + dir_name

        ctk.CTkLabel(master=frame, text=dir_name, text_color="#000000", font=('Ariel', 14, 'bold')).pack(padx= 30, anchor="w")

        for obj in sorted(dir_set):
            name = obj[2:]

            if obj.startswith("F:"):
                ctk.CTkButton(master=frame,text=f"📄   {name}",command=lambda file=obj: self.file_options(file)).pack(pady=5, padx=30, anchor="w")


            elif obj.startswith("D:"):
                ctk.CTkButton(master=frame,text=f"📁   {name}", command=lambda directory=obj: self.directory_options(directory)).pack(pady=5, padx=30, anchor="w")

        return frame

    def file_system_options(self, frame_master):
        #Buttons at the bottom of the main window
        #upload, move dir, logout, refresh, and create dir
        frame = ctk.CTkFrame(master=frame_master)
        frame.configure(fg_color="#FFFFFF")
        frame.configure(width=600)

        button_row = ctk.CTkFrame(frame)

        button_row.configure(fg_color="#FFFFFF")
        button_row.pack(pady=15, fill="x", padx=20)

        upload = ctk.CTkButton(button_row, text="Upload File", command=lambda: self.upload_file()).pack(side="left", padx=10)
        move_dir_up = ctk.CTkButton(button_row, text="Go to Parent", command=lambda: self.go_to_parent_dir()).pack(side="left", padx=10)
        logout = ctk.CTkButton(button_row, text="Logout", command=lambda: self.logout()).pack(side="left", padx=10)
        make_dir = ctk.CTkButton(button_row, text="Make Directory", command=lambda: self.make_dir()).pack(side="left", padx=10)
        refresh_dir = ctk.CTkButton(button_row, text="Refresh Dir", command=lambda: self.refresh_dir()).pack(side="left", padx=10)

        return frame

    def go_to_parent_dir(self):
        #Attempt to move up one dir
        self.client_cmd.change_dir("..")
        self.refresh_dir()

    def upload_file(self):
        #choose a file to uplaod attempt uplaod and handle overwrites
        file_path = filedialog.askopenfilename()
        file_name = os.path.basename(file_path)
        if file_path:
            needsOverwrite =  self.client_cmd.start_upload_file(file_path)

            if needsOverwrite:
                # prompt user overwrite yes no
                user_response = self.overwrite_question(file_name)
                if user_response:
                    self.client_cmd.finish_upload_file(True)
                else:
                    self.client_cmd.cancel_upload_file()
            else:
                self.client_cmd.finish_upload_file()

            self.refresh_dir()

    def overwrite_question(self, file_name):
        #popup to ask the client if they want to overwrite an existing file
        #two buttons yes and no
        overwrite_window = ctk.CTkToplevel(self.window)
        overwrite_window.title("OVERWRITE")
        overwrite_window.geometry("400x150")
        overwrite_window.configure(fg_color="#070F2B")

        overwrite_window.grab_set()
        overwrite_window.focus_force()
        overwrite_window.transient(self.window)


        ctk.CTkLabel(overwrite_window, text="File: " + file_name, font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(overwrite_window, text="Do you want to overwrite the existing file?", font=("Arial", 14)).pack(pady=5)

        overwrite = False

        def confirm():
            nonlocal overwrite
            overwrite = True
            overwrite_window.destroy()

        def cancel():
            nonlocal overwrite
            overwrite = False
            overwrite_window.destroy()

        button_row = ctk.CTkFrame(overwrite_window)

        button_row.configure(fg_color="#070F2B")
        button_row.pack(pady=15, fill="x", padx=20)

        ctk.CTkButton(button_row, text="YES", command=confirm, font=("Arial", 14, "bold"), fg_color="#00CCAA").pack( padx = 5, side="left")
        ctk.CTkButton(button_row, text=" NO", fg_color="#FF0000", font=("Arial", 14, "bold"),  command=cancel).pack( padx = 5, side="left")

        overwrite_window.wait_window()

        return overwrite

    def file_options(self, name):
        #Popup showing the user options for files, download and delete
        self.window.prompt = ctk.CTkToplevel(self.window)
        self.window.prompt.configure(fg_color="#070F2B")
        self.window.prompt.geometry("400x150")
        self.window.prompt.title("File Options")

        label = ctk.CTkLabel(master=self.window.prompt,text=name[2:],text_color="#FFFFFF",font=("Arial", 16, "bold"))
        label.pack(pady=5, padx=20, fill="x")

        self.window.prompt.result_label = ctk.CTkLabel(master=self.window.prompt,text=" ",text_color="#FFFFFF",font=("Arial", 12))
        self.window.prompt.result_label.pack(pady=5, padx=20, fill="x")

        button_row = ctk.CTkFrame(self.window.prompt, fg_color="#070F2B")
        button_row.pack(pady=15, fill="x", padx=20)

        ctk.CTkButton( button_row,text="Download",command=lambda filename=name[2:]: self.download_file(filename)).pack(side="left", padx=20)

        ctk.CTkButton(button_row,text="Delete",command=lambda filename=name[2:]: self.delete_file(filename)).pack(side="left", padx=10)

    def directory_options(self, dir):
        #popup to show user options for dirs, delete, move to
        self.window.prompt = ctk.CTkToplevel(self.window)
        self.window.prompt.configure(fg_color="#070F2B")
        self.window.prompt.geometry("400x150")
        self.window.prompt.title("Directory Options")

        label = ctk.CTkLabel(master=self.window.prompt, text=f"📁 {dir[2:]}", text_color="#FFFFFF", font=("Arial", 16, "bold"))
        label.pack(pady=5, padx=20, fill="x")

        self.window.prompt.result_label = ctk.CTkLabel( master=self.window.prompt,text=" ", text_color="#FFFFFF", font=("Arial", 12) )
        self.window.prompt.result_label.pack(pady=5, padx=20, fill="x")

        button_row = ctk.CTkFrame(self.window.prompt, fg_color="#070F2B")
        button_row.pack(pady=15, fill="x", padx=20)

        ctk.CTkButton(button_row, text="move to", command=lambda name=dir[2:]: self.move_dir(name)).pack(side="left", padx=20)
        ctk.CTkButton(button_row,text="delete",command=lambda name=dir[2:]: self.delete_dir(name)).pack(side="left", padx=10)

    def move_dir(self, dir):
        #attempt to move to dir
        self.client_cmd.change_dir(dir)
        self.refresh_dir()
        self.window.prompt.destroy()
        self.window.prompt = None
        pass

    def delete_dir(self, name):
        #attempt to delete dir
        success = self.client_cmd.delete_dir(name)

        if success:
            self.window.prompt.destroy()
            self.window.prompt = None
        else:
            self.window.prompt.result_label.configure(text="Dir could not be deleted")

        self.refresh_dir()

    def delete_file(self, filename):
        #Attempt to delet file, display if it does not work
        success = self.client_cmd.delete_file(filename)
        if not success:
            self.window.prompt.result_label.configure("File could not be deleted", "#FF0000")
        else:
            self.window.prompt.destroy()
            self.window.prompt = None
        self.refresh_dir()

    def download_file(self, filename):
        #attempt to download file
        success = self.client_cmd.download_file(filename)
        if success:
            self.window.prompt.result_label.configure(text="Successful Download", text_color="#FFFFFF")
        else:
            self.window.prompt.result_label.configure(text="Download Failed", text_color="#FF0000")

    def refresh_dir(self):
        #Refresh the dir display, reset error message
        current_dir = self.client_cmd.get_current_dir()
        self.main_warning("success", "#FFFFFF")

        self.window.frame1.pack_forget()
        self.window.frame1 = self.display_dir(self.window.frame, current_dir)
        self.window.frame1.pack(fill="x", before=self.window.frame2)

    def make_dir(self):
        #attempt to make a dir and display success
        name = self.ask_name_popup("Create Folder", "Folder name:")
        success = self.client_cmd.create_dir(name)
        if success:
            self.main_warning("Directory created", "#FFFFFF")
            self.refresh_dir()
        else:
            self.main_warning("Directory could not be created", "#FF0000")


    def logout(self):
        #attempt logout and close the application
        success = self.client_cmd.logout()
        if success:
            self.window.frame.quit()
            self.window.quit()
            self.window.destroy()

    def ask_name_popup(self, title, prompt):
        #popu up asking the user to enter the name of the new directory
        ask_name = ctk.CTkToplevel()
        ask_name.title(title)
        ask_name.geometry("350x160")
        ask_name.configure(fg_color="#070F2B")

        frame = ctk.CTkFrame(ask_name, fg_color="#070F2B")
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        label = ctk.CTkLabel(frame, text=prompt, text_color="#FFFFFF")
        label.pack(pady=(0, 10))

        entry = ctk.CTkEntry(frame, width=220)
        entry.pack(pady=5)
        entry.focus()

        result = "mydir"

        def submit():
            nonlocal result
            result = entry.get()
            ask_name.destroy()

        btn = ctk.CTkButton(frame, text="OK", command=submit)
        btn.pack(pady=10)

        ask_name.wait_window()

        return result

    def main_warning(self, msg,color):
        #update the main warning label with msg and color
        self.window.frame.warning_label.configure(text=msg, text_color=color)


ui = client_ui()
ui.client_cmd = ClientCmd()
ui.window = ctk.CTk()
ui.login()
ui.window.mainloop()