import ast
import astor
import logging

logger = logging.getLogger(__name__)

def fix_indentation(file_path: str) -> bool:
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        
        tree = ast.parse(content)
        fixed_content = astor.to_source(tree)
        
        with open(file_path, 'w') as file:
            file.write(fixed_content)
        
        logger.info(f"Fixed indentation in {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to fix indentation in {file_path}: {str(e)}")
        return False

def fix_indentation_in_directory(directory: str) -> None:
    import os
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                fix_indentation(file_path)
