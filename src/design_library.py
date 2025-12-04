import os
import itertools
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple


"""
Sequence design utilities for building a peptide / protein variant library.

High-level responsibilities:
1. Mutate specific positions in a parent sequence.
2. Generate combinatorial variants from mutation schemes.
3. Compute simple sequence properties (charge, hydrophobicity, length).
4. Filter sequences based on those properties.
5. Write the resulting library to FASTA (e.g., `library.fasta`).

This module is intentionally self-contained and does not depend on external
packages so it can be used early in the pipeline.
"""


# Kyte–Doolittle hydrophobicity scale
KYTE_DOOLITTLE: Dict[str, float] = {
    "A": 1.8,
    "R": -4.5,
    "N": -3.5,
    "D": -3.5,
    "C": 2.5,
    "Q": -3.5,
    "E": -3.5,
    "G": -0.4,
    "H": -3.2,
    "I": 4.5,
    "L": 3.8,
    "K": -3.9,
    "M": 1.9,
    "F": 2.8,
    "P": -1.6,
    "S": -0.8,
    "T": -0.7,
    "W": -0.9,
    "Y": -1.3,
    "V": 4.2,
}


@dataclass
class SequenceProperties:
    """Simple physico-chemical properties used for filtering."""

    length: int
    net_charge: float
    avg_hydrophobicity: float


def mutate_positions(
    parent_seq: str,
    mutations: Dict[int, str],
) -> str:
    """
    Return a new sequence where specific (1-based) positions are mutated.

    Parameters
    ----------
    parent_seq:
        Original amino-acid sequence.
    mutations:
        Dictionary mapping 1-based positions -> single-letter residue code.

    Notes
    -----
    - Positions are 1-based to align with typical biochemical numbering.
    - No validation is done on the amino-acid alphabet.
    """
    seq_list = list(parent_seq)
    for pos_1b, aa in mutations.items():
        idx = pos_1b - 1
        if idx < 0 or idx >= len(seq_list):
            raise ValueError(f"Mutation position {pos_1b} out of range for length {len(seq_list)}")
        seq_list[idx] = aa
    return "".join(seq_list)


def generate_combinatorial_variants(
    parent_seq: str,
    mutable_positions: Sequence[int],
    residue_choices: Sequence[Sequence[str]],
) -> Iterable[Tuple[str, Dict[int, str]]]:
    """
    Generate all combinatorial variants for the specified positions.

    Parameters
    ----------
    parent_seq:
        The starting sequence.
    mutable_positions:
        Sequence of 1-based positions to mutate.
    residue_choices:
        A sequence of residue lists, one per position in `mutable_positions`.
        Example: positions [10, 15], residue_choices [["A", "D"], ["K", "R"]]
        yields 4 variants.

    Yields
    ------
    (variant_sequence, mutation_dict)
        - variant_sequence: the mutated sequence string.
        - mutation_dict: {position_1b: residue} for that variant.
    """
    if len(mutable_positions) != len(residue_choices):
        raise ValueError("mutable_positions and residue_choices must have the same length")

    for combo in itertools.product(*residue_choices):
        mut_dict = dict(zip(mutable_positions, combo))
        yield mutate_positions(parent_seq, mut_dict), mut_dict


def compute_net_charge(seq: str) -> float:
    """
    Very simple estimate of net charge at neutral pH.

    Assumptions
    -----------
    - Side chains:
        K, R => +1
        H     => +0.1 (often partially protonated)
        D, E  => -1
    - N-terminus => +1
    - C-terminus => -1
    """
    charge = 0.0

    if not seq:
        return 0.0

    # Terminal charges
    charge += 1.0  # N-terminus
    charge -= 1.0  # C-terminus

    for aa in seq:
        if aa == "K" or aa == "R":
            charge += 1.0
        elif aa == "H":
            charge += 0.1
        elif aa == "D" or aa == "E":
            charge -= 1.0

    return charge


def compute_avg_hydrophobicity(seq: str) -> float:
    """
    Compute average Kyte–Doolittle hydrophobicity.
    Unknown residues (e.g., X) are ignored in the average.
    """
    if not seq:
        return 0.0

    total = 0.0
    count = 0
    for aa in seq:
        if aa in KYTE_DOOLITTLE:
            total += KYTE_DOOLITTLE[aa]
            count += 1
    if count == 0:
        return 0.0
    return total / count


def compute_properties(seq: str) -> SequenceProperties:
    """Compute length, net charge, and average hydrophobicity for a sequence."""
    return SequenceProperties(
        length=len(seq),
        net_charge=compute_net_charge(seq),
        avg_hydrophobicity=compute_avg_hydrophobicity(seq),
    )


def filter_sequences(
    sequences: Iterable[Tuple[str, Dict[int, str]]],
    min_length: int = 0,
    max_length: int = 10_000,
    min_hydro: float = -10.0,
    max_hydro: float = 10.0,
    max_abs_charge: float = 999.0,
) -> List[Tuple[str, Dict[int, str], SequenceProperties]]:
    """
    Filter variants by length, hydrophobicity range, and absolute net charge.

    Parameters
    ----------
    sequences:
        Iterable of (sequence, mutation_dict) tuples.
    min_length, max_length:
        Inclusive length bounds.
    min_hydro, max_hydro:
        Inclusive bounds on average hydrophobicity.
    max_abs_charge:
        Maximum allowed |net_charge|.

    Returns
    -------
    List of (sequence, mutation_dict, properties) for variants passing filters.
    """
    passed: List[Tuple[str, Dict[int, str], SequenceProperties]] = []
    for seq, mut_dict in sequences:
        props = compute_properties(seq)
        if not (min_length <= props.length <= max_length):
            continue
        if not (min_hydro <= props.avg_hydrophobicity <= max_hydro):
            continue
        if abs(props.net_charge) > max_abs_charge:
            continue
        passed.append((seq, mut_dict, props))
    return passed


def write_fasta(
    records: Sequence[Tuple[str, Dict[int, str], SequenceProperties]],
    out_path: str,
    prefix: str = " variant",
) -> None:
    """
    Write a set of sequences to a FASTA file.

    Each header will encode mutation info and simple properties for traceability.

    Header format (example)
    -----------------------
    >GRK6_variant_0001|mut=10A;15K|len=576;charge=3.0;KD=-0.5

    Parameters
    ----------
    records:
        List of (sequence, mutation_dict, properties).
    out_path:
        Output FASTA file path.
    prefix:
        Base name used in the FASTA ID, appended with zero-padded index.
    """
    lines: List[str] = []
    for idx, (seq, mut_dict, props) in enumerate(records, start=1):
        mut_str = ",".join(f"{pos}{aa}" for pos, aa in sorted(mut_dict.items()))
        header_id = f"{prefix.strip().replace(' ', '_')}_{idx:04d}"
        header_fields = [
            f"mut={mut_str or 'none'}",
            f"len={props.length}",
            f"charge={props.net_charge:.2f}",
            f"KD={props.avg_hydrophobicity:.3f}",
        ]
        header = f">{header_id}|{'|'.join(header_fields)}"
        lines.append(header)
        lines.append(seq)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def load_first_fasta_sequence(path: str) -> str:
    """
    Load the first sequence from a FASTA file.
    """
    seq_lines: List[str] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if seq_lines:
                    # already collected first sequence
                    break
                continue
            seq_lines.append(line)
    return "".join(seq_lines)


def design_example_library() -> None:
    """
    Example entry point to generate a small library from the GRK6 FASTA.

    This can be used as a starting point and wired into a larger pipeline.
    It intentionally uses conservative mutation and filter settings.
    """
    # Import from fetch_data lazily to avoid circular imports at module load.
    from fetch_data import DATA_DIR, FASTA_PATH

    parent_seq = load_first_fasta_sequence(FASTA_PATH)

    # Example: mutate two positions with limited residue sets.
    # Positions are 1-based indexes on the GRK6 sequence.
    mutable_positions = [50, 100]
    residue_choices = [
        ["A", "D", "K"],  # position 50
        ["L", "F"],       # position 100
    ]

    variants = generate_combinatorial_variants(
        parent_seq=parent_seq,
        mutable_positions=mutable_positions,
        residue_choices=residue_choices,
    )

    filtered = filter_sequences(
        variants,
        min_length=len(parent_seq),
        max_length=len(parent_seq),
        min_hydro=-2.0,
        max_hydro=2.0,
        max_abs_charge=20.0,
    )

    out_fasta = os.path.join(DATA_DIR, "library.fasta")
    write_fasta(filtered, out_fasta, prefix="GRK6_variant")
    print(f"Wrote {len(filtered)} variants to {out_fasta}")


if __name__ == "__main__":
    # Running this module directly will generate an example library.
    design_example_library()


