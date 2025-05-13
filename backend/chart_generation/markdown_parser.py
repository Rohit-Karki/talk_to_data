import re
from typing import List
from .models import DataTable, CodeBlock, Explanation

def extract_data_table(md_text: str) -> List[DataTable]:
    """
    Extract data tables from markdown text.
    
    Args:
        md_text (str): Markdown text containing the data table
        
    Returns:
        List[DataTable]: List of extracted data tables
    """
    matches = re.findall(r"Data Table:\s*(.*?)(?=Code Explanation:|Chart Explanation:|$)", 
                        md_text, re.DOTALL | re.IGNORECASE)
    
    if not matches:
        return []
    
    tables = []
    for match in matches:
        table_text = match.strip()
        table_text = re.sub(r'```.*?```', '', table_text, flags=re.DOTALL)
        
        try:
            lines = [line.strip() for line in table_text.split('\n') if line.strip()]
            if len(lines) < 2:
                continue
                
            headers = [h.strip() for h in lines[0].split('|') if h.strip()]
            if not headers:
                continue
                
            data = []
            for line in lines[1:]:
                row = [cell.strip() for cell in line.split('|') if cell.strip()]
                if len(row) == len(headers):
                    processed_row = {}
                    for header, value in zip(headers, row):
                        try:
                            if '.' in value:
                                processed_row[header] = float(value)
                            else:
                                processed_row[header] = int(value)
                        except ValueError:
                            processed_row[header] = value
                    data.append(processed_row)
            
            if data:
                tables.append(DataTable(
                    headers=headers,
                    data=data,
                    title="Analysis Data Table",
                    description="Data used in the analysis"
                ))
        except Exception as e:
            print(f"Error parsing table: {str(e)}")
            continue
    
    return tables

def extract_chart_explanation(md_text: str) -> str:
    """Extract chart explanation from markdown text."""
    matches = re.findall(r"Chart Explanation:\s*(.*?)(?=Code Explanation:|Data Table:|$)", 
                        md_text, re.DOTALL | re.IGNORECASE)
    
    if not matches:
        return ""
    
    explanation = matches[0].strip()
    explanation = re.sub(r'```.*?```', '', explanation, flags=re.DOTALL)
    return explanation.strip()

def extract_code_explanation(md_text: str) -> str:
    """Extract code explanation from markdown text."""
    matches = re.findall(r"Code Explanation:\s*(.*?)(?=Chart Explanation:|Data Table:|$)", 
                        md_text, re.DOTALL | re.IGNORECASE)
    
    if not matches:
        return ""
    
    explanation = matches[0].strip()
    explanation = re.sub(r'```.*?```', '', explanation, flags=re.DOTALL)
    return explanation.strip()

def extract_code_from_markdown(md_text: str) -> str:
    """Extract Python code from markdown text."""
    code_blocks = re.findall(r"```python\n(.*?)```", md_text, re.DOTALL)
    if not code_blocks:
        code_blocks = re.findall(r"```\n(.*?)```", md_text, re.DOTALL)
    if not code_blocks:
        code_blocks = re.findall(r"```(.*?)```", md_text, re.DOTALL)
    
    if not code_blocks:
        raise ValueError(f"No code blocks found in response. Raw response:\n{md_text}")
    
    return "\n".join([block.strip() for block in code_blocks]) 