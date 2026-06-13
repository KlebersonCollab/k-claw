import os
from tools.file_tools import write_file, replace_string

def test_linter_as_sensor_write(tmp_path):
    # Setup mock workspace
    prev_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        # Test 1: Write valid python file
        res_valid = write_file.invoke({"path": "valid.py", "content": "print('hello')"})
        assert "WARNING: SYNTAX ERROR DETECTED" not in res_valid
        
        # Test 2: Write invalid python file
        res_invalid = write_file.invoke({"path": "invalid.py", "content": "print('hello'"})
        assert "WARNING: SYNTAX ERROR DETECTED" in res_invalid
        assert "SyntaxError" in res_invalid
    finally:
        os.chdir(prev_cwd)

def test_linter_as_sensor_replace(tmp_path):
    # Setup mock workspace
    prev_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        # Create base file
        with open("test_rep.py", "w") as f:
            f.write("def func():\n    pass\n")
            
        # Test 1: Replace with valid syntax
        res_valid = replace_string.invoke({
            "path": "test_rep.py", 
            "old_string": "pass", 
            "new_string": "return True"
        })
        assert "WARNING: SYNTAX ERROR DETECTED" not in res_valid
        
        # Test 2: Replace with invalid syntax
        res_invalid = replace_string.invoke({
            "path": "test_rep.py", 
            "old_string": "return True", 
            "new_string": "return True ="
        })
        assert "WARNING: SYNTAX ERROR DETECTED" in res_invalid
        assert "SyntaxError" in res_invalid
    finally:
        os.chdir(prev_cwd)
