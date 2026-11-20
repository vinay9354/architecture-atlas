# Lab 08 — sample results

One run on a laptop (macOS, Python 3.14) of `python3 measure.py` with the defaults: 100,000 keys,
N = 10 nodes, 100 virtual nodes for experiment A, seed 8. The program is deterministic, so the same
seed prints the same numbers on any machine; only the `finished in` time varies.

```text
100000 keys, N = 10 nodes, seed 8

A. Keys moved when the cluster changes (theory: mod-N moves N/(N+1) = 0.9091 on a join and (N-1)/N = 0.9000 on a leave;
   ring and rendezvous move 1/(N+1) = 0.0909 on a join and 1/N = 0.1000 on a leave)
           scheme |        nodes |        moved |       theory | minimal moves
------------------+--------------+--------------+--------------+--------------
            mod-N |     10 -> 11 |       0.9070 |       0.9091 |            no
            mod-N |      10 -> 9 |       0.9010 |       0.9000 |            no
ring (100 vnodes) |     10 -> 11 |       0.0935 |       0.0909 |           yes
ring (100 vnodes) |      10 -> 9 |       0.1109 |       0.1000 |           yes
       rendezvous |     10 -> 11 |       0.0904 |       0.0909 |           yes
       rendezvous |      10 -> 9 |       0.0991 |       0.1000 |           yes

B. Keys per node (1.0 is perfectly even; cv = standard deviation / mean)
      scheme |       vnodes |     max/mean |     min/mean |           cv | ~1/sqrt(vnodes)
-------------+--------------+--------------+--------------+--------------+----------------
       mod-N |            - |        1.012 |        0.985 |        0.008 |               -
        ring |            1 |        3.589 |        0.072 |        1.214 |           1.000
        ring |           10 |        1.806 |        0.516 |        0.339 |           0.316
        ring |          100 |        1.125 |        0.878 |        0.082 |           0.100
        ring |          200 |        1.079 |        0.930 |        0.050 |           0.071
  rendezvous |            - |        1.015 |        0.990 |        0.009 |               -

C. Keys versus reads per node (ring, 200 vnodes; mean node read share = 10.00%)
                       scenario | keys max/mean | reads max/mean | busiest node % |    top key %
--------------------------------+---------------+----------------+----------------+-------------
                    no hot keys |         1.079 |          1.079 |         10.789 |        0.001
    1% keys get 30% reads, even |         1.079 |          1.103 |         11.027 |        0.030
1% keys get 30% reads, zipf 1.0 |         1.079 |          1.315 |         13.151 |        4.008

finished in 4.0 s
```

A second run with fewer nodes and fewer virtual nodes, `python3 measure.py --nodes 4 --vnodes 10`
(experiment A only):

```text
          scheme |        nodes |        moved |       theory | minimal moves
-----------------+--------------+--------------+--------------+--------------
           mod-N |       4 -> 5 |       0.7997 |       0.8000 |            no
           mod-N |       4 -> 3 |       0.7515 |       0.7500 |            no
ring (10 vnodes) |       4 -> 5 |       0.1245 |       0.2000 |           yes
ring (10 vnodes) |       4 -> 3 |       0.2022 |       0.2500 |           yes
      rendezvous |       4 -> 5 |       0.1989 |       0.2000 |           yes
      rendezvous |       4 -> 3 |       0.2479 |       0.2500 |           yes
```

## What to notice

1. **Mod-N moves almost everything.** Going from 10 to 11 nodes moved 90.7% of keys (theory 90.9%),
   and going from 10 to 9 moved 90.1% (theory 90.0%). Keys moved between old nodes too, which is why
   the `minimal moves` column says `no`: a join reshuffled data the new node never touches.
2. **The ring and rendezvous move only what they must.** About one key in eleven moved on a join and
   one in ten on a leave, and every moved key went to the new node or came from the removed one
   (`minimal moves` = `yes`).
3. **The ring's movement equals the changing node's share of the circle, not the ideal share.**
   Node-9 owned 11.09% of the 100-vnode ring, so removing it moved 11.09% of keys rather than 10%.
   With only 10 virtual nodes and 4 nodes, the new node-4 landed on small arcs and took 12.45% of
   keys instead of the ideal 20%: still minimal movement, but an uneven new member.
4. **Rendezvous hashing is close to theory without any tuning** (9.04% and 9.91%), because every
   node draws an independent score for every key; there are no arcs to be unlucky with.
5. **Virtual nodes buy evenness at about 1/√v.** With one point per node the busiest node held 3.6×
   the mean and the emptiest only 7% of it (cv 1.21). With 10, 100, and 200 points the cv fell to
   0.34, 0.08, and 0.05, close to the 1/√v column. Mod-N and rendezvous are near-perfectly even
   here (cv under 0.01), so the ring pays for cheap rebalancing with a little unevenness.
6. **Even keys are not even load.** On the 200-vnode ring the busiest node held 1.079× the mean
   number of keys. When 1% of keys took 30% of reads spread evenly over those 1,000 hot keys, the
   busiest node's reads rose only to 1.103×, because 1,000 hot keys still average out across 10
   nodes. When the hot share followed a Zipf curve, the single hottest key carried 4.0% of all
   reads, which is 40% of an average node's 10% share, and the busiest node's reads reached 1.315×
   the mean. No placement scheme can split one key; that needs replicas of the hot key, a cache in
   front, or splitting the key itself.

## Answers to the questions in the lab page

- **Why does mod-N move N/(N+1) of keys?** A key keeps its node only when hash mod N equals hash
  mod (N+1). Across any run of N × (N+1) consecutive hash values that happens for exactly N of them
  (the values 0 to N-1), so the fraction that stays is N ÷ (N(N+1)) = 1/(N+1) and the fraction that
  moves is N/(N+1). For N = 10: 10/11 = 0.909. On a leave, the same argument gives (N-1)/N = 0.9.
- **Why does the ring move about 1/(N+1) on a join?** A new node takes over the arcs just before
  each of its points. If points are spread evenly it ends up with a fair 1/(N+1) of the circle, and
  only those keys move. On a leave, the removed node's arcs pass to the next points clockwise, so
  exactly its share moves: 1/N if the ring is even.
- **Why does 1/√v describe the ring's spread?** A node's share of the circle is the sum of v
  roughly independent random arc lengths. The relative spread of a sum of v independent values
  shrinks with √v, so going from 100 to 200 virtual nodes only improves the cv by a factor of √2
  (0.082 to 0.050 here) while doubling the size of the lookup table.
- **Why not use Python's `hash()`?** It is randomized per process for strings unless
  `PYTHONHASHSEED` is fixed. Two runs printed `-4618721796218689602` and `-6407941887335331545` for
  the same shipment ID, so two routers would disagree about which node owns it. MD5 truncated to
  64 bits gave `4501211879696065064` in both runs.
- **What would you change for a hot key?** Measure first (table C names the busiest node and the
  top key's share). Then replicate the hot key to several nodes and spread reads across them, put a
  small local cache in front of the shard, or add a suffix to the key to split one logical key into
  several physical ones. More virtual nodes do not help: they even out keys, and the problem is one
  key.
- **With `--zipf 1.2`** the top key's share rose to 6.92% of all reads and the busiest node's reads
  to 1.576× the mean, while its key count stayed at 1.079×.
