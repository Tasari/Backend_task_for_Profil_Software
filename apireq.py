import requests
import ast
r = requests.get("http://www.omdbapi.com/", 
params = {"t":"se7en", "apikey":"b88afbe7"},
)

print(r.status_code, r.reason)
print(r)
x = r.text
x = ast.literal_eval(x)
print(x)
print(x['Released'])