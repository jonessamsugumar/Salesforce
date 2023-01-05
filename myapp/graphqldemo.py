"""

import graphene
import json

class User(graphene.ObjectType):
    id = graphene.ID()
    username = graphene.String()
    last_login = graphene.DateTime()

class Query(graphene.ObjectType):
    users = graphene.List(User)

    def resolve_is_staff(self,info):
        return True
    is_staff = graphene.Boolean()


schema = graphene.Schema(query = Query)

result = schema.execute(
    '''
    query {
    user(login: "jonessamsugumar3"){
        issues(last : 10, orderBy : { field: CREATED_AT, direction: DESC}){
            nodes{
                title,
                body,
                closedAt
            }
        }
    }
    }
    '''
)

items = dict(result.data.items())
print(items)

"""

import requests

#from __future__ import print_function
import argparse
import json
import os
from urllib.request import urlopen, Request

from python_graphql_client import GraphqlClient

client = GraphqlClient(endpoint="https://api.github.com/graphql")


#Enter the API in API Key field
GITHUB_API_TOKEN = os.environ.get("GITHUB_API_TOKEN")


headers = {"Authorization": "API Key"}


def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section.
  request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
  if request.status_code == 200:
        return request.json()
  else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

  query = """
{
{
  organization(login: $org) {
    membersWithRole(first: 100, after: $after) {
      edges {
        cursor
        node {
          login
          id
        }
        role
      }
    }
  }
}
"""


#Get star details of a repository
def demo(args):
  first_num = args.count
  qs = ["sort:stars", "stars:>1"]
  if args.repo:
    qs += [args.repo]

  if args.new_created:
    from datetime import datetime, timedelta
    qs += ["created:>={:%Y-%m-%d}".format(datetime.now() + timedelta(weeks=-1))]
  if args.new_pushed:
    from datetime import datetime, timedelta
    qs += ["pushed:>={:%Y-%m-%d}".format(datetime.now() + timedelta(weeks=-1))]

    query = """
query {
  search(type: REPOSITORY, query: "%s", first: %d) {
    userCount
    edges {
      node {
        Repository {
          name
          description
          url
        }
      }
    }
  }
}
    """ % (" ".join(qs), first_num)
  req = Request("https://api.github.com/graphql", json.dumps({"query": query}).encode('utf-8'))
  req.add_header("Authorization", "Bearer {}".format(GITHUB_API_TOKEN))
  response = urlopen(req)

  try:
        for edge in json.loads(response.read())["data"]["search"]["edges"]:
            node = edge["node"]
            result = "{} {}".format(
                node["stargazers"]["totalCount"],
                node["name"]
            )
            if args.url and node.get("url"):
                result += " ({})".format(node["url"])
            if args.desc and node.get("description"):
                result += "\n- {}\n".format(node["description"].encode("utf8"))

            print(result)
  except Exception as e:
        print("Code not working")

def make_query(point=None):
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
        "AFTER", '"{}"'.format(point) if point else "null"
    )

def fetch_releases(token):
    repo_list = []
    releases = []
    repo_names = set()
    has_next_page = True
    after_cursor = None

    while has_next_page:
        data = client.execute(
            query=make_query(after_cursor),
            headers={"Authorization": "Bearer {}".format(token)},
        )
        print()
        print(json.dumps(data, indent=4))
        print()
        for repo in data["data"]["viewer"]["repositories"]["nodes"]:
            if repo["releases"]["totalCount"] and repo["name"] not in repo_names:
                repo_list.append(repo)
                repo_names.add(repo["name"])
                releases.append(
                    {
                        "repo": repo["name"],
                        "release": repo["releases"]["nodes"][0]["name"]
                        .replace(repo["name"], "")
                        .strip(),
                        "published_at": repo["releases"]["nodes"][0][
                            "publishedAt"
                        ].split("T")[0],
                        "url": repo["releases"]["nodes"][0]["url"],
                    }
                )
        has_next_page = data["data"]["viewer"]["repositories"]["pageInfo"][
            "hasNextPage"
        ]
        after_cursor = data["data"]["viewer"]["repositories"]["pageInfo"]["endCursor"]
    return releases

def main():
    parser = argparse.ArgumentParser(prog="githubstars", description="List repository stars and info through Github v4 GraphQL API")
    parser.add_argument("repo", help="repository name to search", nargs="?")
    parser.add_argument("--count", help="number of repositories to show", default=10, type=int, metavar="")
    parser.add_argument("--desc", help="show repo description", action="store_true")
    parser.add_argument("--new-created", help="created this week", action="store_true")
    parser.add_argument("--new-pushed", help="pushed this week", action="store_true")
    parser.add_argument("--url", help="show repo url", action="store_true")
    parser.add_argument("--verbose", help="show request detail", action="store_true")
    parser.add_argument("--version", help="show version", action="store_true")

    args = parser.parse_args()
    demo(args)
    fetch_releases(GITHUB_API_TOKEN)

    result = run_query(query) # Execute the query
    remaining_rate_limit = result["data"]["rateLimit"]["remaining"] # Drill down the dictionary
    print("Remaining rate limit - {}".format(remaining_rate_limit))      


if __name__ == "__main__":
    main()




