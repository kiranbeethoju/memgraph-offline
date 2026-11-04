"""Connect to local Memgraph and run a small Cypher query.

Requires the database from this repo to be running:

    ./load-and-start.sh

Then:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python python/quickstart.py

Override the address with MEMGRAPH_URI if Memgraph is not on this machine.
"""

import os

from neo4j import GraphDatabase

URI = os.environ.get("MEMGRAPH_URI", "bolt://localhost:7687")
USER = os.environ.get("MEMGRAPH_USER", "")
PASSWORD = os.environ.get("MEMGRAPH_PASSWORD", "")


def seed_and_query(session) -> None:
    session.run(
        """
        MERGE (a:User {name: $alice})
        MERGE (b:User {name: $bob})
        MERGE (a)-[:KNOWS]->(b)
        """,
        alice="Alice",
        bob="Bob",
    )
    result = session.run(
        """
        MATCH (user:User)-[:KNOWS]->(friend)
        RETURN user.name AS user, friend.name AS friend
        """
    )
    print("Friendships:")
    for record in result:
        print(f"  {record['user']} KNOWS {record['friend']}")


def run_pagerank(session) -> None:
    result = session.run(
        """
        CALL pagerank.get()
        YIELD node, rank
        RETURN node.name AS name, rank
        ORDER BY rank DESC
        """
    )
    print("PageRank:")
    for record in result:
        print(f"  {record['name']}: {record['rank']:.4f}")


def main() -> None:
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    try:
        driver.verify_connectivity()
        print(f"Connected to {URI}")
        with driver.session() as session:
            seed_and_query(session)
            run_pagerank(session)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
