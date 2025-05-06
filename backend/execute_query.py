from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from SQLDatabase import db
from State import State

def execute_query(state: State):
    """Execute SQL query."""
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    return {"result": execute_query_tool.invoke(state["query"])}