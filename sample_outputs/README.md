# Sample load plan outputs

Example outputs for three crate mixes (25 crates each, UK trailer 1360 × 240 × 270 cm).

Regenerate anytime:

```powershell
python generate_sample_outputs.py
```

| Folder | Scenario | Typical result |
|--------|----------|----------------|
| **1_mixed/** | 12 normal + 13 wide | Pairs first, then chessboard — **16 loaded**, 9 overflow |
| **2_all_wide/** | All wide (~131–132 cm width) | Chessboard only — **9 loaded**, 16 overflow |
| **3_all_normal/** | All narrow/pairable (~107–120 cm width) | Pairs only — **16 loaded**, 9 overflow |

Each folder contains:

- `crate_data.xlsx` — input data for that scenario
- `report.txt` — full text report
- `load_plan.png` — floor-plan image

**Normal** = two crates fit side-by-side across the 240 cm trailer width.  
**Wide** = one crate per row on the left or right wall (chessboard).
