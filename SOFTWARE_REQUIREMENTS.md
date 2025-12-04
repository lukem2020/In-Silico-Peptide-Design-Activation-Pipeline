# Software Requirements for Visualization and Binding Simulation

This document outlines the software tools needed to **visualize peptide variants** and **simulate binding interactions** with your target protein. Currently, the pipeline uses placeholder docking scores; these tools would enable real molecular modeling.

---

## 🎨 **1. Visualization Software**

### **Free/Open-Source Options:**

#### **PyMOL** (Recommended for beginners)
- **What it does**: High-quality 3D visualization of protein structures
- **Use cases**: 
  - View receptor structure and binding site
  - Overlay peptide variants
  - Create publication-quality figures
- **Installation**: `conda install -c conda-forge pymol-open-source` or download from [pymol.org](https://pymol.org)
- **Integration**: Can load PDB files directly from `data/P43250_receptor_clean.pdb`

#### **ChimeraX** (Most powerful free option)
- **What it does**: Advanced visualization with built-in analysis tools
- **Use cases**:
  - View structures
  - Analyze binding sites
  - Measure distances/angles
  - Generate movies/animations
- **Installation**: Download from [www.rbvi.ucsf.edu/chimerax](https://www.rbvi.ucsf.edu/chimerax)
- **Integration**: Excellent for analyzing docking poses

#### **VMD** (Visual Molecular Dynamics)
- **What it does**: Visualization and analysis, especially for MD trajectories
- **Use cases**: Viewing MD simulations, analyzing dynamics
- **Installation**: Download from [www.ks.uiuc.edu/Research/vmd](https://www.ks.uiuc.edu/Research/vmd)

#### **Jupyter Notebooks + NGLview**
- **What it does**: Interactive 3D visualization in web browsers
- **Use cases**: Quick inspection, sharing visualizations
- **Installation**: `pip install nglview jupyter`
- **Integration**: Can be integrated into analysis notebooks

### **Commercial Options:**

- **Maestro** (Schrödinger) - Industry standard, expensive
- **Discovery Studio** (Dassault Systèmes) - Comprehensive suite
- **MOE** (Chemical Computing Group) - Popular in pharma

---

## 🔬 **2. Molecular Docking Software** (Binding Simulation)

### **Free/Open-Source:**

#### **AutoDock Vina** (Most Popular - Recommended)
- **What it does**: Predicts how peptides bind to receptors
- **Output**: Binding poses and scores (kcal/mol)
- **Installation**: 
  ```bash
  conda install -c conda-forge autodock-vina
  # OR download from: https://vina.scripps.edu/downloads/
  ```
- **Integration**: Your `parse_docking.py` already parses Vina logs!
- **Usage**: See `src/run_docking.sh` for example commands
- **Pros**: Fast, widely used, good for peptides
- **Cons**: Less accurate for very flexible peptides

#### **GNINA** (Vina-based, improved)
- **What it does**: Enhanced Vina with deep learning scoring
- **Installation**: `conda install -c conda-forge gnina`
- **Pros**: More accurate than Vina
- **Cons**: Requires GPU for best performance

#### **HADDOCK** (For protein-protein docking)
- **What it does**: Specialized for protein-protein/peptide interactions
- **Installation**: Web server at [haddock.science.uu.nl](https://haddock.science.uu.nl) or local install
- **Pros**: Excellent for flexible peptides
- **Cons**: Slower, requires more setup

#### **SwissDock** (Web-based)
- **What it does**: Easy-to-use web interface for docking
- **URL**: [swissdock.ch](http://www.swissdock.ch)
- **Pros**: No installation needed
- **Cons**: Limited customization, slower for many variants

### **Commercial Options:**

- **Glide** (Schrödinger) - Industry standard, very accurate
- **GOLD** (CCDC) - Popular in drug discovery
- **MOE Dock** (Chemical Computing Group)

---

## 🧪 **3. Structure Preparation Tools**

### **For Converting Sequences → 3D Structures:**

#### **AlphaFold2** (For peptide structure prediction)
- **What it does**: Predicts 3D structure from amino acid sequence
- **Installation**: 
  ```bash
  conda install -c conda-forge openfold
  # OR use ColabFold: https://colab.research.google.com/github/sokrypton/ColabFold
  ```
- **Use case**: Generate 3D structures for your peptide variants
- **Integration**: Would feed into docking_prep.py

#### **MODELLER** (For homology modeling)
- **What it does**: Builds 3D models based on similar structures
- **Installation**: `pip install modeller`
- **Use case**: If you have a template structure similar to your peptide

#### **Avogadro** (For small molecule/peptide building)
- **What it does**: Build and optimize small peptide structures
- **Installation**: `conda install -c conda-forge avogadro`

### **For Structure Cleaning/Preparation:**

#### **PDB2PQR** (Already referenced in your code!)
- **What it does**: Adds hydrogens, assigns charges at specific pH
- **Installation**: `pip install pdb2pqr`
- **Integration**: Your `prepare_structures.py` already tries to use it!
- **Use case**: Prepares receptor for docking

#### **OpenBabel** (Format conversion)
- **What it does**: Converts between PDB, MOL2, PDBQT formats
- **Installation**: `conda install -c conda-forge openbabel`
- **Use case**: Converting structures for different docking tools

---

## ⚡ **4. Molecular Dynamics Software** (For Refinement)

### **Free/Open-Source:**

#### **GROMACS** (Most Popular)
- **What it does**: Runs MD simulations to refine docking poses
- **Installation**: `conda install -c conda-forge gromacs`
- **Use case**: Refining top docking poses (Step 7: Refinement)
- **Pros**: Fast, well-documented
- **Cons**: Steep learning curve

#### **AMBER** (Academic license available)
- **What it does**: MD simulations with excellent force fields
- **Installation**: Download from [ambermd.org](https://ambermd.org)
- **Use case**: High-quality refinement
- **Pros**: Excellent for proteins/peptides
- **Cons**: Complex setup

#### **NAMD** (Free for academic use)
- **What it does**: MD simulations, good for large systems
- **Installation**: Download from [www.ks.uiuc.edu/Research/namd](https://www.ks.uiuc.edu/Research/namd)
- **Use case**: Large receptor-peptide complexes

### **Commercial:**

- **Desmond** (Schrödinger) - User-friendly, integrated workflow
- **CHARMM** - Powerful but complex

---

## 📊 **5. Analysis & Scoring Tools**

#### **PLIP** (Protein-Ligand Interaction Profiler)
- **What it does**: Analyzes binding interactions (H-bonds, contacts)
- **Installation**: `pip install plip`
- **Use case**: Post-docking analysis to understand why variants bind

#### **MDTraj** (Python library)
- **What it does**: Analyzes MD trajectories
- **Installation**: `pip install mdtraj`
- **Use case**: Analyzing refinement simulations

---

## 🔧 **Recommended Setup for Your Pipeline**

### **Minimal Setup** (Get started quickly):
1. **PyMOL** - Visualization
2. **AutoDock Vina** - Docking
3. **PDB2PQR** - Structure preparation (already in your code!)

### **Complete Setup** (Production-ready):
1. **ChimeraX** - Advanced visualization
2. **AutoDock Vina** or **GNINA** - Docking
3. **AlphaFold2** or **ColabFold** - Peptide structure prediction
4. **GROMACS** - MD refinement
5. **PLIP** - Interaction analysis

---

## 🚀 **How to Integrate with Your Pipeline**

### **Step 1: Generate 3D Structures for Peptides**
Currently, your pipeline has peptide **sequences** but not 3D structures. You would need to:

```python
# Add to docking_prep.py or create new script:
# 1. Use AlphaFold2/ColabFold to predict 3D structure for each variant
# 2. Save as PDB files
# 3. Convert to PDBQT format for Vina
```

### **Step 2: Run Real Docking**
Replace placeholder scores with actual Vina runs:

```bash
# Modify src/run_docking.sh:
vina --receptor data/P43250_receptor_clean.pdbqt \
     --ligand data/docking/GRK6_variant_0001/ligand.pdbqt \
     --config docking_config.txt \
     --out data/docking/GRK6_variant_0001/docked.pdbqt \
     --log data/docking/GRK6_variant_0001/log.txt
```

### **Step 3: Visualize Results**
```python
# In PyMOL or ChimeraX:
# Load receptor: data/P43250_receptor_clean.pdb
# Load best pose: data/docking/GRK6_variant_0001/docked.pdbqt
# Analyze binding site interactions
```

---

## 📝 **Example Workflow Integration**

```python
# Pseudo-code for integrating real docking:

1. design_library.py → generates sequences ✓ (already done)

2. NEW: predict_structures.py
   - For each variant in library.fasta:
     - Run AlphaFold2/ColabFold to get 3D structure
     - Save as PDB file

3. docking_prep.py → prepares directories ✓ (already done)
   - Also converts PDB → PDBQT format

4. run_docking.sh → runs Vina for each variant
   - Currently placeholder, replace with real Vina calls

5. parse_docking.py → extracts scores ✓ (already done)

6. scoring.py → ranks variants ✓ (already done)

7. visualize_results.py (NEW)
   - Loads receptor + best poses
   - Creates figures showing binding interactions
```

---

## 💡 **Quick Start Recommendations**

**For demonstration purposes:**
- Use **SwissDock** web server to dock 1-2 variants manually
- Use **PyMOL** to visualize the results
- This shows the concept without heavy installation

**For production use:**
- Install **AutoDock Vina** + **PyMOL**
- Integrate into your pipeline
- Add structure prediction step (AlphaFold2/ColabFold)

---

## 📚 **Learning Resources**

- **AutoDock Vina Tutorial**: [vina.scripps.edu/manual](https://vina.scripps.edu/manual)
- **PyMOL Tutorial**: [pymol.org/tutorials](https://pymol.org/tutorials)
- **ChimeraX Tutorial**: [www.rbvi.ucsf.edu/chimerax/docs](https://www.rbvi.ucsf.edu/chimerax/docs)
- **GROMACS Tutorial**: [www.mdtutorials.com/gmx](http://www.mdtutorials.com/gmx)

---

## ⚠️ **Important Notes**

1. **Computational Requirements**: 
   - Docking: Moderate (can run on laptop)
   - MD simulations: High (benefits from GPU/cluster)
   - Structure prediction: High (AlphaFold2 needs GPU)

2. **License Considerations**:
   - Most academic tools are free for research
   - Commercial tools require licenses (often expensive)
   - Check licensing before commercial use

3. **Your Current Pipeline**:
   - Already structured to accept real docking results!
   - Just need to replace placeholder scores with actual Vina output
   - `parse_docking.py` already knows how to read Vina logs

