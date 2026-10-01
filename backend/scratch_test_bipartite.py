import numpy as np
from scipy.optimize import linear_sum_assignment

# Supongamos una matriz de similitud de 4 temas objetivos vs 4 temas comparados:
# Item 0 tiene 0.70 con Cmp 0 y 0.40 con otros.
# Item 1 tiene 0.95 con Cmp 0 y 0.20 con otros.
# Item 2 tiene 0.85 con Cmp 1 y 0.30 con otros.
# Item 3 tiene 0.80 con Cmp 2 y 0.10 con otros.

sim_matrix = np.array([
    [0.70, 0.40, 0.10, 0.10],
    [0.95, 0.20, 0.10, 0.10],
    [0.10, 0.85, 0.30, 0.10],
    [0.10, 0.10, 0.80, 0.10]
])

print("--- GREEDY ALLOCATION (Algoritmo Voraz Actual) ---")
used_cmp = set()
greedy_pairs = []
greedy_total = 0.0

for i in range(4):
    best_j = -1
    best_val = -1.0
    for j in range(4):
        if j not in used_cmp and sim_matrix[i, j] > best_val:
            best_val = sim_matrix[i, j]
            best_j = j
    if best_j != -1:
        used_cmp.add(best_j)
        greedy_pairs.append((i, best_j, best_val))
        greedy_total += best_val

for p in greedy_pairs:
    print(f"  Obj {p[0]} -> Cmp {p[1]} (Score: {p[2]:.2f})")
print(f"Total Greedy Score: {greedy_total:.2f}")

print("\n--- GLOBAL OPTIMAL MATCHING (Hungarian Algorithm / Bipartite Matching) ---")
# Para maximizar, convertimos a costo = 1.0 - sim_matrix
cost_matrix = 1.0 - sim_matrix
row_ind, col_ind = linear_sum_assignment(cost_matrix)

optimal_pairs = []
optimal_total = 0.0
for r, c in zip(row_ind, col_ind):
    val = sim_matrix[r, c]
    optimal_pairs.append((r, c, val))
    optimal_total += val

for p in optimal_pairs:
    print(f"  Obj {p[0]} -> Cmp {p[1]} (Score: {p[2]:.2f})")
print(f"Total Optimal Score: {optimal_total:.2f}")
