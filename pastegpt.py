import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, simpledialog
from ttkwidgets import CheckboxTreeview
from PIL import Image, ImageTk
import re

# File extension to language mapping for code highlighting
LANGUAGE_MAP = {
    '.py': 'python',
    '.js': 'javascript',
    '.html': 'html',
    '.css': 'css',
    '.java': 'java',
    '.c': 'c',
    '.cpp': 'cpp',
    '.h': 'cpp',
    '.cs': 'csharp',
    '.php': 'php',
    '.rb': 'ruby',
    '.go': 'go',
    '.ts': 'typescript',
    '.sh': 'bash',
    '.bat': 'batch',
    '.ps1': 'powershell',
    '.sql': 'sql',
    '.json': 'json',
    '.xml': 'xml',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.md': 'markdown',
    '.txt': 'text',
    '.csv': 'csv'
}

# Configuration constants
MAX_FILE_SIZE = 1024 * 1024  # 1MB default size limit

# Global variables
base_folder = ""  # Base folder path for relative path calculation

def get_full_path(item_id):
    path_parts = []
    current_id = item_id
    while current_id:
        path_parts.insert(0, tree.item(current_id, "text"))
        current_id = tree.parent(current_id)
    return os.path.join(*path_parts)

def get_relative_path(full_path):
    """Returns path relative to the base folder"""
    global base_folder
    if base_folder and full_path.startswith(base_folder):
        rel_path = os.path.relpath(full_path, base_folder)
        return rel_path if rel_path != '.' else os.path.basename(full_path)
    return full_path  # Return full path if can't make it relative

def open_folder():
    global base_folder
    folder_path = filedialog.askdirectory()
    if folder_path:
        base_folder = folder_path  # Set the base folder for relative paths
        populate_tree(folder_path)
        status_var.set(f"Folder opened: {os.path.basename(folder_path)}")
        root.title(f"PasteGPT - {os.path.basename(folder_path)}")

def populate_tree(folder_path):
    tree.delete(*tree.get_children())
    node = tree.insert("", "end", text=folder_path, open=True)
    process_directory(node, folder_path)

def process_directory(parent, path):
    try:
        items = sorted(os.listdir(path), key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
        for item in items:
            if item.startswith('.') and hide_hidden_var.get():
                continue
                
            full_path = os.path.join(path, item)
            try:
                if os.path.isdir(full_path):
                    node = tree.insert(parent, "end", text=item, open=False)
                    # Only if "load on click" option is disabled
                    if not lazy_load_var.get():
                        process_directory(node, full_path)
                else:
                    # Filter by extension if filter is active
                    extension = os.path.splitext(item)[1].lower()
                    if filter_pattern.get() and not re.search(filter_pattern.get(), extension):
                        continue
                    tree.insert(parent, "end", text=item)
            except PermissionError:
                tree.insert(parent, "end", text=f"{item} (Access denied)")
            except Exception as e:
                tree.insert(parent, "end", text=f"{item} (Error: {str(e)})")
    except PermissionError:
        status_var.set(f"Permission error on folder: {path}")
    except Exception as e:
        status_var.set(f"Error reading folder: {str(e)}")

def on_tree_open(event):
    # Handle lazy loading of folders
    if lazy_load_var.get():
        item_id = tree.focus()
        if tree.get_children(item_id) == () and tree.item(item_id, "open"):
            full_path = get_full_path(item_id)
            if os.path.isdir(full_path):
                process_directory(item_id, full_path)

def copy_selected_to_clipboard():
    checked_items = []
    for item in tree.get_children():
        collect_checked_items(item, checked_items)
    
    if not checked_items:
        status_var.set("No files selected")
        return

    clipboard_content = []
    file_count = 0
    binary_count = 0
    error_count = 0
    truncated_count = 0

    # Add header to help LLM understand the content
    clipboard_content.append("# Files for analysis\n")

    for item_id in checked_items:
        full_path = get_full_path(item_id)
        # Get relative path for display
        display_path = get_relative_path(full_path)
        
        if os.path.isfile(full_path):
            try:
                # Check if it's a binary file
                with open(full_path, "rb") as f:
                    first_chunk = f.read(1024)
                    is_binary = b'\0' in first_chunk
                
                if is_binary:
                    binary_count += 1
                    clipboard_content.append(f"## {display_path}\n*Binary file not included*")
                    continue
                
                # Get file size to check against limit
                file_size = os.path.getsize(full_path)
                is_truncated = file_size > MAX_FILE_SIZE
                
                # Try different encodings
                for encoding in ['utf-8', 'latin1', 'cp1252']:
                    try:
                        with open(full_path, "r", encoding=encoding) as file:
                            if is_truncated:
                                file_content = file.read(MAX_FILE_SIZE)
                                truncated_count += 1
                            else:
                                file_content = file.read()
                            
                            # Add line numbers to the content
                            numbered_lines = []
                            for i, line in enumerate(file_content.splitlines(), 1):
                                numbered_lines.append(f"{i}: {line}")
                            
                            numbered_content = "\n".join(numbered_lines)
                            
                            # Determine language for syntax highlighting
                            extension = os.path.splitext(full_path)[1].lower()
                            language = LANGUAGE_MAP.get(extension, '')
                            
                            # Format with markdown
                            header = f"## {display_path}"
                            if is_truncated:
                                header += f" (truncated, showing first {MAX_FILE_SIZE//1024}KB)"
                            
                            if language:
                                clipboard_content.append(f"{header}\n```{language}\n{numbered_content}\n```")
                            else:
                                clipboard_content.append(f"{header}\n```\n{numbered_content}\n```")
                            
                            file_count += 1
                            break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        error_count += 1
                        clipboard_content.append(f"## {display_path}\n*Error: {str(e)}*")
                        break
            except Exception as e:
                error_count += 1
                clipboard_content.append(f"## {display_path}\n*Error: {str(e)}*")

    # Join all contents into a single string
    clipboard_text = "\n\n".join(clipboard_content)

    # Copy to clipboard
    root.clipboard_clear()
    root.clipboard_append(clipboard_text)
    
    # Feedback to user
    status_message = f"Copied {file_count} files to clipboard"
    if binary_count > 0:
        status_message += f", {binary_count} binary files ignored"
    if truncated_count > 0:
        status_message += f", {truncated_count} files truncated"
    if error_count > 0:
        status_message += f", {error_count} errors"
    
    status_var.set(status_message)
    
    # If clipboard is too large, warn the user
    if len(clipboard_text) > 500000:
        messagebox.showwarning("Warning", f"The copied content is very large ({len(clipboard_text)/1000:.1f}KB). It may not be pasteable in some applications.")

def collect_checked_items(item_id, checked_items):
    if tree.tag_has('checked', item_id):
        checked_items.append(item_id)
    
    for child_id in tree.get_children(item_id):
        collect_checked_items(child_id, checked_items)

def set_filter():
    new_filter = simpledialog.askstring("Extension Filter", 
                                      "Enter a regex pattern to filter files (e.g., \\.py$|\\.txt$):",
                                      initialvalue=filter_pattern.get())
    if new_filter is not None:
        filter_pattern.set(new_filter)
        # Reload current folder if there is one
        if len(tree.get_children()) > 0:
            root_item = tree.get_children()[0]
            folder_path = tree.item(root_item, "text")
            populate_tree(folder_path)

def select_all():
    for item in tree.get_children():
        select_all_recursive(item)
    status_var.set("Selected all visible items")

def select_all_recursive(item):
    tree.change_state(item, "checked")
    for child in tree.get_children(item):
        select_all_recursive(child)

def deselect_all():
    for item in tree.get_children():
        deselect_all_recursive(item)
    status_var.set("Deselected all items")

def deselect_all_recursive(item):
    tree.change_state(item, "unchecked")
    for child in tree.get_children(item):
        deselect_all_recursive(child)

def set_max_file_size():
    """Allow user to set the maximum file size for copying"""
    global MAX_FILE_SIZE
    current_size = MAX_FILE_SIZE // 1024
    new_size = simpledialog.askinteger("Maximum File Size", 
                                     f"Enter maximum file size in KB (current: {current_size}KB):",
                                     initialvalue=current_size,
                                     minvalue=10,
                                     maxvalue=10000)
    if new_size:
        MAX_FILE_SIZE = new_size * 1024
        status_var.set(f"Maximum file size set to {new_size}KB")

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("PasteGPT")
    root.geometry("800x600")
    
    # Configuration variables
    filter_pattern = tk.StringVar(value="")
    hide_hidden_var = tk.BooleanVar(value=True)
    lazy_load_var = tk.BooleanVar(value=True)
    
    # Main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Treeview frame
    tree_frame = ttk.Frame(main_frame)
    tree_frame.pack(fill="both", expand=True)
    
    # Status bar
    status_var = tk.StringVar()
    status_var.set("Ready")
    status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # Load images for checkbox states (handling packaged resources)
    try:
        unchecked_path = resource_path("unchecked.png")
        checked_path = resource_path("checked.png")
        unchecked_img = ImageTk.PhotoImage(Image.open(unchecked_path))
        checked_img = ImageTk.PhotoImage(Image.open(checked_path))
    except Exception as e:
        messagebox.showerror("Error", f"Unable to load images: {str(e)}")
        sys.exit(1)

    # Create treeview with scrollbars
    tree = CheckboxTreeview(tree_frame)
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    tree.grid(column=0, row=0, sticky='nsew')
    vsb.grid(column=1, row=0, sticky='ns')
    hsb.grid(column=0, row=1, sticky='ew')
    
    tree_frame.grid_columnconfigure(0, weight=1)
    tree_frame.grid_rowconfigure(0, weight=1)
    
    # Lazy loading handler
    tree.bind("<<TreeviewOpen>>", on_tree_open)

    # Button frame
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x", pady=5)
    
    open_btn = ttk.Button(button_frame, text="Open Folder", command=open_folder)
    open_btn.pack(side="left", padx=5)
    
    copy_btn = ttk.Button(button_frame, text="Copy Selected", command=copy_selected_to_clipboard)
    copy_btn.pack(side="left", padx=5)
    
    filter_btn = ttk.Button(button_frame, text="Extension Filter", command=set_filter)
    filter_btn.pack(side="left", padx=5)
    
    select_all_btn = ttk.Button(button_frame, text="Select All", command=select_all)
    select_all_btn.pack(side="left", padx=5)
    
    deselect_all_btn = ttk.Button(button_frame, text="Deselect All", command=deselect_all)
    deselect_all_btn.pack(side="left", padx=5)

    # Option frame
    option_frame = ttk.Frame(main_frame)
    option_frame.pack(fill="x", pady=5)
    
    hide_hidden_check = ttk.Checkbutton(option_frame, text="Hide hidden files", variable=hide_hidden_var)
    hide_hidden_check.pack(side="left", padx=5)
    
    lazy_load_check = ttk.Checkbutton(option_frame, text="Load folder contents only when expanded", variable=lazy_load_var)
    lazy_load_check.pack(side="left", padx=5)

    # Menu
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Open Folder", command=open_folder, accelerator="Ctrl+O")
    filemenu.add_command(label="Copy Selected", command=copy_selected_to_clipboard, accelerator="Ctrl+C")
    filemenu.add_separator()
    filemenu.add_command(label="Extension Filter", command=set_filter)
    filemenu.add_command(label="Set Max File Size", command=set_max_file_size)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit, accelerator="Alt+F4")
    menubar.add_cascade(label="File", menu=filemenu)
    
    editmenu = tk.Menu(menubar, tearoff=0)
    editmenu.add_command(label="Select All", command=select_all, accelerator="Ctrl+A")
    editmenu.add_command(label="Deselect All", command=deselect_all, accelerator="Ctrl+D")
    menubar.add_cascade(label="Edit", menu=editmenu)
    
    helpmenu = tk.Menu(menubar, tearoff=0)
    helpmenu.add_command(label="About", command=lambda: messagebox.showinfo("About", "PasteGPT - Copy file contents to clipboard\nCreated to work more easily with ChatGPT and other LLMs"))
    menubar.add_cascade(label="Help", menu=helpmenu)
    
    root.config(menu=menubar)
    
    # Keyboard shortcuts
    root.bind("<Control-o>", lambda e: open_folder())
    root.bind("<Control-c>", lambda e: copy_selected_to_clipboard())
    root.bind("<Control-a>", lambda e: select_all())
    root.bind("<Control-d>", lambda e: deselect_all())
    
    # Start with a blank tree
    status_var.set("Ready - Select 'Open Folder' to start")
    
    root.mainloop()