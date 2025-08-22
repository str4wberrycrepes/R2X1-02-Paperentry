# ephemera

# For importing research paper table into neo4j nodes
# IMPORTANT - assumes the neo4j database you are pushing into is empty

# import
from neo4j import GraphDatabase # Neo4j
import pandas # Pandas
import json # Config

# -------------------------------
# Utility Functions
# -------------------------------
def query_database(driver, query):
    """
    Execute a Cypher query on Neo4j.

    Args:
        driver (neo4j.Driver): The Neo4j driver.
        query (str): Cypher query to run.
    """
    return driver.execute_query(query, database_="neo4j")

# -------------------------------
# Main Import Function
# -------------------------------
def import_papers(file_path, conf_path="../../conf.json"):
    """
    Import research papers and their keywords from an Excel file into Neo4j.

    Args:
        file_path (str): Path to the Excel file.
        conf_path (str): Path to JSON config containing Neo4j credentials.
    """
    # Load Neo4j config
    print("Opening config...")
    with open(conf_path, 'r') as file:
        conf = json.load(file)

    # Neo4j connection details
    url = conf["url"]
    neo4j_auth = (conf["user"], conf["pass"])

    # Read Excel file
    print("Reading Excel file...")
    data = pd.read_excel(file_path)

    with GraphDatabase.driver(url, auth=neo4j_auth) as driver:
        # Verify connection
        driver.verify_connectivity()

        # -------------------------------------------------
        # Step 1: Create paper nodes
        # -------------------------------------------------
        print("Creating paper nodes...")
        if not data.empty:
            paper_nodes = [
                f'(:paper {{name:"{row.title}", '
                f'rescode:"{row.batch}_{row.rescode}", '
                f'authors:"{row.authors}", '
                f'batch:"{row.batch}"}})'
                for _, row in data.iterrows()
            ]
            query = "CREATE " + ", ".join(paper_nodes)
            query_database(driver, query)

        # -------------------------------------------------
        # Step 2: Create keyword nodes
        # -------------------------------------------------
        print("Creating keyword nodes...")
        keywords = set()

        for _, row in data.iterrows():
            paper_keywords = str(row.keywords).split(", ")
            keywords.update(paper_keywords)

        if keywords:
            keyword_nodes = [
                f'(:keyword {{name:"{kw}"}})' for kw in keywords
            ]
            query = "CREATE " + ", ".join(keyword_nodes)
            query_database(driver, query)

        # -------------------------------------------------
        # Step 3: Create keyword-paper relationships
        # -------------------------------------------------
        print("Creating relationships...")
        for kw in keywords:
            paper_titles = [
                f'"{row.title}"'
                for _, row in data.iterrows()
                if kw in str(row.keywords).split(", ")
            ]

            if paper_titles:
                titles_str = ", ".join(paper_titles)
                query = (
                    f'MATCH (k:keyword {{name:"{kw}"}}) '
                    f'MATCH (p:paper) '
                    f'WHERE p.name IN [{titles_str}] '
                    f'CREATE (k)-[:IN]->(p)'
                )
                query_database(driver, query)

        print("done!")

if __name__ == "__main__":
    file_path = input("Enter filepath to Excel file: ")
    import_papers(file_path)