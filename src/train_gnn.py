import pandas as pd
import torch
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
import ast

# 1. LOAD & PREPROCESS DATA
print("Loading data...")
df = pd.read_csv("data/user_features.csv")

# Create Labels (0 = Legit, 1 = Fraud)
df['label'] = df['userId'].apply(lambda x: 1 if "MULE" in x or "BOSS" in x or "SHELL" in x else 0)

# Parse the 'interaction_network' column
df['interaction_network'] = df['interaction_network'].apply(ast.literal_eval)

# Map User IDs to numerical indices for PyTorch
id_mapping = {user_id: i for i, user_id in enumerate(df['userId'])}

# 2. BUILD THE GRAPH STRUCTURE (EDGES)
source_nodes = []
target_nodes = []

for idx, row in df.iterrows():
    source_idx = id_mapping[row['userId']]
    targets = row['interaction_network']
    if targets:
        for target_id in targets:
            if target_id in id_mapping:
                target_idx = id_mapping[target_id]
                source_nodes.append(source_idx)
                target_nodes.append(target_idx)

edge_index = torch.tensor([source_nodes, target_nodes], dtype=torch.long)

# 3. PREPARE NODE FEATURES (X)
features = df[['degree']].values
scaler = StandardScaler()
features = scaler.fit_transform(features) 
x = torch.tensor(features, dtype=torch.float)
y = torch.tensor(df['label'].values, dtype=torch.long)

# 4. 80/20 STRATIFIED SPLIT MASKS
num_nodes = df.shape[0]
indices = range(num_nodes)
labels = df['label'].values

train_idx, test_idx = train_test_split(indices, test_size=0.20, stratify=labels, random_state=42)

train_mask = torch.zeros(num_nodes, dtype=torch.bool)
test_mask = torch.zeros(num_nodes, dtype=torch.bool)

train_mask[train_idx] = True
test_mask[test_idx] = True

data = Data(x=x, edge_index=edge_index, y=y, train_mask=train_mask, test_mask=test_mask)

# 5. DEFINE THE GNN MODEL
class FraudGNN(torch.nn.Module):
    def __init__(self):
        super(FraudGNN, self).__init__()
        self.conv1 = GCNConv(1, 16) 
        self.conv2 = GCNConv(16, 2)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, training=self.training)
        x = self.conv2(x, edge_index)
        return F.log_softmax(x, dim=1)

# 6. TRAIN THE MODEL (With Masking & Class Weights)
model = FraudGNN()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

train_labels = data.y[data.train_mask]
num_normal = (train_labels == 0).sum().item()
num_fraud = (train_labels == 1).sum().item()

weight_normal = 1.0
weight_fraud = num_normal / (num_fraud + 1e-5) 
class_weights = torch.tensor([weight_normal, weight_fraud], dtype=torch.float)

print("Training GNN on 80% of the network...")
model.train()
for epoch in range(201):
    optimizer.zero_grad()
    out = model(data)
    
    loss = F.nll_loss(out[data.train_mask], data.y[data.train_mask], weight=class_weights)
    loss.backward()
    optimizer.step()
    
    if epoch % 20 == 0:
        print(f"Epoch {epoch} | Training Loss: {loss.item():.4f}")

# 7. EVALUATE (Blind Test)
model.eval()
with torch.no_grad():
    raw_output = model(data)
    pred = raw_output.argmax(dim=1)

# Extract targets and predictions for the test set
test_actual = data.y[data.test_mask].cpu().numpy()
test_pred = pred[data.test_mask].cpu().numpy()

# Calculate AUC-ROC Score
probabilities = torch.exp(raw_output)
test_fraud_probs = probabilities[data.test_mask, 1].cpu().numpy()
auc_roc = roc_auc_score(test_actual, test_fraud_probs)

print(f"\n--- AUC-ROC Score: {auc_roc:.4f} ---")

# Resume Metrics Proof
print("\n--- INDISPUTABLE ML METRICS (STRICT 80/20 SPLIT) ---")
print(classification_report(test_actual, test_pred, digits=3, target_names=['Normal', 'Fraud']))

# Example Predictions
print("\nExample Predictions (From unseen Test Set):")
test_indices = [i for i, val in enumerate(data.test_mask) if val]
for i in test_indices[:10]:
    status = "FRAUD" if pred[i] == 1 else "SAFE"
    actual = "FRAUD" if data.y[i] == 1 else "SAFE"
    print(f"User {df.iloc[i]['userId']}: Pred={status} | Actual={actual}")