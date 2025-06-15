# Initializing New Skills

This guide explains how to create and initialize new skills for the Open Interpreter.

## Prerequisites

- Python 3.7+
- Basic understanding of Python programming
- Access to the Open Interpreter codebase

## Creating a New Skill

### 1. Create a New Skill File

1. Navigate to the skills directory:
   ```bash
   cd interpreter/core/computer/skills/
   ```

2. Create a new Python file for your skill (e.g., `my_skill.py`)

### 2. Define Your Skill Class

Create a new class that inherits from the base `Skill` class:

```python
from typing import Dict, Any
from ..base_skill import BaseSkill

class MySkill(BaseSkill):
    def __init__(self, computer):
        super().__init__(computer)
        self.name = "my_skill"
        self.description = "A brief description of what this skill does"
        self.parameters = {
            "param1": {"type": "string", "description": "Description of param1"},
            "param2": {"type": "int", "description": "Description of param2"}
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Main execution method for the skill
        
        Args:
            **kwargs: Dictionary containing the parameters specified in self.parameters
            
        Returns:
            Dict containing 'status' and either 'result' or 'error'
        """
        try:
            # Your skill logic here
            result = f"Processed {kwargs.get('param1')} with {kwargs.get('param2')}"
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
```

### 3. Register the Skill

Add an import and registration for your new skill in `__init__.py`:

```python
from .my_skill import MySkill

# Add to the __all__ list
__all__ = [
    # ... other skills
    'MySkill'
]
```

## Skill Structure Best Practices

1. **File Naming**: Use snake_case for skill file names (e.g., `file_search.py`)
2. **Class Naming**: Use PascalCase for skill class names (e.g., `FileSearch`)
3. **Imports**: Keep imports at the top of the file
4. **Error Handling**: Always include try-except blocks
5. **Documentation**: Include docstrings for the class and all methods

## Example: File Search Skill

Here's a complete example of a file search skill:

```python
import os
from typing import Dict, Any, List
from ..base_skill import BaseSkill

class FileSearch(BaseSkill):
    """
    A skill that searches for files containing specific text.
    """
    
    def __init__(self, computer):
        super().__init__(computer)
        self.name = "file_search"
        self.description = "Search for files containing specific text"
        self.parameters = {
            "directory": {
                "type": "string", 
                "description": "Directory to search in",
                "default": "."
            },
            "query": {
                "type": "string", 
                "description": "Text to search for",
                "required": True
            },
            "extensions": {
                "type": "list",
                "items": {"type": "string"},
                "description": "File extensions to include (e.g., ['.txt', '.md'])",
                "default": [".txt", ".md", ".py", ".js", ".html", ".css"]
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Search for files containing the specified query text.
        
        Args:
            directory (str): Directory to search in (default: current directory)
            query (str): Text to search for (required)
            extensions (list): List of file extensions to include
            
        Returns:
            Dict containing 'status' and either 'matches' or 'error'
        """
        try:
            directory = kwargs.get('directory', '.')
            query = kwargs.get('query')
            extensions = kwargs.get('extensions', ['.txt', '.md', '.py', '.js', '.html', '.css'])
            
            if not query:
                return {"status": "error", "message": "Query parameter is required"}
                
            if not os.path.isdir(directory):
                return {"status": "error", "message": f"Directory not found: {directory}"}
            
            matches = []
            
            for root, _, files in os.walk(directory):
                for file in files:
                    # Check file extension
                    if not any(file.lower().endswith(ext.lower()) for ext in extensions):
                        continue
                        
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if query.lower() in content.lower():
                                matches.append({
                                    'file': file_path,
                                    'line_count': len(content.splitlines())
                                })
                    except Exception as e:
                        # Skip files that can't be read
                        continue
            
            return {
                "status": "success",
                "matches": matches,
                "match_count": len(matches)
            }
            
        except Exception as e:
            return {"status": "error", "message": f"An error occurred: {str(e)}"}
```

## Testing Your Skill

1. Create a test script to verify your skill works as expected:

```python
from interpreter.core.computer.skills import FileSearch
from interpreter.core.computer.computer import Computer

# Initialize computer and skill
computer = Computer()
skill = FileSearch(computer)

# Test the skill
result = skill.execute(
    directory="./examples",
    query="hello world",
    extensions=[".py", ".txt"]
)

print(result)
```

2. Run your test script to verify the output.

## Documenting Your Skill

1. Add a docstring at the top of your skill file explaining its purpose
2. Document all parameters in the `parameters` dictionary
3. Include example usage in the docstring
4. Document any dependencies or requirements

## Submitting Your Skill

1. Ensure your code follows the project's coding standards
2. Write unit tests for your skill
3. Update the documentation if needed
4. Create a pull request with a clear description of your changes
