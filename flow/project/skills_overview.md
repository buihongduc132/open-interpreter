# Skills Overview

Skills are reusable, self-contained modules that extend the capabilities of the Open Interpreter. They allow you to encapsulate common tasks and workflows for easy reuse.

## What is a Skill?

A Skill is a Python class that encapsulates a specific capability or workflow. Skills can:

1. Accept input parameters
2. Perform operations using the computer's capabilities
3. Return results or perform actions
4. Maintain state if needed
5. Be easily shared and reused

## Skill Structure

A typical skill has the following structure:

```python
class MySkill:
    def __init__(self, computer):
        self.computer = computer
        self.name = "my_skill"
        self.description = "A brief description of what this skill does"
        self.parameters = {
            "param1": {"type": "string", "description": "Description of param1"},
            "param2": {"type": "int", "description": "Description of param2"}
        }
    
    def execute(self, **kwargs):
        """
        Main execution method for the skill
        """
        # Access parameters
        param1 = kwargs.get('param1')
        param2 = kwargs.get('param2')
        
        try:
            # Skill logic here
            result = f"Processed {param1} with {param2}"
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
```

## Skill Categories

Skills can be categorized based on their functionality:

1. **Utility Skills**: Common tasks like file operations, data processing
2. **Integration Skills**: Connect with external services (APIs, databases)
3. **Workflow Skills**: Combine multiple operations into a single workflow
4. **AI/ML Skills**: Specialized AI/ML operations

## Best Practices

1. **Single Responsibility**: Each skill should do one thing well
2. **Error Handling**: Include comprehensive error handling
3. **Documentation**: Document parameters, return values, and usage examples
4. **Testing**: Include tests for your skills
5. **Dependencies**: Clearly document any external dependencies
6. **Performance**: Be mindful of resource usage
7. **State Management**: Keep state minimal and well-documented

## Example Skills

### File Search Skill
```python
class FileSearchSkill:
    def __init__(self, computer):
        self.computer = computer
        self.name = "file_search"
        self.description = "Search for files containing specific text"
        self.parameters = {
            "directory": {"type": "string", "description": "Directory to search in"},
            "query": {"type": "string", "description": "Text to search for"}
        }
    
    def execute(self, **kwargs):
        directory = kwargs.get('directory', '.')
        query = kwargs.get('query')
        
        if not query:
            return {"status": "error", "message": "Query parameter is required"}
            
        try:
            files_found = []
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith('.txt'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            if query in f.read():
                                files_found.append(file_path)
            
            return {"status": "success", "files_found": files_found}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
```

### Web Scraping Skill
```python
class WebScrapingSkill:
    def __init__(self, computer):
        self.computer = computer
        self.name = "web_scrape"
        self.description = "Scrape content from a web page"
        self.parameters = {
            "url": {"type": "string", "description": "URL to scrape"},
            "selector": {"type": "string", "description": "CSS selector for target elements"}
        }
    
    def execute(self, **kwargs):
        url = kwargs.get('url')
        selector = kwargs.get('selector')
        
        if not url or not selector:
            return {"status": "error", "message": "URL and selector parameters are required"}
            
        try:
            # Use the computer's browser capability
            browser = self.computer.browser.new_tab()
            browser.navigate(url)
            elements = browser.query_selector_all(selector)
            
            results = [element.text for element in elements]
            
            return {"status": "success", "results": results}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            if 'browser' in locals():
                browser.close()
```

## Skill Lifecycle

1. **Initialization**: The skill is loaded and initialized
2. **Validation**: Input parameters are validated
3. **Execution**: The skill's main logic runs
4. **Cleanup**: Resources are released
5. **Response**: Results or errors are returned
