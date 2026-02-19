def find_paths(graph_engine, start_entity, depth=2):
    visited = set()
    paths = []

    def dfs(entity, current_path, level):
        if level > depth:
            return

        visited.add(entity)

        for src, rel, tgt in graph_engine.relations:
            if src == entity:
                new_path = current_path + [(rel, tgt)]
                paths.append(new_path)
                if tgt not in visited:
                    dfs(tgt, new_path, level + 1)

    dfs(start_entity, [], 0)

    return paths



# Enterprise Adds:

# 1) Multi-hop traversal

# 2) Risk-aware reasoning

# 3) Decision enrichment