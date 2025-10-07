"""
File Upload and Processing Handler
Supports CSV, Excel (xlsx, xls), and JSON files
"""

import pandas as pd
import json
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from loguru import logger
import sys
from datetime import datetime
import hashlib

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import settings


class FileProcessor:
    """
    Handle file uploads, validation, and processing
    """
    
    def __init__(self):
        """Initialize file processor"""
        self.allowed_extensions = settings.allowed_extensions
        self.max_file_size = settings.max_upload_size_mb * 1024 * 1024  # Convert to bytes
        self.upload_dir = settings.upload_dir
    
    def validate_file(self, file_name: str, file_size: int) -> Tuple[bool, str]:
        """
        Validate uploaded file
        
        Args:
            file_name: Name of the uploaded file
            file_size: Size of file in bytes
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file extension
        file_ext = Path(file_name).suffix.lower()
        if file_ext not in self.allowed_extensions:
            return False, f"File type '{file_ext}' not supported. Allowed: {', '.join(self.allowed_extensions)}"
        
        # Check file size
        if file_size > self.max_file_size:
            max_mb = self.max_file_size / (1024 * 1024)
            actual_mb = file_size / (1024 * 1024)
            return False, f"File too large ({actual_mb:.2f}MB). Maximum size: {max_mb:.0f}MB"
        
        # Check if file is empty
        if file_size == 0:
            return False, "File is empty"
        
        return True, ""
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """
        Generate unique filename using timestamp and hash
        
        Args:
            original_filename: Original name of the file
        
        Returns:
            Unique filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = Path(original_filename).suffix
        name_without_ext = Path(original_filename).stem
        
        # Create hash from original name and timestamp
        hash_str = hashlib.md5(f"{name_without_ext}{timestamp}".encode()).hexdigest()[:8]
        
        return f"{name_without_ext}_{timestamp}_{hash_str}{file_ext}"
    
    def save_uploaded_file(self, uploaded_file, unique_name: str) -> str:
        """
        Save uploaded file to disk
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            unique_name: Unique filename to save as
        
        Returns:
            Full path to saved file
        """
        file_path = self.upload_dir / unique_name
        
        try:
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            logger.info(f"✅ File saved: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"❌ Failed to save file: {e}")
            raise
    
    def read_file(self, file_path: str) -> Tuple[Optional[pd.DataFrame], str]:
        """
        Read file into pandas DataFrame
        
        Args:
            file_path: Path to the file
        
        Returns:
            Tuple of (DataFrame, file_type)
        """
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
                return df, 'csv'
            
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
                return df, 'xlsx' if file_ext == '.xlsx' else 'xls'
            
            elif file_ext == '.json':
                # Try to read as JSON array
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Convert to DataFrame
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                elif isinstance(data, dict):
                    # If it's a dict, try to convert it
                    df = pd.DataFrame([data])
                else:
                    raise ValueError("JSON must be an array of objects or a single object")
                
                return df, 'json'
            
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
        
        except Exception as e:
            logger.error(f"❌ Failed to read file: {e}")
            return None, ""
    
    def detect_encoding(self, file_path: str) -> str:
        """
        Detect file encoding for better CSV reading
        
        Args:
            file_path: Path to the file
        
        Returns:
            Detected encoding
        """
        try:
            import chardet
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())
            return result['encoding']
        except:
            return 'utf-8'  # Default fallback
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file
        
        Args:
            file_path: Path to the file
        
        Returns:
            Dictionary with file information
        """
        path = Path(file_path)
        
        return {
            'filename': path.name,
            'extension': path.suffix,
            'size_bytes': path.stat().st_size,
            'size_mb': round(path.stat().st_size / (1024 * 1024), 2),
            'created': datetime.fromtimestamp(path.stat().st_ctime),
            'modified': datetime.fromtimestamp(path.stat().st_mtime),
        }
    
    def process_uploaded_file(self, uploaded_file) -> Dict[str, Any]:
        """
        Complete file processing pipeline
        
        Args:
            uploaded_file: Streamlit UploadedFile object
        
        Returns:
            Dictionary with processing results
        """
        result = {
            'success': False,
            'dataframe': None,
            'file_path': None,
            'file_info': None,
            'error': None
        }
        
        try:
            # Validate file
            is_valid, error_msg = self.validate_file(uploaded_file.name, uploaded_file.size)
            if not is_valid:
                result['error'] = error_msg
                return result
            
            # Generate unique filename
            unique_name = self.generate_unique_filename(uploaded_file.name)
            
            # Save file
            file_path = self.save_uploaded_file(uploaded_file, unique_name)
            
            # Read file into DataFrame
            df, file_type = self.read_file(file_path)
            if df is None:
                result['error'] = "Failed to read file"
                return result
            
            # Get file info
            file_info = self.get_file_info(file_path)
            file_info['type'] = file_type
            file_info['original_name'] = uploaded_file.name
            
            result['success'] = True
            result['dataframe'] = df
            result['file_path'] = file_path
            result['file_info'] = file_info
            
            logger.info(f"✅ File processed successfully: {uploaded_file.name}")
            
        except Exception as e:
            logger.error(f"❌ File processing failed: {e}")
            result['error'] = str(e)
        
        return result


# Global instance
file_processor = FileProcessor()

