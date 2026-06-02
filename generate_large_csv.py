import pandas as pd
import random
import os

print("Generating Enterprise-Scale Dataset (70,500 transactions)...")

# 1. Initialize Normal Users
num_normal_users = 15000
interactions = {f"U{i}": [] for i in range(1, num_normal_users + 1)}

# 2. Inject Normal Transactions (The 99.3% Noise)
print("Injecting 70,000 normal transactions...")
for _ in range(70000):
    sender = f"U{random.randint(1, num_normal_users)}"
    receiver = f"U{random.randint(1, num_normal_users)}"
    interactions[sender].append(receiver)

# 3. Inject Fraud Rings (The 0.7% Signal)
print("Injecting 50 Money Laundering Rings...")
for ring_id in range(50):
    boss = f"BOSS_{ring_id}"
    shell = f"SHELL_{ring_id}"
    
    interactions[boss] = []
    if shell not in interactions:
        interactions[shell] = []

    # Boss sends to 5 Mules, each Mule sends to 1 Shell
    for m in range(5):
        mule = f"MULE_{ring_id}_{m}"
        interactions[boss].append(mule)
        interactions[mule] = [shell]

# 4. Build the DataFrame for PyTorch
print("Compiling features...")
data = []
for user_id, targets in interactions.items():
    data.append({
        "userId": user_id,
        "interaction_network": str(targets), # PyTorch script expects a stringified list
        "degree": len(targets) # The out-degree feature
    })

df = pd.DataFrame(data)

# Ensure the 'data' directory exists
os.makedirs('data', exist_ok=True)

# Save to the exact location your GNN reads from
df.to_csv("data/user_features.csv", index=False)

print("\n--- DATASET READY ---")
print(f"Total Users (Nodes): {len(df)}")
print(f"Total Transactions (Edges): {df['degree'].sum()}")
print("Saved to data/user_features.csv. You may now run train_gnn.py.")