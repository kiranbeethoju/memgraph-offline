"""Connect to local Dgraph, store two people, and read them back.

Requires the database from this repo to be running:

    ./load-and-start.sh

Then:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python python/quickstart.py

Override the address with DGRAPH_GRPC if Alpha is not on this machine.
The value is host:port with no scheme, for example 192.168.1.20:9080.
"""

import json
import os

import pydgraph

GRPC = os.environ.get("DGRAPH_GRPC", "localhost:9080")

SCHEMA = """
name: string @index(exact) .
age: int .
friend: [uid] @reverse .

type Person {
    name
    age
    friend
}
"""


def set_schema(client: pydgraph.DgraphClient) -> None:
    client.alter(pydgraph.Operation(schema=SCHEMA))


def alice_exists(client: pydgraph.DgraphClient) -> bool:
    result = client.txn(read_only=True).query(
        '{ all(func: eq(name, "Alice")) { uid } }'
    )
    return bool(json.loads(result.json)["all"])


def store_people(client: pydgraph.DgraphClient) -> None:
    if alice_exists(client):
        return
    people = {
        "uid": "_:alice",
        "dgraph.type": "Person",
        "name": "Alice",
        "age": 26,
        "friend": {
            "uid": "_:bob",
            "dgraph.type": "Person",
            "name": "Bob",
            "age": 24,
        },
    }
    txn = client.txn()
    try:
        txn.mutate(set_obj=people)
        txn.commit()
    finally:
        txn.discard()


def query_alice(client: pydgraph.DgraphClient) -> None:
    query = """query all($a: string) {
        all(func: eq(name, $a)) {
            name
            age
            friend { name age }
        }
    }"""
    result = client.txn(read_only=True).query(query, variables={"$a": "Alice"})
    people = json.loads(result.json)["all"]
    print(f"Connected to {GRPC}")
    print(f"People named Alice: {len(people)}")
    for person in people:
        friends = ", ".join(friend["name"] for friend in person.get("friend", []))
        print(f"  {person['name']} age {person['age']} friend {friends}")


def main() -> None:
    stub = pydgraph.DgraphClientStub(GRPC)
    client = pydgraph.DgraphClient(stub)
    try:
        set_schema(client)
        store_people(client)
        query_alice(client)
    finally:
        stub.close()


if __name__ == "__main__":
    main()
