import pandas as pd
import torch
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import ast

# 1. LOAD & PREPROCESS DATA
print("Loading data...")
df = pd.read_csv("data/user_features.csv")

# Create Labels (0 = Legit, 1 = Fraud)
# In the real world, you'd have actual labels. Here, we use our naming convention.
df['label'] = df['userId'].apply(lambda x: 1 if "MULE" in x or "BOSS" in x or "SHELL" in x else 0)

# Parse the 'interaction_network' column (it was saved as a string "[...]")
df['interaction_network'] = df['interaction_network'].apply(ast.literal_eval)

# Map User IDs to numerical indices (0, 1, 2...) for PyTorch
id_mapping = {user_id: i for i, user_id in enumerate(df['userId'])}

# 2. BUILD THE GRAPH STRUCTURE (EDGES)
source_nodes = []
target_nodes = []

for idx, row in df.iterrows():
    source_idx = id_mapping[row['userId']]
    targets = row['interaction_network']
    if targets: # If user sent money to anyone
        for target_id in targets:
            if target_id in id_mapping: # Ensure target exists
                target_idx = id_mapping[target_id]
                source_nodes.append(source_idx)
                target_nodes.append(target_idx)

# Convert to PyTorch Tensor (2 x Number_of_Edges)
edge_index = torch.tensor([source_nodes, target_nodes], dtype=torch.long)

# 3. PREPARE NODE FEATURES (X)
# We use 'degree' and 'total_sent' as inputs. 
# Ideally, we'd add more (avg_transaction_val, time_variance, etc.)
#features = df[['degree', 'total_sent']].values
# We only give it 'degree'. We hide the money amount. 
# Now it HAS to look at the graph structure to find the "Star" shape.
features = df[['degree']].values
scaler = StandardScaler()
features = scaler.fit_transform(features) # Normalize data (crucial for AI)
x = torch.tensor(features, dtype=torch.float)
y = torch.tensor(df['label'].values, dtype=torch.long)

# 4. DEFINE THE GNN MODEL (Graph Convolutional Network)
class FraudGNN(torch.nn.Module):
    def __init__(self):
        super(FraudGNN, self).__init__()
        # Layer 1: Takes 2 features (degree, amount) -> Hidden Layer 16
        #self.conv1 = GCNConv(2, 16) 
        self.conv1 = GCNConv(1, 16) # Expects 1 feature (Degree only)
        # Layer 2: Hidden 16 -> Output 2 (Safe vs Fraud)
        self.conv2 = GCNConv(16, 2)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        
        # Pass 1: Aggregates info from immediate neighbors
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, training=self.training)
        
        # Pass 2: Aggregates info from neighbors of neighbors (2 hops)
        x = self.conv2(x, edge_index)
        
        return F.log_softmax(x, dim=1)

# 5. TRAIN THE MODEL
model = FraudGNN()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
data = Data(x=x, edge_index=edge_index, y=y)

print("Training GNN...")
model.train()
for epoch in range(201):
    optimizer.zero_grad()
    out = model(data)
    loss = F.nll_loss(out, data.y)
    loss.backward()
    optimizer.step()
    
    if epoch % 20 == 0:
        print(f"Epoch {epoch} | Loss: {loss.item():.4f}")

# 6. EVALUATE
model.eval()
pred = model(data).argmax(dim=1)
correct = (pred == data.y).sum()
acc = int(correct) / int(data.y.shape[0])
print(f"Final Accuracy: {acc:.2%}")

# Show some examples
print("\n🔍 Example Predictions:")
for i in range(10):
    status = "FRAUD" if pred[i] == 1 else "SAFE"
    actual = "FRAUD" if data.y[i] == 1 else "SAFE"
    print(f"User {df.iloc[i]['userId']}: Pred={status} | Actual={actual}")