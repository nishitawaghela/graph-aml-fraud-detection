
// 🕵️‍♂️ PHASE 1: EXPLORATION & DEBUGGING


// 1. View Raw Data (The "Star Field")
// Use this to see if data exists. Most nodes will be unconnected.
MATCH (n) 
RETURN n 
LIMIT 300;

// 2. View Only Active Transactions
// Filters out isolated users and shows only people sending money.
MATCH p=()-[r:TRANSACTION]->() 
RETURN p 
LIMIT 50;



// 🕵️‍♂️ PHASE 2: FRAUD DETECTION ALGORITHMS


// 3. Detect "Smurfing" Rings (Table Output)
// Logic: Find a BOSS who sends 'Placement' money to Mules, 
// who then send 'Layering' money to a SHELL company.
// Threshold: At least 2 Mules must be involved.
MATCH (boss:User)-[t1:TRANSACTION {type: 'Placement'}]->(mule:User)-[t2:TRANSACTION {type: 'Layering'}]->(shell:User)
WITH boss, shell, count(mule) AS mule_count, collect(mule.id) AS mules
WHERE mule_count >= 2
RETURN boss.id AS Criminal_Mastermind, shell.id AS Laundering_Company, mule_count, mules;

// 4. Visualize "Smurfing" Rings (Graph Output)
// Returns the actual PATHS (arrows and circles) instead of a table.
// Use this in Neo4j Browser to see the red spider-web patterns.
MATCH path = (boss:User)-[:TRANSACTION]->(mule:User)-[:TRANSACTION]->(shell:User)
WITH boss, shell, count(mule) as mule_count, collect(path) as paths
WHERE mule_count >= 2
RETURN paths;

