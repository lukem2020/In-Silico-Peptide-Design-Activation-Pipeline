import os
import requests
import logging
import json

UNIPROT_ID = "P43250"
# Go up one level from src/ to root, then into data/
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
FASTA_PATH = os.path.join(DATA_DIR, "%s.fasta" % UNIPROT_ID)
METADATA_PATH = os.path.join(DATA_DIR, "%s_metadata.json" % UNIPROT_ID)
STRUCTURE_PATH = os.path.join(DATA_DIR, "%s_structure.pdb" % UNIPROT_ID)

logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

def fetch_uniprot_fasta(uniprot_id, out_path):
    """Fetch protein FASTA sequence from UniProt."""
    url = "https://rest.uniprot.org/uniprotkb/%s.fasta" % uniprot_id
    try:
        response = requests.get(url)
    except Exception as e:
        logging.error("Error fetching FASTA for %s: %s", uniprot_id, str(e))
        return False

    if response.status_code == 200:
        try:
            with open(out_path, "w") as f:
                f.write(response.text)
            print("FASTA for %s saved to %s" % (uniprot_id, out_path))
            return True
        except Exception as e:
            logging.error("Error writing FASTA to file %s: %s", out_path, str(e))
            return False
    else:
        logging.error("Failed to fetch FASTA for %s. Status code: %d", uniprot_id, response.status_code)
        print("Failed to fetch FASTA for %s. Status code: %d" % (uniprot_id, response.status_code))
        return False

def fetch_uniprot_metadata(uniprot_id, out_path):
    """Fetch protein metadata from UniProt in JSON format."""
    url = "https://rest.uniprot.org/uniprotkb/%s.json" % uniprot_id
    try:
        response = requests.get(url)
    except Exception as e:
        logging.error("Error fetching metadata for %s: %s", uniprot_id, str(e))
        return False

    if response.status_code == 200:
        try:
            data = response.json()
            with open(out_path, "w") as f:
                json.dump(data, f, indent=2)
            print("Metadata for %s saved to %s" % (uniprot_id, out_path))
            return True
        except Exception as e:
            logging.error("Error writing metadata to file %s: %s", out_path, str(e))
            return False
    else:
        logging.error("Failed to fetch metadata for %s. Status code: %d", uniprot_id, response.status_code)
        print("Failed to fetch metadata for %s. Status code: %d" % (uniprot_id, response.status_code))
        return False

def fetch_structure(uniprot_id, out_path):
    """Fetch PDB structure from AlphaFold DB (preferred) or RCSB PDB."""
    # Try AlphaFold first (most reliable for UniProt IDs)
    alphafold_url = "https://alphafold.ebi.ac.uk/api/prediction/%s" % uniprot_id
    try:
        response = requests.get(alphafold_url)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                # Get the first (and usually only) prediction
                pdb_url = data[0].get("pdbUrl")
                if pdb_url:
                    pdb_response = requests.get(pdb_url)
                    if pdb_response.status_code == 200:
                        with open(out_path, "w") as f:
                            f.write(pdb_response.text)
                        print("AlphaFold structure for %s saved to %s" % (uniprot_id, out_path))
                        return True
                    else:
                        logging.error("Failed to download PDB from AlphaFold. Status code: %d", pdb_response.status_code)
    except Exception as e:
        logging.error("Error fetching AlphaFold structure for %s: %s", uniprot_id, str(e))

    # Fallback: Try to get PDB ID from UniProt metadata and fetch from RCSB
    try:
        metadata_url = "https://rest.uniprot.org/uniprotkb/%s.json" % uniprot_id
        metadata_response = requests.get(metadata_url)
        if metadata_response.status_code == 200:
            metadata = metadata_response.json()
            # Look for PDB cross-references
            pdb_ids = []
            if "uniProtKBCrossReferences" in metadata:
                for ref in metadata["uniProtKBCrossReferences"]:
                    if ref.get("database") == "PDB":
                        pdb_ids.append(ref.get("id"))
            
            if pdb_ids:
                # Use the first PDB ID
                pdb_id = pdb_ids[0]
                rcsb_url = "https://files.rcsb.org/download/%s.pdb" % pdb_id
                pdb_response = requests.get(rcsb_url)
                if pdb_response.status_code == 200:
                    with open(out_path, "w") as f:
                        f.write(pdb_response.text)
                    print("PDB structure %s for %s saved to %s" % (pdb_id, uniprot_id, out_path))
                    return True
    except Exception as e:
        logging.error("Error fetching PDB structure for %s: %s", uniprot_id, str(e))

    print("Warning: Could not fetch structure for %s from AlphaFold or RCSB PDB" % uniprot_id)
    return False

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print("Fetching data for UniProt ID: %s" % UNIPROT_ID)
    print("-" * 50)
    
    # Fetch FASTA sequence
    fetch_uniprot_fasta(UNIPROT_ID, FASTA_PATH)
    
    # Fetch metadata
    fetch_uniprot_metadata(UNIPROT_ID, METADATA_PATH)
    
    # Fetch structure (AlphaFold or PDB)
    fetch_structure(UNIPROT_ID, STRUCTURE_PATH)
    
    print("-" * 50)
    print("Data fetching complete!")
