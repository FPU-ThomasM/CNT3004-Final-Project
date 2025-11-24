import customtkinter as ctk
import time


class client_ui:
    def __init__(self):
        self.window = None
        self.user = None
        self.password = None
        ctk.set_appearance_mode("Dark")


    def login(self, failed = False):
        self.window = ctk.CTk()
        self.window.configure(fg_color="#070F2B")
        self.window.title("CNT3004 File Server Login")
        self.window.geometry("400x300")
        self.user = ctk.CTkEntry(master=self.window, placeholder_text="Username", fg_color="#1B1A55")
        self.password = ctk.CTkEntry(master=self.window, placeholder_text="Password", show="*", fg_color="#1B1A55")
        login_button = ctk.CTkButton(master=self.window, text="Login", command=self.login_failed, fg_color="#3C3D37")

        warning = "Login Failed! Invalid username or password."
        self.window.warning_label = ctk.CTkLabel(master=self.window, text=warning, text_color="#070F2B")
        self.window.warning_label.pack(pady=(10, 10))

        self.user.pack(pady=(40, 10))
        self.password.pack(pady=10)
        login_button.pack(pady=20)
        self.window.mainloop()

    def send_login(self):
        return {"user": self.user.get(), "password": self.password.get()}

    def login_failed(self):
        self.window.warning_label.configure(True, text_color="#FF3333")
        #self.window.destroy()
        #self.login(True)


    def main_window(self):
        self.window = ctk.CTk()
        self.window.title("CNT3004 File Server")
        self.window.geometry("800x600")
        self.window.configure(fg_color="#070F2B")




        self.window.mainloop()

    def display_dir(self, dir_string):
        frame = ctk.CTkScrollableFrame(master=self.window)
        frame.configure(fg_color="#070F2B")



        return frame

ui = client_ui()
ui.login()
#ui.main_window()