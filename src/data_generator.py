import random
import time
from faker import Faker
from neo4j import GraphDatabase

# CONFIGURATION
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "12345678") 

fake = Faker()

class BankDataGenerator:
    def __init__(self):
        # 1. Connect to the Database
        try:
            self.driver = GraphDatabase.driver(URI, auth=AUTH)
            self.driver.verify_connectivity()
            print(" Connected to Neo4j!")
        except Exception as e:
            print(f" Connection Failed: {e}")

    def close(self):
        self.driver.close()

    def run_query(self, query, parameters=None):
        with self.driver.session() as session:
            session.run(query, parameters)

    # 2. CREATE LEGIT USERS
    def create_users(self, num_users=50):
        print(f"Creating {num_users} users...")
        query = """
        UNWIND $props AS map
        MERGE (u:User {id: map.id})
        SET u.name = map.name
        """
        # Generate a list of fake people
        props = [{'id': f"U{i}", 'name': fake.name()} for i in range(num_users)]
        self.run_query(query, {'props': props})

    # 3. INJECT RANDOM NOISE (The "Messy" Part)
    def inject_random_noise(self, num_transactions=500):
        print(f" Injecting {num_transactions} random transactions (Noise)...")
        # Get all user IDs
        with self.driver.session() as session:
            result = session.run("MATCH (u:User) RETURN u.id AS id")
            all_users = [record["id"] for record in result]
        
        if len(all_users) < 2:
            print(" Not enough users to create noise.")
            return

        for _ in range(num_transactions):
            sender = random.choice(all_users)
            receiver = random.choice(all_users)
            if sender != receiver:
                # Random small amounts looking like normal coffee/rent
                amount = random.randint(10, 500) 
                query = """
                MATCH (s:User {id: $s_id}), (r:User {id: $r_id})
                MERGE (s)-[:TRANSACTION {amount: $amt, type: 'Normal', timestamp: $time}]->(r)
                """
                self.run_query(query, {'s_id': sender, 'r_id': receiver, 'amt': amount, 'time': time.time()})

    # 4. INJECT MONEY LAUNDERING RING (The "Feature")
    def inject_money_laundering(self, ring_id):
        print(f"Injecting Money Laundering Ring #{ring_id}...")
        
        # A. Create the Criminals
        boss = f"BOSS_{ring_id}"
        mules = [f"MULE_{ring_id}_{i}" for i in range(5)] # 5 Mules
        
        # B. The 'Placement' Phase: Boss sends money to Mules
        for mule in mules:
            query = """
            MERGE (b:User {id: $boss_id})
            MERGE (m:User {id: $mule_id})
            MERGE (b)-[:TRANSACTION {amount: 9000, type: 'Placement', timestamp: $time}]->(m)
            """
            self.run_query(query, {'boss_id': boss, 'mule_id': mule, 'time': time.time()})

        # C. The 'Layering' Phase: Mules send to a Shell Company
        shell_company = f"SHELL_{ring_id}"
        for mule in mules:
            query = """
            MERGE (m:User {id: $mule_id})
            MERGE (s:User {id: $shell_id})
            MERGE (m)-[:TRANSACTION {amount: 8500, type: 'Layering', timestamp: $time}]->(s)
            """
            self.run_query(query, {'mule_id': mule, 'shell_id': shell_company, 'time': time.time()})

if __name__ == "__main__":
    gen = BankDataGenerator()
    
    # 1. Clear database first (Optional, but good for clean testing)
    # gen.run_query("MATCH (n) DETACH DELETE n")

    # 2. Create a larger population
    gen.create_users(1000) 
    
    # 3. Inject Random Noise
    gen.inject_random_noise(2000) 
    
    # 4. Inject multiple Fraud Rings
    for i in range(10):
        gen.inject_money_laundering(i)
    
    gen.close()
    print("Data Injection Complete (Hard Mode).")