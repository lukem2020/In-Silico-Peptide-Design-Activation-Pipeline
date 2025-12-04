#!/bin/bash
# AutoDock Vina docking script
# Runs docking for all peptide variants against the receptor

# Configuration
CONFIG_FILE="data/docking_config.txt"
RECEPTOR="data/P43250_receptor_clean.pdbqt"
DOCKING_ROOT="data/docking"

# Check if Vina is installed
if ! command -v vina &> /dev/null; then
    echo "Error: AutoDock Vina not found!"
    echo "Install with: conda install -c conda-forge autodock-vina"
    exit 1
fi

# Check if receptor exists
if [ ! -f "$RECEPTOR" ]; then
    echo "Error: Receptor PDBQT not found: $RECEPTOR"
    echo "Run convert_to_pdbqt.py first to convert receptor."
    exit 1
fi

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Warning: Config file not found: $CONFIG_FILE"
    echo "Creating default config..."
    cat > "$CONFIG_FILE" << EOF
receptor = $RECEPTOR
center_x = 0.0
center_y = 0.0
center_z = 0.0
size_x = 20.0
size_y = 20.0
size_z = 20.0
exhaustiveness = 8
num_modes = 10
EOF
    echo "Default config created. Update center_x/y/z with actual binding site coordinates!"
fi

# Run docking for each variant
echo "Starting docking for all variants..."
echo "=================================="

for variant_dir in "$DOCKING_ROOT"/GRK6_variant_*/; do
    if [ ! -d "$variant_dir" ]; then
        continue
    fi
    
    variant_id=$(basename "$variant_dir")
    ligand_pdbqt="$variant_dir/ligand.pdbqt"
    output_pdbqt="$variant_dir/docked.pdbqt"
    log_file="$variant_dir/log.txt"
    
    if [ ! -f "$ligand_pdbqt" ]; then
        echo "Warning: $ligand_pdbqt not found, skipping $variant_id"
        continue
    fi
    
    echo "Docking $variant_id..."
    vina \
        --receptor "$RECEPTOR" \
        --ligand "$ligand_pdbqt" \
        --config "$CONFIG_FILE" \
        --out "$output_pdbqt" \
        --log "$log_file"
    
    if [ $? -eq 0 ]; then
        echo "✓ $variant_id complete"
    else
        echo "✗ $variant_id failed"
    fi
    echo ""
done

echo "=================================="
echo "Docking complete!"
echo "Run parse_docking.py to extract scores."

