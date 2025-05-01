"""
Custom implementation of the aider Model, Coder, and InputOutput classes
to provide compatibility with the actual aider CLI tool for the MCP server.
"""
import os
import subprocess
import tempfile
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Path to the aider CLI tool
AIDER_PATH = "/Users/eiliya/.local/share/uv/tools/aider-chat/bin/aider"

class Model:
    """
    Simplified replacement for aider.models.Model
    """
    def __init__(self, model_name):
        self.model_name = model_name
        
    def __repr__(self):
        return f"Model(model_name={self.model_name})"
    
    def complete(self, prompt, stream=False):
        """
        Implementation that uses the aider CLI
        
        Args:
            prompt (str): The prompt to send to the model
            stream (bool): Whether to stream the response (not used with CLI)
            
        Returns:
            str: The model's response
        """
        # The model_name is passed to the CLI through command line arguments
        # in the Coder.run() method, so we don't need to implement this method
        # with the actual completion logic.
        # This is just a placeholder.
        return f"Using aider CLI with model {self.model_name}"


class InputOutput:
    """
    Simplified replacement for aider.io.InputOutput
    """
    def __init__(self, yes=False, chat_history_file=None):
        self.yes = yes
        self.chat_history_file = chat_history_file
        
    def __repr__(self):
        return f"InputOutput(yes={self.yes}, chat_history_file={self.chat_history_file})"


class Coder:
    """
    Replacement for aider.coders.Coder that uses the aider CLI tool
    """
    def __init__(self, model, io, fnames, read_only_fnames, 
                 auto_commits=False, suggest_shell_commands=False, 
                 detect_urls=False, use_git=True):
        self.model = model
        self.io = io
        self.fnames = fnames
        self.read_only_fnames = read_only_fnames
        self.auto_commits = auto_commits
        self.suggest_shell_commands = suggest_shell_commands
        self.detect_urls = detect_urls
        self.use_git = use_git
    
    @classmethod
    def create(cls, main_model, io, fnames, read_only_fnames=None, 
               auto_commits=False, suggest_shell_commands=False, 
               detect_urls=False, use_git=True):
        """
        Factory method to create a Coder instance
        """
        if read_only_fnames is None:
            read_only_fnames = []
            
        return cls(
            model=main_model,
            io=io,
            fnames=fnames,
            read_only_fnames=read_only_fnames,
            auto_commits=auto_commits,
            suggest_shell_commands=suggest_shell_commands,
            detect_urls=detect_urls,
            use_git=use_git
        )
    
    def run(self, prompt):
        """
        Implementation that uses the aider CLI to perform real code edits
        
        Args:
            prompt (str): The natural language instruction for code changes
            
        Returns:
            str: The result of executing the aider CLI command
        """
        # Create a temporary file for the prompt
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            prompt_file = f.name
            f.write(prompt)
        
        try:
            # Build the aider command
            cmd = [AIDER_PATH]
            
            # Add model flag (use from environment variable if not specified)
            if hasattr(self.model, 'model_name') and self.model.model_name:
                cmd.extend(['--model', self.model.model_name])
            
            # Add yes flag
            if hasattr(self.io, 'yes') and self.io.yes:
                cmd.append('--yes')
            
            # Add auto commits flag
            if not self.auto_commits:
                cmd.append('--no-auto-commits')

            # Add file paths with appropriate flags
            
            # First add read-only files with the /read flag
            for read_only_file in self.read_only_fnames:
                cmd.extend(['/read', read_only_file])
            
            # Then add editable files with the /add flag
            for editable_file in self.fnames:
                cmd.extend(['/add', editable_file])
            
            # Turn off stream flag for CLI usage
            cmd.append('--no-stream')
            
            # Add the message from the prompt file
            cmd.extend(['--message-file', prompt_file])
            
            print(f"Executing command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,  # Capture stdout
                stderr=subprocess.PIPE,  # Capture stderr
                text=True,
                check=False,
            )

            # Return a combination or just stdout/stderr based on success
            if result.returncode == 0:
                return "Success: Aider command completed."
            else:
                error_msg = f"Error (code {result.returncode}): {result.stderr.strip()}"
                print(f"Aider CLI error: {error_msg}")  # Log the error
                return f"Failed: {error_msg}"
        
        except Exception as e:
            error_msg = f"Exception running aider CLI: {str(e)}"
            print(error_msg)
            return error_msg
        
        finally:
            # Clean up the temporary file
            if os.path.exists(prompt_file):
                os.unlink(prompt_file)
