# ephemera

# --- Imports ---
import rdflib  # RDF and OWL parsing
from neo4j import GraphDatabase  # Neo4j driver
from urllib.parse import urlparse  # Extract fragment from URIs
import json  # Config file loading

# -------------------------------
# Utility Functions
# -------------------------------
def query_database(driver, query):
    """
    Execute a Cypher query in Neo4j.

    Args:
        driver (neo4j.Driver): The Neo4j database driver.
        query (str): Cypher query string.

    Returns:
        tuple: (records, summary, keys) from query execution.
    """
    records, summary, keys = driver.execute_query(
        query,
        database_="neo4j",
    )

    return [records, summary, keys]

def get_relationships(graph, classes, relation):
    """
    Extract relationships of a given type between classes in the RDF graph.

    Args:
        graph (rdflib.Graph): Parsed RDF graph.
        classes (dict): Map of URI -> class name.
        relation (rdflib.term.URIRef): Relationship predicate to search for.

    Returns:
        list[tuple]: List of (source, target) relationships.
    """
    results = []
    for s, p, o in graph.triples((None, relation, None)):
        s, o = str(s), str(o)
        if s in classes and o in classes:
            results.append((classes[s], classes[o]))
    return results

def parse_rdf(file_path):
    """
    Parse an RDF/OWL file and extract ontology structure.

    Args:
        file_path (str): Path to the RDF/OWL file.

    Returns:
        dict: {
            'classes': list[str],
            'subclasses': list[tuple],
            'disjoints': list[tuple]
        }
    """
    g = rdflib.Graph().parse(file_path, format="xml")

    # Extract classes
    classes = {}
    for s, p, o in g.triples((None, rdflib.RDF.type, rdflib.OWL.Class)):
        class_url = str(s)
        class_name = urlparse(class_url).fragment or class_url
        classes[class_url] = class_name

    # Extract subclass & disjoint relationships
    subclasses = get_relationships(g, classes, rdflib.RDFS.subClassOf)
    disjoints = get_relationships(g, classes, rdflib.OWL.disjointWith)

    return {
        'classes': list(classes.values()),
        'subclasses': subclasses,
        'disjoints': disjoints
    }

# -------------------------------
# Neo4j Import
# -------------------------------
def import_to_neo4j(data, conf):
    """
    Import parsed ontology data into a Neo4j graph database.

    Args:
        data (dict): Parsed ontology data.
        conf (dict): Neo4j configuration {'url': str, 'user': str, 'pass': str}.
    """
    url = conf["url"]
    neo4j_auth = (conf["user"], conf["pass"])

    with GraphDatabase.driver(url, auth=neo4j_auth) as driver:
        # Verify connection
        try:
            driver.verify_connectivity()
        except Exception:
            print("\033[91mFATAL: Could not connect to Neo4j. Check URL/credentials.\033[0m")
            exit(1)

        # Clear database
        query_database(driver, "MATCH (n) DETACH DELETE n")

        # Create class nodes
        if data["classes"]:
            create_query = "CREATE " + ", ".join(
                f'(:Class {{name: "{name}"}})' for name in data["classes"]
            )
            query_database(driver, create_query)

        # Create subclass relationships
        for sub, sup in data["subclasses"]:
            query = f"""
                MATCH (sub:Class {{name: "{sub}"}})
                MATCH (sup:Class {{name: "{sup}"}})
                CREATE (sub)-[:SUBCLASS_OF]->(sup)
            """
            query_database(driver, query)

        # Create disjoint relationships
        for a, b in data["disjoints"]:
            query = f"""
                MATCH (a:Class {{name: "{a}"}})
                MATCH (b:Class {{name: "{b}"}})
                CREATE (a)-[:DISJOINT_WITH]->(b)
            """
            query_database(driver, query)

        print("Data successfully imported to Neo4j.")


# -------------------------------
# Main Script
# -------------------------------
if __name__ == "__main__":
    # Path to RDF file
    rdf_path = input("Enter filepath to Ontology (rdf) file: ")

    # Parse RDF
    ontology_data = parse_rdf(rdf_path)

    # Display extracted data
    print("Classes:", ontology_data['classes'])
    print("Subclass relations:", ontology_data['subclasses'])
    print("Disjoint relations:", ontology_data['disjoints'])

    # Load Neo4j config
    print("Opening config...")
    with open('../../conf.json', 'r') as file:
        config = json.load(file)

    # Import to Neo4j
    import_to_neo4j(ontology_data, config)