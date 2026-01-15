// 1. Create a Graph Projection named 'bankGraph'
CALL gds.graph.project(
  'bankGraph',       // Name of the in-memory graph
  'User',            // Node Label
  'TRANSACTION'      // Relationship Type
)
YIELD graphName, nodeCount, relationshipCount;

// 2. Stream PageRank results
CALL gds.pageRank.stream('bankGraph')
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS user, score
// Filter for high scores (Top influential nodes)
ORDER BY score DESC
RETURN user.id, score
LIMIT 10;

// 3. Find Connected Components (Islands)
CALL gds.wcc.stream('bankGraph')
YIELD nodeId, componentId
WITH gds.util.asNode(nodeId) AS user, componentId
RETURN componentId, count(*) AS group_size, collect(user.id) AS members
ORDER BY group_size DESC;