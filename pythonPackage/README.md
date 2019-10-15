# scripts
1) Download the leanix_python_client-0.2.0.whl file to your project directory
2) Install the package with 
```python
pip install leanix_python_client-0.2.0.whl
```
3) Import the Python client with:
```python
import lxpy
```
4) Create a configuration object:
```python
config = lxpy.ClientConfiguration(
    base_url=environ.get('BASE_URL', 'customer.leanix.net'),
    api_token=environ.get('API_TOKEN', 'my-api-token')
)
```
5) Create an API Client with the configuration object
```python
pathfinder = lxpy.Pathfinder(config)
```
6) Use any of the swagger endpoints. Example with GraphQL:
```python
query = {
    "query": "{allFactSheets{edges{node{name}}}",
    "variables": {}
}
results = pathfinder.post('/graphql', body=query)
```