"""M2.B1: Magnitude diagnosis.

Paired test between best resource and others.
Classes: decided, tied, degenerate.
"""
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from scipy import stats
from wq_buffering.contention_sim import simulate_contention, SwapConfig
from wq_buffering.comprehensive_eval import MEMORY_PROFILES, make_decoherence_model
from wq_buffering.memory import MemoryFamily
from wq_buffering.noise import NoiseType
import networkx as nx

# Use a subset of the atlas
families = [
    (MemoryFamily.TRAPPED_ION, "Trapped Ion"),
    (MemoryFamily.NEUTRAL_ATOM, "Neutral Atom"),
    (MemoryFamily.AFC, "AFC"),
]
N = 5
topologies = {
    "chain": lambda n: nx.path_graph(n),
    "star": lambda n: nx.star_graph(n - 1),
    "rgg": lambda n: nx.random_geometric_graph(n, radius=2.0, seed=42),
}
# Fix RGG
def make_rgg(n):
    G = nx.random_geometric_graph(n, radius=2.0, seed=42)
    if not nx.is_connected(G):
        for i in range(n - 1):
            if not G.has_edge(i, i + 1):
                G.add_edge(i, i + 1)
    return G
topologies["rgg"] = make_rgg

m_values = [1, 4, 8, 16]
traffic_values = [1.0, 10.0, 50.0]
n_seeds = 10
n_requests = 200
delta = 0.10  # relative improvement

# 7 resources
resources = ["capacity", "generation", "retrieval", "coherence", "routing", "deadline", "topology"]

def run_config(G, placement, profile, dec, config, traffic, seed, n_req, intervention=None):
    """Run simulation with optional intervention."""
    cfg = SwapConfig(
        p_gen=config.p_gen, t_attempt=config.t_attempt,
        F_initial=config.F_initial, deadline=config.deadline,
        F_min=config.F_min, T_obs=config.T_obs,
        warmup_fraction=config.warmup_fraction,
        retrieval_in_delivery=config.retrieval_in_delivery,
    )
    if intervention == "capacity":
        placement = {k: max(1, int(v * (1 + delta))) for k, v in placement.items()}
    elif intervention == "generation":
        cfg.p_gen = config.p_gen * (1 + delta)
    elif intervention == "retrieval":
        # Increase retrieval_efficiency by delta
        import dataclasses
        profile = dataclasses.replace(profile, retrieval_efficiency=min(1.0, profile.retrieval_efficiency * (1 + delta)))
    elif intervention == "coherence":
        # Increase T2 by delta
        import dataclasses
        profile = dataclasses.replace(profile, T2=profile.T2 * (1 + delta))
    elif intervention == "deadline":
        cfg.deadline = config.deadline * (1 + delta)
    elif intervention == "routing":
        pass  # routing not easily intervened
    elif intervention == "topology":
        pass  # topology not easily intervened in this framework
    
    res = simulate_contention(
        topology=G, placement=placement,
        profile=profile, decoherence=dec,
        noise_type=NoiseType.DEPOLARIZING, config=cfg,
        arrival_rate=traffic, n_requests=n_req, random_seed=seed,
    )
    return res.get("A_req", 0.0)

results = []
configs_run = 0
for fam_enum, fam_name in families:
    profile = MEMORY_PROFILES[fam_enum]
    dec = make_decoherence_model(NoiseType.DEPOLARIZING, 'medium', profile)
    for topo_name, topo_fn in topologies.items():
        G = topo_fn(N)
        for m in m_values:
            placement = {i: m for i in G.nodes()}
            for traffic in traffic_values:
                config = SwapConfig(
                    p_gen=0.005, t_attempt=1e-3,
                    F_initial=0.99, deadline=10.0, F_min=0.5,
                    T_obs=200.0, warmup_fraction=0.1,
                    retrieval_in_delivery=True,
                )
                # Run baseline and interventions for each seed
                for seed in range(n_seeds):
                    try:
                        baseline = run_config(G, placement, profile, dec, config, traffic, seed, n_requests)
                        deltas = {}
                        for res_name in resources:
                            intervened = run_config(G, placement, profile, dec, config, traffic, seed, n_requests, res_name)
                            deltas[res_name] = intervened - baseline
                        
                        # Magnitude diagnosis
                        max_delta = max(deltas.values())
                        best_resource = max(deltas, key=deltas.get)
                        
                        # Classification
                        epsilon = 0.001  # degeneracy threshold
                        if max_delta < epsilon:
                            classification = "degenerate"
                        else:
                            # Paired test: best vs second-best
                            sorted_deltas = sorted(deltas.values(), reverse=True)
                            if len(sorted_deltas) > 1:
                                gap = sorted_deltas[0] - sorted_deltas[1]
                                # If gap is small relative to max_delta, it's tied
                                if gap < 0.1 * max_delta:
                                    classification = "tied"
                                else:
                                    classification = "decided"
                            else:
                                classification = "decided"
                        
                        results.append({
                            "family": fam_name, "topology": topo_name, "m": m,
                            "traffic": traffic, "seed": seed,
                            "baseline_A_req": baseline,
                            "deltas": deltas,
                            "best_resource": best_resource,
                            "max_delta": max_delta,
                            "classification": classification,
                        })
                    except Exception as e:
                        results.append({
                            "family": fam_name, "topology": topo_name, "m": m,
                            "traffic": traffic, "seed": seed,
                            "error": str(e),
                            "classification": "error",
                        })
                configs_run += 1
                if configs_run % 10 == 0:
                    print(f"  {configs_run} configs done")

# Summarize
classifications = [r.get("classification", "error") for r in results]
n_decided = sum(1 for c in classifications if c == "decided")
n_tied = sum(1 for c in classifications if c == "tied")
n_degenerate = sum(1 for c in classifications if c == "degenerate")
n_error = sum(1 for c in classifications if c == "error")
n_total = len(classifications)

print(f"\nMagnitude Diagnosis Summary:")
print(f"  Total: {n_total}")
print(f"  Decided: {n_decided} ({100*n_decided/n_total:.1f}%)")
print(f"  Tied: {n_tied} ({100*n_tied/n_total:.1f}%)")
print(f"  Degenerate: {n_degenerate} ({100*n_degenerate/n_total:.1f}%)")
print(f"  Error: {n_error} ({100*n_error/n_total:.1f}%)")

# Per-family
for fam_name in ["Trapped Ion", "Neutral Atom", "AFC"]:
    fam_results = [r for r in results if r.get("family") == fam_name]
    fam_classes = [r.get("classification", "error") for r in fam_results]
    n_d = sum(1 for c in fam_classes if c == "decided")
    n_t = sum(1 for c in fam_classes if c == "tied")
    n_deg = sum(1 for c in fam_classes if c == "degenerate")
    n_f = len(fam_classes)
    print(f"\n  {fam_name}: {n_f} total, {n_d} decided ({100*n_d/n_f:.1f}%), {n_t} tied ({100*n_t/n_f:.1f}%), {n_deg} degenerate ({100*n_deg/n_f:.1f}%)")

with open(os.path.join(os.path.dirname(__file__), "magnitude_diagnosis.json"), "w") as f:
    json.dump({"results": results, "n_seeds": n_seeds, "n_requests": n_requests, "delta": delta}, f, indent=2)
print(f"\nSaved {len(results)} results to magnitude_diagnosis.json")
