import subprocess
import os
import json
import pandas as pd
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict
from llm import llm

# --- State Definition ---
class GraphState(TypedDict):
    user_query: str
    data: pd.DataFrame  # Or metadata about the data
    suggested_charts: List[str]
    generated_visualizations: List[Dict]

# --- Node 1: Plan Charts (Same as before) ---
plan_prompt = PromptTemplate.from_template("""Given the user query: '{user_query}' and the following data (or description of data): '{data}', suggest a few relevant chart types that could be generated to address the query. Explain your reasoning for each suggestion.

Chart Suggestions:""")

def plan_charts(state: GraphState):
    prompt_value = plan_prompt.invoke(state)
    response = llm.invoke(prompt_value)
    suggestions = [line.split(":")[0].strip() for line in response.content.split("\n") if ":" in line]
    return {"suggested_charts": suggestions}

# --- Node 2: Generate and Explain Chart (Dynamic) ---
generate_prompt = PromptTemplate.from_template("""You are an expert data visualization coder. Given the user query: '{user_query}', the following data: '{data}', and the requested chart type: '{chart_type}', generate Python code using matplotlib only to create this chart. Also, explain the code, provide a sample data table, explain the data table, and explain the chart after it would be generated. Format your response as a JSON object with the keys: 'code', 'code_explanation', 'data_table', 'data_table_explanation', and 'chart_explanation'.

Chart Type: {chart_type}
Code and Explanation:""")

def generate_and_explain_chart(state: GraphState):
    if not state.get("suggested_charts"):
        return {"generated_visualization": None}

    chart_type = state["suggested_charts"].pop(0)
    prompt_value = generate_prompt.invoke({"user_query": state["user_query"], "data": state["data"].head().to_string(), "chart_type": chart_type})
    response = llm.invoke(prompt_value)
    try:
        visualization_data = json.loads(response.content)
        code_to_execute = visualization_data["code"]
        chart_filename = f"{visualization_data['message_id']}_{chart_type.lower().replace(' ', '_')}.png"

        # --- UNSAFE: Direct use of exec() is strongly discouraged ---
        # --- Instead, use a sandboxed environment like Docker ---
        # try:
        #     # This is highly insecure for production
        #     local_vars = {}
        #     exec(code_to_execute, globals(), local_vars)
        #     # Assuming the code saves the plot to a file named 'temp_chart.png'
        #     if 'plt' in local_vars:
        #         local_vars['plt'].savefig(chart_filename)
        #     visualization_data["chart"] = chart_filename
        # except Exception as e:
        #     visualization_data["chart"] = f"Error generating chart: {e}"
        # --- End of unsafe exec() block ---

        # --- Safer approach using subprocess and a separate script ---
        with open("temp_plot_script.py", "w") as f:
            f.write(code_to_execute)

        try:
            subprocess.run(["python", "temp_plot_script.py", chart_filename], check=True, timeout=10) # Add timeout
            visualization_data["chart"] = chart_filename
        except subprocess.CalledProcessError as e:
            visualization_data["chart"] = f"Error generating chart: {e}"
        except subprocess.TimeoutExpired:
            visualization_data["chart"] = "Error: Chart generation timed out."
        finally:
            os.remove("temp_plot_script.py")
        # --- End of safer subprocess approach ---

        visualization_data["data_table"] = {"columns": state["data"].columns.tolist(), "rows": state["data"].head(5).values.tolist()}
        visualization_data["data_table_explanation"] = f"A preview of the first few rows of the data used for the {chart_type}."
        visualization_data["message_id"] = f"visualization_{len(state.get('generated_visualizations', [])) + 1}"
        return {"generated_visualization": visualization_data}
    except json.JSONDecodeError as e:
        return {"generated_visualization": f"Error decoding JSON: {e}"}

# --- Define the Langgraph (Same as before) ---
builder = StateGraph(GraphState)
builder.add_node("plan_charts", plan_charts)
builder.add_node("generate_and_explain", generate_and_explain_chart)

builder.set_entry_point("plan_charts")
builder.add_edge("plan_charts", "generate_and_explain")

def should_continue(state):
    return bool(state.get("suggested_charts"))

builder.add_conditional_edges("generate_and_explain", should_continue, {"true": "generate_and_explain", "false": END})

graph = builder.compile()

# --- Example Usage (Same as before) ---
if __name__ == "__main__":
    user_query = "Perform EDA of this data using different charts and plots."
    data = pd.read_csv("bank.csv")

    result = graph.invoke({"user_query": user_query, "data": data, "suggested_charts": [], "generated_visualizations": []})
    print(json.dumps(result['generated_visualizations'], indent=2))