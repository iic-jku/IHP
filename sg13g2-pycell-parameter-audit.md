# IHP SG13G2 PyCell parameter audit

Which parameters each KLayout PCell declares, and which of them anything actually consumes.

**451 parameter declarations across 33 PCells; 200 (44%) are never read by any code in the PDK.**

## Method

Static analysis of `libs.tech/klayout/python/sg13g2_pycell_lib/`. A parameter counts as *used* if any of these hold:

| Role | Meaning |
|---|---|
| `layout` | Read as `params['x']` by the PCell's Python code (or an ancestor class) — it affects the generated geometry. |
| `cb-read` | Read via `iPDK_getParamValue` by a Tcl callback proc reachable from this device's registration. |
| `cb-write` | Written via `iPDK_setParamValue` by such a proc — the GUI field is kept up to date. |
| `cb-trigger` | Listed in `callbacks.json` for this device, so editing it fires a callback. |
| **unused** | None of the above. Declared, shown in the PCell dialog, read by nothing. |

Details of the resolution:

- **PCell set** comes from `moduleNames` in `sg13g2_pycell_lib/__init__.py`; each `<name>_code` module is registered as PCell `<name>`.
- **Inheritance is followed.** `dpantenna` inherits `guardRingType` / `guardRingDistance` from `DeviceBase`, the resistors from `ResistorBase`, the RF FETs from `rfmosfet_base`. Inherited params are listed with their declaring class.
- **The `#ifdef KLAYOUT` preprocessor is respected.** Twelve device files wrap `defineParamSpecs` in `#ifdef KLAYOUT` / `#else`; `KLAYOUT` is defined when running inside KLayout, so only the `#ifdef` branch is analysed. The `#else` branch (the fuller Cadence CDF set) never reaches the KLayout GUI and is noted separately per device.
- **Tcl callbacks are resolved transitively.** For each device, `callbacks.json` names the procs; the analysis follows the call graph through `callbacks/*.tcl` (comments stripped) and collects every `iPDK_getParamValue` / `iPDK_setParamValue` target reachable from them.
- **Unreachable procs do not count.** A proc that exists but is neither registered in `callbacks.json` nor called by a registered proc can never run — see [Dead callback code](#dead-callback-code).

Not covered: nothing outside this library reads PCell parameters. The xschem symbols in `libs.tech/xschem/sg13g2_pr/` carry their own independent parameter sets (e.g. `dpantenna.sym` uses only `name`, `model`, `l`, `w`, `spiceprefix`), and no KLayout DRC/LVS deck references these names.

## Summary

| PCell | Source | Declared | Used | Unused | Callback procs |
|---|---|---:|---:|---:|---|
| `rhigh` | [rhigh_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/rhigh_code.py) | 28 | 13 | **15** | `CbRes` |
| `rppd` | [rppd_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/rppd_code.py) | 28 | 13 | **15** | `CbRes` |
| `rsil` | [rsil_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/rsil_code.py) | 25 | 11 | **14** | `CbRes` |
| `dantenna` | [dantenna_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/dantenna_code.py) | 20 | 8 | **12** | `CbDiode` |
| `npn13G2L` | [npn13G2L_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/npn13G2L_code.py) | 14 | 3 | **11** | — |
| `npn13G2V` | [npn13G2V_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/npn13G2V_code.py) | 14 | 3 | **11** | — |
| `dpantenna` | [dpantenna_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/dpantenna_code.py) | 19 | 8 | **11** | `CbDiode` |
| `cmim` | [cmim_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/cmim_code.py) | 16 | 6 | **10** | `CbCap` |
| `npn13G2` | [npn13G2_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/npn13G2_code.py) | 22 | 13 | **9** | — |
| `pnpMPA` | [pnpMPA_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/pnpMPA_code.py) | 11 | 2 | **9** | — |
| `rfcmim` | [rfcmim_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/rfcmim_code.py) | 10 | 4 | **6** | `CbCap` |
| `rfnmos` | [rfnmos_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/rfnmos_code.py) | 13 | 7 | **6** | — |
| `rfnmosHV` | [rfnmosHV_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/rfnmosHV_code.py) | 13 | 7 | **6** | — |
| `rfpmos` | [rfpmos_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/rfpmos_code.py) | 13 | 7 | **6** | — |
| `rfpmosHV` | [rfpmosHV_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/rfpmosHV_code.py) | 13 | 7 | **6** | — |
| `isolbox` | [isolbox_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/isolbox_code.py) | 18 | 12 | **6** | `isol_l`, `isol_w`, `isol_well`, `isolbox_cb` |
| `nmos` | [nmos_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/nmos_code.py) | 13 | 8 | **5** | `NLCB_mos_w`, `NLCB_mos_ng`, `NLCB_mos_l` |
| `nmosHV` | [nmosHV_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/nmosHV_code.py) | 13 | 8 | **5** | `NLCB_mos_w`, `NLCB_mos_ng`, `NLCB_mos_l` |
| `pmos` | [pmos_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/pmos_code.py) | 13 | 8 | **5** | `NLCB_mos_w`, `NLCB_mos_ng`, `NLCB_mos_l` |
| `pmosHV` | [pmosHV_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/pmosHV_code.py) | 13 | 8 | **5** | `NLCB_mos_w`, `NLCB_mos_ng`, `NLCB_mos_l` |
| `ptap1` | [ptap1_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/ptap1_code.py) | 7 | 2 | **5** | — |
| `ntap1` | [ntap1_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/ntap1_code.py) | 7 | 2 | **5** | — |
| `schottky` | [schottky_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/schottky_code.py) | 8 | 4 | **4** | — |
| `inductor2` | [inductor2_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/inductor2_code.py) | 20 | 17 | **3** | `inductor_w`, `inductor_s`, `inductor_nr`, `inductor_d` |
| `inductor3` | [inductor3_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/inductor3_code.py) | 20 | 17 | **3** | `inductor_w`, `inductor_s`, `inductor_nr`, `inductor_d` |
| `sealring` | [sealring_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/sealring_code.py) | 9 | 7 | **2** | `NLCB_w`, `NLCB_l` |
| `bondpad` | [bondpad_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/bondpad_code.py) | 13 | 11 | **2** | `CbBondpad`, `bondpad_cb` |
| `SVaricap` | [SVaricap_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/SVaricap_code.py) | 7 | 5 | **2** | `CbSVaricap_wl` |
| `NoFillerStack` | [NoFillerStack_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/NoFillerStack_code.py) | 12 | 11 | **1** | — |
| `via_stack` | [via_stack_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/via_stack_code.py) | 8 | 8 | 0 | — |
| `esd` | [esd_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/esd_code.py) | 1 | 1 | 0 | — |
| `rfmosfet_base` | [rfmosfet_base_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/rfmosfet_base_code.py) | 7 | 7 | 0 | — |
| `guard_ring` | [guard_ring_code.py](../pdks/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib/ihp/guard_ring_code.py) | 3 | 3 | 0 | — |

## The recurring dead set

Most of the unused declarations are the same handful of Cadence CDF parameters repeated device by device. Frequency across all PCells:

| Parameter | Unused in | PCells |
|---|---:|---|
| `model` | 23 | `nmos`, `nmosHV`, `pmos`, `pmosHV`, `cmim`, `rsil`, `rhigh`, `rppd`, `npn13G2`, `npn13G2L`, `npn13G2V`, `dantenna`, `dpantenna`, `bondpad`, `rfcmim`, `rfnmos`, `rfnmosHV`, `rfpmos`, `rfpmosHV`, `SVaricap`, `pnpMPA`, `isolbox`, `schottky` |
| `cdf_version` | 18 | `nmos`, `nmosHV`, `pmos`, `pmosHV`, `cmim`, `rsil`, `rhigh`, `rppd`, `sealring`, `npn13G2`, `npn13G2L`, `npn13G2V`, `inductor2`, `inductor3`, `dantenna`, `dpantenna`, `isolbox`, `schottky` |
| `Display` | 18 | `nmos`, `nmosHV`, `pmos`, `pmosHV`, `cmim`, `rsil`, `rhigh`, `rppd`, `sealring`, `npn13G2`, `npn13G2L`, `npn13G2V`, `inductor2`, `inductor3`, `dantenna`, `dpantenna`, `isolbox`, `schottky` |
| `m` | 15 | `nmos`, `nmosHV`, `pmos`, `pmosHV`, `cmim`, `rsil`, `rhigh`, `rppd`, `npn13G2`, `npn13G2L`, `npn13G2V`, `dantenna`, `dpantenna`, `pnpMPA`, `schottky` |
| `trise` | 14 | `nmos`, `nmosHV`, `pmos`, `pmosHV`, `cmim`, `rsil`, `rhigh`, `rppd`, `npn13G2`, `npn13G2L`, `npn13G2V`, `dantenna`, `dpantenna`, `pnpMPA` |
| `Wmin` | 9 | `cmim`, `rsil`, `rhigh`, `rppd`, `rfcmim`, `rfnmos`, `rfnmosHV`, `rfpmos`, `rfpmosHV` |
| `Lmin` | 9 | `cmim`, `rsil`, `rhigh`, `rppd`, `rfcmim`, `rfnmos`, `rfnmosHV`, `rfpmos`, `rfpmosHV` |
| `bn` | 9 | `rsil`, `rhigh`, `rppd`, `npn13G2`, `npn13G2L`, `npn13G2V`, `dantenna`, `SVaricap`, `isolbox` |
| `Rspec` | 5 | `rsil`, `rhigh`, `rppd`, `ptap1`, `ntap1` |
| `rfmode` | 4 | `rfnmos`, `rfnmosHV`, `rfpmos`, `rfpmosHV` |
| `ws` | 4 | `rfnmos`, `rfnmosHV`, `rfpmos`, `rfpmosHV` |
| `calculate` | 4 | `rfnmos`, `rfnmosHV`, `rfpmos`, `rfpmosHV` |
| `PSmin` | 3 | `rsil`, `rhigh`, `rppd` |
| `Rkspec` | 3 | `rsil`, `rhigh`, `rppd` |
| `Rzspec` | 3 | `rsil`, `rhigh`, `rppd` |
| `tc1` | 3 | `rsil`, `rhigh`, `rppd` |
| `tc2` | 3 | `rsil`, `rhigh`, `rppd` |
| `Icmax` | 3 | `npn13G2`, `npn13G2L`, `npn13G2V` |
| `Iarea` | 3 | `npn13G2`, `npn13G2L`, `npn13G2V` |
| `area` | 3 | `npn13G2`, `npn13G2L`, `npn13G2V` |
| `region` | 3 | `dantenna`, `dpantenna`, `pnpMPA` |
| `Calculate` | 3 | `ptap1`, `ntap1`, `pnpMPA` |
| `Cspec` | 2 | `cmim`, `rfcmim` |
| `Cmax` | 2 | `cmim`, `rfcmim` |
| `PWB` | 2 | `rhigh`, `rppd` |
| `Vbe` | 2 | `npn13G2L`, `npn13G2V` |
| `Vce` | 2 | `npn13G2L`, `npn13G2V` |
| `mergeStat` | 2 | `inductor2`, `inductor3` |
| `off` | 2 | `dantenna`, `dpantenna` |
| `Vd` | 2 | `dantenna`, `dpantenna` |
| `perim` | 2 | `dantenna`, `dpantenna` |
| `dtemp` | 2 | `dantenna`, `dpantenna` |
| `mode` | 2 | `dantenna`, `dpantenna` |
| `R` | 2 | `ptap1`, `ntap1` |
| `A` | 2 | `ptap1`, `ntap1` |
| `Perim` | 2 | `ptap1`, `ntap1` |
| `ic` | 1 | `cmim` |
| `padPin` | 1 | `bondpad` |
| `wfeed` | 1 | `rfcmim` |
| `minLW` | 1 | `NoFillerStack` |
| `a` | 1 | `pnpMPA` |
| `p` | 1 | `pnpMPA` |
| `ac` | 1 | `pnpMPA` |
| `pc` | 1 | `pnpMPA` |
| `aw` | 1 | `isolbox` |
| `pw` | 1 | `isolbox` |

These fall into three groups:

1. **Netlist / simulation parameters** — `model`, `m`, `trise`, `dtemp`, `region`, `off`, `Vd`, `perim`, `mode`, `ic`, `Vbe`, `Vce`, `tc1`, `tc2`. In the Cadence PDK these are consumed by the *netlister*, not the PCell. The KLayout PyCell only draws geometry, so nothing reads them. They exist so the parameter set matches the Cadence cell.
2. **CDF UI machinery** — `cdf_version`, `Display`. Pure Cadence infrastructure with no KLayout equivalent.
3. **Derived read-outs whose callback was never wired up** — `R`, `A`, `Perim`, `a`, `p`, `ac`, `pc`, `Icmax`, `Iarea`, `area`, `aw`, `pw`, `mergeStat`, and the `Wmin`/`Lmin`/`Cmax`/`Cspec`/`Rspec` limit displays. These are the genuinely misleading ones: the dialog shows a number that was computed once from the default `w`/`l` and then goes stale.

## Notable findings

### Devices with no callbacks at all

`npn13G2`, `npn13G2L`, `npn13G2V`, `via_stack`, `ptap1`, `ntap1`, `esd`, `rfmosfet_base`, `rfnmos`, `rfnmosHV`, `rfpmos`, `rfpmosHV`, `NoFillerStack`, `pnpMPA`, `schottky`, `guard_ring`

For these, every derived/computed parameter is frozen at its default. Worth singling out:

- **`ptap1` / `ntap1`** — declare `Calculate`, `R`, `A`, `Perim`, `Rspec` and register no callback, so the resistance and area read-outs never update and `Calculate` does nothing. There is no Tcl tap callback at all; the only `CbTapCalc` is the Python one in `utility_functions.py`, which runs once at declaration time to seed the default `R` string.
- **`pnpMPA`** — declares `Calculate`, `a`, `p`, `ac`, `pc`, and `diode_cb.tcl` even has a dedicated `if {$cell == "pnpMPA"}` branch that computes `ac`/`pc`. But `pnpMPA` is absent from `callbacks.json`, so that branch never executes.
- **`rfnmos` / `rfnmosHV` / `rfpmos` / `rfpmosHV`** — declare `calculate`, `ws`, `Wmin`, `Lmin`, `rfmode`. `mos_cb.tcl` handles `ws` for the plain MOS devices, but the RF variants are not registered.
- **`npn13G2L` / `npn13G2V`** — 11 of 14 parameters unused; only `Nx`, `le` and `we` reach the layout code.

### Dead callback code

Three procs are defined but neither registered in `callbacks.json` nor called by any registered proc, so the parameters they maintain are unreachable:

| Proc | File | Maintains | Reachable? |
|---|---|---|---|
| `isolbox_done` | `callbacks/isolbox_cb.tcl:223` | `aw`, `pw` | no — never called |
| `l2_ind_lvs_cb` | `callbacks/inductor_cb.tcl:233` | `mergeStat` | no — never called |
| `CbSVaricap_thickO` | `callbacks/cap_cb.tcl:446` | `thickO`, `model` | no — not registered for `SVaricap` |

### Cleanest devices

`via_stack`, `esd`, `rfmosfet_base`, `guard_ring` — every declared parameter is consumed.

### The `#ifdef KLAYOUT` split

Twelve files already strip the CDF residue for the KLayout build. Their `#else` branches declare parameters that only a Cadence run would see:

| PCell | Extra parameters in the `#else` (Cadence) branch |
|---|---|
| `via_stack` | `cdf_version` |
| `ptap1` | `Display`, `Lmin`, `Wmin`, `cdf_version`, `m` |
| `ntap1` | `Display`, `Lmin`, `Wmin`, `cdf_version`, `m` |
| `bondpad` | `Display`, `cdf_version` |
| `rfcmim` | `Display`, `cdf_version`, `ic`, `m`, `trise` |
| `rfnmos` | `Display`, `cdf_version`, `m`, `trise` |
| `rfnmosHV` | `Display`, `cdf_version`, `m`, `trise` |
| `rfpmos` | `Display`, `cdf_version`, `m`, `trise` |
| `rfpmosHV` | `Display`, `cdf_version`, `m`, `trise` |
| `NoFillerStack` | `Display`, `cdf_version` |
| `SVaricap` | `Display`, `cdf_version` |
| `pnpMPA` | `Display`, `cdf_version` |

The devices *without* an `#ifdef` — notably `dantenna`, `dpantenna`, `cmim`, the resistors, and the bipolars — still carry the full CDF set in the KLayout GUI. That inconsistency is the single largest source of the unused declarations above.

## Per-PCell detail

### `bondpad`

`ihp/bondpad_code.py` &nbsp;·&nbsp; 13 declared, 2 unused &nbsp;·&nbsp; callbacks: `CbBondpad`, `bondpad_cb`

| Parameter | Declared in | Role |
|---|---|---|
| `model` | — | **unused** |
| `shape` | — | `layout` |
| `stack` | — | `layout` |
| `fill` | — | `layout` |
| `FlipChip` | — | `layout`, `cb-read`, `cb-trigger` |
| `diameter` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `hwquota` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `topMetal` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `bottomMetal` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `addFillerEx` | — | `layout` |
| `passEncl` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `padType` | — | `layout`, `cb-read`, `cb-trigger` |
| `padPin` | — | **unused** |

*Cadence-only (`#else` branch, not present in KLayout):* `Display`, `cdf_version`

### `cmim`

`ihp/cmim_code.py` &nbsp;·&nbsp; class chain: `cmim` → `DeviceBase` &nbsp;·&nbsp; 16 declared, 10 unused &nbsp;·&nbsp; callbacks: `CbCap`

| Parameter | Declared in | Role |
|---|---|---|
| `cdf_version` | — | **unused** |
| `Display` | — | **unused** |
| `Calculate` | — | `cb-read`, `cb-trigger` |
| `model` | — | **unused** |
| `C` | — | `cb-read`, `cb-write`, `cb-trigger` |
| `w` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `l` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `Cspec` | — | **unused** |
| `Wmin` | — | **unused** |
| `Lmin` | — | **unused** |
| `Cmax` | — | **unused** |
| `ic` | — | **unused** |
| `m` | — | **unused** |
| `trise` | — | **unused** |
| `guardRingType` | `DeviceBase` | `layout` |
| `guardRingDistance` | `DeviceBase` | `layout` |

### `dantenna`

`ihp/dantenna_code.py` &nbsp;·&nbsp; class chain: `dantenna` → `DeviceBase` &nbsp;·&nbsp; 20 declared, 12 unused &nbsp;·&nbsp; callbacks: `CbDiode`

| Parameter | Declared in | Role |
|---|---|---|
| `cdf_version` | — | **unused** |
| `Display` | — | **unused** |
| `model` | — | **unused** |
| `Calculate` | — | `cb-read`, `cb-trigger` |
| `w` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `l` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `a` | — | `cb-read`, `cb-write`, `cb-trigger` |
| `p` | — | `cb-write`, `cb-trigger` |
| `addRecLayer` | — | `layout` |
| `bn` | — | **unused** |
| `off` | — | **unused** |
| `Vd` | — | **unused** |
| `perim` | — | **unused** |
| `m` | — | **unused** |
| `trise` | — | **unused** |
| `region` | — | **unused** |
| `dtemp` | — | **unused** |
| `mode` | — | **unused** |
| `guardRingType` | `DeviceBase` | `layout` |
| `guardRingDistance` | `DeviceBase` | `layout` |

### `dpantenna`

`ihp/dpantenna_code.py` &nbsp;·&nbsp; class chain: `dpantenna` → `DeviceBase` &nbsp;·&nbsp; 19 declared, 11 unused &nbsp;·&nbsp; callbacks: `CbDiode`

| Parameter | Declared in | Role |
|---|---|---|
| `cdf_version` | — | **unused** |
| `Display` | — | **unused** |
| `model` | — | **unused** |
| `Calculate` | — | `cb-read`, `cb-trigger` |
| `w` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `l` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `a` | — | `cb-read`, `cb-write`, `cb-trigger` |
| `p` | — | `cb-write`, `cb-trigger` |
| `addRecLayer` | — | `layout` |
| `off` | — | **unused** |
| `Vd` | — | **unused** |
| `perim` | — | **unused** |
| `m` | — | **unused** |
| `trise` | — | **unused** |
| `region` | — | **unused** |
| `dtemp` | — | **unused** |
| `mode` | — | **unused** |
| `guardRingType` | `DeviceBase` | `layout` |
| `guardRingDistance` | `DeviceBase` | `layout` |

### `esd`

`ihp/esd_code.py` &nbsp;·&nbsp; 1 declared, 0 unused &nbsp;·&nbsp; no callbacks registered

| Parameter | Declared in | Role |
|---|---|---|
| `model` | — | `layout` |

### `guard_ring`

`ihp/guard_ring_code.py` &nbsp;·&nbsp; 3 declared, 0 unused &nbsp;·&nbsp; no callbacks registered

| Parameter | Declared in | Role |
|---|---|---|
| `type` | — | `layout` |
| `w` | — | `layout` |
| `h` | — | `layout` |

### `inductor2`

`ihp/inductor2_code.py` &nbsp;·&nbsp; class chain: `inductor2` → `inductors` → `DeviceBase` &nbsp;·&nbsp; 20 declared, 3 unused &nbsp;·&nbsp; callbacks: `inductor_w`, `inductor_s`, `inductor_nr`, `inductor_d`

| Parameter | Declared in | Role |
|---|---|---|
| `cdf_version` | `inductors` | **unused** |
| `Display` | `inductors` | **unused** |
| `model` | `inductors` | `layout` |
| `w` | `inductors` | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `s` | `inductors` | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `d` | `inductors` | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `r` | `inductors` | `layout` |
| `l` | `inductors` | `layout` |
| `nr_r` | `inductors` | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `blockqrc` | `inductors` | `layout` |
| `subE` | `inductors` | `layout` |
| `lEstim` | `inductors` | `cb-write` |
| `rEstim` | `inductors` | `cb-write` |
| `Wmin` | `inductors` | `cb-read` |
| `Smin` | `inductors` | `cb-read` |
| `Dmin` | `inductors` | `cb-read`, `cb-write` |
| `minNr_t` | `inductors` | `cb-read` |
| `mergeStat` | `inductors` | **unused** |
| `guardRingType` | `DeviceBase` | `layout` |
| `guardRingDistance` | `DeviceBase` | `layout` |

### `inductor3`

`ihp/inductor3_code.py` &nbsp;·&nbsp; class chain: `inductor3` → `inductors` → `DeviceBase` &nbsp;·&nbsp; 20 declared, 3 unused &nbsp;·&nbsp; callbacks: `inductor_w`, `inductor_s`, `inductor_nr`, `inductor_d`

| Parameter | Declared in | Role |
|---|---|---|
| `cdf_version` | `inductors` | **unused** |
| `Display` | `inductors` | **unused** |
| `model` | `inductors` | `layout` |
| `w` | `inductors` | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `s` | `inductors` | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `d` | `inductors` | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `r` | `inductors` | `layout` |
| `l` | `inductors` | `layout` |
| `nr_r` | `inductors` | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `blockqrc` | `inductors` | `layout` |
| `subE` | `inductors` | `layout` |
| `lEstim` | `inductors` | `cb-write` |
| `rEstim` | `inductors` | `cb-write` |
| `Wmin` | `inductors` | `cb-read` |
| `Smin` | `inductors` | `cb-read` |
| `Dmin` | `inductors` | `cb-read`, `cb-write` |
| `minNr_t` | `inductors` | `cb-read` |
| `mergeStat` | `inductors` | **unused** |
| `guardRingType` | `DeviceBase` | `layout` |
| `guardRingDistance` | `DeviceBase` | `layout` |

### `isolbox`

`ihp/isolbox_code.py` &nbsp;·&nbsp; 18 declared, 6 unused &nbsp;·&nbsp; callbacks: `isol_l`, `isol_w`, `isol_well`, `isolbox_cb`

| Parameter | Declared in | Role |
|---|---|---|
| `cdf_version` | — | **unused** |
| `Display` | — | **unused** |
| `model` | — | **unused** |
| `l` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `w` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `wellwidth` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `diode_layer` | — | `layout` |
| `cont_ring` | — | `layout` |
| `calculate` | — | `cb-read`, `cb-trigger` |
| `pwell_w` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `Bv` | — | `cb-read`, `cb-write`, `cb-trigger` |
| `a` | — | `cb-write` |
| `p` | — | `cb-write` |
| `aw` | — | **unused** |
| `pw` | — | **unused** |
| `Wmin` | — | `cb-read`, `cb-write` |
| `Lmin` | — | `cb-read`, `cb-write` |
| `bn` | — | **unused** |

### `nmos`

`ihp/nmos_code.py` &nbsp;·&nbsp; class chain: `nmos` → `DeviceBase` &nbsp;·&nbsp; 13 declared, 5 unused &nbsp;·&nbsp; callbacks: `NLCB_mos_w`, `NLCB_mos_ng`, `NLCB_mos_l`

| Parameter | Declared in | Role |
|---|---|---|
| `cdf_version` | — | **unused** |
| `Display` | — | **unused** |
| `model` | — | **unused** |
| `w` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `ws` | — | `cb-write`, `cb-trigger` |
| `l` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `Wmin` | — | `cb-read` |
| `Lmin` | — | `cb-read` |
| `ng` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `m` | — | **unused** |
| `trise` | — | **unused** |
| `guardRingType` | `DeviceBase` | `layout` |
| `guardRingDistance` | `DeviceBase` | `layout` |

### `nmosHV`

`ihp/nmosHV_code.py` &nbsp;·&nbsp; class chain: `nmosHV` → `DeviceBase` &nbsp;·&nbsp; 13 declared, 5 unused &nbsp;·&nbsp; callbacks: `NLCB_mos_w`, `NLCB_mos_ng`, `NLCB_mos_l`

| Parameter | Declared in | Role |
|---|---|---|
| `cdf_version` | — | **unused** |
| `Display` | — | **unused** |
| `model` | — | **unused** |
| `w` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `ws` | — | `cb-write`, `cb-trigger` |
| `l` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `Wmin` | — | `cb-read` |
| `Lmin` | — | `cb-read` |
| `ng` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `m` | — | **unused** |
| `trise` | — | **unused** |
| `guardRingType` | `DeviceBase` | `layout` |
| `guardRingDistance` | `DeviceBase` | `layout` |

### `NoFillerStack`

`ihp/NoFillerStack_code.py` &nbsp;·&nbsp; 12 declared, 1 unused &nbsp;·&nbsp; no callbacks registered

| Parameter | Declared in | Role |
|---|---|---|
| `w` | — | `layout` |
| `l` | — | `layout` |
| `minLW` | — | **unused** |
| `noAct` | — | `layout` |
| `noGP` | — | `layout` |
| `noM1` | — | `layout` |
| `noM2` | — | `layout` |
| `noM3` | — | `layout` |
| `noM4` | — | `layout` |
| `noM5` | — | `layout` |
| `noTM1` | — | `layout` |
| `noTM2` | — | `layout` |

*Cadence-only (`#else` branch, not present in KLayout):* `Display`, `cdf_version`

### `npn13G2`

`ihp/npn13G2_code.py` &nbsp;·&nbsp; 22 declared, 9 unused &nbsp;·&nbsp; no callbacks registered

| Parameter | Declared in | Role |
|---|---|---|
| `cdf_version` | — | **unused** |
| `Display` | — | **unused** |
| `model` | — | **unused** |
| `Nx` | — | `layout` |
| `Ny` | — | `layout` |
| `le` | — | `layout` |
| `we` | — | `layout` |
| `STI` | — | `layout` |
| `baspolyx` | — | `layout` |
| `bipwinx` | — | `layout` |
| `bipwiny` | — | `layout` |
| `empolyx` | — | `layout` |
| `empolyy` | — | `layout` |
| `Icmax` | — | **unused** |
| `Iarea` | — | **unused** |
| `area` | — | **unused** |
| `bn` | — | **unused** |
| `m` | — | **unused** |
| `trise` | — | **unused** |
| `Text` | — | `layout` |
| `CMetY1` | — | `layout` |
| `CMetY2` | — | `layout` |

### `npn13G2L`

`ihp/npn13G2L_code.py` &nbsp;·&nbsp; 14 declared, 11 unused &nbsp;·&nbsp; no callbacks registered

| Parameter | Declared in | Role |
|---|---|---|
| `cdf_version` | — | **unused** |
| `Display` | — | **unused** |
| `model` | — | **unused** |
| `Nx` | — | `layout` |
| `le` | — | `layout` |
| `we` | — | `layout` |
| `Icmax` | — | **unused** |
| `Iarea` | — | **unused** |
| `area` | — | **unused** |
| `bn` | — | **unused** |
| `Vbe` | — | **unused** |
| `Vce` | — | **unused** |
| `m` | — | **unused** |
| `trise` | — | **unused** |

### `npn13G2V`

`ihp/npn13G2V_code.py` &nbsp;·&nbsp; 14 declared, 11 unused &nbsp;·&nbsp; no callbacks registered

| Parameter | Declared in | Role |
|---|---|---|
| `cdf_version` | — | **unused** |
| `Display` | — | **unused** |
| `model` | — | **unused** |
| `Nx` | — | `layout` |
| `le` | — | `layout` |
| `we` | — | `layout` |
| `Icmax` | — | **unused** |
| `Iarea` | — | **unused** |
| `area` | — | **unused** |
| `bn` | — | **unused** |
| `Vbe` | — | **unused** |
| `Vce` | — | **unused** |
| `m` | — | **unused** |
| `trise` | — | **unused** |

### `ntap1`

`ihp/ntap1_code.py` &nbsp;·&nbsp; 7 declared, 5 unused &nbsp;·&nbsp; no callbacks registered

| Parameter | Declared in | Role |
|---|---|---|
| `Calculate` | — | **unused** |
| `R` | — | **unused** |
| `w` | — | `layout` |
| `l` | — | `layout` |
| `A` | — | **unused** |
| `Perim` | — | **unused** |
| `Rspec` | — | **unused** |

*Cadence-only (`#else` branch, not present in KLayout):* `Display`, `Lmin`, `Wmin`, `cdf_version`, `m`

### `pmos`

`ihp/pmos_code.py` &nbsp;·&nbsp; class chain: `pmos` → `DeviceBase` &nbsp;·&nbsp; 13 declared, 5 unused &nbsp;·&nbsp; callbacks: `NLCB_mos_w`, `NLCB_mos_ng`, `NLCB_mos_l`

| Parameter | Declared in | Role |
|---|---|---|
| `cdf_version` | — | **unused** |
| `Display` | — | **unused** |
| `model` | — | **unused** |
| `w` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `ws` | — | `cb-write`, `cb-trigger` |
| `l` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `Wmin` | — | `cb-read` |
| `Lmin` | — | `cb-read` |
| `ng` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `m` | — | **unused** |
| `trise` | — | **unused** |
| `guardRingType` | `DeviceBase` | `layout` |
| `guardRingDistance` | `DeviceBase` | `layout` |

### `pmosHV`

`ihp/pmosHV_code.py` &nbsp;·&nbsp; class chain: `pmosHV` → `DeviceBase` &nbsp;·&nbsp; 13 declared, 5 unused &nbsp;·&nbsp; callbacks: `NLCB_mos_w`, `NLCB_mos_ng`, `NLCB_mos_l`

| Parameter | Declared in | Role |
|---|---|---|
| `cdf_version` | — | **unused** |
| `Display` | — | **unused** |
| `model` | — | **unused** |
| `w` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `ws` | — | `cb-write` |
| `l` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `Wmin` | — | `cb-read` |
| `Lmin` | — | `cb-read` |
| `ng` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `m` | — | **unused** |
| `trise` | — | **unused** |
| `guardRingType` | `DeviceBase` | `layout` |
| `guardRingDistance` | `DeviceBase` | `layout` |

### `pnpMPA`

`ihp/pnpMPA_code.py` &nbsp;·&nbsp; 11 declared, 9 unused &nbsp;·&nbsp; no callbacks registered

| Parameter | Declared in | Role |
|---|---|---|
| `model` | — | **unused** |
| `Calculate` | — | **unused** |
| `w` | — | `layout` |
| `l` | — | `layout` |
| `a` | — | **unused** |
| `p` | — | **unused** |
| `ac` | — | **unused** |
| `pc` | — | **unused** |
| `m` | — | **unused** |
| `trise` | — | **unused** |
| `region` | — | **unused** |

*Cadence-only (`#else` branch, not present in KLayout):* `Display`, `cdf_version`

### `ptap1`

`ihp/ptap1_code.py` &nbsp;·&nbsp; 7 declared, 5 unused &nbsp;·&nbsp; no callbacks registered

| Parameter | Declared in | Role |
|---|---|---|
| `Calculate` | — | **unused** |
| `R` | — | **unused** |
| `w` | — | `layout` |
| `l` | — | `layout` |
| `A` | — | **unused** |
| `Perim` | — | **unused** |
| `Rspec` | — | **unused** |

*Cadence-only (`#else` branch, not present in KLayout):* `Display`, `Lmin`, `Wmin`, `cdf_version`, `m`

### `rfcmim`

`ihp/rfcmim_code.py` &nbsp;·&nbsp; 10 declared, 6 unused &nbsp;·&nbsp; callbacks: `CbCap`

| Parameter | Declared in | Role |
|---|---|---|
| `Calculate` | — | `cb-read`, `cb-trigger` |
| `model` | — | **unused** |
| `C` | — | `cb-read`, `cb-write`, `cb-trigger` |
| `w` | — | `cb-read`, `cb-write`, `cb-trigger` |
| `l` | — | `cb-read`, `cb-write`, `cb-trigger` |
| `wfeed` | — | **unused** |
| `Cspec` | — | **unused** |
| `Wmin` | — | **unused** |
| `Lmin` | — | **unused** |
| `Cmax` | — | **unused** |

*Cadence-only (`#else` branch, not present in KLayout):* `Display`, `cdf_version`, `ic`, `m`, `trise`

### `rfmosfet_base`

`ihp/rfmosfet_base_code.py` &nbsp;·&nbsp; 7 declared, 0 unused &nbsp;·&nbsp; no callbacks registered

| Parameter | Declared in | Role |
|---|---|---|
| `l` | — | `layout` |
| `w` | — | `layout` |
| `ng` | — | `layout` |
| `cnt_rows` | — | `layout` |
| `Met2Cont` | — | `layout` |
| `gat_ring` | — | `layout` |
| `guard_ring` | — | `layout` |

### `rfnmos`

`ihp/rfnmos_code.py` &nbsp;·&nbsp; class chain: `rfnmos` → `rfmosfet_base` &nbsp;·&nbsp; 13 declared, 6 unused &nbsp;·&nbsp; no callbacks registered

| Parameter | Declared in | Role |
|---|---|---|
| `rfmode` | — | **unused** |
| `model` | — | **unused** |
| `w` | — | `layout` |
| `ws` | — | **unused** |
| `l` | — | `layout` |
| `ng` | — | `layout` |
| `calculate` | — | **unused** |
| `cnt_rows` | — | `layout` |
| `Met2Cont` | — | `layout` |
| `gat_ring` | — | `layout` |
| `guard_ring` | — | `layout` |
| `Wmin` | — | **unused** |
| `Lmin` | — | **unused** |

*Cadence-only (`#else` branch, not present in KLayout):* `Display`, `cdf_version`, `m`, `trise`

### `rfnmosHV`

`ihp/rfnmosHV_code.py` &nbsp;·&nbsp; class chain: `rfnmosHV` → `rfmosfet_base` &nbsp;·&nbsp; 13 declared, 6 unused &nbsp;·&nbsp; no callbacks registered

| Parameter | Declared in | Role |
|---|---|---|
| `rfmode` | — | **unused** |
| `model` | — | **unused** |
| `w` | — | `layout` |
| `ws` | — | **unused** |
| `l` | — | `layout` |
| `ng` | — | `layout` |
| `calculate` | — | **unused** |
| `cnt_rows` | — | `layout` |
| `Met2Cont` | — | `layout` |
| `gat_ring` | — | `layout` |
| `guard_ring` | — | `layout` |
| `Wmin` | — | **unused** |
| `Lmin` | — | **unused** |

*Cadence-only (`#else` branch, not present in KLayout):* `Display`, `cdf_version`, `m`, `trise`

### `rfpmos`

`ihp/rfpmos_code.py` &nbsp;·&nbsp; class chain: `rfpmos` → `rfmosfet_base` &nbsp;·&nbsp; 13 declared, 6 unused &nbsp;·&nbsp; no callbacks registered

| Parameter | Declared in | Role |
|---|---|---|
| `rfmode` | — | **unused** |
| `model` | — | **unused** |
| `w` | — | `layout` |
| `ws` | — | **unused** |
| `l` | — | `layout` |
| `ng` | — | `layout` |
| `calculate` | — | **unused** |
| `cnt_rows` | — | `layout` |
| `Met2Cont` | — | `layout` |
| `gat_ring` | — | `layout` |
| `guard_ring` | — | `layout` |
| `Wmin` | — | **unused** |
| `Lmin` | — | **unused** |

*Cadence-only (`#else` branch, not present in KLayout):* `Display`, `cdf_version`, `m`, `trise`

### `rfpmosHV`

`ihp/rfpmosHV_code.py` &nbsp;·&nbsp; class chain: `rfpmosHV` → `rfmosfet_base` &nbsp;·&nbsp; 13 declared, 6 unused &nbsp;·&nbsp; no callbacks registered

| Parameter | Declared in | Role |
|---|---|---|
| `rfmode` | — | **unused** |
| `model` | — | **unused** |
| `w` | — | `layout` |
| `ws` | — | **unused** |
| `l` | — | `layout` |
| `ng` | — | `layout` |
| `calculate` | — | **unused** |
| `cnt_rows` | — | `layout` |
| `Met2Cont` | — | `layout` |
| `gat_ring` | — | `layout` |
| `guard_ring` | — | `layout` |
| `Wmin` | — | **unused** |
| `Lmin` | — | **unused** |

*Cadence-only (`#else` branch, not present in KLayout):* `Display`, `cdf_version`, `m`, `trise`

### `rhigh`

`ihp/rhigh_code.py` &nbsp;·&nbsp; class chain: `rhigh` → `ResistorBase` → `DeviceBase` &nbsp;·&nbsp; 28 declared, 15 unused &nbsp;·&nbsp; callbacks: `CbRes`

| Parameter | Declared in | Role |
|---|---|---|
| `cdf_version` | — | **unused** |
| `Display` | — | **unused** |
| `Calculate` | — | `cb-read`, `cb-trigger` |
| `Recommendation` | — | `cb-trigger` |
| `model` | — | **unused** |
| `R` | — | `cb-read`, `cb-write`, `cb-trigger` |
| `w` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `l` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `b` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `ps` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `Imax` | — | `cb-write` |
| `bn` | — | **unused** |
| `Wmin` | — | **unused** |
| `Lmin` | — | **unused** |
| `PSmin` | — | **unused** |
| `Rspec` | — | **unused** |
| `Rkspec` | — | **unused** |
| `Rzspec` | — | **unused** |
| `tc1` | — | **unused** |
| `tc2` | — | **unused** |
| `PWB` | — | **unused** |
| `m` | — | **unused** |
| `trise` | — | **unused** |
| `NumberOfSegments` | `ResistorBase` | `layout` |
| `SegmentConnection` | `ResistorBase` | `layout` |
| `SegmentSpacing` | `ResistorBase` | `layout` |
| `guardRingType` | `DeviceBase` | `layout` |
| `guardRingDistance` | `DeviceBase` | `layout` |

### `rppd`

`ihp/rppd_code.py` &nbsp;·&nbsp; class chain: `rppd` → `ResistorBase` → `DeviceBase` &nbsp;·&nbsp; 28 declared, 15 unused &nbsp;·&nbsp; callbacks: `CbRes`

| Parameter | Declared in | Role |
|---|---|---|
| `cdf_version` | — | **unused** |
| `Display` | — | **unused** |
| `Calculate` | — | `cb-read`, `cb-trigger` |
| `Recommendation` | — | `cb-trigger` |
| `model` | — | **unused** |
| `R` | — | `cb-read`, `cb-write`, `cb-trigger` |
| `w` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `l` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `b` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `ps` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `Imax` | — | `cb-write` |
| `bn` | — | **unused** |
| `Wmin` | — | **unused** |
| `Lmin` | — | **unused** |
| `PSmin` | — | **unused** |
| `Rspec` | — | **unused** |
| `Rkspec` | — | **unused** |
| `Rzspec` | — | **unused** |
| `tc1` | — | **unused** |
| `tc2` | — | **unused** |
| `PWB` | — | **unused** |
| `m` | — | **unused** |
| `trise` | — | **unused** |
| `NumberOfSegments` | `ResistorBase` | `layout` |
| `SegmentConnection` | `ResistorBase` | `layout` |
| `SegmentSpacing` | `ResistorBase` | `layout` |
| `guardRingType` | `DeviceBase` | `layout` |
| `guardRingDistance` | `DeviceBase` | `layout` |

### `rsil`

`ihp/rsil_code.py` &nbsp;·&nbsp; class chain: `rsil` → `ResistorBase` → `DeviceBase` &nbsp;·&nbsp; 25 declared, 14 unused &nbsp;·&nbsp; callbacks: `CbRes`

| Parameter | Declared in | Role |
|---|---|---|
| `cdf_version` | — | **unused** |
| `Display` | — | **unused** |
| `Calculate` | — | `cb-read`, `cb-trigger` |
| `model` | — | **unused** |
| `R` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `w` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `l` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `ps` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `Imax` | — | `cb-write` |
| `bn` | — | **unused** |
| `Wmin` | — | **unused** |
| `Lmin` | — | **unused** |
| `PSmin` | — | **unused** |
| `Rspec` | — | **unused** |
| `Rkspec` | — | **unused** |
| `Rzspec` | — | **unused** |
| `tc1` | — | **unused** |
| `tc2` | — | **unused** |
| `m` | — | **unused** |
| `trise` | — | **unused** |
| `NumberOfSegments` | `ResistorBase` | `layout` |
| `SegmentConnection` | `ResistorBase` | `layout` |
| `SegmentSpacing` | `ResistorBase` | `layout` |
| `guardRingType` | `DeviceBase` | `layout` |
| `guardRingDistance` | `DeviceBase` | `layout` |

### `schottky`

`ihp/schottky_code.py` &nbsp;·&nbsp; 8 declared, 4 unused &nbsp;·&nbsp; no callbacks registered

| Parameter | Declared in | Role |
|---|---|---|
| `cdf_version` | — | **unused** |
| `Display` | — | **unused** |
| `model` | — | **unused** |
| `w` | — | `layout` |
| `l` | — | `layout` |
| `Nx` | — | `layout` |
| `Ny` | — | `layout` |
| `m` | — | **unused** |

### `sealring`

`ihp/sealring_code.py` &nbsp;·&nbsp; 9 declared, 2 unused &nbsp;·&nbsp; callbacks: `NLCB_w`, `NLCB_l`

| Parameter | Declared in | Role |
|---|---|---|
| `cdf_version` | — | **unused** |
| `Display` | — | **unused** |
| `l` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `w` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `addLabel` | — | `layout` |
| `addSlit` | — | `layout` |
| `Lmin` | — | `cb-read` |
| `Wmin` | — | `cb-read` |
| `edgeBox` | — | `layout` |

### `SVaricap`

`ihp/SVaricap_code.py` &nbsp;·&nbsp; class chain: `SVaricap` → `DeviceBase` &nbsp;·&nbsp; 7 declared, 2 unused &nbsp;·&nbsp; callbacks: `CbSVaricap_wl`

| Parameter | Declared in | Role |
|---|---|---|
| `model` | — | **unused** |
| `w` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `l` | — | `layout`, `cb-read`, `cb-write`, `cb-trigger` |
| `Nx` | — | `layout` |
| `bn` | — | **unused** |
| `guardRingType` | `DeviceBase` | `layout` |
| `guardRingDistance` | `DeviceBase` | `layout` |

*Cadence-only (`#else` branch, not present in KLayout):* `Display`, `cdf_version`

### `via_stack`

`ihp/via_stack_code.py` &nbsp;·&nbsp; 8 declared, 0 unused &nbsp;·&nbsp; no callbacks registered

| Parameter | Declared in | Role |
|---|---|---|
| `b_layer` | — | `layout` |
| `t_layer` | — | `layout` |
| `vn_columns` | — | `layout` |
| `vn_rows` | — | `layout` |
| `vt1_columns` | — | `layout` |
| `vt1_rows` | — | `layout` |
| `vt2_columns` | — | `layout` |
| `vt2_rows` | — | `layout` |

*Cadence-only (`#else` branch, not present in KLayout):* `cdf_version`
