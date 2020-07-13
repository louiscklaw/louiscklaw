#!/usr/bin/env python3

from python_graphql_client import GraphqlClient
import feedparser
import httpx
import json
import pathlib
import re
import os, sys

root = pathlib.Path(__file__).parent.resolve()
client = GraphqlClient(endpoint="https://api.github.com/graphql")

TOKEN = os.environ.get("GITHUB_TRAVIS_TOKEN", "")


def make_query(after_cursor=None):
    return """
query {
  viewer {
    repositories(first: 100, privacy: PUBLIC, after:AFTER) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        name
        releases(last:1) {
          totalCount
          nodes {
            name
            publishedAt
            url
          }
        }
      }
    }
  }
}
""".replace(
        "AFTER", '"{}"'.format(after_cursor) if after_cursor else "null"
    )

def fetch_releases(oauth_token):
  repos = []
  releases = []
  repo_names = set()
  has_next_page = True
  after_cursor = None

  while has_next_page:
    data = client.execute(
      query=make_query(after_cursor),
      headers={"Authorization": "Bearer {}".format(oauth_token)},
    )
    print()
    print(json.dumps(data, indent=2))
    print()
    for repo in data["data"]["viewer"]["repositories"]["nodes"]:
      if repo["releases"]["totalCount"] and repo["name"] not in repo_names:
        repos.append(repo)
        try:
          repo_names.add(repo["name"])
          # releases.append({
          #     "repo": repo["name"],
          #     "release": repo["releases"]["nodes"][0]["name"]
          #     .replace(repo["name"], "")
          #     .strip(),
          #     "published_at": repo["releases"]["nodes"][0][
          #         "publishedAt"
          #     ].split("T")[0],
          #     "url": repo["releases"]["nodes"][0]["url"],
          #   })
        except Exception as e:
          print(repo)
          sys.exit()
          raise e

    has_next_page = data["data"]["viewer"]["repositories"]["pageInfo"]["hasNextPage"]
    after_cursor = data["data"]["viewer"]["repositories"]["pageInfo"]["endCursor"]
  return releases

if __name__ == "__main__":
  readme = root / "README.md"
  releases = fetch_releases(TOKEN)

  print(releases)
