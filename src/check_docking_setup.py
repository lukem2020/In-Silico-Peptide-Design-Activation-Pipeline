#!/usr/bin/env python3
"""
Check if everything is ready for docking.

This script verifies:
1. Required software is installed (Vina, OpenBabel)
2. Receptor structure exists and is in correct format
3. Peptide structures exist (PDB files)
4. Structures are converted to PDBQT format
5. Docking config file exists
"""

import os
import subprocess
import sys
from pathlib import Path

from fetch_data import DATA_DIR

# Colors for terminal output (works on most systems)
# Use ASCII-safe characters for Windows compatibility
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
CHECK = 'OK'
CROSS = 'X'
WARN = '!'

def check_command(cmd, name):
    """Check if a command is available."""
    try:
        result = subprocess.run(
            [cmd, "--version"] if cmd != "vina" else [cmd, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 or cmd in result.stdout or cmd in result.stderr:
            print(f"{GREEN}[OK]{RESET} {name} is installed")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print(f"{RED}[X]{RESET} {name} is NOT installed")
    print(f"   Install with: conda install -c conda-forge {cmd}")
    return False


def check_file(path, name, required=True):
    """Check if a file exists."""
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"{GREEN}[OK]{RESET} {name} exists ({size:,} bytes)")
        return True
    else:
        if required:
            print(f"{RED}[X]{RESET} {name} NOT found: {path}")
        else:
            print(f"{YELLOW}[!]{RESET} {name} not found (optional): {path}")
        return False


def main():
    """Check docking setup."""
    print("=" * 70)
    print("DOCKING SETUP CHECKER")
    print("=" * 70)
    print()
    
    all_ok = True
    
    # Check software
    print("1. SOFTWARE INSTALLATION")
    print("-" * 70)
    vina_ok = check_command("vina", "AutoDock Vina")
    obabel_ok = check_command("obabel", "OpenBabel")
    print()
    
    # Check receptor
    print("2. RECEPTOR STRUCTURE")
    print("-" * 70)
    receptor_pdb = os.path.join(DATA_DIR, "P43250_receptor_clean.pdb")
    receptor_pdbqt = os.path.join(DATA_DIR, "P43250_receptor_clean.pdbqt")
    
    receptor_pdb_ok = check_file(receptor_pdb, "Receptor PDB")
    receptor_pdbqt_ok = check_file(receptor_pdbqt, "Receptor PDBQT", required=False)
    print()
    
    # Check peptide structures
    print("3. PEPTIDE STRUCTURES")
    print("-" * 70)
    docking_root = os.path.join(DATA_DIR, "docking")
    
    if not os.path.exists(docking_root):
        print(f"{RED}✗{RESET} Docking directory not found: {docking_root}")
        print("   Run: python src/docking_prep.py")
        all_ok = False
    else:
        variant_dirs = sorted(Path(docking_root).glob("GRK6_variant_*"))
        if not variant_dirs:
            print(f"{RED}✗{RESET} No variant directories found")
            print("   Run: python src/docking_prep.py")
            all_ok = False
        else:
            pdb_count = 0
            pdbqt_count = 0
            
            for variant_dir in variant_dirs:
                variant_id = variant_dir.name
                ligand_pdb = variant_dir / "ligand.pdb"
                ligand_pdbqt = variant_dir / "ligand.pdbqt"
                
                if ligand_pdb.exists():
                    pdb_count += 1
                if ligand_pdbqt.exists():
                    pdbqt_count += 1
            
            total = len(variant_dirs)
            print(f"   Found {total} variant directories")
            print(f"   {GREEN}[OK]{RESET} PDB structures: {pdb_count}/{total}")
            print(f"   {GREEN if pdbqt_count == total else YELLOW}[{'OK' if pdbqt_count == total else '!'}]{RESET} PDBQT structures: {pdbqt_count}/{total}")
            
            if pdb_count == 0:
                print(f"\n   {RED}[!]{RESET} No PDB files found!")
                print("   You need to generate 3D structures first.")
                print("   See: GET_REAL_DOCKING_SCORES.md - Step 3")
                all_ok = False
            elif pdbqt_count < total:
                print(f"\n   {YELLOW}[!]{RESET} Some PDBQT files missing!")
                print("   Run: python src/convert_to_pdbqt.py")
                all_ok = False
    print()
    
    # Check config
    print("4. DOCKING CONFIGURATION")
    print("-" * 70)
    config_file = os.path.join(DATA_DIR, "docking_config.txt")
    config_ok = check_file(config_file, "Docking config", required=False)
    if not config_ok:
        print("   Create config file or use command-line arguments")
    print()
    
    # Check existing results
    print("5. EXISTING DOCKING RESULTS")
    print("-" * 70)
    results_csv = os.path.join(DATA_DIR, "docking_results.csv")
    if os.path.exists(results_csv):
        # Check if scores are real or placeholders
        with open(results_csv) as f:
            lines = f.readlines()[1:]  # Skip header
            real_scores = sum(1 for line in lines if float(line.split(',')[1]) != 0.0)
            total_scores = len(lines)
        
        if real_scores > 0:
            print(f"   {GREEN}[OK]{RESET} Found {real_scores} real docking scores!")
        else:
            print(f"   {YELLOW}[!]{RESET} All scores are placeholders (0.0)")
            print("   Run docking to get real scores")
    else:
        print(f"   {YELLOW}[!]{RESET} No docking results file yet")
    print()
    
    # Summary
    print("=" * 70)
    if all_ok and vina_ok and obabel_ok and receptor_pdb_ok:
        print(f"{GREEN}[OK] READY FOR DOCKING!{RESET}")
        print()
        print("Next steps:")
        if not receptor_pdbqt_ok:
            print("  1. Convert receptor: python src/convert_to_pdbqt.py")
        if pdbqt_count < total:
            print("  2. Convert peptides: python src/convert_to_pdbqt.py")
        if not config_ok:
            print("  3. Create config file (or use command-line args)")
        print("  4. Run docking: bash src/run_docking.sh")
    else:
        print(f"{RED}[X] NOT READY YET{RESET}")
        print()
        print("Missing requirements:")
        if not vina_ok:
            print("  - Install AutoDock Vina")
        if not obabel_ok:
            print("  - Install OpenBabel")
        if not receptor_pdb_ok:
            print("  - Run: python src/prepare_structures.py")
        if pdb_count == 0:
            print("  - Generate peptide 3D structures (see GET_REAL_DOCKING_SCORES.md)")
    print("=" * 70)
    
    return all_ok and vina_ok and obabel_ok and receptor_pdb_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

