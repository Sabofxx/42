def package_dependency_resolver(packages: dict[str, list[str]]) -> list[str]:
    if not packages:
        return []

    # Filtrer les dependances qui ne sont pas dans le dict
    deps = {}
    for name, dependencies in packages.items():
        deps[name] = [d for d in dependencies if d in packages]

    # In-degree de chaque noeud
    in_degree = {}
    for name, dependencies in deps.items():
        in_degree[name] = len(dependencies)

    # File initiale : noeuds sans dependance, alphabetique
    queue = []
    for name in in_degree:
        if in_degree[name] == 0:
            queue.append(name)
    queue.sort()

    result = []
    while queue:
        current = queue.pop(0)
        result.append(current)
        # Decrementer les noeuds qui dependent de current
        for name, dependencies in deps.items():
            if current in dependencies:
                in_degree[name] -= 1
                if in_degree[name] == 0:
                    queue.append(name)
        queue.sort()

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
