import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components


# 1. SESSION STATE (The "Temporary Database")

# This keeps the data alive while the user is clicking around
if 'data' not in st.session_state:
    # Initialize with some default demo data so it's not empty
    st.session_state['data'] = pd.DataFrame([
        {"source": "BOSS_DEMO", "target": "MULE_1", "type": "Placement", "amount": 10000},
        {"source": "BOSS_DEMO", "target": "MULE_2", "type": "Placement", "amount": 10000},
        {"source": "MULE_1", "target": "SHELL_CO", "type": "Layering", "amount": 9500},
        {"source": "MULE_2", "target": "SHELL_CO", "type": "Layering", "amount": 9500},
    ])

def add_transaction(source, target, tx_type, amount):
    new_row = {"source": source, "target": target, "type": tx_type, "amount": amount}
    st.session_state['data'] = pd.concat([st.session_state['data'], pd.DataFrame([new_row])], ignore_index=True)


# 2. UI CONFIGURATION

st.set_page_config(page_title="AML Fraud Playground", layout="wide")
st.title("AML Fraud Detection: Interactive Playground")
st.markdown("Use the sidebar to **Upload Your Own Data** or **Add Transactions** manually.")
st.markdown("---")

# 3. SIDEBAR: DATA INPUT

st.sidebar.header("Data Input")

# OPTION A: UPLOAD CSV
uploaded_file = st.sidebar.file_uploader("Upload CSV (source, target, amount)", type="csv")
if uploaded_file is not None:
    try:
        uploaded_df = pd.read_csv(uploaded_file)
        # minimal validation
        if {'source', 'target'}.issubset(uploaded_df.columns):
            st.session_state['data'] = uploaded_df
            st.sidebar.success("Dataset Loaded!")
        else:
            st.sidebar.error("CSV must have 'source' and 'target' columns.")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

st.sidebar.markdown("---")

# OPTION B: MANUAL ENTRY
st.sidebar.subheader("Add Single Transaction")
with st.sidebar.form("add_tx_form"):
    s_id = st.text_input("Source User ID", "Bad_Guy")
    t_id = st.text_input("Target User ID", "Mule_Account")
    amt = st.number_input("Amount ($)", min_value=0, value=5000)
    type_tx = st.selectbox("Type", ["Normal", "Placement", "Layering"])
    
    submitted = st.form_submit_button("Add to Graph")
    if submitted:
        add_transaction(s_id, t_id, type_tx, amt)
        st.sidebar.success(f"Added: {s_id} -> {t_id}")


# 4. MAIN DASHBOARD

df = st.session_state['data']

# STATS
col1, col2, col3 = st.columns(3)
unique_users = pd.concat([df['source'], df['target']]).unique()
col1.metric("Total Users", len(unique_users))
col2.metric("Total Transactions", len(df))
col3.metric("Total Volume", f"${df['amount'].sum():,}")

# LAYOUT: GRAPH (Left) | TABLE (Right)
col_graph, col_table = st.columns([2, 1])

with col_graph:
    st.subheader("Live Network Graph")
    
    # PYVIS VISUALIZATION
    net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
    
    # Build Graph from Dataframe
    for _, row in df.iterrows():
        s, t = str(row['source']), str(row['target'])
        
        # Simple Logic: Color "Layering" red
        color = "#ff4b4b" if row.get('type') in ['Layering', 'Placement'] else "#00ff00"
        
        net.add_node(s, label=s, color="#ffffff" if s not in ["BOSS_DEMO", "SHELL_CO"] else "#ff0000", size=15)
        net.add_node(t, label=t, color="#ffffff", size=15)
        net.add_edge(s, t, title=f"${row.get('amount', 0)}", color=color)

    # Save
    net.repulsion(node_distance=100, spring_length=100)
    try:
        net.save_graph("graph.html")
        with open("graph.html", 'r', encoding='utf-8') as f:
            html_string = f.read()
        components.html(html_string, height=600)
    except Exception as e:
        st.error(f"Graph Error: {e}")

with col_table:
    st.subheader("Live Data")
    # Allow user to delete data (Reset)
    if st.button("Clear All Data"):
        st.session_state['data'] = pd.DataFrame(columns=["source", "target", "type", "amount"])
        st.rerun()
        
    st.dataframe(df, height=500, width='stretch')