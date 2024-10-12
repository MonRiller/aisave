import os, json
import customtkinter as ctk
from aisave import base
from aisave.crypto import load_info, save_info
from aisave.cve import update_cves
from PIL import Image



def get_users():
    return [file[:-4] for file in os.listdir(os.path.join(base, "data")) if file[-4:] == ".enc"]

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AISAVE")
        self.geometry("1400x800")
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.bind("<Control-d>", lambda event: self.destroy())

        self.settings = json.loads(open(os.path.join(base, "data", "settings.json"), 'r').read())
        self.apply_settings()

        # <a href="https://www.flaticon.com/free-icons/settings" title="settings icons">Settings icons created by See Icons - Flaticon</a>
        cog = Image.open(os.path.join(base, "data", "settings.png"))
        cog_ctk = ctk.CTkImage(cog, cog, size=(30, 30))
        self.settings_button = ctk.CTkButton(self, image=cog_ctk, text="", width=40, height=40, fg_color="transparent", command=lambda: SettingsPopup(self))
        self.settings_button.grid(row=0, column=2, padx=10, pady=10, sticky="ne")

        self.spacer = ctk.CTkFrame(self, width=40, height=40, fg_color="transparent")
        self.spacer.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        self.page = None
        self.show_page(LoginFrame(self))

    def apply_settings(self):
        ctk.set_appearance_mode(self.settings["theme"])
        ctk.set_default_color_theme(self.settings["color"])
        with open(os.path.join(base, "data", "settings.json"), 'w') as file:
            file.write(json.dumps(self.settings))

    def show_page(self, page):
        if self.page is not None:
            self.page.destroy()
        self.page = page
        self.page.configure(fg_color="transparent")
        page.grid(row=0, column=1, padx=10, pady=20, sticky="n")

    def login(self, username, password):
        if username not in get_users():
            self.page.warning.configure(text="User does not exist")
            return

        info = load_info(username, password)
        if info is None:
            self.page.warning.configure(text="Decryption error")
            return

        self.show_page(MainFrame(self, info))

    def register(self, username, password, repeat):
        if username == "" or username is None:
            self.page.warning.configure(text="Username must not be empty")
            return

        if password == "" or password is None:
            self.page.warning.configure(text="Password must not be empty")
            return

        if username in get_users():
            self.page.warning.configure(text="User already exists")
            return

        if password != repeat:
            self.page.warning.configure(text="Passwords do not match")
            return

        info = {"username":username, "password":password, "systems":{}}
        save_info(info)
        self.show_page(MainFrame(self, info))

class ReturnButton(ctk.CTkButton):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        if self.cget("command") != None:
            self.fg_hold = self.cget("fg_color")
            self.bind("<Return>", lambda event: self.cget("command")())
            self.bind("<FocusIn>", lambda event: self.configure(fg_color=self.cget("hover_color")))
            self.bind("<FocusOut>", lambda event: self.configure(fg_color=self.fg_hold))

class SettingsPopup(ctk.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("Settings")
        self.grid_columnconfigure((0, 1), weight=1)

        self.style_label = ctk.CTkLabel(self, text="Style", font=("Roboto", 24))
        self.style_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="w")

        self.style_frame = ctk.CTkFrame(self)
        self.style_frame.grid(row=1, column=0, columnspan=2, padx=10, sticky="new")

        self.theme_label = ctk.CTkLabel(self.style_frame, text="Theme:")
        self.theme_label.grid(row=0, column=0, padx=(20, 10), pady=10, sticky="w")

        self.theme = ctk.CTkOptionMenu(self.style_frame, values=["light", "dark"], command=lambda choice: master.settings.update({"theme": choice}))
        self.theme.set(master.settings["theme"])
        self.theme.grid(row=0, column=1, pady=10, sticky="e")

        self.color_label = ctk.CTkLabel(self.style_frame, text="Color:")
        self.color_label.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="w")

        self.color = ctk.CTkOptionMenu(self.style_frame, values=["blue", "dark-blue", "green"], command=lambda choice: master.settings.update({"color": choice}))
        self.color.set(master.settings["color"])
        self.color.grid(row=1, column=1, pady=10, sticky="e")

        self.apply_button = ReturnButton(self, text="Apply", command=master.apply_settings)
        self.apply_button.grid(row=2, column=0, padx=(10, 5), pady=10, sticky="ew")

        self.cancel_button = ReturnButton(self, text="Cancel", command=self.destroy)
        self.cancel_button.grid(row=2, column=1, padx=(5, 10), pady=10, sticky="ew")

        self.cve_label = ctk.CTkLabel(self, text="CVEs", font=("Roboto", 24))
        self.cve_label.grid(row=3, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="w")

        self.cve_button = ReturnButton(self, text="Update CVE database (takes a while)", command=update_cves)
        self.cve_button.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="ew")

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.configure(fg_color="transparent")

        self.title = ctk.CTkLabel(self, text="Login", font=("Roboto", 24))
        self.title.grid(row=0, column=0, sticky="ew", padx=10, pady=10, columnspan=2)

        self.username_label = ctk.CTkLabel(self, text="Username:")
        self.username_label.grid(row=1, column=0, sticky="w", padx=10, pady=(10, 0))
        self.username_entry = ctk.CTkEntry(self, width=200)
        self.username_entry.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 5), columnspan=2)

        self.password_label = ctk.CTkLabel(self, text="Password:")
        self.password_label.grid(row=3, column=0, sticky="w", padx=10, pady=(10, 0))
        self.password_entry = ctk.CTkEntry(self, show="*", width=200)
        self.password_entry.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 5), columnspan=2)

        login_lambda = lambda event=None: master.login(self.username_entry.get(), self.password_entry.get())
        self.username_entry.bind("<Return>", login_lambda)
        self.password_entry.bind("<Return>", login_lambda)

        self.login_button = ReturnButton(self, text="Login", command=login_lambda)
        self.login_button.grid(row=5, column=0, sticky="ew", padx=(10, 5), pady=20)

        self.register_button= ReturnButton(self, text="New user", command=lambda: app.show_page(RegisterFrame(master)))
        self.register_button.grid(row=5, column=1, sticky="ew", padx=(5, 10), pady=20)

        self.warning = ctk.CTkLabel(self, text="", text_color="red")
        self.warning.grid(row=6, column=0, sticky="ew", padx=10, pady=0, columnspan=2)

class RegisterFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.title = ctk.CTkLabel(self, text="Register", font=("Roboto", 24))
        self.title.grid(row=0, column=0, sticky="ew", padx=10, pady=20, columnspan=2)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=200)
        self.username_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=10, columnspan=2)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=200)
        self.password_entry.grid(row=2, column=0, sticky="ew", padx=10, pady=10, columnspan=2)

        self.repeat_entry = ctk.CTkEntry(self, placeholder_text="Repeat password", show="*", width=200)
        self.repeat_entry.grid(row=3, column=0, sticky="ew", padx=10, pady=10, columnspan=2)

        register_lambda = lambda event=None: master.register(self.username_entry.get(), self.password_entry.get(), self.repeat_entry.get())
        self.username_entry.bind("<Return>", register_lambda)
        self.password_entry.bind("<Return>", register_lambda)
        self.repeat_entry.bind("<Return>", register_lambda)

        self.register_button= ReturnButton(self, text="Register", command=register_lambda)
        self.register_button.grid(row=4, column=0, sticky="ew", padx=(10, 5), pady=(10, 0))

        self.login_button = ReturnButton(self, text="Return to login", command=lambda: app.show_page(LoginFrame(master)))
        self.login_button.grid(row=4, column=1, sticky="ew", padx=(5, 10), pady=(10, 0))

        self.warning = ctk.CTkLabel(self, text="", text_color="red")
        self.warning.grid(row=5, column=0, sticky="ew", padx=10, pady=10, columnspan=2)

class AddEditDeleteFrame(ctk.CTkScrollableFrame):
    class EditDeleteItem(ctk.CTkFrame):
        def __init__(self, master, name, display_popup, edit_popup, deleter, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.name = name
            self.grid_columnconfigure((0, 1, 2), weight=1)

            self.item = ReturnButton(self, text=name, anchor="w", border_spacing=10, command=lambda: display_popup(name), corner_radius=0)
            self.item.grid(row=0, column=0, padx=0, sticky="nesw")

            #<a href="https://www.flaticon.com/free-icons/ui" title="ui icons">Ui icons created by Ferdinand - Flaticon</a>
            pen = Image.open(os.path.join(base, "data", "edit.png"))
            pen_image = ctk.CTkImage(pen, pen, size=(30, 30))
            self.editor = ReturnButton(self, image=pen_image, text="", width=40, height=40, command=lambda: edit_popup(name, master.refresh), corner_radius=0)
            self.editor.grid(row=0, column=1, sticky="nesw")

            def delete():
                deleter(name)
                self.destroy()
            #<a href="https://www.flaticon.com/free-icons/delete" title="delete icons">Delete icons created by IYAHICON - Flaticon</a>
            trash = Image.open(os.path.join(base, "data", "trash.png"))
            trash_image = ctk.CTkImage(trash, trash, size=(25, 25))
            self.trasher = ReturnButton(self, image=trash_image, text="", width=40, height=40, command=delete, corner_radius=0)
            self.trasher.grid(row=0, column=2, sticky="nesw")

        def delete(self):
            self.master.state_dict.pop(self.name)
            self.destroy()

    def __init__(self, master, item_names, add_popup, display_popup, edit_popup, deleter, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.item_names = item_names
        self.add_popup = add_popup
        self.display_popup = display_popup
        self.edit_popup = edit_popup
        self.deleter = deleter
        self.refresh(item_names)

    def refresh(self, item_names):
        for widget in self.winfo_children():
            widget.destroy()
        self.adder = ReturnButton(self, text="Add new", height=40, command=lambda: self.add_popup(self.refresh), corner_radius=0)
        self.adder.grid(row=0, column=0, sticky="new", padx=10, pady=5)
        self.items = []
        for i, name in enumerate(sorted(item_names)):
            self.items.append(AddEditDeleteFrame.EditDeleteItem(self, name, self.display_popup, self.edit_popup, self.deleter))
            self.items[i].grid(row=i+1, column=0, sticky="new", padx=10, pady=5)

class CheckList(ctk.CTkScrollableFrame):
    def __init__(self, master, options, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.items = []
        if len(options) > 0:
            for i, option in enumerate(options):
                self.items.append(ctk.CTkCheckBox(self, text=option, on_value=1, off_value=0))
                self.items[i].grid(row=i, column=0, padx=10, pady=5)
        else:
            self.empty = ctk.CTkLabel(self, text="None to display")
            self.empty.grid(row=0, column=0, padx=10, pady=5)

    def get(self):
        return [item.cget("text") for item in self.items if self.item.get() == 1]

class HardwareFrame(ctk.CTkFrame):
    class AddPopup(ctk.CTkToplevel):
        def __init__(self, master, info, sysname, refresh, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.info = info
            self.sysname = sysname
            self.refresh = refresh

            self.name_label = ctk.CTkLabel(self, text="Name:", anchor="w")
            self.name_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.name_entry = ctk.CTkEntry(self)
            self.name_entry.bind("<Return>", lambda event: self.add())
            self.name_entry.grid(row=2, column=0, columnspan=2, sticky="new", padx=10, pady=0)

            self.description_label = ctk.CTkLabel(self, text="Description:", anchor="w")
            self.description_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.description_entry = ctk.CTkTextbox(self, border_width=2, border_color=("#a0a0a0", "#606060"))
            self.description_entry.grid(row=6, column=0, columnspan=2, sticky="new", padx=10, pady=0)

            self.vulnerabilities_label = ctk.CTkLabel(self, text="Vulnerabilities:", anchor="w")
            self.vulnerabilities_label.grid(row=7, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.vulnerabilities_checklist = CheckList(self, sorted(info["systems"][sysname]["hardware vulnerabilities"].keys()))
            self.vulnerabilities_checklist.grid(row=8, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.adder = ReturnButton(self, text="Add", command=self.add)
            self.adder.grid(row=9, column=0, sticky="new", padx=(10, 5), pady=5)

            self.cancel = ReturnButton(self, text="Cancel", command=self.destroy)
            self.cancel.grid(row=9, column=1, sticky="new", padx=(5, 10), pady=5)

            self.warning = ctk.CTkLabel(self, text="", text_color="red")
            self.warning.grid(row=10, column=0, columnspan=2, sticky="new", padx=10, pady=5)

        def add(self):
            if self.name_entry.get() == "":
                self.warning.configure(text="Must have non-empty name")
                return

            if self.name_entry.get() in self.info["systems"][self.sysname]["hardware"].keys():
                self.warning.configure(text=f"Hardware {self.name_entry.get()} already exists")
                return

            self.info["systems"][self.sysname]["hardware"][self.name_entry.get()] = {"description":  self.description_entry.get("0.0", "end"), "vulnerabilities":self.vulnerabilities_checklist.get()}
            self.refresh(self.info["systems"][self.sysname]["hardware"].keys())
            self.destroy()

    class DisplayPopup(ctk.CTkToplevel):
        def __init__(self, master, info, sysname, hardname, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.info = info
            self.sysname = sysname
            self.hardname = hardname

            self.name_label = ctk.CTkLabel(self, text="Name:", anchor="w")
            self.name_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.name_entry = ctk.CTkEntry(self)
            self.name_entry.insert(0, hardname)
            self.name_entry.configure(state="disabled")
            self.name_entry.grid(row=2, column=0, columnspan=2, sticky="new", padx=10, pady=0)

            self.description_label = ctk.CTkLabel(self, text="Description:", anchor="w")
            self.description_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.description_entry = ctk.CTkTextbox(self, border_width=2, border_color=("#a0a0a0", "#606060"))
            self.description_entry.insert("0.0", info["systems"][sysname]["hardware"][hardname]["description"])
            self.description_entry.configure(state="disabled")
            self.description_entry.grid(row=6, column=0, columnspan=2, sticky="new", padx=10, pady=0)

            self.vulnerabilities_label = ctk.CTkLabel(self, text="Vulnerabilities:", anchor="w")
            self.vulnerabilities_label.grid(row=7, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.vulnerabilities_checklist = CheckList(self, sorted(info["systems"][sysname]["hardware vulnerabilities"].keys()))
            for item in self.vulnerabilities_checklist.items:
                if item.cget("text") in info["systems"][sysname][hardname]["vulnerabilities"]:
                    item.select()
                item.configure(state="disabled")
            self.vulnerabilities_checklist.grid(row=8, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.close = ReturnButton(self, text="Close", command=self.destroy)
            self.close.grid(row=9, column=1, padx=10, pady=5)

    class EditPopup(ctk.CTkToplevel):
        def __init__(self, master, info, sysname, hardname, refresh, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.info = info
            self.sysname = sysname
            self.hardname = hardname
            self.refresh = refresh

            self.name_label = ctk.CTkLabel(self, text="Name:", anchor="w")
            self.name_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.name_entry = ctk.CTkEntry(self)
            self.name_entry.insert(0, hardname)
            self.name_entry.bind("<Return>", lambda event: self.edit())
            self.name_entry.grid(row=2, column=0, columnspan=2, sticky="new", padx=10, pady=0)

            self.description_label = ctk.CTkLabel(self, text="Description:", anchor="w")
            self.description_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.description_entry = ctk.CTkTextbox(self, border_width=2, border_color=("#a0a0a0", "#606060"))
            self.description_entry.insert("0.0", info["systems"][sysname]["hardware"][hardname]["description"])
            self.description_entry.grid(row=6, column=0, columnspan=2, sticky="new", padx=10, pady=0)

            self.vulnerabilities_label = ctk.CTkLabel(self, text="Vulnerabilities:", anchor="w")
            self.vulnerabilities_label.grid(row=7, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.vulnerabilities_checklist = CheckList(self, sorted(info["systems"][sysname]["hardware vulnerabilities"].keys()))
            for item in self.vulnerabilities_checklist.items:
                if item.cget("text") in info["systems"][sysname][hardname]["vulnerabilities"]:
                    item.select()
            self.vulnerabilities_checklist.grid(row=8, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.applier = ReturnButton(self, text="Apply", command=self.apply)
            self.applier.grid(row=9, column=0, sticky="new", padx=(10, 5), pady=5)

            self.cancel = ReturnButton(self, text="Cancel", command=self.destroy)
            self.cancel.grid(row=9, column=1, sticky="new", padx=(5, 10), pady=5)

            self.warning = ctk.CTkLabel(self, text="", text_color="red")
            self.warning.grid(row=10, column=0, columnspan=2, sticky="new", padx=10, pady=5)

        def apply(self):
            if self.name_entry.get() != self.hardname:
                if self.name_entry.get() == "":
                    self.warning.configure(text="Must have non-empty name")
                    return

                if self.name_entry.get() in self.info["systems"][self.sysname]["hardware"].keys():
                    self.warning.configure(text=f"Hardware {self.name_entry.get()} already exists")
                    return

            self.info["systems"][self.sysname]["hardware"][self.name_entry.get()] = {"description":  self.description_entry.get("0.0", "end"), "vulnerabilities":self.vulnerabilities_checklist.get()}

            if self.name_entry.get() != self.hardname:
                self.info["systems"][self.sysname]["hardware"].pop(self.hardname)
                for vulnerabilitiy in self.info["systems"][self.sysname]["hardware vulnerabilities"].keys():
                    if self.hardname in self.info["systems"][self.sysname]["hardware vulnerabilities"][vulnerability]["hardwares"]:
                        self.info["systems"][self.sysname]["hardware vulnerabilities"][vulnerability]["hardwares"].remove(self.hardname)
                        self.info["systems"][self.sysname]["hardware vulnerabilities"][vulnerability]["hardwares"].append(self.name_entry.get())
                for software in self.info["systems"][self.sysname]["software"].keys():
                    if self.hardname in self.info["systems"][self.sysname]["software"][software]["hardwares"]:
                        self.info["systems"][self.sysname]["software"][software]["hardwares"].remove(self.hardname)
                        self.info["systems"][self.sysname]["software"][software]["hardwares"].append(self.name_entry.get())
            self.refresh(self.info["systems"][self.sysname]["hardware"].keys())
            self.destroy()

    def delete(self, hardname):
        self.info["systems"][self.sysname]["hardware"].pop(hardname)
        for vulnerabilitiy in self.info["systems"][self.sysname]["hardware vulnerabilities"].keys():
            if hardname in self.info["systems"][self.sysname]["hardware vulnerabilities"][vulnerability]["hardwares"]:
                self.info["systems"][self.sysname]["hardware vulnerabilities"][vulnerability]["hardwares"].remove(hardname)
        for software in self.info["systems"][self.sysname]["software"].keys():
            if self.hardname in self.info["systems"][self.sysname]["software"][software]["hardwares"]:
                self.info["systems"][self.sysname]["software"][software]["hardwares"].remove(hardname)


    def __init__(self, master, info, sysname, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.info = info
        self.sysname = sysname

        self.hardware_label = ctk.CTkLabel(self, text="System hardware:", anchor="w")
        self.hardware_label.grid(row=0, column=0, sticky="nw", padx=10, pady=5)

        self.hardware_list = AddEditDeleteFrame(self, self.info["systems"][self.sysname]["hardware"].keys(),
                                                lambda refresh: HardwareFrame.AddPopup(self, info, sysname, refresh),
                                                lambda hardname: HardwareFrame.DisplayPopup(self, info, sysname, hardname),
                                                lambda hardname, refresh: HardwareFrame.EditPopup(self, info, sysname, hardname, refresh),
                                                lambda hardname: self.delete(hardname),
                                                fg_color="transparent")
        self.hardware_list.grid(row=1, column=0, sticky="nesw", padx=10, pady=5)

class SystemSettings(ctk.CTkFrame):
    def __init__(self, master, info, sysname, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.info = info
        self.sysname = sysname

        self.name_label = ctk.CTkLabel(self, text="Name:", anchor="w")
        self.name_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.bind("<Return>", lambda event: self.edit_system())
        self.name_entry.grid(row=2, column=0, columnspan=2, sticky="new", padx=10, pady=0)

        self.api_label = ctk.CTkLabel(self, text="OpenAI API key:", anchor="w")
        self.api_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

        self.api_entry= ctk.CTkEntry(self)
        self.api_entry.bind("<Return>", lambda event: self.edit_system())
        self.api_entry.grid(row=4, column=0, columnspan=2, sticky="new", padx=10, pady=0)

        self.description_label = ctk.CTkLabel(self, text="Description:", anchor="w")
        self.description_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

        self.description_entry = ctk.CTkTextbox(self, border_width=2, border_color=("#a0a0a0", "#606060"))
        self.description_entry.grid(row=6, column=0, columnspan=2, sticky="new", padx=10, pady=0)

        self.applier = ReturnButton(self, text="Apply", command=self.edit_system)
        self.applier.grid(row=7, column=0, sticky="new", padx=(10, 5), pady=5)

        self.cancel = ReturnButton(self, text="Cancel", command=self.reset)
        self.cancel.grid(row=7, column=1, sticky="new", padx=(5, 10), pady=5)

        self.deleter = ReturnButton(self, text="Delete System", fg_color="#ff0000", hover_color="#bb0000", command=lambda: SystemSettings.DeleteConfirmation(self, info, sysname))
        self.deleter.grid(row=8, column=0, columnspan=2, padx=10, pady=(5, 0), sticky="new")

        self.warning = ctk.CTkLabel(self, text="", text_color="red")
        self.warning.grid(row=9, column=0, columnspan=2, sticky="new", padx=10, pady=5)

        self.reset()

    class DeleteConfirmation(ctk.CTkToplevel):
        def __init__(self, master, info, sysname, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.info = info
            self.sysname = sysname

            self.confirmation1 = ctk.CTkLabel(self, text=f"Are you sure you want to delete system {sysname}?")
            self.confirmation1.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="new")

            self.confirmation2 = ctk.CTkLabel(self, text="This action cannot be undone.")
            self.confirmation2.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="new")

            self.confirm_button = ReturnButton(self, text="Confirm", fg_color="#ff0000", hover_color="#bb0000", command=self.delete)
            self.confirm_button.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="ew")

            self.cancel_button = ReturnButton(self, text="Cancel", command=self.destroy)
            self.cancel_button.grid(row=2, column=1, padx=(5, 10), pady=5, sticky="ew")

        def delete(self):
            self.info["systems"].pop(self.sysname)
            app.show_page(MainFrame(app, self.info))

    def reset(self):
        self.name_entry.delete(0, len(self.name_entry.get()))
        self.name_entry.insert(0, self.sysname)
        self.api_entry.delete(0, len(self.api_entry.get()))
        self.api_entry.insert(0, self.info["systems"][self.sysname]["api-key"])
        self.description_entry.delete("0.0", "end") 
        self.description_entry.insert("0.0", text=self.info["systems"][self.sysname]["description"])

    def edit_system(self):
        if self.name_entry.get() != self.sysname:
            if self.name_entry.get() == "":
                self.warning.configure(text="Name cannot be empty")
                return
            if self.name_entry.get() in self.info["systems"].keys():
                self.warning.configure(text=f"System with name {self.name_entry.get()} already exists")
                return
        old_sys = self.info["systems"][self.sysname]
        self.info["systems"][self.name_entry.get()] = {
            "description":  self.description_entry.get("0.0", "end"),
            "api-key": self.api_entry.get(),
            "hardware":old_sys["hardware"],
            "hardware vulnerabilities":old_sys["hardware vulnerabilities"],
            "software":old_sys["software"],
            "software vulnerabilities":old_sys["software vulnerabilities"],
            "functions":old_sys["functions"],
            "chats":old_sys["chats"],
        }
        if self.name_entry.get() != self.sysname:
            self.info["systems"].pop(self.sysname)
        app.show_page(SystemPage(app, self.info, self.name_entry.get()))


class SystemMenu(ctk.CTkTabview):
    def __init__(self, master, info, sysname, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.info = info
        self.sysname=sysname

        tabs = ["Hardware", "Software", "Functionality", "Analysis", "Settings"]
        for tab in tabs:
            self.add(tab)
        self.set(tabs[0])

        self.tab("Hardware").grid_columnconfigure(0, weight=1)
        self.hardwareFrame = HardwareFrame(self.tab("Hardware"), info, sysname)
        self.hardwareFrame.grid(row=0, column=0, sticky="nesw")
        self.systemSettings = SystemSettings(self.tab("Settings"), info, sysname)
        self.systemSettings.grid(row=0, column=0)

class SystemPage(ctk.CTkFrame):
    def __init__(self, master, info, sysname, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.info = info
        self.name = sysname

        self.name_label = ctk.CTkLabel(self, text=sysname, font=("Roboto", 24))
        self.name_label.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.description = ctk.CTkTextbox(self, fg_color="transparent",  height=80)
        self.description.insert("0.0", text=self.info["systems"][sysname]["description"])
        self.description.configure(state="disabled")
        self.description.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        self.menu = SystemMenu(self, self.info, sysname, fg_color="transparent")
        self.menu.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        self.returner = ReturnButton(self, text="Return", command=lambda: app.show_page(MainFrame(app, info)))
        self.returner.grid(row=3, column=0, padx=10, pady=5)

    def destroy(self):
        save_info(self.info)
        super().destroy()

class MainFrame(ctk.CTkFrame):
    class AddSystem(ctk.CTkToplevel):
        def __init__(self, master, info, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.info = info

            self.title = ctk.CTkLabel(self, text="New System", font=("Roboto", 24))
            self.title.grid(row=0, column=0, columnspan=2, sticky="new", padx=10, pady=10)

            self.name_label = ctk.CTkLabel(self, text="Name:", anchor="w")
            self.name_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.name_entry = ctk.CTkEntry(self)
            self.name_entry.bind("<Return>", lambda event: self.add_system())
            self.name_entry.grid(row=2, column=0, columnspan=2, sticky="new", padx=10, pady=0)

            self.api_label = ctk.CTkLabel(self, text="OpenAI API key:", anchor="w")
            self.api_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.api_entry= ctk.CTkEntry(self)
            self.api_entry.bind("<Return>", lambda event: self.add_system())
            self.api_entry.grid(row=4, column=0, columnspan=2, sticky="new", padx=10, pady=0)

            self.description_label = ctk.CTkLabel(self, text="Description:", anchor="w")
            self.description_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.description_entry = ctk.CTkTextbox(self, border_width=2, border_color=("#a0a0a0", "#606060"))
            self.description_entry.grid(row=6, column=0, columnspan=2, sticky="new", padx=10, pady=0)

            self.adder = ReturnButton(self, text="Add", command=self.add_system)
            self.adder.grid(row=7, column=0, sticky="new", padx=(10, 5), pady=(10, 0))

            self.cancel = ReturnButton(self, text="Cancel", command=self.destroy)
            self.cancel.grid(row=7, column=1, sticky="new", padx=(5, 10), pady=(10, 0))

            self.warning = ctk.CTkLabel(self, text="", text_color="red")
            self.warning.grid(row=8, column=0, columnspan=2, sticky="new", padx=10, pady=5)

        def add_system(self):
            if self.name_entry.get() == "":
                self.warning.configure(text="Must have non-empty name")
                return

            if self.name_entry.get() in self.info["systems"].keys():
                self.warning.configure(text=f"System {self.name_entry.get()} already exists")
                return

            self.info["systems"][self.name_entry.get()] = {"description":  self.description_entry.get("0.0", "end"), "api-key": self.api_entry.get(), "hardware":{}, "hardware vulnerabilities":{}, "software":{}, "software vulnerabilities":{}, "functions":{}, "chats":{}}
            app.show_page(SystemPage(app, self.info, self.name_entry.get()))


    class SystemsChoice(ctk.CTkScrollableFrame):
        def __init__(self, master, info, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.grid_columnconfigure(0, weight=1)

            def scroll(speed):
                try:
                    self._parent_canvas.yview("scroll", speed, "units")
                except:
                    pass

            self.bind_all("<Button-4>", lambda e: scroll(-1))
            self.bind_all("<Button-5>", lambda e: scroll(1))

            self.adder = ReturnButton(self, text="Add new", height=40, corner_radius=0, command=lambda: MainFrame.AddSystem(self, info))
            self.adder.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

            self.items = []
            for i, system in enumerate(sorted(info["systems"].keys())):
                self.items.append(ReturnButton(self, text=system, anchor="w", height=40, border_spacing=10, corner_radius=0, command=lambda system=system: app.show_page(SystemPage(app, info, system))))
                self.items[i].grid(row=i+1, column=0, sticky="ew", padx=10, pady=5)

    def __init__(self, master, info, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.info = info

        self.title = ctk.CTkLabel(self, text=f"Welcome {info['username']}", font=("Roboto", 24))
        self.title.grid(row=0, column=0, sticky="new", padx=10, pady=10)

        self.system_label = ctk.CTkLabel(self, text="Choose a system:")
        self.system_label.grid(row=3, column=0, sticky="nw", padx=10, pady=(20, 0))

        self.system_adder = MainFrame.SystemsChoice(self, info)
        self.system_adder.grid(row=4, column=0, sticky="new")
        self.system_adder.configure(width=self.system_adder.cget("width") + 40)

        self.return_button = ReturnButton(self, text="Logout", command=lambda: app.show_page(LoginFrame(master)))
        self.return_button.grid(row=5, column=0, padx=10, pady=10)

    def destroy(self):
        save_info(self.info)
        super().destroy()

app = App()

def main():
    app.mainloop()

if __name__ == "__main__":
    main()
