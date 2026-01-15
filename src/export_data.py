import pandas as pd
from neo4j import GraphDatabase

# CONFIGURATION
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "12345678") 

def export_to_csv():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    
    query = """
    MATCH (u:User)
    OPTIONAL MATCH (u)-[r:TRANSACTION]->(target)
    RETURN 
        u.id AS userId,
        u.name AS name,
        count(r) AS degree,
        sum(r.amount) AS total_sent,
        collect(target.id) AS interaction_network
    """
    
    print("⏳ Exporting data from Neo4j...")
    with driver.session() as session:
        result = session.run(query)
        data = [record.data() for record in result]
    
    # Convert to Pandas DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv("data/user_features.csv", index=False)
    print(f"✅ Exported {len(df)} users to 'data/user_features.csv'")
    driver.close()

if __name__ == "__main__":
    export_to_csv()