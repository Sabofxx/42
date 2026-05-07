def package_dependency_resolver(packages: dict[str, list[str]]) -> list[str]:
    if not packages:
        return []

    # Filtrer les dépendances inexistantes
    deps = {name: [d for d in dependencies if d in packages]
            for name, dependencies in packages.items()}

    # Compter les dépendances de chaque package
    count = {name: len(d) for name, d in deps.items()}

    # File triée alphabétiquement (déterministe)
    heap = sorted(name for name, c in count.items() if c == 0)

    result = []
    while heap:
        current = heap.pop(0)
        result.append(current)
        for name, dependencies in deps.items():
            if current in dependencies:
                count[name] -= 1
                if count[name] == 0:
                    heap.append(name)
        heap.sort()  # Maintenir l'ordre alphabétique

    return result if len(result) == len(packages) else []

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
