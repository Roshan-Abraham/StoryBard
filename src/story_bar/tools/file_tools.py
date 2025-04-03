from .base import ToolNode, ToolInput, ToolOutput
from typing import Optional
from pydantic import Field
from ..utils.file_manager import FileManager

class FileWriterInput(ToolInput):
    thread_id: str = Field(description="Thread identifier for the session")
    filename: str = Field(description="Name of the file to write")
    content: str = Field(description="Content to write to the file")
    subfolder: Optional[str] = Field(default=None, description="Optional subfolder path")

class FileWriterOutput(ToolOutput):
    file_path: str

class FileWriterNode(ToolNode):
    """Node for writing files to session storage"""
    input_model = FileWriterInput
    output_model = FileWriterOutput
    
    def __init__(self):
        super().__init__(
            name="file_writer",
            description="Writes content to a file in the session directory"
        )
        self.file_manager = FileManager()
        
    def _execute(self, validated_input: FileWriterInput) -> FileWriterOutput:
        file_path = self.file_manager.write_file(
            validated_input.thread_id,
            validated_input.filename,
            validated_input.content,
            validated_input.subfolder
        )
        return FileWriterOutput(file_path=file_path)

class FileReaderInput(ToolInput):
    thread_id: str = Field(description="Thread identifier for the session")
    filename: str = Field(description="Name of the file to read")
    subfolder: Optional[str] = Field(default=None, description="Optional subfolder path")

class FileReaderOutput(ToolOutput):
    content: str

class FileReaderNode(ToolNode):
    """Node for reading files from session storage"""
    input_model = FileReaderInput
    output_model = FileReaderOutput
    
    def __init__(self):
        super().__init__(
            name="file_reader",
            description="Reads content from a file in the session directory"
        )
        self.file_manager = FileManager()
        
    def _execute(self, validated_input: FileReaderInput) -> FileReaderOutput:
        content = self.file_manager.read_file(
            validated_input.thread_id,
            validated_input.filename,
            validated_input.subfolder
        )
        return FileReaderOutput(content=content)
