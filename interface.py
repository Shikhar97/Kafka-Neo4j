from neo4j import GraphDatabase

class Interface:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

    def bfs(self, start_node, last_node):
        # TODO: Implement this method
        graph_name = "bfs_graph"
        create_graph_query = """
                CALL gds.graph.project( '%s', 'Location', 'TRIP')""" % graph_name
        with self._driver.session() as session:
            result = session.run(create_graph_query)
        get_bfs_nodes = """
        MATCH (pickup:Location{name:%s}), (dropoff:Location{name:%s})
                WITH id(pickup) AS source, id(dropoff) AS targetNodes       
                CALL gds.bfs.stream('%s', {
                            sourceNode: source,
                            targetNodes: targetNodes 
            })
            YIELD path
            RETURN path""" % (start_node, last_node, graph_name)
        with self._driver.session() as session:
            result = session.run(get_bfs_nodes)
            return result.data()

    def pagerank(self, max_iterations, weight_property):
        # TODO: Implement this method
        graph_name = "page_rank_graph"
        create_graph_query = """
        CALL gds.graph.project(
            '%s',
            'Location',
            'TRIP',
            {
                relationshipProperties: '%s'
            })""" % (graph_name, weight_property)
        with self._driver.session() as session:
            result = session.run(create_graph_query)

        write_page_rank = """
        CALL gds.pageRank.write('%s', {
                                maxIterations: %s,
                                dampingFactor: 0.85,
                                relationshipWeightProperty: '%s',
                                writeProperty: 'score'
                                });""" % (graph_name, max_iterations, weight_property)
        with self._driver.session() as session:
            result = session.run(write_page_rank)

        get_node_query = """
        MATCH (n:Location)
                            WITH n, n.score as score
                            ORDER BY score DESC
                            WITH COLLECT(n)[0] as maxNode, COLLECT(n)[-1] as minNode
                            RETURN maxNode, minNode
                        """
        with self._driver.session() as session:
            result = session.run(get_node_query)
            output = result.data()
        # print([output[0]["maxNode"], output[0]["minNode"]])
        return [output[0]["maxNode"], output[0]["minNode"]]

