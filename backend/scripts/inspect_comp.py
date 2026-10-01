import sqlite3

conn = sqlite3.connect('data/convcomp.db')
c = conn.cursor()

c.execute("SELECT id, course_name, university, filename FROM syllabi")
for s in c.fetchall():
    print(f"Syllabus {s[0]}: Course='{s[1]}' | Univ='{s[2]}' | File='{s[3]}'")

comp_id = 'COMP-B7809E5AA543'
print(f"\n=======================================================")
print(f"--- COMPARISON {comp_id} ---")
print(f"=======================================================")
c.execute("SELECT id, objective_syllabus_id, compared_syllabus_id, global_score, objective_coverage, compared_coverage FROM comparisons WHERE id = ?", (comp_id,))
print(c.fetchone())

c.execute("""
    SELECT objective_title, compared_title, classification, composite_score, semantic_sim, lexical_sim, keyword_overlap
    FROM content_matches
    WHERE comparison_id = ?
    ORDER BY composite_score DESC
""", (comp_id,))
for m in c.fetchall():
    print(f"[{m[2]}] score={m[3]:.3f} (sem={m[4]:.2f}, lex={m[5]:.2f}, kw={m[6]:.2f}) | Obj: {m[0][:35]} <===> Cmp: {m[1][:35]}")

print(f"\n--- UNMATCHED OBJECTIVE FOR {comp_id} ---")
c.execute("""
    SELECT title, section_name, best_candidate_title, best_score
    FROM unmatched_items
    WHERE comparison_id = ? AND syllabus_role = 'OBJECTIVE'
""", (comp_id,))
for u in c.fetchall():
    b_score = f"{u[3]:.3f}" if u[3] is not None else "N/A"
    print(f"Obj Unmatched: {u[0][:40]} ({u[1]}) | Best: {u[2]} ({b_score})")

print(f"\n--- UNMATCHED COMPARED FOR {comp_id} ---")
c.execute("""
    SELECT title, section_name, best_candidate_title, best_score
    FROM unmatched_items
    WHERE comparison_id = ? AND syllabus_role = 'COMPARED'
""", (comp_id,))
for u in c.fetchall():
    b_score = f"{u[3]:.3f}" if u[3] is not None else "N/A"
    print(f"Cmp Unmatched: {u[0][:40]} ({u[1]}) | Best: {u[2]} ({b_score})")
