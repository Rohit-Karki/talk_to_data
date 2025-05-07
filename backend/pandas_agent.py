from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from llm import llm
from langchain_experimental.agents.agent_toolkits import create_python_agent
from langchain_experimental.tools.python.tool import PythonREPLTool

def pandas_agent(df):
    # Create a Python agent for executing code
    python_agent = create_python_agent(
        llm=llm,
        tool=PythonREPLTool(),
        verbose=True
    )
    
    # Create the pandas agent with the Python agent
    agent = create_pandas_dataframe_agent(
        llm=llm,
        df=df,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        # python_agent=python_agent,
        allow_dangerous_code=True
    )
    return agent