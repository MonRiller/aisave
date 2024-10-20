import os, json
import customtkinter as ctk
from aisave import base
from aisave.crypto import load_info, save_info
from aisave.cve import update_cves, search_cves
from aisave.classic_analysis import sys_score
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
            self.grid_columnconfigure(0, weight=1)

            self.item = ReturnButton(self, text=name, anchor="w", border_spacing=10, command=lambda: display_popup(name), corner_radius=0)
            self.configure(fg_color=self.item.cget("fg_color"))
            self.item.grid(row=0, column=0, padx=0, sticky="nesw")

            #<a href="https://www.flaticon.com/free-icons/ui" title="ui icons">Ui icons created by Ferdinand - Flaticon</a>
            pen = Image.open(os.path.join(base, "data", "edit.png"))
            pen_image = ctk.CTkImage(pen, pen, size=(30, 30))
            self.editor = ReturnButton(self, image=pen_image, text="", width=40, height=40, command=lambda: edit_popup(name, master.refresh), corner_radius=0)
            self.editor.grid(row=0, column=1, sticky="nsw")

            def delete():
                deleter(name)
                self.destroy()
            #<a href="https://www.flaticon.com/free-icons/delete" title="delete icons">Delete icons created by IYAHICON - Flaticon</a>
            trash = Image.open(os.path.join(base, "data", "trash.png"))
            trash_image = ctk.CTkImage(trash, trash, size=(25, 25))
            self.trasher = ReturnButton(self, image=trash_image, text="", width=40, height=40, command=delete, corner_radius=0)
            self.trasher.grid(row=0, column=2, sticky="nsw")

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

        self.search_entry = ctk.CTkEntry(self, placeholder_text="search")
        self.search_entry.bind("<KeyRelease>", lambda event: self.search(self.search_entry.get()))
        self.search_entry.grid(row=0, column=0, sticky="new", padx=10, pady=10)
        self.items = []
        self.empty = ctk.CTkLabel(self, text="None to display")
        self.empty.grid(row=1, column=0, padx=10, pady=5)
        if len(options) > 0:
            self.empty.grid_remove()
            for i, option in enumerate(options):
                self.items.append(ctk.CTkCheckBox(self, text=option, onvalue=1, offvalue=0))
                self.items[i].grid(row=i+2, column=0, padx=10, pady=5, sticky="new")
        else:
            self.search_entry.grid_remove()

    def search(self, string):
        flag = True
        low_string = string.lower()
        for item in self.items:
            if low_string in item.cget("text").lower():
                item.grid()
                flag = False
            else:
                item.grid_remove()
        if flag:
            self.empty.grid()
        else:
            self.empty.grid_remove()

    def get(self):
        return [item.cget("text") for item in self.items if item.get() == 1]

class ComponentFrame(ctk.CTkFrame):
    class AddPopup(ctk.CTkToplevel):
        def __init__(self, master, info, sysname, refresh, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.grid_columnconfigure((0, 1), weight=1)
            self.info = info
            self.sysname = sysname
            self.refresh = refresh

            self.name_label = ctk.CTkLabel(self, text="Name:", anchor="w")
            self.name_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.name_entry = ctk.CTkEntry(self)
            self.name_entry.bind("<Return>", lambda event: self.add())
            self.name_entry.grid(row=1, column=0, columnspan=2, sticky="new", padx=10, pady=0)

            self.description_label = ctk.CTkLabel(self, text="Description:", anchor="w")
            self.description_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.description_entry = ctk.CTkTextbox(self, height=150, border_width=2, fg_color=self.name_entry.cget("fg_color"), border_color=("#a0a0a0", "#606060"))
            self.description_entry.grid(row=3, column=0, columnspan=2, sticky="nesw", padx=10, pady=0)

            self.dependency_label = ctk.CTkLabel(self, text="Direct dependencies:", anchor="w")
            self.dependency_label.grid(row=4, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.dependency_checklist = CheckList(self, sorted(info["systems"][sysname]["components"].keys()))
            self.dependency_checklist.grid(row=5, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.adder = ReturnButton(self, text="Add", command=self.add)
            self.adder.grid(row=6, column=0, sticky="new", padx=(10, 5), pady=5)

            self.close = ReturnButton(self, text="Close", command=self.destroy)
            self.close.grid(row=6, column=1, sticky="new", padx=(5, 10), pady=5)

            self.warning = ctk.CTkLabel(self, text="", text_color="red")
            self.warning.grid(row=7, column=0, columnspan=2, sticky="new", padx=10, pady=5)

        def add(self):
            if self.name_entry.get() == "":
                self.warning.configure(text="Must have non-empty name")
                return

            if self.name_entry.get() in self.info["systems"][self.sysname]["components"].keys():
                self.warning.configure(text=f"Component {self.name_entry.get()} already exists")
                return

            self.info["systems"][self.sysname]["components"][self.name_entry.get()] = {"description":  self.description_entry.get("0.0", "end"), "dependencies":self.dependency_checklist.get()}
            self.refresh(self.info["systems"][self.sysname]["components"].keys())

            self.name_entry.delete(0, len(self.name_entry.get()))
            self.description_entry.delete("0.0", "end")
            self.dependency_checklist.destroy()
            self.dependency_checklist = CheckList(self, sorted(self.info["systems"][self.sysname]["components"].keys()))
            self.dependency_checklist.grid(row=5, column=0, columnspan=2, sticky="new", padx=10, pady=5)
            self.warning.configure(text="")

    class DisplayPopup(ctk.CTkToplevel):
        def __init__(self, master, info, sysname, name, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.grid_columnconfigure(0, weight=1)
            self.info = info
            self.sysname = sysname
            self.name = name

            self.name_label = ctk.CTkLabel(self, text="Name:", anchor="w")
            self.name_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10,0))

            self.name_entry = ctk.CTkEntry(self)
            self.name_entry.insert(0, name)
            self.name_entry.configure(state="disabled")
            self.name_entry.grid(row=1, column=0, sticky="new", padx=10, pady=0)

            self.description_label = ctk.CTkLabel(self, text="Description:", anchor="w")
            self.description_label.grid(row=2, column=0, sticky="w", padx=10, pady=(10,0))

            self.description_entry = ctk.CTkTextbox(self, height=150, border_width=2, fg_color=self.name_entry.cget("fg_color"), border_color=("#a0a0a0", "#606060"))
            self.description_entry.insert("0.0", info["systems"][sysname]["components"][name]["description"])
            self.description_entry.configure(state="disabled")
            self.description_entry.grid(row=3, column=0, sticky="nesw", padx=10, pady=0)

            self.dependency_label = ctk.CTkLabel(self, text="Direct dependencies:", anchor="w")
            self.dependency_label.grid(row=4, column=0, sticky="new", padx=10, pady=5)

            self.dependency_checklist = CheckList(self, sorted([comp for comp in info["systems"][sysname]["components"].keys() if comp != name]))
            dependencies = info["systems"][sysname]["components"][name]["dependencies"]
            for item in self.dependency_checklist.items:
                if item.cget("text") in dependencies:
                    item.select()
                item.configure(state="disabled")
            self.dependency_checklist.grid(row=5, column=0, sticky="new", padx=10, pady=5)

            self.close = ReturnButton(self, text="Close", command=self.destroy)
            self.close.grid(row=6, column=0, padx=10, pady=5)

    class EditPopup(ctk.CTkToplevel):
        def __init__(self, master, info, sysname, name, refresh, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.grid_columnconfigure((0, 1), weight=1)
            self.info = info
            self.sysname = sysname
            self.name = name
            self.refresh = refresh

            self.name_label = ctk.CTkLabel(self, text="Name:", anchor="w")
            self.name_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.name_entry = ctk.CTkEntry(self)
            self.name_entry.insert(0, name)
            self.name_entry.bind("<Return>", lambda event: self.edit())
            self.name_entry.grid(row=1, column=0, columnspan=2, sticky="nesw", padx=10, pady=0)

            self.description_label = ctk.CTkLabel(self, text="Description:", anchor="w")
            self.description_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.description_entry = ctk.CTkTextbox(self, height=150, border_width=2, fg_color=self.name_entry.cget("fg_color"), border_color=("#a0a0a0", "#606060"))
            self.description_entry.insert("0.0", info["systems"][sysname]["components"][name]["description"])
            self.description_entry.grid(row=3, column=0, columnspan=2, sticky="nesw", padx=10, pady=0)

            self.dependency_label = ctk.CTkLabel(self, text="Direct dependencies:", anchor="w")
            self.dependency_label.grid(row=4, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.dependency_checklist = CheckList(self, sorted([comp for comp in self.info["systems"][sysname]["components"].keys() if comp != name]))
            dependencies = info["systems"][sysname]["components"][name]["dependencies"]
            for item in self.dependency_checklist.items:
                if item.cget("text") in dependencies:
                    item.select()
            self.dependency_checklist.grid(row=5, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.applier = ReturnButton(self, text="Apply", command=self.apply)
            self.applier.grid(row=6, column=0, sticky="new", padx=(10, 5), pady=5)

            self.cancel = ReturnButton(self, text="Cancel", command=self.destroy)
            self.cancel.grid(row=6, column=1, sticky="new", padx=(5, 10), pady=5)

            self.warning = ctk.CTkLabel(self, text="", text_color="red")
            self.warning.grid(row=7, column=0, columnspan=2, sticky="new", padx=10, pady=5)

        def apply(self):
            if self.name_entry.get() != self.name:
                if self.name_entry.get() == "":
                    self.warning.configure(text="Must have non-empty name")
                    return

                if self.name_entry.get() in self.info["systems"][self.sysname]["components"].keys():
                    self.warning.configure(text=f"Component {self.name_entry.get()} already exists")
                    return

            self.info["systems"][self.sysname]["components"][self.name_entry.get()] = {"description": self.description_entry.get("0.0", "end"), "dependencies":self.dependency_checklist.get()}

            if self.name_entry.get() != self.name:
                self.info["systems"][self.sysname]["components"].pop(self.name)
                for component in self.info["systems"][self.sysname]["components"].keys():
                    dependencies = self.info["systems"][self.sysname]["components"][component]["dependencies"]
                    if self.name in dependencies:
                        dependencies.remove(self.name)
                        dependencies.append(self.name_entry.get())

                for vulnerability in self.info["systems"][self.sysname]["vulnerabilities"].keys():
                    components = self.info["systems"][self.sysname]["vulnerabilities"][vulnerability]["components"]
                    if self.name in components:
                        components.remove(self.name)
                        components.append(self.name_entry.get())

                for functionality in self.info["systems"][self.sysname]["functionalities"].keys():
                    components = self.info["systems"][self.sysname]["functionalities"][functionality]["components"]
                    if self.name in components:
                        components.remove(self.name)
                        components.append(self.name_entry.get())

            self.refresh(self.info["systems"][self.sysname]["components"].keys())
            self.destroy()

    def delete(self, name):
        self.info["systems"][self.sysname]["components"].pop(name)
        for component in self.info["systems"][self.sysname]["components"].keys():
            dependencies = self.info["systems"][self.sysname]["components"][component]["dependencies"]
            if name in dependencies:
                dependencies.remove(name)

        for vulnerability in self.info["systems"][self.sysname]["vulnerabilities"].keys():
            components = self.info["systems"][self.sysname]["vulnerabilities"][vulnerability]["components"]
            if name in components:
                components.remove(name)

        for functionality in self.info["systems"][self.sysname]["functionalities"].keys():
            components = self.info["systems"][self.sysname]["functionalities"][functionality]["components"]
            if name in components:
                components.remove(name)

    def __init__(self, master, info, sysname, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.info = info
        self.sysname = sysname

        self.component_label= ctk.CTkLabel(self, text="System components:", anchor="w")
        self.component_label.grid(row=0, column=0, sticky="nw", padx=10, pady=5)

        self.component_list = AddEditDeleteFrame(self, self.info["systems"][self.sysname]["components"].keys(),
                                                lambda refresh: ComponentFrame.AddPopup(self, info, sysname, refresh),
                                                lambda name: ComponentFrame.DisplayPopup(self, info, sysname, name),
                                                lambda name, refresh: ComponentFrame.EditPopup(self, info, sysname, name, refresh),
                                                lambda name: self.delete(name),
                                                fg_color="transparent")
        self.component_list.grid(row=1, column=0, sticky="nesw", padx=10, pady=5)

class VulnerabilityFrame(ctk.CTkFrame):
    class AddPopup(ctk.CTkToplevel):
        class AddFrame(ctk.CTkFrame):
            def __init__(self, master, info, sysname, refresh, *args, **kwargs):
                super().__init__(master, *args, **kwargs)
                self.grid_columnconfigure((0, 1), weight=1)
                self.info = info
                self.sysname = sysname
                self.refresh = refresh

                self.name_label = ctk.CTkLabel(self, text="Name:", anchor="w")
                self.name_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

                self.name_entry = ctk.CTkEntry(self)
                self.name_entry.bind("<Return>", lambda event: self.add())
                self.name_entry.grid(row=1, column=0, columnspan=2, sticky="new", padx=10, pady=0)

                self.description_label = ctk.CTkLabel(self, text="Description:", anchor="w")
                self.description_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

                self.description_entry = ctk.CTkTextbox(self, height=150, border_width=2, fg_color=self.name_entry.cget("fg_color"), border_color=("#a0a0a0", "#606060"))
                self.description_entry.grid(row=3, column=0, columnspan=2, sticky="nesw", padx=10, pady=0)

                self.component_label = ctk.CTkLabel(self, text="Components:", anchor="w")
                self.component_label.grid(row=4, column=0, columnspan=2, sticky="new", padx=10, pady=5)

                self.component_checklist = CheckList(self, sorted(info["systems"][sysname]["components"].keys()))
                self.component_checklist.grid(row=5, column=0, columnspan=2, sticky="new", padx=10, pady=5)

                self.score_label = ctk.CTkLabel(self, text="", anchor="w")
                self.score_label.grid(row=6, column=0, columnspan=2, sticky="new", padx=10, pady=5)

                self.score_slider = ctk.CTkSlider(self, from_=0, to=10, number_of_steps=100, command=lambda score: self.score_label.configure(text=f"Risk rating: {score:.1f}"))
                self.score_slider.set(0)
                self.score_slider.grid(row=7, column=0, columnspan=2, sticky="new", padx=10, pady=5)

                self.score_label.configure(text=f"Risk rating: {self.score_slider.get():.1f}")

                self.adder = ReturnButton(self, text="Add", command=self.add)
                self.adder.grid(row=8, column=0, sticky="new", padx=(10, 5), pady=5)

                self.close = ReturnButton(self, text="Close", command=master.destroy)
                self.close.grid(row=8, column=1, sticky="new", padx=(5, 10), pady=5)

                self.warning = ctk.CTkLabel(self, text="", text_color="red")
                self.warning.grid(row=9, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            def add(self):
                if self.name_entry.get() == "":
                    self.warning.configure(text="Must have non-empty name")
                    return

                if self.name_entry.get() in self.info["systems"][self.sysname]["vulnerabilities"].keys():
                    self.warning.configure(text=f"Vulnerability {self.name_entry.get()} already exists")
                    return

                self.info["systems"][self.sysname]["vulnerabilities"][self.name_entry.get()] = {"description": self.description_entry.get("0.0", "end"), "components": self.component_checklist.get(), "score": self.score_slider.get()}

                self.refresh(self.info["systems"][self.sysname]["vulnerabilities"].keys())

                self.name_entry.delete(0, len(self.name_entry.get()))
                self.description_entry.delete("0.0", "end")
                self.component_checklist.destroy()
                self.component_checklist = CheckList(self, sorted(self.info["systems"][self.sysname]["components"].keys()))
                self.component_checklist.grid(row=5, column=0, columnspan=2, sticky="new", padx=10, pady=5)
                self.score_slider.set(0)
                self.score_label.configure(text=f"Risk rating: {self.score_slider.get():.1f}")
                self.warning.configure(text="")

        class SearchFrame(ctk.CTkFrame):
            def __init__(self, master, addFrame, *args, **kwargs):
                super().__init__(master, *args, **kwargs)
                self.grid_columnconfigure(0, weight=1)
                self.grid_rowconfigure(2, weight=1)
                self.addFrame = addFrame

                self.header = ctk.CTkLabel(self, text="CVE Database", font=("Roboto", 24))
                self.header.grid(row=0, column=0, columnspan=2, sticky="new", padx=20, pady=10)

                self.search_query = ctk.CTkEntry(self, placeholder_text="Search query", width=400)
                self.search_query.bind("<Return>", lambda event: self.search())
                self.search_query.grid(row=1, column=0, sticky="new", padx=(10, 5), pady=5)

                #<a href="https://www.flaticon.com/free-icons/search" title="search icons">Search icons created by Freepik - Flaticon</a>
                glass = Image.open(os.path.join(base, "data", "search.png"))
                glass_ctk = ctk.CTkImage(glass, glass, size=(20, 20))
                self.search_button = ctk.CTkButton(self, image=glass_ctk, text="", width=30, height=30, command=self.search)
                self.search_button.grid(row=1, column=1, padx=(5, 10), pady=5, sticky="ne")

                self.results_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
                self.results_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nesw")

                self.empty = ctk.CTkTextbox(self.results_frame, width=400, fg_color="transparent")
                self.empty.insert("0.0", "No results")
                self.empty.configure("disabled")
                self.empty.grid(row=0, column=0, sticky="new")

                self.results = []

            def search(self):
                for item in self.results:
                    item.destroy()
                self.results = []

                cves = search_cves(self.search_query.get())
                sort = sorted(cves.keys(), key=lambda k: cves[k], reverse=True)
                if len(sort) == 0:
                    self.empty.grid()
                    return

                self.empty.grid_remove()
                if len(sort) > 50:
                    sort = sort[:50]
                for i, cve in enumerate(sort):
                    self.results.append(ctk.CTkTextbox(self.results_frame, width=400))
                    self.results[i].insert("0.0", f"{cve[1]}\nRisk rating: {cve[3]}\n{cve[2]}")
                    self.results[i].configure(state="disabled")
                    self.results[i].bind("<Button-1>", lambda event, cve=cve: self.add(cve))
                    self.results[i].grid(row=i+1, column=0, padx=(0, 10), pady=5)

            def add(self, cve):
                self.addFrame.name_entry.delete(0, len(self.addFrame.name_entry.get()))
                self.addFrame.name_entry.insert(0, cve[1])
                self.addFrame.description_entry.delete("0.0", "end")
                self.addFrame.description_entry.insert("0.0", cve[2])
                self.addFrame.score_label.configure(text=f"Risk rating: {cve[3]:.1f}")
                self.addFrame.score_slider.set(float(cve[3]))

        def __init__(self, master, info, sysname, refresh, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.grid_columnconfigure((0, 1), weight=1)

            self.addFrame = VulnerabilityFrame.AddPopup.AddFrame(self, info, sysname, refresh)
            self.addFrame.grid(row=0, column=1, sticky="nesw", padx=10, pady=10)

            self.searchFrame = VulnerabilityFrame.AddPopup.SearchFrame(self, self.addFrame)
            self.searchFrame.grid(row=0, column=0, sticky="nesw", padx=10, pady=10)

    class DisplayPopup(ctk.CTkToplevel):
        def __init__(self, master, info, sysname, name, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.grid_columnconfigure(0, weight=1)
            self.info = info
            self.sysname = sysname
            self.name = name

            self.name_label = ctk.CTkLabel(self, text="Name:", anchor="w")
            self.name_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10,0))

            self.name_entry = ctk.CTkEntry(self)
            self.name_entry.insert(0, name)
            self.name_entry.configure(state="disabled")
            self.name_entry.grid(row=1, column=0, sticky="new", padx=10, pady=0)

            self.description_label = ctk.CTkLabel(self, text="Description:", anchor="w")
            self.description_label.grid(row=2, column=0, sticky="w", padx=10, pady=(10,0))

            self.description_entry = ctk.CTkTextbox(self, height=150, border_width=2, fg_color=self.name_entry.cget("fg_color"), border_color=("#a0a0a0", "#606060"))
            self.description_entry.insert("0.0", info["systems"][sysname]["vulnerabilities"][name]["description"])
            self.description_entry.configure(state="disabled")
            self.description_entry.grid(row=3, column=0, sticky="nesw", padx=10, pady=0)

            self.component_label = ctk.CTkLabel(self, text="Components:", anchor="w")
            self.component_label.grid(row=4, column=0, sticky="new", padx=10, pady=5)

            self.component_checklist = CheckList(self, sorted(info["systems"][sysname]["components"].keys()))
            components = info["systems"][sysname]["vulnerabilities"][self.name]["components"]
            for item in self.component_checklist.items:
                if item.cget("text") in components:
                    item.select()
                item.configure(state="disabled")
            self.component_checklist.grid(row=5, column=0, sticky="new", padx=10, pady=5)

            self.score_label = ctk.CTkLabel(self, text="", anchor="w")
            self.score_label.grid(row=6, column=0, sticky="new", padx=10, pady=5)

            self.score_slider = ctk.CTkSlider(self, from_=0, to=10, number_of_steps=100)
            self.score_slider.set(info["systems"][sysname]["vulnerabilities"][name]["score"])
            self.score_slider.configure(state="disabled")
            self.score_slider.grid(row=7, column=0, sticky="new", padx=10, pady=5)

            self.score_label.configure(text=f"Risk rating: {self.score_slider.get():.1f}")

            self.close = ReturnButton(self, text="Close", command=self.destroy)
            self.close.grid(row=8, column=0, padx=10, pady=5)

    class EditPopup(ctk.CTkToplevel):
        def __init__(self, master, info, sysname, name, refresh, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.grid_columnconfigure((0, 1), weight=1)
            self.info = info
            self.sysname = sysname
            self.name = name
            self.refresh = refresh

            self.name_label = ctk.CTkLabel(self, text="Name:", anchor="w")
            self.name_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.name_entry = ctk.CTkEntry(self)
            self.name_entry.insert(0, name)
            self.name_entry.bind("<Return>", lambda event: self.edit())
            self.name_entry.grid(row=1, column=0, columnspan=2, sticky="new", padx=10, pady=0)

            self.description_label = ctk.CTkLabel(self, text="Description:", anchor="w")
            self.description_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.description_entry = ctk.CTkTextbox(self, height=150, border_width=2, fg_color=self.name_entry.cget("fg_color"), border_color=("#a0a0a0", "#606060"))
            self.description_entry.insert("0.0", info["systems"][sysname]["vulnerabilities"][name]["description"])
            self.description_entry.grid(row=3, column=0, columnspan=2, sticky="nesw", padx=10, pady=0)

            self.component_label = ctk.CTkLabel(self, text="Components:", anchor="w")
            self.component_label.grid(row=4, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.component_checklist = CheckList(self, sorted(info["systems"][sysname]["components"].keys()))
            components = info["systems"][sysname]["vulnerabilities"][self.name]["components"]
            for item in self.component_checklist.items:
                if item.cget("text") in components:
                    item.select()
            self.component_checklist.grid(row=5, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.score_label = ctk.CTkLabel(self, text="", anchor="w")
            self.score_label.grid(row=6, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.score_slider = ctk.CTkSlider(self, from_=0, to=10, number_of_steps=100, command=lambda score: self.score_label.configure(text=f"Risk rating: {score:.1f}"))
            self.score_slider.set(info["systems"][sysname]["vulnerabilities"][name]["score"])
            self.score_slider.grid(row=7, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.score_label.configure(text=f"Risk rating: {self.score_slider.get():.1f}")

            self.applier = ReturnButton(self, text="Apply", command=self.apply)
            self.applier.grid(row=8, column=0, sticky="new", padx=(10, 5), pady=5)

            self.cancel = ReturnButton(self, text="Cancel", command=self.destroy)
            self.cancel.grid(row=8, column=1, sticky="new", padx=(5, 10), pady=5)

            self.warning = ctk.CTkLabel(self, text="", text_color="red")
            self.warning.grid(row=9, column=0, columnspan=2, sticky="new", padx=10, pady=5)

        def apply(self):
            if self.name_entry.get() != self.name:
                if self.name_entry.get() == "":
                    self.warning.configure(text="Must have non-empty name")
                    return

                if self.name_entry.get() in self.info["systems"][self.sysname]["vulnerabilities"].keys():
                    self.warning.configure(text=f"Vulnerability {self.name_entry.get()} already exists")
                    return

            self.info["systems"][self.sysname]["vulnerabilities"][self.name_entry.get()] = {"description": self.description_entry.get("0.0", "end"), "score": self.score_slider.get(), "components":self.component_checklist.get()}

            if self.name_entry.get() != self.name:
                self.info["systems"][self.sysname]["vulnerabilities"].pop(self.name)

            self.refresh(self.info["systems"][self.sysname]["vulnerabilities"].keys())
            self.destroy()

    def delete(self, name):
        self.info["systems"][self.sysname]["vulnerabilities"].pop(name)

    def __init__(self, master, info, sysname, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.info = info
        self.sysname = sysname

        self.vulnerability_label = ctk.CTkLabel(self, text="System vulnerabilities:", anchor="w")
        self.vulnerability_label.grid(row=0, column=0, sticky="nw", padx=10, pady=5)

        self.vulnerability_list = AddEditDeleteFrame(self, self.info["systems"][self.sysname]["vulnerabilities"].keys(),
                                                lambda refresh: VulnerabilityFrame.AddPopup(self, info, sysname, refresh),
                                                lambda name: VulnerabilityFrame.DisplayPopup(self, info, sysname, name),
                                                lambda name, refresh: VulnerabilityFrame.EditPopup(self, info, sysname, name, refresh),
                                                lambda name: self.delete(name),
                                                fg_color="transparent")
        self.vulnerability_list.grid(row=1, column=0, sticky="nesw", padx=10, pady=5)

class FunctionalityFrame(ctk.CTkFrame):
    class AddPopup(ctk.CTkToplevel):
        def __init__(self, master, info, sysname, refresh, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.info = info
            self.sysname = sysname
            self.refresh = refresh

            self.name_label = ctk.CTkLabel(self, text="Name:", anchor="w")
            self.name_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.name_entry = ctk.CTkEntry(self)
            self.name_entry.bind("<Return>", lambda event: self.add())
            self.name_entry.grid(row=1, column=0, columnspan=2, sticky="new", padx=10, pady=0)

            self.description_label = ctk.CTkLabel(self, text="Description:", anchor="w")
            self.description_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.description_entry = ctk.CTkTextbox(self, height=150, border_width=2, fg_color=self.name_entry.cget("fg_color"), border_color=("#a0a0a0", "#606060"))
            self.description_entry.grid(row=3, column=0, columnspan=2, sticky="new", padx=10, pady=0)

            self.component_label = ctk.CTkLabel(self, text="Direct dependencies:", anchor="w")
            self.component_label.grid(row=4, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.component_checklist = CheckList(self, sorted(info["systems"][sysname]["components"].keys()))
            self.component_checklist.grid(row=5, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.score_label = ctk.CTkLabel(self, text="", anchor="w")
            self.score_label.grid(row=6, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.score_slider = ctk.CTkSlider(self, from_=0, to=10, number_of_steps=100, command=lambda score: self.score_label.configure(text=f"Importance score: {score:.1f}"))
            self.score_slider.set(0)
            self.score_slider.grid(row=7, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.score_label.configure(text=f"Importance score: {self.score_slider.get():.1f}")

            self.adder = ReturnButton(self, text="Add", command=self.add)
            self.adder.grid(row=8, column=0, sticky="new", padx=(10, 5), pady=5)

            self.close = ReturnButton(self, text="Close", command=self.destroy)
            self.close.grid(row=8, column=1, sticky="new", padx=(5, 10), pady=5)

            self.warning = ctk.CTkLabel(self, text="", text_color="red")
            self.warning.grid(row=9, column=0, columnspan=2, sticky="new", padx=10, pady=5)

        def add(self):
            if self.name_entry.get() == "":
                self.warning.configure(text="Must have non-empty name")
                return

            if self.name_entry.get() in self.info["systems"][self.sysname]["functionalities"].keys():
                self.warning.configure(text=f"Functionality {self.name_entry.get()} already exists")
                return

            self.info["systems"][self.sysname]["functionalities"][self.name_entry.get()] = {"description": self.description_entry.get("0.0", "end"), "components": self.component_checklist.get(), "score": self.score_slider.get()}

            self.refresh(self.info["systems"][self.sysname]["functionalities"].keys())

            self.name_entry.delete(0, len(self.name_entry.get()))
            self.description_entry.delete("0.0", "end")
            self.component_checklist.destroy()
            self.component_checklist = CheckList(self, sorted(self.info["systems"][self.sysname]["components"].keys()))
            self.component_checklist.grid(row=5, column=0, columnspan=2, sticky="new", padx=10, pady=5)
            self.score_slider.set(0)
            self.score_label.configure(text=f"Importance score: {self.score_slider.get():.1f}")
            self.warning.configure(text="")

    class DisplayPopup(ctk.CTkToplevel):
        def __init__(self, master, info, sysname, name, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.info = info
            self.sysname = sysname
            self.name = name

            self.name_label = ctk.CTkLabel(self, text="Name:", anchor="w")
            self.name_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10,0))

            self.name_entry = ctk.CTkEntry(self)
            self.name_entry.insert(0, name)
            self.name_entry.configure(state="disabled")
            self.name_entry.grid(row=1, column=0, sticky="new", padx=10, pady=0)

            self.description_label = ctk.CTkLabel(self, text="Description:", anchor="w")
            self.description_label.grid(row=2, column=0, sticky="w", padx=10, pady=(10,0))

            self.description_entry = ctk.CTkTextbox(self, height=150, border_width=2, fg_color=self.name_entry.cget("fg_color"), border_color=("#a0a0a0", "#606060"))
            self.description_entry.insert("0.0", info["systems"][sysname]["functionalities"][name]["description"])
            self.description_entry.configure(state="disabled")
            self.description_entry.grid(row=3, column=0, sticky="new", padx=10, pady=0)

            self.component_label = ctk.CTkLabel(self, text="Direct dependencies:", anchor="w")
            self.component_label.grid(row=4, column=0, sticky="new", padx=10, pady=5)

            self.component_checklist = CheckList(self, sorted(info["systems"][sysname]["components"].keys()))
            components = info["systems"][sysname]["functionalities"][self.name]["components"]
            for item in self.component_checklist.items:
                if item.cget("text") in components:
                    item.select()
                item.configure(state="disabled")
            self.component_checklist.grid(row=5, column=0, sticky="new", padx=10, pady=5)

            self.score_label = ctk.CTkLabel(self, text="", anchor="w")
            self.score_label.grid(row=6, column=0, sticky="new", padx=10, pady=5)

            self.score_slider = ctk.CTkSlider(self, from_=0, to=10, number_of_steps=100)
            self.score_slider.set(info["systems"][sysname]["functionalities"][name]["score"])
            self.score_slider.configure(state="disabled")
            self.score_slider.grid(row=7, column=0, sticky="new", padx=10, pady=5)

            self.score_label.configure(text=f"Importance score: {self.score_slider.get():.1f}")

            self.close = ReturnButton(self, text="Close", command=self.destroy)
            self.close.grid(row=8, column=0, padx=10, pady=5)

    class EditPopup(ctk.CTkToplevel):
        def __init__(self, master, info, sysname, name, refresh, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.info = info
            self.sysname = sysname
            self.name = name
            self.refresh = refresh

            self.name_label = ctk.CTkLabel(self, text="Name:", anchor="w")
            self.name_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.name_entry = ctk.CTkEntry(self)
            self.name_entry.insert(0, name)
            self.name_entry.bind("<Return>", lambda event: self.edit())
            self.name_entry.grid(row=1, column=0, columnspan=2, sticky="new", padx=10, pady=0)

            self.description_label = ctk.CTkLabel(self, text="Description:", anchor="w")
            self.description_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))

            self.description_entry = ctk.CTkTextbox(self, height=150, border_width=2, fg_color=self.name_entry.cget("fg_color"), border_color=("#a0a0a0", "#606060"))
            self.description_entry.insert("0.0", info["systems"][sysname]["functionalities"][name]["description"])
            self.description_entry.grid(row=3, column=0, columnspan=2, sticky="new", padx=10, pady=0)

            self.component_label = ctk.CTkLabel(self, text="Direct dependencies:", anchor="w")
            self.component_label.grid(row=4, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.component_checklist = CheckList(self, sorted(info["systems"][sysname]["components"].keys()))
            components = info["systems"][sysname]["functionalities"][self.name]["components"]
            for item in self.component_checklist.items:
                if item.cget("text") in components:
                    item.select()
            self.component_checklist.grid(row=5, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.score_label = ctk.CTkLabel(self, text="", anchor="w")
            self.score_label.grid(row=6, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.score_slider = ctk.CTkSlider(self, from_=0, to=10, number_of_steps=100, command=lambda score: self.score_label.configure(text=f"Importance score: {score:.1f}"))
            self.score_slider.set(info["systems"][sysname]["functionalities"][name]["score"])
            self.score_slider.grid(row=7, column=0, columnspan=2, sticky="new", padx=10, pady=5)

            self.score_label.configure(text=f"Importance score: {self.score_slider.get():.1f}")

            self.applier = ReturnButton(self, text="Apply", command=self.apply)
            self.applier.grid(row=8, column=0, sticky="new", padx=(10, 5), pady=5)

            self.cancel = ReturnButton(self, text="Cancel", command=self.destroy)
            self.cancel.grid(row=8, column=1, sticky="new", padx=(5, 10), pady=5)

            self.warning = ctk.CTkLabel(self, text="", text_color="red")
            self.warning.grid(row=9, column=0, columnspan=2, sticky="new", padx=10, pady=5)

        def apply(self):
            if self.name_entry.get() != self.name:
                if self.name_entry.get() == "":
                    self.warning.configure(text="Must have non-empty name")
                    return

                if self.name_entry.get() in self.info["systems"][self.sysname]["functionalities"].keys():
                    self.warning.configure(text=f"Functionality {self.name_entry.get()} already exists")
                    return

            self.info["systems"][self.sysname]["functionalities"][self.name_entry.get()] = {"description": self.description_entry.get("0.0", "end"), "score": self.score_slider.get(), "components":self.component_checklist.get()}

            if self.name_entry.get() != self.name:
                self.info["systems"][self.sysname]["functionalities"].pop(self.name)

            self.refresh(self.info["systems"][self.sysname]["functionalities"].keys())
            self.destroy()

    def delete(self, name):
        self.info["systems"][self.sysname]["functionalities"].pop(name)

    def __init__(self, master, info, sysname, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.info = info
        self.sysname = sysname

        self.functionality_label = ctk.CTkLabel(self, text="System functionalities:", anchor="w")
        self.functionality_label.grid(row=0, column=0, sticky="nw", padx=10, pady=5)

        self.functionality_list = AddEditDeleteFrame(self, self.info["systems"][self.sysname]["functionalities"].keys(),
                                                lambda refresh: FunctionalityFrame.AddPopup(self, info, sysname, refresh),
                                                lambda name: FunctionalityFrame.DisplayPopup(self, info, sysname, name),
                                                lambda name, refresh: FunctionalityFrame.EditPopup(self, info, sysname, name, refresh),
                                                lambda name: self.delete(name),
                                                fg_color="transparent")
        self.functionality_list.grid(row=1, column=0, sticky="nesw", padx=10, pady=5)

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

        self.description_entry = ctk.CTkTextbox(self, height=150, border_width=2, fg_color=self.name_entry.cget("fg_color"), border_color=("#a0a0a0", "#606060"))
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
        self.info["systems"][self.name_entry.get()] = self.info["systems"][self.sysname]
        self.info["systems"][self.name_entry.get()].update({
            "description":  self.description_entry.get("0.0", "end"),
            "api-key": self.api_entry.get(),
        })
        if self.name_entry.get() != self.sysname:
            self.info["systems"].pop(self.sysname)
        app.show_page(SystemPage(app, self.info, self.name_entry.get()))

class AnalysisFrame(ctk.CTkScrollableFrame):
    class OrderedFrame(ctk.CTkScrollableFrame):
        def __init__(self, master, label, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.grid_columnconfigure((0, 1), weight=1)
            self.label = label

            self.empty = ctk.CTkLabel(self, text="No vulnerabilities to show")
            self.empty.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="new")

            self.items = []
            self.significances = []

        def refresh(self, dictionary):
            for item in self.items:
                item.destroy()

            for significance in self.significances:
                significance.destroy()

            if len(dictionary.keys()) == 0:
                self.empty.grid()
                return

            self.empty.grid_remove()
            ordered_keys = sorted(dictionary.keys(), key=lambda k: dictionary[k], reverse=True)
            for i, key in enumerate(ordered_keys):
                item = ctk.CTkLabel(self, text=key, anchor="w")
                item.grid(row=i + 1, column=0, padx=10, pady=5, sticky="new")
                self.items.append(item)
                significance = ctk.CTkLabel(self, text=f"{self.label}: {dictionary[key]:.1f}", anchor="w")
                significance.grid(row=i + 1, column=1, padx=10, pady=5, sticky="new")
                self.significances.append(significance)

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.configure(height=400)

        self.score = ctk.CTkLabel(self, text="Security score: 0.0%", font=("Roboto", 24))
        self.score.grid(row=0, column=0, sticky="new", padx=20, pady=10)

        self.vulns_label = ctk.CTkLabel(self, text="Vulnerabilities ranked by significance", font=("Roboto", 20))
        self.vulns_label.grid(row=1, column=0, sticky="new", padx=10, pady=5)

        self.vulns = AnalysisFrame.OrderedFrame(self, "Significance")
        self.vulns.grid(row=2, column=0, sticky="new", padx=10, pady=5)

        self.components_label = ctk.CTkLabel(self, text="Components ranked by vulnerability", font=("Roboto", 20))
        self.components_label.grid(row=3, column=0, sticky="new", padx=10, pady=5)

        self.components = AnalysisFrame.OrderedFrame(self, "Component vulnerability")
        self.components.grid(row=4, column=0, sticky="new", padx=10, pady=5)

        self.functionalities_label = ctk.CTkLabel(self, text="Functionalities ranked by vulnerability", font=("Roboto", 20))
        self.functionalities_label.grid(row=5, column=0, sticky="new", padx=10, pady=5)

        self.functionalities = AnalysisFrame.OrderedFrame(self, "Functionality vulnerability")
        self.functionalities.grid(row=6, column=0, sticky="new", padx=10, pady=5)

    def refresh(self, sysinfo):
        score, component_scores, functionality_scores = sys_score(sysinfo)
        self.score.configure(text=f"Security score: {score * 100:.1f}%")

        vulnerability_significance = {}
        vulnerabilities = list(sysinfo["vulnerabilities"].keys())
        for vulnerability in vulnerabilities:
            vuln_obj = sysinfo["vulnerabilities"].pop(vulnerability)
            tmp_score, _, _ = sys_score(sysinfo)
            vulnerability_significance[vulnerability] = (tmp_score - score) * 100
            sysinfo["vulnerabilities"][vulnerability] = vuln_obj
        self.vulns.refresh(vulnerability_significance)
        self.components.refresh(component_scores)
        self.functionalities.refresh(functionality_scores)

class SystemMenu(ctk.CTkTabview):
    def __init__(self, master, info, sysname, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.info = info
        self.sysname=sysname

        tabs = ["Components", "Vulnerabilities", "Functionalities", "Analysis", "AI Chat", "Settings"]
        for tab in tabs:
            self.add(tab)
            self.tab(tab).grid_columnconfigure(0, weight=1)
        self.set(tabs[0])

        self.componentFrame= ComponentFrame(self.tab("Components"), info, sysname)
        self.componentFrame.grid(row=0, column=0, sticky="nesw")

        self.vulnerabilityFrame = VulnerabilityFrame(self.tab("Vulnerabilities"), info, sysname)
        self.vulnerabilityFrame.grid(row=0, column=0, sticky="nesw")

        self.functionalityFrame= FunctionalityFrame(self.tab("Functionalities"), info, sysname)
        self.functionalityFrame.grid(row=0, column=0, sticky="nesw")

        self.analysisFrame = AnalysisFrame(self.tab("Analysis"))
        self.analysisFrame.grid(row=0, column=0, sticky="nesw")
        self.configure(command=lambda: self.analysisFrame.refresh(self.info["systems"][self.sysname]))

        self.systemSettings = SystemSettings(self.tab("Settings"), info, sysname)
        self.systemSettings.grid(row=0, column=0, )

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

            self.description_entry = ctk.CTkTextbox(self, height=150, border_width=2, fg_color=self.name_entry.cget("fg_color"), border_color=("#a0a0a0", "#606060"))
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

            self.info["systems"][self.name_entry.get()] = {"description":  self.description_entry.get("0.0", "end"), "api-key": self.api_entry.get(), "components":{}, "vulnerabilities":{}, "functionalities":{}, "chats":{}}
            app.show_page(SystemPage(app, self.info, self.name_entry.get()))


    class SystemsChoice(ctk.CTkScrollableFrame):
        def __init__(self, master, info, *args, **kwargs):
            super().__init__(master, *args, **kwargs)
            self.grid_columnconfigure(0, weight=1)

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
