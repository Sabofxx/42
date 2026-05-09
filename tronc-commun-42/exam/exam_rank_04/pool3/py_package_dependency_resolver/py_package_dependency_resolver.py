def package_dependency_resolver(packages: dict[str, list[str]]) -> list[str]:
    if not packages:
        return []

    # Filtrer les dependances qui ne sont pas dans le dict
    deps = {}
    for name, dependencies in packages.items():
        deps[name] = [d for d in dependencies if d in packages]

    # In-degree de chaque noeud
    in_degree = {name: len(d) for name, d in deps.items()}

    # File initiale : noeuds sans dependance, alphabetique
    queue = sorted(name for name, deg in in_degree.items() if deg == 0)
    result = []

    # BFS niveau par niveau (chaque "vague" alphabetique avant la suivante)
    while queue:
        next_queue = []
        for current in queue:
            result.append(current)
            for name, dependencies in deps.items():
                if current in dependencies:
                    in_degree[name] -= 1
                    if in_degree[name] == 0:
                        next_queue.append(name)
        queue = sorted(next_queue)

    # Cycle ? len(result) != len(packages)
    if len(result) != len(packages):
        return []
    return result


# res = package_dependency_resolver({"app": ["database"], "database": ["driver"], "driver": []})
# print(f"excepted: [\"driver\", \"database\", \"app\"]")
# print(f"got: {res}\n")

# res = package_dependency_resolver({"A": [], "B": ["A"], "C": ["A", "B"]})
# print(f"excepted: [\"A\", \"B\", \"C\"]")
# print(f"got: {res}\n")

# res = package_dependency_resolver({"X": ["Y"], "Y": ["X"]})
# print(f"excepted: []")
# print(f"got: {res}\n")

# res = package_dependency_resolver({"web": [], "api": [], "frontend": ["web"], "backend": ["api"]})
# print(f"excepted: [\"api\", \"web\", \"backend\", \"frontend\"]")
# print(f"got: {res}\n")
