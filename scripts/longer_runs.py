"""M2.B4: Longer runs (1000 requests instead of 200)."""
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import networkx as nx
from wq_buffering.contention_sim import simulate_contention, SwapConfig
from wq_buffering.comprehensive_eval import MEMORY_PROFILES, make_decoherence_model
from wq_buffering.memory import MemoryFamily
from wq_buffering.noise import NoiseType

def make_rgg(n):
    G = nx.random_geometric_graph(n, radius=2.0, seed=42)
    if not nx.is_connected(G):
        for i in range(n - 1):
            if not G.has_edge(i, i + 1):
                G.add_edge(i, i + 1)
    return G

N = 5
topologies = {"chain": lambda n: nx.path_graph(n), "star": lambda n: nx.star_graph(n-1), "rgg": make_rgg}
families = [(MemoryFamily.TRAPPED_ION, "Trapped Ion"), (MemoryFamily.NEUTRAL_ATOM, "Neutral Atom"), (MemoryFamily.AFC, "AFC")]
m_values = [1, 4, 16]
traffic_values = [1.0, 50.0]
n_seeds = 5

results = []
for n_req in [200, 1000]:
    for fam_enum, fam_name in families:
        profile = MEMORY_PROFILES[fam_enum]
        dec = make_decoherence_model(NoiseType.DEPOLARIZING, 'medium', profile)
        for topo_name, topo_fn in topologies.items():
            G = topo_fn(N)
            for m in m_values:
                placement = {i: m for i in G.nodes()}
                config = SwapConfig(
                    p_gen=0.005, t_attempt=1e-3,
                    F_initial=0.99, deadline=10.0, F_min=0.5,
                    T_obs=200.0, warmup_fraction=0.1,
                    retrieval_in_delivery=True,
                )
                a_reqs = []
                for seed in range(n_seeds):
                    try:
                        res = simulate_contention(
                            topology=G, placement=placement,
                            profile=profile, decoherence=dec,
                            noise_type=NoiseType.DEPOLARIZING, config=config,
                            arrival_rate=10.0, n_requests=n_req, random_seed=seed,
                        )
                        a_req = res.get("A_req", 0.0)
                        a_reqs.append(a_req)
                        results.append({
                            "n_requests": n_req, "family": fam_name, "topology": topo_name,
                            "m": m, "seed": seed, "A_req": a_req,
                        })
                    except Exception as e:
                        results.append({
                            "n_requests": n_req, "family": fam_name, "topology": topo_name,
                            "m": m, "seed": seed, "A_req": 0.0, "error": str(e),
                        })

# Compare stability
print("n_req | Family | Topology | m | Mean A_req | Std | CV")
print("------|--------|----------|---|------------|-----|---")
for n_req in [200, 1000]:
    for fam_name in ["Trapped Ion", "Neutral Atom", "AFC"]:
        for topo_name in ["chain", "star", "rgg"]:
            for m in m_values:
                subset = [r for r in results if r["n_requests"] == n_req and r["family"] == fam_name and r["topology"] == topo_name and r["m"] == m and "error" not in r]
                if subset:
                    vals = [r["A_req"] for r in subset]
                    mean = np.mean(vals)
                    std = np.std(vals)
                    cv = std / mean if mean > 0 else float('inf')
                    print(f"{n_req:5d} | {fam_name:12s} | {topo_name:8s} | {m:2d} | {mean:.4f} | {std:.4f} | {cv:.4f}")

# Overall CV comparison
cv_200 = []
cv_1000 = []
for fam_name in ["Trapped Ion", "Neutral Atom", "AFC"]:
    for topo_name in ["chain", "star", "rgg"]:
        for m in m_values:
            s200 = [r["A_req"] for r in results if r["n_requests"] == 200 and r["family"] == fam_name and r["topology"] == topo_name and r["m"] == m and "error" not in r]
            s1000 = [r["A_req"] for r in results if r["n_requests"] == 1000 and r["family"] == fam_name and r["topology"] == topo_name and r["m"] == m and "error" not in r]
            if s200 and s1000:
                m200 = np.mean(s200)
                m1000 = np.mean(s1000)
                if m200 > 0: cv_200.append(np.std(s200)/m200)
                if m1000 > 0: cv_1000.append(np.std(s1000)/m1000)

print(f"\nOverall CV: 200 req = {np.mean(cv_200):.4f}, 1000 req = {np.mean(cv_1000):.4f}")
print(f"Improvement: {100*(1 - np.mean(cv_1000)/np.mean(cv_200)):.1f}%")

with open(os.path.join(os.path.dirname(__file__), "longer_runs.json"), "w") as f:
    json.dump({"results": results, "n_seeds": n_seeds}, f, indent=2)
print(f"\nSaved {len(results)} results to longer_runs.json")
