import matplotlib.pyplot as plt

def determine_chart_type(query: str) -> str:
    """Determine the most appropriate chart type based on the query."""
    query = query.lower()
    if any(word in query for word in ['trend', 'time', 'line']):
        return 'line'
    elif any(word in query for word in ['distribution', 'histogram', 'density']):
        return 'histogram'
    elif any(word in query for word in ['scatter', 'correlation', 'relationship']):
        return 'scatter'
    elif any(word in query for word in ['pie', 'proportion', 'percentage']):
        return 'pie'
    elif any(word in query for word in ['box', 'quartile', 'outlier']):
        return 'box'
    else:
        return 'bar'

def setup_plot_style():
    """Set up consistent plot styling."""
    plt.rcParams['figure.facecolor'] = '#F0F0F0'
    plt.rcParams['axes.facecolor'] = '#F0F0F0'
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.color'] = '#FFFFFF'
    plt.rcParams['grid.alpha'] = 0.3

def determine_code_type(code: str) -> str:
    """Determine the type of code block based on its content."""
    code = code.lower()
    
    if 'plot' in code or 'chart' in code or 'figure' in code:
        return 'visualization'
    elif 'describe' in code or 'info' in code or 'value_counts' in code:
        return 'eda'
    elif 'corr' in code or 'correlation' in code:
        return 'correlation'
    elif 'groupby' in code or 'aggregate' in code:
        return 'aggregation'
    elif 'fillna' in code or 'dropna' in code:
        return 'data_cleaning'
    else:
        return 'general' 