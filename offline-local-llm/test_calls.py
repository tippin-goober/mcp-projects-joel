import requests, json

URL = "http://127.0.0.1:8765/mcp"

def call(method, params, id):
    r = requests.post(URL, json={"jsonrpc":"2.0","id":id,"method":method,"params":params})
    print(f"\n== {method} ==")
    print(json.dumps(r.json(), indent=2))

if __name__ == "__main__":
    call("run_python", {"code":"print(sum([1,2,3]))"}, 1)
    call("list_files", {"path":"."}, 2)
    call("sql_query", {"query":"select * from notes"}, 3)
