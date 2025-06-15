# Available Instructions

This document lists all available instructions that can be used with the Open Interpreter. Each instruction is designed to perform a specific task or operation.

## Core Instructions

### 1. File Operations
- `read_file`: Read content from a file
- `write_file`: Write content to a file
- `list_directory`: List contents of a directory
- `create_directory`: Create a new directory
- `delete_file`: Delete a file
- `move_file`: Move or rename a file
- `copy_file`: Copy a file to a new location

### 2. System Commands
- `run_command`: Execute a shell command
- `get_system_info`: Get information about the system
- `list_processes`: List running processes
- `kill_process`: Terminate a running process

### 3. Web Browsing
- `open_url`: Open a URL in the browser
- `extract_content`: Extract content from a web page
- `fill_form`: Fill out a web form
- `click_element`: Click on a web element
- `screenshot`: Take a screenshot of the current page

### 4. User Interface
- `move_mouse`: Move the mouse cursor
- `click_mouse`: Perform a mouse click
- `type_text`: Type text at the current cursor position
- `press_key`: Simulate a key press
- `get_clipboard`: Get clipboard contents
- `set_clipboard`: Set clipboard contents

### 5. Data Processing
- `parse_json`: Parse a JSON string
- `generate_json`: Generate JSON data
- `filter_data`: Filter a list based on criteria
- `sort_data`: Sort a list of items
- `transform_data`: Apply a transformation to data

## Example Usage

### Reading and Processing a File
```python
# Read a file
content = computer.files.read("data.txt")

# Process the content
lines = content.split("\n")
filtered = [line for line in lines if "important" in line]

# Write results to a new file
computer.files.write("filtered_data.txt", "\n".join(filtered))
```

### Web Scraping Example
```python
# Open a webpage
browser = computer.browser.new_tab()
browser.navigate("https://example.com")

# Extract all links
links = browser.query_selector_all("a")
link_urls = [link.get_attribute("href") for link in links]

# Process the links
for url in link_urls[:5]:  # Process first 5 links
    print(f"Processing: {url}")
    # Additional processing...
```

### System Monitoring
```python
# Get system information
info = computer.os.system_info()
print(f"CPU Usage: {info['cpu_percent']}%")
print(f"Memory Usage: {info['memory_percent']}%")

# List top 5 processes by CPU usage
processes = sorted(
    computer.os.list_processes(),
    key=lambda p: p.get('cpu_percent', 0),
    reverse=True
)
for proc in processes[:5]:
    print(f"{proc['name']}: {proc['cpu_percent']}%")
```

## Instruction Reference

### File Operations

#### read_file
```python
data = computer.files.read("path/to/file.txt")
```

**Parameters:**
- `path` (str): Path to the file to read

**Returns:**
- Content of the file as a string

---

#### write_file
```python
computer.files.write("path/to/file.txt", "content")
```

**Parameters:**
- `path` (str): Path to the file to write
- `content` (str): Content to write to the file

---

### System Commands

#### run_command
```python
result = computer.os.run("ls -la")
```

**Parameters:**
- `command` (str): Command to execute
- `cwd` (str, optional): Working directory
- `timeout` (int, optional): Timeout in seconds

**Returns:**
- Dictionary with 'stdout', 'stderr', and 'returncode'

---

### Web Browsing

#### open_url
```python
browser = computer.browser.new_tab()
browser.navigate("https://example.com")
```

**Parameters:**
- `url` (str): URL to navigate to

---

#### extract_content
```python
elements = browser.query_selector_all("p")
texts = [el.text for el in elements]
```

**Parameters:**
- `selector` (str): CSS selector for target elements

**Returns:**
- List of matching elements

---

## Best Practices

1. **Error Handling**: Always include error handling for file operations and network requests
2. **Resource Management**: Close browser tabs and file handles when done
3. **Input Validation**: Validate all input parameters
4. **Rate Limiting**: Be mindful of rate limits when making web requests
5. **Security**: Never execute untrusted code or commands
6. **Performance**: Use appropriate data structures and algorithms
7. **Logging**: Include logging for important operations

## Creating Custom Instructions

To create custom instructions, refer to the [Initializing Skills](initializing_skills.md) documentation.
