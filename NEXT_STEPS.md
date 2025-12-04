# Immediate Next Steps to Complete the Pipeline

## Current Status ✅

**What's Working:**
- ✅ Data fetching (sequences, structures)
- ✅ Structure preparation (receptor cleaning)
- ✅ Library design (variant generation)
- ✅ Docking preparation (directory structure)
- ✅ Docking parsing (can read Vina logs)
- ✅ Scoring and ranking
- ✅ Selection for synthesis

**What's Missing:**
- ❌ **3D structures for peptide variants** (only have sequences)
- ❌ **Receptor in PDBQT format** (needed for Vina)
- ❌ **Peptides in PDBQT format** (needed for Vina)
- ❌ **Docking configuration file** (grid box coordinates)
- ❌ **Actual docking execution** (run_docking.sh is placeholder)

---

## 🎯 Immediate Action Plan

### **Step 1: Install Required Software** (15-30 minutes)

```bash
# Option A: Using conda (recommended)
conda install -c conda-forge autodock-vina
conda install -c conda-forge openbabel
pip install pdb2pqr

# Option B: Manual installation
# Download Vina from: https://vina.scripps.edu/downloads/
# Download OpenBabel from: https://openbabel.org/wiki/Category:Installation
```

**Verify installation:**
```bash
vina --version
obabel -V
pdb2pqr --version
```

---

### **Step 2: Generate 3D Structures for Peptides** (1-2 hours)

**Problem:** Your pipeline currently has peptide **sequences** (FASTA) but docking needs **3D structures** (PDB files).

**Solution Options:**

#### **Option A: Use ColabFold (Easiest - No GPU needed)**
1. Go to: https://colab.research.google.com/github/sokrypton/ColabFold
2. For each variant sequence, paste into ColabFold
3. Download the predicted PDB structure
4. Save to: `data/docking/GRK6_variant_XXXX/ligand.pdb`

#### **Option B: Use AlphaFold2 (Local - Requires GPU)**
```bash
# Install AlphaFold2
conda install -c conda-forge openfold

# Predict structure for each variant
# (Would need to write a script to automate this)
```

#### **Option C: Use MODELLER (If you have a template)**
```bash
pip install modeller
# Build homology models based on similar peptide structures
```

**For now (quick demo):** You could manually create simple extended peptide structures or use a web tool like PEP-FOLD3: https://bioserv.rpbs.univ-paris-diderot.fr/services/PEP-FOLD3/

---

### **Step 3: Convert Structures to PDBQT Format** (30 minutes)

**Create a new script: `src/convert_to_pdbqt.py`**

```python
import os
import subprocess
from pathlib import Path

def convert_pdb_to_pdbqt(pdb_path, pdbqt_path):
    """Convert PDB to PDBQT using OpenBabel."""
    cmd = ['obabel', pdb_path, '-O', pdbqt_path, '-xr']
    subprocess.run(cmd, check=True)

# Convert receptor
convert_pdb_to_pdbqt(
    'data/P43250_receptor_clean.pdb',
    'data/P43250_receptor_clean.pdbqt'
)

# Convert each peptide variant
for variant_dir in Path('data/docking').glob('GRK6_variant_*'):
    ligand_pdb = variant_dir / 'ligand.pdb'
    ligand_pdbqt = variant_dir / 'ligand.pdbqt'
    if ligand_pdb.exists():
        convert_pdb_to_pdbqt(str(ligand_pdb), str(ligand_pdbqt))
```

**Or use MGLTools (AutoDock Tools):**
- Download from: http://mgltools.scripps.edu/downloads
- Use `prepare_receptor4.py` and `prepare_ligand4.py`

---

### **Step 4: Create Docking Configuration File** (15 minutes)

**Create: `data/docking_config.txt`**

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
- Use PyMOL/ChimeraX to visualize the receptor
- Identify the binding site location
- Update `center_x`, `center_y`, `center_z` to that location
- Or use a tool like `fpocket` to detect pockets automatically

---

### **Step 5: Implement Real Docking** (30 minutes)

**Update `src/run_docking.sh`:**

```bash
#!/bin/bash
# Real docking with AutoDock Vina

CONFIG_FILE="data/docking_config.txt"
RECEPTOR="data/P43250_receptor_clean.pdbqt"

for variant_dir in data/docking/GRK6_variant_*/; do
    variant_id=$(basename "$variant_dir")
    ligand_pdbqt="$variant_dir/ligand.pdbqt"
    output_pdbqt="$variant_dir/docked.pdbqt"
    log_file="$variant_dir/log.txt"
    
    if [ -f "$ligand_pdbqt" ]; then
        echo "Docking $variant_id..."
        vina \
            --receptor "$RECEPTOR" \
            --ligand "$ligand_pdbqt" \
            --config "$CONFIG_FILE" \
            --out "$output_pdbqt" \
            --log "$log_file"
    else
        echo "Warning: $ligand_pdbqt not found, skipping $variant_id"
    fi
done

echo "Docking complete!"
```

**Or create Python version: `src/run_docking.py`:**

```python
import os
import subprocess
from pathlib import Path

CONFIG_FILE = "data/docking_config.txt"
RECEPTOR = "data/P43250_receptor_clean.pdbqt"
DOCKING_ROOT = "data/docking"

for variant_dir in Path(DOCKING_ROOT).glob("GRK6_variant_*"):
    variant_id = variant_dir.name
    ligand_pdbqt = variant_dir / "ligand.pdbqt"
    output_pdbqt = variant_dir / "docked.pdbqt"
    log_file = variant_dir / "log.txt"
    
    if ligand_pdbqt.exists():
        cmd = [
            "vina",
            "--receptor", RECEPTOR,
            "--ligand", str(ligand_pdbqt),
            "--config", CONFIG_FILE,
            "--out", str(output_pdbqt),
            "--log", str(log_file),
        ]
        subprocess.run(cmd, check=True)
        print(f"Docked {variant_id}")
    else:
        print(f"Warning: {ligand_pdbqt} not found")
```

---

### **Step 6: Run the Complete Pipeline** (5 minutes)

```bash
# 1. Generate peptide structures (manual or automated)
# 2. Convert to PDBQT
python src/convert_to_pdbqt.py

# 3. Run docking
bash src/run_docking.sh
# OR
python src/run_docking.py

# 4. Parse results (will now find real scores!)
python src/parse_docking.py

# 5. Score and rank
python src/scoring.py

# 6. Select top candidates
python src/select_for_synthesis.py --top 3
```

---

## 🚀 Quick Start (Minimal Viable Pipeline)

**If you want to test with just ONE variant first:**

1. **Get 3D structure for one variant:**
   - Use ColabFold or PEP-FOLD3 web server
   - Save as `data/docking/GRK6_variant_0001/ligand.pdb`

2. **Convert to PDBQT:**
   ```bash
   obabel data/docking/GRK6_variant_0001/ligand.pdb \
          -O data/docking/GRK6_variant_0001/ligand.pdbqt -xr
   obabel data/P43250_receptor_clean.pdb \
          -O data/P43250_receptor_clean.pdbqt -xr
   ```

3. **Create simple config:**
   ```bash
   # Use receptor center as binding site (rough estimate)
   # You'll need to adjust coordinates based on actual binding site
   ```

4. **Run docking:**
   ```bash
   vina --receptor data/P43250_receptor_clean.pdbqt \
        --ligand data/docking/GRK6_variant_0001/ligand.pdbqt \
        --center_x 0 --center_y 0 --center_z 0 \
        --size_x 20 --size_y 20 --size_z 20 \
        --out data/docking/GRK6_variant_0001/docked.pdbqt \
        --log data/docking/GRK6_variant_0001/log.txt
   ```

5. **Parse results:**
   ```bash
   python src/parse_docking.py
   # Should now show real binding score instead of 0.0!
   ```

---

## 📋 Checklist

- [ ] Install AutoDock Vina
- [ ] Install OpenBabel (for PDB→PDBQT conversion)
- [ ] Generate 3D structures for peptide variants
- [ ] Convert receptor PDB → PDBQT
- [ ] Convert peptide PDBs → PDBQT
- [ ] Create docking configuration file (with binding site coordinates)
- [ ] Update `run_docking.sh` or create `run_docking.py`
- [ ] Run docking for all variants
- [ ] Verify `parse_docking.py` picks up real scores
- [ ] Re-run scoring and selection with real docking data

---

## 💡 Pro Tips

1. **Start with one variant** to test the workflow before running all 6
2. **Use web servers** (ColabFold, PEP-FOLD3) if you don't have GPU access
3. **Binding site location**: If you don't know it, use a tool like `fpocket` or visualize in PyMOL to find pockets
4. **Docking grid size**: Start with 20×20×20 Å, adjust based on peptide size
5. **Exhaustiveness**: Higher (16-32) = more accurate but slower

---

## 🎯 Expected Outcome

After completing these steps:
- `data/docking/GRK6_variant_XXXX/log.txt` files will contain real binding scores
- `data/docking_results.csv` will have actual kcal/mol values (typically -5 to -12 for good binders)
- `scored_variants.csv` will rank variants based on real docking + sequence properties
- You'll have actual binding poses in `docked.pdbqt` files for visualization

---

## Need Help?

- **Vina documentation**: https://vina.scripps.edu/manual
- **OpenBabel docs**: https://openbabel.org/docs/current/
- **ColabFold**: https://colab.research.google.com/github/sokrypton/ColabFold
- **PEP-FOLD3**: https://bioserv.rpbs.univ-paris-diderot.fr/services/PEP-FOLD3/

