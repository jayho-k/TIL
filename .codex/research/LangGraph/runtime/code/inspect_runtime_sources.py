"""Print pinned source identities and symbol locations used in runtime notes."""

import ast
import hashlib
import json
from importlib.metadata import version
from pathlib import Path


FILES = [
    "langgraph/graph/state.py", "langgraph/graph/message.py",
    "langgraph/channels/last_value.py", "langgraph/channels/binop.py",
    "langgraph/channels/delta.py", "langgraph/pregel/main.py",
    "langgraph/pregel/_read.py", "langgraph/pregel/_write.py",
    "langgraph/pregel/_algo.py", "langgraph/pregel/_loop.py",
    "langgraph/pregel/_runner.py", "langgraph/pregel/_checkpoint.py",
    "langgraph/pregel/_messages.py", "langgraph/types.py",
    "langgraph/errors.py", "langgraph/checkpoint/base/__init__.py",
    "deepagents/graph.py", "deepagents/_messages_reducer.py",
    "langgraph/pregel/_retry.py", "langgraph/pregel/_executor.py",
    "langgraph/_internal/_retry.py", "langgraph/_internal/_timeout.py",
    "langgraph/_internal/_runnable.py", "langgraph/_internal/_cache.py",
    "langgraph/runtime.py", "langgraph/config.py",
    "langgraph/cache/memory/__init__.py",
]


class Symbols(ast.NodeVisitor):
    def __init__(self):
        self.scope = []
        self.items = []

    def record(self, node, kind):
        self.items.append({"name": ".".join([*self.scope, node.name]), "kind": kind,
                           "line": node.lineno, "end_line": node.end_lineno})
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_ClassDef(self, node):
        self.record(node, "class")

    def visit_FunctionDef(self, node):
        self.record(node, "function")

    def visit_AsyncFunctionDef(self, node):
        self.record(node, "async_function")


def main():
    import langgraph.graph.state

    root = Path(langgraph.graph.state.__file__).resolve().parents[2]
    files = {}
    for relative in FILES:
        data = (root / relative).read_bytes()
        visitor = Symbols()
        visitor.visit(ast.parse(data))
        files[relative] = {"sha256": hashlib.sha256(data).hexdigest(), "symbols": visitor.items}
    print(json.dumps({"verified_date": "2026-10-05", "source_root": str(root),
                      "versions": {name: version(name) for name in ["langgraph", "langgraph-checkpoint", "deepagents"]},
                      "files": files}, separators=(",", ":"), ensure_ascii=True))


if __name__ == "__main__":
    main()
