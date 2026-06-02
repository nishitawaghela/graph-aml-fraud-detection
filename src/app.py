import streamlit as st
from neo4j import GraphDatabase
from pyvis.network import Network
import pandas as pd
import streamlit.components.v1 as components

# CONFIGURATION
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "12345678") 

# 1. CONNECT TO DATABASE
@st.cache_resource
def get_driver():
    return GraphDatabase.driver(URI, auth=AUTH)

def get_user_data(user_id):
    driver = get_driver()
    query = """
    MATCH (u:User {id: $id})
    OPTIONAL MATCH (u)-[r:TRANSACTION]-(other)
    RETURN u, collect(r) as txs, collect(other) as others
    """
    with driver.session() as session:
        result = session.run(query, id=user_id).single()
        return result

def get_high_risk_users():
    driver = get_driver()
    # Find users involved in 'Structuring' (Many small transactions)
    query = """
    MATCH (u:User)-[r:TRANSACTION]->()
    WITH u, count(r) as tx_count
    WHERE tx_count > 5
    RETURN u.id as user_id
    LIMIT 10
    """
    with driver.session() as session:
        return [record["user_id"] for record in session.run(query)]

# 2. UI LAYOUT
st.set_page_config(page_title="AML Fraud Detection", layout="wide")

st.title("AML Fraud Detection System")
st.markdown("---") # Divider

# Sidebar
st.sidebar.header(" Investigation Console")
high_risk_users = get_high_risk_users()
selected_user = st.sidebar.selectbox("Select Flagged User", high_risk_users)
user_input = st.sidebar.text_input("Manual User Search", selected_user)

if st.sidebar.button("Run Analysis", type="primary"):
    target_id = user_input if user_input else selected_user
    
    # 3. FETCH DATA
    data = get_user_data(target_id)
    
    if not data:
        st.error(f"User {target_id} not found!")
    else:
        # 4. TOP ROW: METRICS
        # We use 4 columns to spread out the KPI cards
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        tx_count = len(data['txs'])
        risk_score = min(100, tx_count * 10) # Placeholder heuristic
        
        kpi1.metric("Target ID", target_id)
        kpi2.metric("Total Transactions", tx_count)
        kpi3.metric("Risk Score", f"{risk_score}/100")
        
        with kpi4:
            # FIX: Use standard if/else block to avoid printing raw objects
            if risk_score > 50:
                st.error("HIGH RISK")
            else:
                st.success("SAFE USER")

        st.markdown("---")

        # 5. MAIN CONTENT: GRAPH + TABLE (Side-by-Side)
        # Ratio: 2 parts Graph, 1 part Table
        col_graph, col_table = st.columns([2, 1]) 
        
        with col_graph:
            st.subheader("Network Topology")
            # Create PyVis Network
            net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
            
            # Add Central Node
            net.add_node(target_id, label=target_id, color="#ff4b4b", title="Target", size=20)
            
            # Add Neighbors
            if data['others']:
                for i, other in enumerate(data['others']):
                    tx = data['txs'][i]
                    # Color logic: Red for Layering, Green for Normal
                    color = "#00ff00" if tx['type'] == 'Normal' else "#ff0000"
                    
                    # Add Node
                    net.add_node(other['id'], label=other['id'], title=f"Type: {tx['type']}", size=15)
                    
                    # Add Edge
                    label = f"${tx['amount']}"
                    net.add_edge(target_id, other['id'], title=label, color=color, width=2)

            # Physics settings for better stability
            net.repulsion(node_distance=100, central_gravity=0.2, spring_length=100, spring_strength=0.05)

            # Save and Render
            net.save_graph("graph.html")
            with open("graph.html", 'r', encoding='utf-8') as f:
                html_string = f.read()
            components.html(html_string, height=600, scrolling=False)

        with col_table:
            st.subheader("Transaction Log")
            if data['txs']:
                tx_data = [{"To/From": data['others'][i]['id'], "Amt": t['amount'], "Type": t['type']} 
                          for i, t in enumerate(data['txs'])]
                df_tx = pd.DataFrame(tx_data)
                # Show a clean interactive table
                st.dataframe(df_tx, height=600, use_container_width=True)
            else:
                st.info("No transactions found.")