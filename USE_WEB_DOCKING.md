# Using Web-Based AutoDock Vina (Tamarind Bio)

Instead of installing Vina locally, you can use the web interface at: **https://app.tamarind.bio/tools/autodock-vina**

This is perfect for:
- ✅ Quick testing without installation
- ✅ Small number of variants (like your 6 variants)
- ✅ No local software setup needed

---

## Step-by-Step Guide

### Step 1: Prepare Your Files

You'll need:
1. **Receptor file** (PDB format): `data/P43250_receptor_clean.pdb`
2. **Ligand files** (PDB format): One for each variant (you'll need to generate these first)

**Note:** The web tool needs PDB files, not PDBQT. That's fine - we can work with that!

---

### Step 2: Generate Peptide 3D Structures

**You still need this step!** The web tool needs 3D structures (PDB files) for your peptides.

**Easiest method:**
1. Go to **ColabFold**: https://colab.research.google.com/github/sokrypton/ColabFold
2. For each variant:
   - Get sequence from `data/docking/GRK6_variant_XXXX/ligand.fasta`
   - Paste into ColabFold
   - Download the PDB structure
   - Save as: `data/docking/GRK6_variant_XXXX/ligand.pdb`

---

### Step 3: Run Docking on Web Interface

For **each of your 6 variants**:

1. **Go to:** https://app.tamarind.bio/tools/autodock-vina

2. **Upload files:**
   - **Receptor:** Upload `data/P43250_receptor_clean.pdb`
   - **Ligand:** Upload `data/docking/GRK6_variant_XXXX/ligand.pdb`

3. **Configure docking:**
   - **Binding site:** You'll need to specify coordinates
     - If unknown, use center of receptor: (0, 0, 0)
     - Box size: 20×20×20 Å
   - **Exhaustiveness:** 8 (default is fine)
   - **Number of modes:** 10

4. **Run docking** and wait for results

5. **Download results:**
   - Download the **log file** (contains binding scores)
   - Download the **docked pose** (optional, for visualization)

6. **Save to your pipeline:**
   - Save log file as: `data/docking/GRK6_variant_XXXX/log.txt`
   - Save docked pose as: `data/docking/GRK6_variant_XXXX/docked.pdbqt` (or `.pdb`)

---

### Step 4: Parse Results

Once you have log files for all variants:

```bash
# Your existing script will automatically find and parse them!
python src/parse_docking.py
```

**Check results:**
```bash
cat data/docking_results.csv
# Should now show real scores instead of 0.0!
```

---

## Quick Workflow Summary

```
For each variant (0001-0006):
1. Generate 3D structure → ligand.pdb
2. Upload receptor + ligand to Tamarind Bio
3. Run docking
4. Download log.txt → save to data/docking/GRK6_variant_XXXX/
5. Repeat for next variant

Then:
6. python src/parse_docking.py  (extracts scores)
7. python src/scoring.py         (ranks variants)
8. python src/select_for_synthesis.py --top 3
```

---

## Finding Binding Site Coordinates

If you don't know the binding site location:

### Option A: Use Receptor Center (Quick Test)
- Center: (0, 0, 0)
- Size: 30×30×30 Å (larger box to cover more area)

### Option B: Use PyMOL (If Available)
1. Load receptor: `data/P43250_receptor_clean.pdb`
2. Visualize and identify binding site
3. Get coordinates from selection

### Option C: Use fpocket (Automatic)
```bash
# If you install fpocket
fpocket -f data/P43250_receptor_clean.pdb
# Check output for largest pocket coordinates
```

### Option D: Check Literature/UniProt
- Look up GRK6 binding site information
- Use known binding site coordinates if available

---

## What the Log File Should Look Like

The web tool should provide a log file with content like:

```
REMARK VINA RESULT:    -7.234      0.000      0.000
REMARK VINA RESULT:    -6.891      0.000      0.000
...
```

Your `parse_docking.py` script will automatically extract the first (best) score.

---

## Advantages of Web-Based Approach

✅ **No installation needed** - works immediately
✅ **No local computational resources** - runs in cloud
✅ **User-friendly interface** - easier than command line
✅ **Good for small batches** - perfect for your 6 variants

## Disadvantages

❌ **Manual work** - need to run each variant separately
❌ **Time consuming** - 6 variants × ~5-10 min each = 30-60 minutes
❌ **Not scalable** - wouldn't work for 100+ variants
❌ **Requires internet** - need web access

---

## Alternative: Hybrid Approach

You could:
1. **Test with web tool** for 1-2 variants to verify workflow
2. **Install locally** if you want to automate for all variants
3. **Use web tool** for final validation of top candidates

---

## After Getting Results

Once you have log files for all variants:

```bash
# 1. Parse docking results (extracts scores from logs)
python src/parse_docking.py

# 2. Check that scores are real now
cat data/docking_results.csv
# Should see values like -7.2, -6.8, etc. instead of 0.0

# 3. Re-score with real docking data
python src/scoring.py

# 4. Select top candidates
python src/select_for_synthesis.py --top 3
```

---

## Troubleshooting

### "Log file format not recognized"
- Make sure the log file contains "REMARK VINA RESULT:" lines
- Check that you downloaded the correct file from Tamarind Bio

### "Still showing 0.0 scores"
- Verify log files are in correct location: `data/docking/GRK6_variant_XXXX/log.txt`
- Check that log files contain actual scores (not empty)
- Run `python src/parse_docking.py` again

### "Can't find binding site"
- Start with large box (30×30×30) at center (0,0,0)
- Refine coordinates after seeing initial results

---

## Next Steps

1. **Generate peptide structures** (ColabFold - see Step 2 above)
2. **Run docking on web** for each variant
3. **Save log files** to correct directories
4. **Parse results** with your pipeline

Good luck! 🚀

