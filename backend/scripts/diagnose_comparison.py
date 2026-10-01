import sqlite3

conn = sqlite3.connect('data/convcomp.db')
c = conn.cursor()

comp_id = 'COMP-5EBC9F1F68DF'

c.execute("SELECT id, objective_syllabus_id, compared_syllabus_id, global_score, objective_coverage, compared_coverage FROM comparisons WHERE id = ?", (comp_id,))
comp = c.fetchone()
print(f"Comparison: {comp}")

obj_id = comp[1]
cmp_id = comp[2]

c.execute("SELECT id, unit_number, title, text FROM content_items WHERE syllabus_id = ? ORDER BY unit_number, order_num", (obj_id,))
obj_items = c.fetchall()

c.execute("SELECT id, unit_number, title, text FROM content_items WHERE syllabus_id = ? ORDER BY unit_number, order_num", (cmp_id,))
cmp_items = c.fetchall()

print(f"\n--- OBJECTIVE ITEMS ({len(obj_items)}) ---")
for it in obj_items:
    print(f"[{it[0]}] U{it[1]}: {it[2]}")

print(f"\n--- COMPARED ITEMS ({len(cmp_items)}) ---")
for it in cmp_items:
    print(f"[{it[0]}] U{it[1]}: {it[2]}")

c.execute("""
    SELECT cm.objective_item_id, cm.compared_item_id, cm.objective_title, cm.compared_title,
           cm.classification, cm.composite_score, cm.semantic_sim, cm.lexical_sim, cm.keyword_overlap
    FROM content_matches cm
    WHERE cm.comparison_id = ?
    ORDER BY cm.composite_score DESC
""", (comp_id,))
matches = c.fetchall()

print(f"\n--- MATCHES ({len(matches)}) ---")
matched_obj_ids = set()
for m in matches:
    if m[4] in ('MATCH', 'PARTIAL_MATCH'):
        matched_obj_ids.add(m[0])
    print(f"[{m[4]}] Score={m[5]:.3f} (sem={m[6]:.2f}, lex={m[7]:.2f}, kw={m[8]:.2f})\n  Obj: {m[2]}\n  Cmp: {m[3]}")

print(f"\n--- UNMATCHED OBJECTIVE ITEMS ({len(obj_items) - len(matched_obj_ids)}) ---")
for it in obj_items:
    if it[0] not in matched_obj_ids:
        print(f"[UNMATCHED] [{it[0]}] U{it[1]}: {it[2]}")
        print(f"   Snippet: {it[3][:120]}...\n")
