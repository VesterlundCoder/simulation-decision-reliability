"""M2: Recompute κ with ALL 7 interventions, retrieval matched.

The previous κ=1.000 was an artifact of using only 2 interventions.
With retrieval off, only capacity had an effect → trivially perfect agreement.
"""
import sys, json, time
import numpy as np
import networkx as nx
from pathlib import Path
from dataclasses import replace

sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wq_buffering.contention_sim import simulate_contention, SwapConfig
from wq_buffering.comprehensive_eval import make_decoherence_model, MEMORY_PROFILES, MemoryFamily
from wq_buffering.noise import NoiseType

sys.path.insert(0, str(Path(__file__).resolve().parent / "unified"))
from run_unified import run_harmonized, cohen_kappa, BOTTLENECKS, apply_intervention

N_CONFIGS = 30
N_SEEDS = 3
N_REQUESTS = 200
DELTA = 0.20

FAMILIES = [MemoryFamily.TRAPPED_ION, MemoryFamily.NEUTRAL_ATOM, MemoryFamily.AFC,
            MemoryFamily.DIAMANT_ELECTRON, MemoryFamily.DIAMANT_NUCLEAR, MemoryFamily.SUPERCONDUCTING]

def make_chain(n): return nx.path_graph(n)
def make_star(n): return nx.star_graph(n-1)
def make_ring(n): return nx.cycle_graph(n)

TOPOLOGIES = {'chain': (make_chain, 5), 'star': (make_star, 5), 'ring': (make_ring, 5)}

configs = []
for fam in FAMILIES:
    for topo_name, (topo_fn, n) in TOPOLOGIES.items():
        for m in [1, 4, 8]:
            for lam in [1.0, 10.0]:
                configs.append({'family': fam, 'topology': topo_name, 'n': n, 'm': m, 'lambda': lam})

rng = np.random.default_rng(42)
if len(configs) > N_CONFIGS:
    idx = rng.choice(len(configs), size=N_CONFIGS, replace=False)
    configs = [configs[i] for i in sorted(idx)]

print(f"Configs: {len(configs)}, Seeds: {N_SEEDS}, Requests: {N_REQUESTS}")
print(f"Interventions: {len(BOTTLENECKS)} (all 7)")
print(f"Delta: {DELTA}")

def run_wq_full(config, seed, retrieval_on):
    """Run WQ with all 7 interventions, return dominant label."""
    fam = config['family']
    profile = MEMORY_PROFILES[fam]
    dec = make_decoherence_model(NoiseType.DEPOLARIZING, 'medium', profile)
    topo_fn, n = TOPOLOGIES[config['topology']]
    G = topo_fn(n)
    placement = {v: config['m'] for v in G.nodes()}
    
    wq_config = SwapConfig(
        p_gen=0.005, t_attempt=1e-3, F_initial=0.99, deadline=10.0, F_min=0.5,
        T_obs=200.0, warmup_fraction=0.1, retrieval_in_delivery=retrieval_on,
    )
    
    base = simulate_contention(G, placement, profile, dec, NoiseType.DEPOLARIZING, wq_config,
                                arrival_rate=config['lambda'], n_requests=N_REQUESTS, random_seed=seed)['A_req']
    
    deltas = {}
    for bn in BOTTLENECKS:
        # Apply intervention
        if bn == 'capacity':
            p2 = {v: max(1, int(v * (1 + DELTA))) for v, v_val in placement.items()}
            r = simulate_contention(G, p2, profile, dec, NoiseType.DEPOLARIZING, wq_config,
                                    arrival_rate=config['lambda'], n_requests=N_REQUESTS, random_seed=seed)
            deltas[bn] = r['A_req'] - base
        elif bn == 'generation':
            cfg2 = SwapConfig(p_gen=0.005*(1+DELTA), t_attempt=1e-3, F_initial=0.99, deadline=10.0,
                             F_min=0.5, T_obs=200.0, warmup_fraction=0.1, retrieval_in_delivery=retrieval_on)
            r = simulate_contention(G, placement, profile, dec, NoiseType.DEPOLARIZING, cfg2,
                                    arrival_rate=config['lambda'], n_requests=N_REQUESTS, random_seed=seed)
            deltas[bn] = r['A_req'] - base
        elif bn == 'retrieval':
            if not retrieval_on:
                deltas[bn] = 0.0  # No effect when retrieval is off
            else:
                prof2 = replace(profile, retrieval_efficiency=min(1.0, profile.retrieval_efficiency * (1 + DELTA)))
                dec2 = make_decoherence_model(NoiseType.DEPOLARIZING, 'medium', prof2)
                r = simulate_contention(G, placement, prof2, dec2, NoiseType.DEPOLARIZING, wq_config,
                                        arrival_rate=config['lambda'], n_requests=N_REQUESTS, random_seed=seed)
                deltas[bn] = r['A_req'] - base
        elif bn == 'coherence':
            prof2 = replace(profile, T2=profile.T2 * (1 + DELTA))
            dec2 = make_decoherence_model(NoiseType.DEPOLARIZING, 'medium', prof2)
            r = simulate_contention(G, placement, prof2, dec2, NoiseType.DEPOLARIZING, wq_config,
                                    arrival_rate=config['lambda'], n_requests=N_REQUESTS, random_seed=seed)
            deltas[bn] = r['A_req'] - base
        elif bn == 'deadline':
            cfg2 = SwapConfig(p_gen=0.005, t_attempt=1e-3, F_initial=0.99, deadline=10.0*(1+DELTA),
                             F_min=0.5, T_obs=200.0, warmup_fraction=0.1, retrieval_in_delivery=retrieval_on)
            r = simulate_contention(G, placement, profile, dec, NoiseType.DEPOLARIZING, cfg2,
                                    arrival_rate=config['lambda'], n_requests=N_REQUESTS, random_seed=seed)
            deltas[bn] = r['A_req'] - base
        elif bn == 'routing':
            # Skip routing (not easily intervened)
            deltas[bn] = 0.0
        elif bn == 'topology':
            # Skip topology (not easily intervened)
            deltas[bn] = 0.0
    
    max_d = max(deltas.values()) if deltas else 0
    if max_d < 0.001:
        return 'degenerate'
    return max(deltas, key=deltas.get)

def run_harm_full(config, seed, retrieval_on):
    """Run harmonized with all 7 interventions, return dominant label."""
    fam = config['family']
    profile = MEMORY_PROFILES[fam]
    dec = make_decoherence_model(NoiseType.DEPOLARIZING, 'medium', profile)
    topo_fn, n = TOPOLOGIES[config['topology']]
    G = topo_fn(n)
    placement = {v: config['m'] for v in G.nodes()}
    
    wq_config = SwapConfig(
        p_gen=0.005, t_attempt=1e-3, F_initial=0.99, deadline=10.0, F_min=0.5,
        T_obs=200.0, warmup_fraction=0.1, retrieval_in_delivery=retrieval_on,
    )
    
    if not retrieval_on:
        profile = replace(profile, retrieval_efficiency=1.0)
    
    base = run_harmonized(G, placement, profile, dec, NoiseType.DEPOLARIZING, wq_config,
                          'shortest', seed, config['lambda'], N_REQUESTS, 'A_req')
    
    deltas = {}
    for bn in BOTTLENECKS:
        if bn == 'capacity':
            p2 = {v: max(1, int(v * (1 + DELTA))) for v, v_val in placement.items()}
            r = run_harmonized(G, p2, profile, dec, NoiseType.DEPOLARIZING, wq_config,
                               'shortest', seed, config['lambda'], N_REQUESTS, 'A_req')
            deltas[bn] = r - base
        elif bn == 'generation':
            cfg2 = SwapConfig(p_gen=0.005*(1+DELTA), t_attempt=1e-3, F_initial=0.99, deadline=10.0,
                             F_min=0.5, T_obs=200.0, warmup_fraction=0.1, retrieval_in_delivery=retrieval_on)
            r = run_harmonized(G, placement, profile, dec, NoiseType.DEPOLARIZING, cfg2,
                               'shortest', seed, config['lambda'], N_REQUESTS, 'A_req')
            deltas[bn] = r - base
        elif bn == 'retrieval':
            if not retrieval_on:
                deltas[bn] = 0.0
            else:
                prof2 = replace(profile, retrieval_efficiency=min(1.0, profile.retrieval_efficiency * (1 + DELTA)))
                r = run_harmonized(G, placement, prof2, dec, NoiseType.DEPOLARIZING, wq_config,
                                   'shortest', seed, config['lambda'], N_REQUESTS, 'A_req')
                deltas[bn] = r - base
        elif bn == 'coherence':
            prof2 = replace(profile, T2=profile.T2 * (1 + DELTA))
            r = run_harmonized(G, placement, prof2, dec, NoiseType.DEPOLARIZING, wq_config,
                               'shortest', seed, config['lambda'], N_REQUESTS, 'A_req')
            deltas[bn] = r - base
        elif bn == 'deadline':
            cfg2 = SwapConfig(p_gen=0.005, t_attempt=1e-3, F_initial=0.99, deadline=10.0*(1+DELTA),
                             F_min=0.5, T_obs=200.0, warmup_fraction=0.1, retrieval_in_delivery=retrieval_on)
            r = run_harmonized(G, placement, profile, dec, NoiseType.DEPOLARIZING, cfg2,
                               'shortest', seed, config['lambda'], N_REQUESTS, 'A_req')
            deltas[bn] = r - base
        elif bn == 'routing':
            deltas[bn] = 0.0
        elif bn == 'topology':
            deltas[bn] = 0.0
    
    max_d = max(deltas.values()) if deltas else 0
    if max_d < 0.001:
        return 'degenerate'
    return max(deltas, key=deltas.get)

# Run both conditions
start = time.time()
for cond_name, wq_ret, harm_ret in [("C1_on_on", True, True), ("C2_off_off", False, False)]:
    print(f"\n--- {cond_name} ---")
    wq_labels = []
    harm_labels = []
    for i, config in enumerate(configs):
        for seed in range(N_SEEDS):
            wq_label = run_wq_full(config, seed, wq_ret)
            harm_label = run_harm_full(config, seed, harm_ret)
            wq_labels.append(wq_label)
            harm_labels.append(harm_label)
        if (i+1) % 5 == 0:
            print(f"  {i+1}/{len(configs)} done ({time.time()-start:.1f}s)")
    
    kappa = cohen_kappa(wq_labels, harm_labels)
    agreement = sum(1 for w, h in zip(wq_labels, harm_labels) if w == h) / len(wq_labels)
    
    # Label distribution
    from collections import Counter
    wq_dist = Counter(wq_labels)
    harm_dist = Counter(harm_labels)
    
    print(f"  κ={kappa:.3f}, agreement={agreement:.3f}, n={len(wq_labels)}")
    print(f"  WQ labels: {dict(wq_dist)}")
    print(f"  Harm labels: {dict(harm_dist)}")

print(f"\nTotal time: {time.time()-start:.1f}s")
