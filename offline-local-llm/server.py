import json, os, sqlite3, sys, io
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class RPCRequest(BaseModel):
    jsonrpc: str
    method: str
    id: str | int | None = None
    params: dict | None = None

def rpc_result(id, result):
    return {"jsonrpc": "2.0", "id": id, "result": result}

def rpc_error(id, code, message):
    return {"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}}

def tool_run_python(params):
    code = params.get("code","")
    old_stdout, old_stderr = sys.stdout, sys.stderr
    buf_out, buf_err = io.StringIO(), io.StringIO()
    sys.stdout, sys.stderr = buf_out, buf_err
    try:
        exec(code, {"__builtins__": {"print": print, "range": range, "len": len}}, {})
        return {"stdout": buf_out.getvalue(), "stderr": buf_err.getvalue()}
    except Exception as e:
        return {"stdout": buf_out.getvalue(), "stderr": f"{type(e).__name__}: {e}"}
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr

def tool_list_files(params):
    path = params.get("path",".")
    try:
        files = os.listdir(path)
        return {"path": os.path.abspath(path), "files": files}
    except Exception as e:
        return {"error": str(e)}

def tool_sql_query(params):
    q = params.get("query","")
    if not q.lower().strip().startswith(("select", "pragma")):
        return {"error": "Read-only. Use SELECT/PRAGMA only."}
    try:
        con = sqlite3.connect("db.sqlite")
        con.row_factory = sqlite3.Row
        rows = con.execute(q).fetchall()
        con.close()
        return {"rows": [dict(r) for r in rows]}
    except Exception as e:
        return {"error": str(e)}

TOOLS = {
    "run_python": tool_run_python,
    "list_files": tool_list_files,
    "sql_query": tool_sql_query,
}

@app.post("/mcp")
async def mcp_endpoint(req: Request):
    data = await req.json()
    rpc = RPCRequest(**data)
    if rpc.method not in TOOLS:
        return rpc_error(rpc.id, -32601, f"Unknown method {rpc.method}")
    try:
        result = TOOLS[rpc.method](rpc.params or {})
        return rpc_result(rpc.id, result)
    except Exception as e:
        return rpc_error(rpc.id, -32000, str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8765)
