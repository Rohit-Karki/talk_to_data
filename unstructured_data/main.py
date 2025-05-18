import pandas as pd
from pymongo import MongoClient

def main():

    # Replace with your actual credentials and database
    username = "root"
    password = "example"
    host = "mongo"
    port = 27017
    auth_db = "unstructured_database"  # or the name of the database that holds your user

    uri = f"mongodb://{username}:{password}@{host}:{port}/{auth_db}"

    # Load CSV
    df = pd.read_csv("sms_data.csv")

    # Connect to MongoDB
    client = MongoClient("mongodb://root:example@mongo:27017/")
    print(client.list_database_names())
    # db = client["unstructured_database"]
    # collection = db["messages"]

    # # Convert DataFrame rows to dicts and insert into MongoDB
    # data = df.to_dict(orient="records")
    # collection.insert_many(data)

    # print("Data inserted successfully!")

if __name__ == "__main__":
    main()
