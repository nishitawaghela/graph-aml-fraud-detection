import time
import random
from collections import defaultdict

print("1. Loading mock 70,500 edge graph into memory...")
graph = defaultdict(list)
for _ in range(70500):
    sender = f"U{random.randint(1, 15000)}"
    receiver = f"U{random.randint(1, 15000)}"
    graph[sender].append(receiver)

def get_2_hop_neighborhood(target_node):
    hop_1 = graph.get(target_node, [])
    hop_2 = []
    for neighbor in hop_1:
        hop_2.extend(graph.get(neighbor, []))
    return hop_1, hop_2

print("2. Running 100 random 2-hop traversals...")
latencies = []

for _ in range(100):
    test_node = f"U{random.randint(1, 15000)}"
    start_time = time.perf_counter() 
    get_2_hop_neighborhood(test_node)
    end_time = time.perf_counter()
    latencies.append((end_time - start_time) * 1000) 

avg_latency = sum(latencies) / len(latencies)
print(f"\n--- RESUME METRICS PROOF ---")
print(f"Average Latency for 2-hop traversal: {avg_latency:.4f} ms")