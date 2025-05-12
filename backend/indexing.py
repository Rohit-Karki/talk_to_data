from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import json

# Function that stores the max,min & mean for numerical values
def return_vals(df,c):
    if isinstance(df[c].iloc[0], (int, float, complex)):
        return [max(df[c]), min(df[c]), np.mean(df[c])]
# For datetime we need to store that information as string
    elif(isinstance(df[c].iloc[0],datetime.datetime)):
        return [str(max(df[c])), str(min(df[c])), str(np.mean(df[c]))]
    else:
# For categorical variables you can store the top 10 most frequent items and their frequency
        return list(df[c].value_counts()[:10])

# declare a dictionary 
dict_ = {}
for c in df.columns:
# storing the column name, data type and content
  dict_[c] = {'column_name':c,'type':str(type(df[c].iloc[0])), 'variable_information':return_vals(df,c)}
# After looping storing the information as a json dump that can be loaded 
# into a llama-index Document

# Writing the information into dataframe.json 

with open("dataframe.json", "w") as fp:
    json.dump(dict_ ,fp) 


# Load documents from JSON
loader = JSONLoader(file_path='dataframe.json')
documents = loader.load()

# Create vector store index
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)