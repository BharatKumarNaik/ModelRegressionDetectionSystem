import os
from src.utils.logger import logging
from src.utils.exception import MRDException
import json
import sys

class JsonUtils:
    def write_json(path: str, content):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            json_str = json.dumps(content, indent=4, ensure_ascii=False)
        except TypeError:
            # Fallback: coerce anything non-serializable to string instead of crashing
            logging.warning("Standard json.dumps failed, retrying with default=str")
            try:
                json_str = json.dumps(content, indent=4, ensure_ascii=False, default=str)
            except Exception as e:
                # Last resort: dump as plain text so nothing is lost
                txt_path = os.path.splitext(path)[0] + ".txt"
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(repr(content))
                logging.error(f"JSON serialization failed entirely, wrote raw text to {txt_path}: {e}")
                return False
        with open(path, "w", encoding="utf-8") as f:
            f.write(json_str)
        return True


    def read_json(path:str):
        try:
            with open(path,'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            raise MRDException(e,sys) from e
