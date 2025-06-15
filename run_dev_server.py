import uvicorn
from interpreter.core.async_core import AsyncInterpreter
import os
import dotenv

dotenv.load_dotenv()

# Configure your AsyncInterpreter instance for development

def create_app():
    """
    Factory function to create and configure the FastAPI application.
    This helps ensure a fresh instance is created when Uvicorn reloads.
    """
    # debug=True and verbose=True will enable more detailed logging from OpenInterpreter
    # disable_telemetry=True is optional, but often preferred during development
    interpreter_instance = AsyncInterpreter(
        debug=True,
        verbose=True,
        # model='i',
        disable_telemetry=True  # Optional: disable telemetry for dev
    )
    print("--- New AsyncInterpreter instance created ---")
    print(f"Interpreter Debug Mode: {interpreter_instance.debug}")
    print(f"Interpreter Verbose Mode: {interpreter_instance.verbose}")
    print(f"Telemetry Disabled: {interpreter_instance.disable_telemetry}")
    print("-------------------------------------------")
    # The FastAPI app instance is accessible via interpreter_instance.server.app
    return interpreter_instance.server.app

# Create the app instance for Uvicorn to discover
app = create_app()

if __name__ == "__main__":
    # Determine host and port (can be overridden by environment variables)
    # Use static defaults or environment variables directly for uvicorn.run
    run_host = os.getenv("INTERPRETER_HOST", "127.0.0.1")
    run_port = int(os.getenv("INTERPRETER_PORT", 8000))

    print(f"Uvicorn will attempt to start Open Interpreter development server on http://{run_host}:{run_port}")
    print("Uvicorn will auto-reload on code changes.")

    uvicorn.run(
        "run_dev_server:app",  # Pass the app as an import string
        host=run_host,
        port=run_port,
        reload=True,
        reload_dirs=["interpreter"], # Watch the 'interpreter' directory for changes
        log_level="debug"  # Increased log level for Uvicorn
    )
