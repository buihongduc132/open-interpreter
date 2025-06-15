# Configuration Profiles

Configuration profiles allow you to customize the behavior of the Open Interpreter. Here's how to set up and manage your profiles.

## Setting Up a Profile

1. Create a new Python file in the `config` directory (e.g., `my_profile.py`)
2. Define your configuration settings as a Python dictionary

Example profile (`config/my_profile.py`):

```python
profile = {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000,
    "auto_run": True,
    "debug_mode": False,
    "api_key": "your-api-key-here"  # Store sensitive data in environment variables
}
```

## Using a Profile

To use a specific profile, import it when initializing the interpreter:

```python
from interpreter import interpreter
from config.my_profile import profile

# Apply the profile
for key, value in profile.items():
    setattr(interpreter, key, value)
```

## Environment Variables

For sensitive information like API keys, use environment variables:

```python
import os

profile = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    # other settings...
}
```

## Available Configuration Options

- `model`: The AI model to use (e.g., "gpt-4", "gpt-3.5-turbo")
- `temperature`: Controls randomness (0.0 to 1.0)
- `max_tokens`: Maximum number of tokens to generate
- `auto_run`: Whether to automatically run code blocks
- `debug_mode`: Enable debug output
- `api_key`: Your API key for the AI service

## Best Practices

1. Never commit API keys or sensitive data to version control
2. Use environment variables for sensitive information
3. Create different profiles for different use cases (e.g., development, production)
4. Document your configuration options in the profile file
