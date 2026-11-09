import os, sys, re, difflib

REPL = [
    ("sedracoin/sedrad", "kaspanet/kaspad"),
    ("SEDRA", "KASPA"), ("Sedra", "Kaspa"), ("sedra", "kaspa"),
    ("SEEP", "SOMPI"), ("Seep", "Sompi"), ("seep", "sompi"),
]

def norm(s):
    for a, b in REPL:
        s = s.replace(a, b)
    return s

def load(root):
    out = {}
    for dp, dn, fn in os.walk(root):
        for f in fn:
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, root).replace("\\", "/")
            if not rel.endswith((".go", ".proto", ".mod", ".sum", ".sh", ".md", ".json", ".yml", ".yaml")):
                continue
            try:
                txt = open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            out[norm(rel)] = norm(txt)
    return out

def compare(a, b, detail=False):
    only_a = sorted(set(a) - set(b)); only_b = sorted(set(b) - set(a))
    changed = []; lines = 0
    for k in sorted(set(a) & set(b)):
        if a[k] != b[k]:
            d = [l for l in difflib.unified_diff(b[k].splitlines(), a[k].splitlines(), lineterm="", n=0)
                 if (l.startswith("+") or l.startswith("-")) and not l.startswith(("+++", "---"))]
            if d:
                changed.append((k, len(d))); lines += len(d)
    return only_a, only_b, changed, lines

if __name__ == "__main__":
    base = sys.argv[1]; sed = load(sys.argv[2])
    if len(sys.argv) > 3 and sys.argv[3] == "detail":
        k = load(base)
        oa, ob, ch, ln = compare(sed, k)
        print("ONLY_IN_SEDRA", len(oa)); [print("  +", x) for x in oa]
        print("ONLY_IN_KASPAD", len(ob)); [print("  -", x) for x in ob]
        print("CHANGED", len(ch), "difflines", ln)
        for x in sorted(ch, key=lambda t: -t[1]): print("  ~", x[1], x[0])
    else:
        for d in sorted(os.listdir(base)):
            if not d.startswith("kaspad-"): continue
            k = load(os.path.join(base, d))
            oa, ob, ch, ln = compare(sed, k)
            print(f"{d:24} onlySedra={len(oa):4} onlyKaspad={len(ob):4} changedFiles={len(ch):4} diffLines={ln}")
