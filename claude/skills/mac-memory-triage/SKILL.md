---
name: mac-memory-triage
description: Triage macOS memory pressure and sluggishness on this Mac with read-only commands. TRIGGER when user invokes /mac-memory-triage, reports the Mac being slow or heavy, mentions Activity Monitor memory pressure (yellow/red), or asks what is eating memory.
---

# Mac Memory Triage

Observed numbers and version pins in this file are from a 2026-07 session on this machine unless noted otherwise

## Stance

- Read-only investigation first
- Report findings before stopping or killing anything
- The user decides remediation
- Propose levers with expected recovery size

## Step 1 — Pressure snapshot

- `memory_pressure -Q` — system-wide free percentage
  - 39-42% observed during a warn episode, 54% after recovery
- `sysctl kern.memorystatus_vm_pressure_level`
  - 1 normal, 2 warn, 4 critical, matching Apple's DISPATCH_MEMORYPRESSURE_NORMAL/WARN/CRITICAL constants (0x1/0x2/0x4)
  - warn corresponded to the yellow Activity Monitor pressure graph on this machine
- `sysctl vm.swapusage` — swap used vs allocated
- `vm_stat` — values are in pages
  - read the page size from the header line, 16384 bytes on this machine
- `uptime` — needed to judge cumulative counters

## Step 2 — Who is consuming

- `top -l 1 -o mem -n 20 -stats pid,command,mem,cmprs,ppid`
  - rank processes by MEM, the documented physical memory footprint column
  - a CMPRS value close to MEM marks a long-idle, mostly compressed process
  - man top does not document how CMPRS relates to MEM, so do not sum the two columns
- Per-app RSS aggregation, run this verbatim:

```
ps -axo rss,comm | awk '{rss=$1; $1=""; name=$0; sub(/^ /,"",name); n=split(name,parts,"/"); app=name; for(i=1;i<=n;i++){if(parts[i] ~ /\.app$/){app=parts[i]; break}}; sum[app]+=rss; cnt[app]++} END {for(a in sum) printf "%8.1f MB  %3d procs  %s\n", sum[a]/1024, cnt[a], a}' | sort -rn | head -25
```

- `top -l 2 -o cpu -s 2 -n 12 -stats pid,command,cpu,mem` for CPU ranking, use only the second sample
  - the first sample of `top -l` reports unusable CPU percentages

## Step 3 — Attribution and long runners

- `ps -axo pid,etime,rss,command` for process uptimes
  - flag Electron apps and browsers running for days
- A `com.apple.Virtualization.VirtualMachine` process signals a VM
  - check the apple/container CLI with `container ls` and `container builder status`
  - the builder is stopped with `container builder stop`, subcommand verified via `container builder --help`, container 1.1.0
- For Electron apps (Rambox etc.) sum all helper processes, and check etime of the main process

## Interpretation pitfalls

- Compressor: pages stored x page size = uncompressed data held
  - pages occupied x page size = physical cost
  - roughly 3:1 ratio observed here
- swapins/swapouts/pageins are cumulative since boot
  - divide by uptime for a rate
  - near-zero delta between two top samples means no active thrash at sampling time, state that explicitly in the report
- PhysMem used close to total is normal macOS behavior
  - judge by pressure level, compressor size, and swap growth instead
- RSS aggregation double-counts shared memory and understates long-idle compressed or swapped apps
  - label which metric each reported number uses
- WebKit WebContent XPC processes (ppid 1) serve whichever app hosts a WKWebView
  - attribute a WebContent process to a specific app only with evidence

## Countermeasure levers

Ordered by impact observed on this machine:

1. Forgotten VMs and container runtimes (a buildkit VM held a ~1.3GB footprint with 2GB allocated)
1. Background updaters such as JetBrains Toolbox (~780MB footprint, mostly compressed while idle)
   - quitting and launching weekly keeps updates
1. Browser consolidation when Safari and Chrome run simultaneously
1. Restarting long-lived Electron apps (Rambox after 6 days: 18 processes, 1.75GB+ RSS)
1. Music.app (~1GB within minutes) vs the macOS Background Sounds feature (the `heard` daemon, ~10MB) for BGM
1. WindowServer high CPU (~48% observed) is itself a direct cause of UI sluggishness
   - investigate constantly-redrawing apps

## Baseline for this machine (2026-07)

- 16GB M3 MacBook (Mac15,3), company machine
- Usual heavy set: Rambox, Chrome, Safari, Claude, plus occasional apple/container VMs
- Healthy: compressor around 4.5GB, pressure level 1
- Warn episode observed: compressor 6.5-7.4GB, swap 3.7GB/5GB, pressure level 2

## Continuous monitoring

Design ideas for a snapshot/feedback loop live in `references/feedback-loop.md` in this skill directory
