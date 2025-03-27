# PasteGPT

Desktop application that allows users to select files within a folder structure and copy their contents to the clipboard, facilitating sharing with ChatGPT or other Large Language Models.

![Screenshot](screenshot.png)

## Features

- Visual navigation of folder structure
- Multiple file selection via checkboxes
- Automatic clipboard copy with LLM-optimized format
- Support for text files in various encodings (UTF-8, Latin-1, CP1252)
- Automatic detection of binary files
- File type filtering using regular expressions
- Lazy loading of folders to improve performance
- Customizable display options
- Keyboard shortcuts for common operations
- Detailed operation feedback
- Markdown-formatted output with syntax highlighting
- Automatic language detection for better code formatting
- Large file truncation to prevent clipboard issues

## Installation

### Prerequisites

- Python 3.6+
- pip (Python package manager)

### Manual Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/pastegpt.git
   cd pastegpt
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python pastegpt.py
   ```

### Creating a standalone executable

To create a standalone executable:

```
python install.py
```

The executable will be available in the `dist/` folder.

## Usage

1. Launch the application
2. Click on "Open Folder" or use Ctrl+O to select a folder
3. Navigate the folder structure and select desired files by clicking the checkboxes
4. Use "Select All" (Ctrl+A) or "Deselect All" (Ctrl+D) to speed up selection
5. Set file type filters if needed via "Extension Filter"
6. Click on "Copy Selected" or use Ctrl+C to copy the content to the clipboard
7. Paste the content into ChatGPT or any text editor

### Configuration Options

- **Hide hidden files**: Hides files that start with a dot (.)
- **Load folder contents only when expanded**: Improves performance by loading folder contents only when they are opened
- **Maximum file size**: Limits the size of copied files to prevent clipboard issues (default: 1MB)

### Content Formatting

When copying files to the clipboard, PasteGPT:

1. Formats content with Markdown headings for file paths (shown as relative paths)
2. Wraps code in ```language syntax highlighting blocks based on file extension
3. Adds line numbers to each line for easy reference in conversations
4. Automatically detects and indicates binary files
5. Truncates large files with size indicators
6. Adds a header to help LLMs understand the content

### Keyboard Shortcuts

- **Ctrl+O**: Open folder
- **Ctrl+C**: Copy selected
- **Ctrl+A**: Select all
- **Ctrl+D**: Deselect all
- **Alt+F4**: Exit

## License

MIT - See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or a pull request on GitHub.

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
