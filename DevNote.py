import os
import time
import tkinter as tk
import datetime
from tkinter import messagebox
import shutil
import re
import webbrowser

#import subprocess
#DETACHED_PROCESS = 0x00000008
#subprocess.Popen(["pythonw", "NewDevNote.pyw"], creationflags=DETACHED_PROCESS, close_fds=True)

bkcolor = [ 'black', 'black', 'black', 'black', 'black', 'black', 'black', 'black', 'black' ]
fgcolor = [ 'white', 'chartreuse', 'brown1', 'gold', 'cyan', 'rosybrown', 'cornsilk', 'orange', 'greenyellow' ]

os.environ["TK_SILENCE_DEPRECATION"] = "1"

class TextBlock:
    def __init__(self, master, idx, save_dir):
        self.idx = idx
        self.frame = tk.Frame(master, bg='black', bd=1, relief='solid')
        self.frame.pack(side='left', fill='both', expand=True)
        self.y_scrollbar = tk.Scrollbar(self.frame, orient='vertical', bg='white', activebackground='gray')
        self.y_scrollbar.pack(side='right', fill='y')
        self.x_scrollbar = tk.Scrollbar(self.frame, orient='horizontal', bg='white', activebackground='gray')
        self.x_scrollbar.pack(side='bottom', fill='x')
        self.text = tk.Text(self.frame, wrap='none', xscrollcommand=self.x_scrollbar.set, yscrollcommand=self.y_scrollbar.set, bg=bkcolor[idx], fg=fgcolor[idx], font=('Consolas', 13), undo=True)
        self.text.pack(side='left', fill='both', expand=True)
        self.x_scrollbar.config(command=self.text.xview)
        self.y_scrollbar.config(command=self.text.yview)
        self.text.insert('end', f'{idx}')
        self.text.config(self.text.config(insertontime=500, insertwidth=1, insertofftime=250, insertbackground=fgcolor[idx],cursor='xterm'))
        self.filepath = os.path.join(save_dir, f'Dev_Note_{idx}.txt')
        self.load_text()
        self.text.bind("<Control-z>", self.undo)
        self.text.bind("<Control-y>", self.redo)

        # bind right mouse button
        self.text.bind("<Button-3>", self.show_popup_menu)
        self.selected_text = ''

    def show_popup_menu(self, event):
        self.selected_text = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)

        popup_menu = tk.Menu(self.text, tearoff=0)
        popup_menu.add_command(label="Cut", accelerator="Ctrl+X", command=self.cut)
        popup_menu.add_command(label="Copy", accelerator="Ctrl+C", command=self.copy)
        popup_menu.add_command(label="Paste", accelerator="Ctrl+V", command=self.paste)
        popup_menu.add_separator()
        if self.is_url(self.selected_text):
            popup_menu.add_command(label="Open in Browser", command=self.open_url)
        popup_menu.tk_popup(event.x_root, event.y_root)

        self.text.focus_set()

    def cut(self, event=None):
        self.text.event_generate("<<Cut>>")

    def copy(self, event=None):
        self.text.event_generate("<<Copy>>")

    def paste(self, event=None):
        self.text.event_generate("<<Paste>>")

    def open_url(self, event=None):
        webbrowser.open(self.selected_text)

    def is_url(self, text):
        # regex pattern to match url
        pattern = re.compile(
            r'(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+'
        )
        if pattern.match(text):
            return True
        else:
            return False

    def show_menu(self, event):
        """Shows the context menu"""
        try:
            self.text.tag_remove("sel", "1.0", "end")
            self.text.tag_add("sel", "insert")
        except tk.TclError:
            pass

        if self.is_link_selected():
            self.menu.entryconfigure("用瀏覽器開啟", state="normal")
        else:
            self.menu.entryconfigure("用瀏覽器開啟", state="disabled")

        self.menu.tk_popup(event.x_root, event.y_root)

    def is_link_selected(self):
        """Returns True if a link is selected"""
        tags = self.text.tag_names("sel.first")
        return "url" in tags

    def open_link_in_browser(self):
        """Opens the selected link in the default browser"""
        sel = self.text.get("sel.first", "sel.last")
        if self.is_link_selected() and sel.startswith("http"):
            webbrowser.open(sel)

    def save_text(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write(self.text.get('1.0', 'end'))
            f.close()

    def load_text(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                f.close()
        except FileNotFoundError:
            text = f'TextBlock {self.idx}'
        self.text.delete('1.0', 'end')
        self.text.insert('end', text)
        self.text.edit_reset()

    def undo():
        try:
            self.text.edit_undo()
        except:
            pass

    def redo():
        try:
            self.text.edit_redo()
        except:
            pass

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.iconbitmap('./devnote/fdg.ico')
        self.root.geometry('1440x800')
        self.root.config(bg='black')
        self.root.title("Alex's DevNote")

        self.menu = tk.Menu(self.root, tearoff=0)
        self.root.config(menu=self.menu)
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open Note Dir", command=self.open_file_explorer)
        self.file_menu.add_command(label="Open Backup Dir", command=self.open_backup_dir)
        self.file_menu.add_command(label="Save All", command=self.save_all_text)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        #self.edit_menu = tk.Menu(self.menu, tearoff=0)
        #self.menu.add_cascade(label="Edit", menu=self.edit_menu)
        #self.edit_menu.add_command(label="Undo", command=self.open_file_explorer)

        self.save_dir = './devnote'
        self.backup_dir = self.save_dir + '/backup'
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        self.text_blocks = []
        self.enable_9 = True
        for i in range(3):
            for j in range(3):
                if self.enable_9:
                    idx = j * 3 + i
                    text_block = TextBlock(self.root, idx, self.save_dir)
                    text_block.frame.place(relx=i/3, rely=j/3, relwidth=1/3, relheight=1/3)
                else:
                    if (i == 2 and j == 2) or (i == 1 and j == 2):
                        continue
                    idx = j * 3 + i
                    text_block = TextBlock(self.root, idx, self.save_dir)
                    if i == 0 and j == 2:
                        text_block.frame.place(relx=i/3, rely=j/3, relwidth=1, relheight=1/3)
                    else:
                        text_block.frame.place(relx=i/3, rely=j/3, relwidth=1/3, relheight=1/3)
                self.text_blocks.append(text_block)

        for scrollbar in (self.root.winfo_children()[2], self.root.winfo_children()[3]):
            scrollbar.config(width=5)

        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.save_interval = 60  # 儲存間隔時間（秒）
        self.last_save_time = time.time()  # 上次儲存時間
        self.root.after(1000, self.check_save)

    def open_file_explorer(self):
        os.startfile(os.path.abspath(self.save_dir))

    def open_backup_dir(self):
        os.startfile(os.path.abspath(self.backup_dir))
		
    def check_save(self):
        now = time.time()
        if now - self.last_save_time >= self.save_interval:
            self.save_all_text()
            self.last_save_time = now
            self.update_title()
        self.root.after(1000, self.check_save)

    def save_all_text_manual(self, event=None):
        for text_block in self.text_blocks:
            text_block.save_text()

    def save_all_text(self):
        # backup old file to backup/runtime
        runtime_backup_dir = self.backup_dir + "/runtime"
        if not os.path.exists(runtime_backup_dir):
            os.makedirs(runtime_backup_dir)
        src_dir = self.save_dir
        dst_dir = runtime_backup_dir
        for file in os.listdir(src_dir):
            src_file_path = os.path.join(src_dir, file)
            dst_file_path = os.path.join(dst_dir, file)
            if os.path.isfile(src_file_path):
                shutil.copy(src_file_path, dst_file_path)

        # save txt files
        for text_block in self.text_blocks:
            text_block.save_text()

        # backup every 5 minutes and keep 2 days
        now = datetime.datetime.now()
        today = now.strftime('%Y.%m.%d')
        time =  now.strftime('%Y%m%d-%H%M')
        minute = now.strftime('%M')
        new_backup = self.backup_dir + '/' + today + '/' + time
        if int(minute) % 5 == 0:
            os.makedirs(new_backup)
            src_dir = self.save_dir
            dst_dir = new_backup
            for file in os.listdir(src_dir):
                src_file_path = os.path.join(src_dir, file)
                dst_file_path = os.path.join(dst_dir, file)
                if os.path.isfile(src_file_path):
                    shutil.copy(src_file_path, dst_file_path)
            last2day = (now-datetime.timedelta(hours=48)).strftime('%Y.%m.%d')
            remove_path = self.backup_dir + '/' + last2day
            if os.path.exists(remove_path):
                shutil.rmtree(remove_path)

    def update_title(self):
        now = time.strftime('%Y.%m.%d %H:%M')
        self.root.title(f"Alex's DevNote - saved at {now}")

    def on_closing(self):
        result = messagebox.askyesnocancel("Save", "Do you save note file before exit?")
        if result is not None:
            if result:
                self.save_all_text()
            self.root.destroy()

if __name__ == '__main__':
    app = App()
    app.root.mainloop()
