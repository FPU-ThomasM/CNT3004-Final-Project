import customtkinter as ctk
import tkinter as tk
import subprocess
from threading import Thread
import ast

from boto3.s3.inject import download_file

class ClientCmd:
    def __init__(self):
        self.p = None

    def login(self, username, password):
        self.p = subprocess.Popen(["python clientApplication.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, text=True)
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
    
    def delete_file(self, filename):
        self.p.stdin.write(f"Delete {filename}\n")
        self.p.stdin.flush()

        self.p.stdout.readline()
        self.p.stdout.readline()
        self.p.stdout.readline()
        result = self.p.stdout.readline()
        self.p.stdout.readline()

        return result != "File Deleted"

    def get_current_dir(self):
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


class client_ui:
    def __init__(self):
        self.client_cmd = None
        self.window = None
        self.user = None
        self.password = None
        ctk.set_appearance_mode("Dark")


    def login(self, failed = False):
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
        if self.client_cmd.login(self.user.get(), self.password.get()):
            self.main_window()
        else:
            self.login_failed()

    def login_failed(self):
        self.window.frame.warning_label.configure(True, text_color="#FF3333")
        #self.window.destroy()
        #self.login(True)


    def main_window(self):
        self.window.title("CNT3004 File Server")
        self.window.geometry("800x600")
        self.window.configure(fg_color="#070F2B")
        self.window.frame.destroy()

        current_dir = self.client_cmd.get_current_dir()

        frame = ctk.CTkFrame(master=self.window)
        frame.configure(fg_color="#FFFFFF")

        frame1 = self.display_dir(frame, current_dir)
        frame2 = self.file_system_options(frame)

        frame1.pack(fill ="x")
        frame2.pack()


        self.window.frame = frame
        self.window.frame.pack(expand=True, fill="x", padx=10, pady=10)
        self.window.mainloop()

    def display_dir(self, frame_master, dir_set):
        frame = ctk.CTkScrollableFrame(master=frame_master)
        frame.configure(fg_color="#FFFFFF")
        frame.configure(width=600)
        for obj in sorted(dir_set):
            name = obj[2:]

            if obj.startswith("F:"):
                ctk.CTkButton(master=frame,text=f"📄   {name}",command=lambda file=obj: self.file_options(file)).pack(pady=5, padx=30, anchor="w")


            elif obj.startswith("D:"):
                ctk.CTkButton(master=frame,text=f"📁   {name}", command=lambda directory=obj: self.directory_options(directory)).pack(pady=5, padx=30, anchor="w")

        return frame

    def file_system_options(self, frame_master):
        frame = ctk.CTkFrame(master=frame_master)
        frame.configure(fg_color="#FFFFFF")
        frame.configure(width=600)

        button_row = ctk.CTkFrame(frame)

        button_row.configure(fg_color="#FFFFFF")
        button_row.pack(pady=15, fill="x", padx=20)

        upload = ctk.CTkButton(button_row, text="Upload File").pack(side="left", padx=10)
        move_dir_up = ctk.CTkButton(button_row, text="Go to Parent").pack(side="left", padx=10)
        logout = ctk.CTkButton(button_row, text="Logout").pack(side="left", padx=10)
        make_dir = ctk.CTkButton(button_row, text="Make Directory").pack(side="left", padx=10)

        return frame

    def file_options(self, name):
        self.window.prompt = ctk.CTk()
        self.window.prompt.configure(fg_color="#070F2B")
        self.window.prompt.geometry("400x100")
        label = ctk.CTkLabel(master=self.window.prompt, text=name[2:], fg_color="#070F2B", text_color="#FFFFFF", font=("Arial", 16, "bold"))

        label.pack(pady=5, padx =20, fill= "x")

        button_row = ctk.CTkFrame(self.window.prompt)
        button_row.configure(fg_color="#070F2B")
        button_row.pack(pady=15, fill="x", padx=20)

        download_button = ctk.CTkButton(button_row, text="download").pack(side="left", padx=20)
        delete_button = ctk.CTkButton(button_row, text="delete", command=lambda filename=name[2:]: self.delete_file(filename)).pack(side="left", padx=10)

    def directory_options(self, dir):
        self.window = ctk.CTk()
        self.window.configure(fg_color="#070F2B")
        self.window.geometry("400x100")
        label = ctk.CTkLabel(master=self.window, text=f"📁 {dir[2:]}", fg_color="#070F2B", text_color="#FFFFFF", font=("Arial", 16, "bold"))

        label.pack(pady=5, padx=20, fill="x")

        button_row = ctk.CTkFrame(self.window)
        button_row.configure(fg_color="#070F2B")
        button_row.pack(pady=15, fill="x", padx=20)

        download_button = ctk.CTkButton(button_row, text="move to").pack(side="left", padx=20)
        delete_button = ctk.CTkButton(button_row, text="delete").pack(side="left", padx=10)
    
    def delete_file(self, filename):
        success = self.client_cmd.delete_file(filename)
        self.window.prompt.destroy()
        self.window.prompt = None
        print(success)


ui = client_ui()
ui.client_cmd = ClientCmd()
ui.window = ctk.CTk()
ui.login()
ui.window.mainloop()

"""if ui.window is not None:
    ui.window.prompt.destroy()"""
#ui.main_window()