# Step-by-Step Guide: Getting Real Docking Scores

This guide will walk you through getting real docking scores for your peptide variants.

---

## 🎯 Quick Overview

**What we need:**
1. 3D structures for your 6 peptide variants (currently only have sequences)
2. Convert receptor and peptides to PDBQT format
3. Run AutoDock Vina docking
4. Parse the results (your pipeline will do this automatically!)

**Time estimate:** 2-3 hours (mostly waiting for structure prediction)

---

## Step 1: Check What You Have ✅

Let's first see what's already in place:

```bash
# Check if you have the receptor structure
ls data/P43250_receptor_clean.pdb

# Check what's in docking directories
ls data/docking/GRK6_variant_0001/
```

**Expected:** You should see `ligand.fasta` files but no `ligand.pdb` files yet.

---

## Step 2: Install Required Software (15 minutes)

### Option A: Using Conda (Recommended)

```bash
# Activate your virtual environment first
source .venv/Scripts/activate  # Windows Git Bash
# OR
.venv\Scripts\activate.bat     # Windows CMD

# Install AutoDock Vina
conda install -c conda-forge autodock-vina

# Install OpenBabel (for PDB→PDBQT conversion)
conda install -c conda-forge openbabel

# Verify installation
vina --version
obabel -V
```

### Option B: Manual Installation

**AutoDock Vina:**
- Download from: https://vina.scripps.edu/downloads/
- Extract and add to PATH

**OpenBabel:**
- Download from: https://openbabel.org/wiki/Category:Installation
- Or use: `pip install openbabel-wheel` (if available)

---

## Step 3: Generate 3D Structures for Peptides (1-2 hours)

**This is the main step!** You need 3D structures (PDB files) for each variant.

### Method A: ColabFold (Easiest - No GPU needed) ⭐ RECOMMENDED

1. **Go to ColabFold:**
   - Open: https://colab.research.google.com/github/sokrypton/ColabFold
   - Click "Runtime" → "Change runtime type" → Select "T4 GPU" (free tier)

2. **For each variant, do this:**
   - Get the sequence from `data/docking/GRK6_variant_XXXX/ligand.fasta`
   - Paste into ColabFold
   - Click "Run" and wait ~5-10 minutes
   - Download the PDB file
   - Save as: `data/docking/GRK6_variant_XXXX/ligand.pdb`

3. **Quick script to extract sequences:**
   ```bash
   # View all sequences at once
   for dir in data/docking/GRK6_variant_*/; do
       echo "=== $(basename $dir) ==="
       grep -v ">" "$dir/ligand.fasta" | tr -d '\n'
       echo ""
   done
   ```

### Method B: PEP-FOLD3 (Web Server - Very Fast)

1. Go to: https://bioserv.rpbs.univ-paris-diderot.fr/services/PEP-FOLD3/
2. Paste sequence
3. Submit (takes ~1-2 minutes)
4. Download PDB structure
5. Save to appropriate directory

### Method C: Local AlphaFold2 (If you have GPU)

```bash
# Install
conda install -c conda-forge openfold

# Predict structure (would need custom script)
# This is more complex - use ColabFold instead
```

**For now, I recommend Method A (ColabFold)** - it's free, no installation needed, and works well for peptides.

---

## Step 4: Convert Structures to PDBQT Format (5 minutes)

Once you have PDB files, convert them:

```bash
# Use the helper script I created
python src/convert_to_pdbqt.py
```

This will:
- Convert `data/P43250_receptor_clean.pdb` → `.pdbqt`
- Convert all `data/docking/GRK6_variant_XXXX/ligand.pdb` → `ligand.pdbqt`

**Or manually:**
```bash
# Convert receptor
obabel data/P43250_receptor_clean.pdb -O data/P43250_receptor_clean.pdbqt -xr

# Convert each peptide
obabel data/docking/GRK6_variant_0001/ligand.pdb \
       -O data/docking/GRK6_variant_0001/ligand.pdbqt -xr
# Repeat for variants 0002-0006
```

---

## Step 5: Create Docking Configuration (10 minutes)

Create `data/docking_config.txt`:

```txt
receptor = data/P43250_receptor_clean.pdbqt
center_x = 0.0
center_y = 0.0
center_z = 0.0
size_x = 20.0
size_y = 20.0
size_z = 20.0
exhaustiveness = 8
num_modes = 10
```

**Finding the binding site coordinates:**

### Option A: Use PyMOL (if installed)
```python
# In PyMOL
load data/P43250_receptor_clean.pdb
# Visualize and find binding site
# Get coordinates from selection
```

### Option B: Use fpocket (automatic pocket detection)
```bash
# Install fpocket
conda install -c conda-forge fpocket

# Find pockets
fpocket -f data/P43250_receptor_clean.pdb

# Check output for largest pocket coordinates
```

### Option C: Use known binding site (if available)
- Check UniProt entry for binding site information
- Or use literature/experimental data

**For testing:** Start with center at (0, 0, 0) and size 20×20×20 Å. You can refine later.

---

## Step 6: Run Docking (10-30 minutes)

```bash
# Make script executable (if needed)
chmod +x src/run_docking.sh

# Run docking for all variants
bash src/run_docking.sh
```

**Or use Python version:**
```bash
python src/run_docking.py  # (if I create this)
```

**What happens:**
- Vina docks each peptide variant to the receptor
- Creates `docked.pdbqt` files (binding poses)
- Creates `log.txt` files (with binding scores)

**Expected output:**
```
Docking GRK6_variant_0001...
✓ GRK6_variant_0001 complete
Docking GRK6_variant_0002...
✓ GRK6_variant_0002 complete
...
```

---

## Step 7: Parse Results (Automatic!)

```bash
# Your existing script will now find REAL scores!
python src/parse_docking.py
```

**Check the results:**
```bash
# View docking results
cat data/docking_results.csv

# Should now show real scores like:
# GRK6_variant_0001,-7.2
# GRK6_variant_0002,-6.8
# etc. (instead of 0.0)
```

---

## Step 8: Re-run Scoring with Real Data

```bash
# Now scoring will use real docking scores!
python src/scoring.py

# Check updated scores
cat data/scored_variants.csv

# Select top candidates
python src/select_for_synthesis.py --top 3
```

---

## 🎉 Success Checklist

- [ ] Installed AutoDock Vina
- [ ] Installed OpenBabel
- [ ] Generated 3D structures for all 6 variants (saved as `ligand.pdb`)
- [ ] Converted receptor to PDBQT
- [ ] Converted all peptides to PDBQT
- [ ] Created docking config file
- [ ] Ran docking (have `log.txt` files)
- [ ] Parsed results (scores are NOT 0.0 anymore!)
- [ ] Re-scored variants with real data

---

## 🐛 Troubleshooting

### "Vina not found"
- Make sure it's installed: `conda install -c conda-forge autodock-vina`
- Check PATH: `which vina` or `vina --version`

### "OpenBabel not found"
- Install: `conda install -c conda-forge openbabel`
- Or: `pip install openbabel-wheel`

### "No PDB files found"
- You need to generate 3D structures first (Step 3)
- Use ColabFold or PEP-FOLD3

### "Docking failed"
- Check that PDBQT files exist
- Verify config file path is correct
- Make sure receptor PDBQT is valid

### "All scores still 0.0"
- Check that `log.txt` files exist in docking directories
- Verify Vina actually ran (check for `docked.pdbqt` files)
- Look at log files to see if there were errors

---

## 📊 Expected Results

**Before (placeholders):**
```
variant_id,docking_score
GRK6_variant_0001,0.0
GRK6_variant_0002,0.0
...
```

**After (real scores):**
```
variant_id,docking_score
GRK6_variant_0001,-7.2
GRK6_variant_0002,-6.8
GRK6_variant_0003,-8.1
GRK6_variant_0004,-7.9
GRK6_variant_0005,-6.5
GRK6_variant_0006,-6.3
```

**Note:** Scores are typically negative (lower = better binding). Values between -5 and -12 kcal/mol are common for peptides.

---

## 🚀 Quick Start (Test with One Variant First)

Want to test the workflow with just one variant?

1. Generate structure for `GRK6_variant_0001` using ColabFold
2. Save as `data/docking/GRK6_variant_0001/ligand.pdb`
3. Convert: `obabel data/docking/GRK6_variant_0001/ligand.pdb -O data/docking/GRK6_variant_0001/ligand.pdbqt -xr`
4. Convert receptor: `obabel data/P43250_receptor_clean.pdb -O data/P43250_receptor_clean.pdbqt -xr`
5. Run single docking:
   ```bash
   vina --receptor data/P43250_receptor_clean.pdbqt \
        --ligand data/docking/GRK6_variant_0001/ligand.pdbqt \
        --center_x 0 --center_y 0 --center_z 0 \
        --size_x 20 --size_y 20 --size_z 20 \
        --out data/docking/GRK6_variant_0001/docked.pdbqt \
        --log data/docking/GRK6_variant_0001/log.txt
   ```
6. Check log: `cat data/docking/GRK6_variant_0001/log.txt`
7. Parse: `python src/parse_docking.py`
8. Verify: `cat data/docking_results.csv` (should show real score for variant 0001)

Once this works, repeat for all variants!

---

## 💡 Pro Tips

1. **Start with one variant** to test the workflow
2. **Use ColabFold** - it's free and works well for peptides
3. **Binding site coordinates** - if unknown, start with (0,0,0) and large box (30×30×30)
4. **Docking time** - each variant takes 1-5 minutes depending on exhaustiveness
5. **Check log files** - they contain useful information about the docking run

Good luck! 🎯

