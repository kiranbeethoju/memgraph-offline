"""Read the sample film and company graphs from local Dgraph.

Requires the database from this repo to be running. Startup loads the data:

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

FILMS = """{
  films(func: type(Movie), orderasc: released) {
    title
    released
    in_genre { name }
    directors: ~directed { name }
  }
}"""

COMPANIES = """{
  companies(func: type(Company), orderasc: name) {
    name
    industry
    founded
    people: ~works_at { name }
    projects: ~owned_by { name }
  }
}"""


def query(client: pydgraph.DgraphClient, dql: str) -> dict:
    result = client.txn(read_only=True).query(dql)
    return json.loads(result.json)


def print_films(films: list) -> None:
    print(f"Films: {len(films)}")
    for film in films:
        genres = ", ".join(item["name"] for item in film.get("in_genre", []))
        directors = ", ".join(item["name"] for item in film.get("directors", []))
        print(f"  {film['released']} {film['title']} ({genres}) directed by {directors}")


def print_companies(companies: list) -> None:
    print(f"Companies: {len(companies)}")
    for company in companies:
        people = ", ".join(item["name"] for item in company.get("people", []))
        projects = ", ".join(item["name"] for item in company.get("projects", []))
        print(f"  {company['name']} ({company['industry']}) people: {people}; projects: {projects}")


def main() -> None:
    stub = pydgraph.DgraphClientStub(GRPC)
    client = pydgraph.DgraphClient(stub)
    try:
        films = query(client, FILMS)["films"]
        companies = query(client, COMPANIES)["companies"]
        print(f"Connected to {GRPC}")
        if not films and not companies:
            print("No sample data found. Run ./scripts/seed.sh after Alpha is up.")
            return
        print_films(films)
        print_companies(companies)
    finally:
        stub.close()


if __name__ == "__main__":
    main()
