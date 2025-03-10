import os
import tkinter as tk
from tkinter import filedialog, ttk
from ttkwidgets import CheckboxTreeview
from PIL import Image, ImageTk

def toggle_check(event):
    item_id = tree.identify("item", event.x, event.y)
    current_image = tree.item(item_id, "image")
    new_image = checked_img if current_image == unchecked_img else unchecked_img
    tree.item(item_id, image=new_image)

def open_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        populate_tree(folder_path)

def populate_tree(folder_path):
    tree.delete(*tree.get_children())
    node = tree.insert("", "end", text=folder_path, open=True)
    process_directory(node, folder_path)

def process_directory(parent, path):
    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            node = tree.insert(parent, "end", text=item, open=False)
            process_directory(node, full_path)
        else:
            tree.insert(parent, "end", text=item)

def gather_checked_items(item_id, contents_list):
    image = tree.item(item_id, "image")
    if image == checked_img:
        full_path = get_full_path(item_id)
        try:
            with open(full_path, "r", encoding="utf-8") as file:
                contents_list.append(f"## {full_path} ##")
                contents_list.append(file.read())
        except UnicodeDecodeError:
            with open(full_path, "r", encoding="latin1") as file:
                contents_list.append(f"## {full_path} ##")
                contents_list.append(file.read())
    for child_id in tree.get_children(item_id):
        gather_checked_items(child_id, contents_list)

def get_full_path(item_id):
    path_parts = []
    while item_id:
        path_parts.insert(0, tree.item(item_id, "text"))
        item_id = tree.parent(item_id)
    return os.path.join(*path_parts)

def get_all_checked_items(tree):
    checked_items = []

    def recurse(item):
        if 'checked' in tree.item(item, 'tags'):
            checked_items.append(item)
        for child in tree.get_children(item):
            recurse(child)

    for root_item in tree.get_children():
        recurse(root_item)

    return checked_items

def copy_selected_to_clipboard():
    selected_items = get_all_checked_items(tree)
    if not selected_items:
        return

    clipboard_content = []

    for item_id in selected_items:
        full_path = get_full_path(item_id)
        if os.path.isfile(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as file:
                    file_content = file.read()
            except UnicodeDecodeError:
                with open(full_path, "r", encoding="latin1") as file:
                    file_content = file.read()

            # Add the file path and its content to the clipboard content
            clipboard_content.append(f"## {full_path} ##\n{file_content}")

    # Join all contents into a single string
    clipboard_text = "\n".join(clipboard_content)

    # Copy to clipboard
    root.clipboard_clear()
    root.clipboard_append(clipboard_text)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("File Tree Viewer")

    # Load images for checkbox states
    unchecked_img = ImageTk.PhotoImage(Image.open("unchecked.png"))
    checked_img = ImageTk.PhotoImage(Image.open("checked.png"))

    tree = CheckboxTreeview(root)
    tree.pack(fill="both", expand=True)

    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Open Folder", command=open_folder)
    filemenu.add_command(label="Copy Selected", command=copy_selected_to_clipboard)
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu=menubar)

    root.mainloop()