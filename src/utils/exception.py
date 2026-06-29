import sys
from src.utils.logger import logging

class MRDException(Exception):
    def __init__(self, error_message: str,error_detail: sys):
        self.error_message = error_message
        self.exc_tb = error_detail.exc_info()[2]
        self.lineno = self.exc_tb.tb_lineno
        self.file_name = self.exc_tb.tb_frame.f_code.co_filename
    def __str__(self):
        return f"Error occured in script: {self.file_name} at line number: {self.lineno} with error message: {self.error_message}"

