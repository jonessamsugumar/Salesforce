import requests

url = 'https://api.github.com/graphql'
json = { 'query' : '{ viewer { repositories(first: 30) { totalCount pageInfo { hasNextPage endCursor } edges { node { name } } } } }' }
#api_token = "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"
api_token = "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"
headers = {'Authorization': 'token %s' % api_token}

r = requests.post(url=url, json=json, headers=headers)
print (r.text)