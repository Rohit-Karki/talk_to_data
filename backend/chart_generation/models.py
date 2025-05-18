from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
from datetime import datetime

class CodeBlock(BaseModel):
    code: str
    type: str = Field(..., description="Type of code block (visualization, eda, correlation, etc.)")
    language: str = "python"

class Explanation(BaseModel):
    text: str
    type: str = Field(..., description="Type of explanation (code, chart, data)")
    section: Optional[str] = None

class DataTable(BaseModel):
    headers: List[str]
    data: List[Dict[str, Union[str, float, int]]]
    title: Optional[str] = None
    description: Optional[str] = None

class Visualization(BaseModel):
    type: str = Field(..., description="Type of visualization (line, bar, scatter, etc.)")
    title: str
    description: str
    data: Dict[str, Union[str, float, int]]
    config: Optional[Dict] = None

class AnalysisResult(BaseModel):
    code_blocks: List[CodeBlock]
    explanations: List[Explanation]
    # data_tables: List[DataTable]
    visualizations: List[Visualization]
    metadata: Dict[str, Union[List[str], tuple]]
    timestamp: datetime = Field(default_factory=datetime.now) 