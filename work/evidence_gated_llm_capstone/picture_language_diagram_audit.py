"""Diagram-to-runtime-assurance audit for multimodal medical LLM inputs.

This synthetic audit translates diagrammatic sources into conservative runtime
permissions. The core source is Jaffe and Liu's picture-language program:
artifacts in a language L may simulate a target reality R only through an
explicit simulation map S. The final row adds an Axelrod-style repeated-game
diagram as a consent/adoption noise analogy, using the Veritasium page only as
popular orientation and the primary literature as the scientific anchor.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"


@dataclass(frozen=True)
class DiagramArtifact:
    diagram_id: str
    source_family: str
    page_or_context: str
    diagram_role: str
    diagram_object: str
    mathematical_lesson: str
    medical_runtime_lesson: str
    required_gate: str
    permission: str
    transfer_resets_validation: bool = False
    virtual_state_warning: bool = False
    noise_sensitive_interaction: bool = False


DIAGRAMS: tuple[DiagramArtifact, ...] = (
    DiagramArtifact(
        diagram_id="circle_angle_picture_proof",
        source_family="Jaffe-Liu picture language program",
        page_or_context="PDF page 3",
        diagram_role="proof picture",
        diagram_object="circle-angle relation",
        mathematical_lesson="A compact picture can guide or carry proof only when its formal rules are explicit.",
        medical_runtime_lesson="A wound photo, waveform, or chart screenshot can explain a claim, but it cannot authorize a clinical claim without the rule set that links picture features to clinical state.",
        required_gate="formal rule/provenance gate",
        permission="PROOF_STATUS_OR_PROVENANCE_AUDIT_ONLY",
    ),
    DiagramArtifact(
        diagram_id="feynman_virtual_exchange",
        source_family="Jaffe-Liu picture language program",
        page_or_context="PDF page 4",
        diagram_role="simulation boundary",
        diagram_object="Feynman-style exchange diagram",
        mathematical_lesson="Whether a pictured entity is treated as real or virtual depends on the chosen simulation.",
        medical_runtime_lesson="Latent states, imputed values, reconstructed notes, and generated captions must stay labeled as virtual until validated against the clinical target.",
        required_gate="real-versus-virtual state gate",
        permission="ABSTAIN_PROVENANCE",
        virtual_state_warning=True,
    ),
    DiagramArtifact(
        diagram_id="lattice_duality",
        source_family="Jaffe-Liu picture language program",
        page_or_context="PDF page 6",
        diagram_role="duality picture",
        diagram_object="lattice and dual lattice",
        mathematical_lesson="A visual duality can preserve a relationship while changing the representation.",
        medical_runtime_lesson="Coarse-graining or blurring may preserve some invariants while flipping others, so the runtime monitor must test the boundary after transformation.",
        required_gate="coarse-graining invariant gate",
        permission="STRESS_TEST_BOUNDARY",
        transfer_resets_validation=True,
    ),
    DiagramArtifact(
        diagram_id="fourier_multiplication_convolution",
        source_family="Jaffe-Liu picture language program",
        page_or_context="PDF page 6",
        diagram_role="transform picture",
        diagram_object="string Fourier transform, multiplication, and convolution",
        mathematical_lesson="A rotation or transform can exchange operations while preserving a formal identity.",
        medical_runtime_lesson="Modality transforms such as speech-to-text, image summarization, coding, or privacy blurring need decodability and provenance checks before downstream claims inherit evidence.",
        required_gate="decodability/provenance gate",
        permission="ABSTAIN_PROVENANCE",
        transfer_resets_validation=True,
    ),
    DiagramArtifact(
        diagram_id="max_ghz_quon_rotation",
        source_family="Jaffe-Liu picture language program",
        page_or_context="PDF pages 8-10",
        diagram_role="basis-change picture",
        diagram_object="Max/GHZ/quon rotation",
        mathematical_lesson="A rotated or reused picture can represent a different algebraic object under a different simulation map.",
        medical_runtime_lesson="The same screenshot, plot, or body image can mean different things under different preprocessing, population, device, or clinical-context maps.",
        required_gate="simulation-map identity gate",
        permission="PROOF_STATUS_OR_PROVENANCE_AUDIT_ONLY",
        transfer_resets_validation=True,
    ),
    DiagramArtifact(
        diagram_id="three_dimensional_teleportation",
        source_family="Jaffe-Liu picture language program",
        page_or_context="PDF page 11",
        diagram_role="protocol picture",
        diagram_object="three-dimensional teleportation representation",
        mathematical_lesson="A complex protocol can be inspected pictorially only when each operation has a declared role.",
        medical_runtime_lesson="An agentic multimodal workflow may be auditable as a staged diagram, but every handoff, authority boundary, and output action needs an explicit runtime gate.",
        required_gate="handoff/authority gate",
        permission="WORKFLOW_AUDIT_ONLY",
    ),
    DiagramArtifact(
        diagram_id="simulation_clock",
        source_family="Jaffe-Liu picture language program",
        page_or_context="PDF page 12",
        diagram_role="abstraction-simulation clock",
        diagram_object="R1 -> L1 -> R2 -> L2 -> R3 -> L3 -> R4 progression",
        mathematical_lesson="Repeated movement between reality and language can discover new structures, but each transfer creates a new validation problem.",
        medical_runtime_lesson="A clinical note, caption, image, embedding, summary, and answer are different evidence objects; each transfer resets provenance and validation requirements.",
        required_gate="transfer-reset gate",
        permission="ABSTAIN_PROVENANCE",
        transfer_resets_validation=True,
    ),
    DiagramArtifact(
        diagram_id="iterated_prisoners_dilemma_noise",
        source_family="Veritasium orientation plus Axelrod cooperation literature",
        page_or_context="Veritasium page dated 2024-01-15; Axelrod/Hamilton 1981 and Wu/Axelrod 1995",
        diagram_role="repeated-game interaction diagram",
        diagram_object="Prisoner's Dilemma payoff matrix and repeated trust/noise dynamics",
        mathematical_lesson="Repeated interaction can sustain cooperation, but noisy actions can cause mistaken retaliation unless the strategy distinguishes error from intent.",
        medical_runtime_lesson="Low adoption, missing data, family-consent conflict, or clinician disagreement should be audited for noise, burden, and context before the system treats it as defection or refusal.",
        required_gate="noise/context/adoption gate",
        permission="CONSENT_STRATEGY_AUDIT_ONLY",
        noise_sensitive_interaction=True,
    ),
    DiagramArtifact(
        diagram_id="loop_equation_hierarchy",
        source_family="Bourgade-Huang random-matrix loop-equation characterization",
        page_or_context="arXiv:2607.07617, submitted 2026-07-08",
        diagram_role="hierarchy/invariant diagram",
        diagram_object="bulk and edge loop-equation hierarchy for Sine_beta and Airy_beta statistics",
        mathematical_lesson="Universal local statistics are characterized by a hierarchy of approximate equations, not by visual resemblance to a reference ensemble.",
        medical_runtime_lesson="Population, sensor, transcript, or genomic clusters that look universal should still pass the declared hierarchy of endpoint, provenance, transport, privacy, and authority checks before the LLM transports a claim.",
        required_gate="universality/invariant hierarchy gate",
        permission="UNIVERSALITY_AUDIT_ONLY",
        transfer_resets_validation=True,
    ),
)


def rows() -> list[dict[str, object]]:
    return [asdict(item) for item in DIAGRAMS]


def permission_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in DIAGRAMS:
        counts[item.permission] = counts.get(item.permission, 0) + 1
    return dict(sorted(counts.items()))


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    filename = "arialbd.ttf" if bold else "arial.ttf"
    path = Path(r"C:\Windows\Fonts") / filename
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _wrapped_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    width: int,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: tuple[int, int, int],
    line_height: int,
) -> int:
    x, y = xy
    # Fixed-width wrapping is good enough for this internal QA figure.
    for line in wrap(text, width=max(16, width // 11)):
        draw.text((x, y), line, fill=fill, font=font)
        y += line_height
    return y


def plot_runtime_map() -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / "picture_language_runtime_map.png"
    image = Image.new("RGB", (1900, 1120), "white")
    draw = ImageDraw.Draw(image)
    title = _font(40, bold=True)
    h2 = _font(28, bold=True)
    body = _font(23)
    small = _font(20)
    tiny = _font(18)

    navy = (22, 42, 66)
    teal = (35, 137, 131)
    amber = (214, 142, 36)
    gray = (82, 90, 99)
    light = (240, 246, 247)
    pale_amber = (252, 244, 232)
    line = (176, 190, 197)

    draw.text((70, 45), "Picture-Language Runtime Assurance Map", fill=navy, font=title)
    draw.text(
        (70, 100),
        "Diagrammatic, audio, image, caption, and dashboard artifacts can help clinicians only after the L-to-R simulation map is explicit.",
        fill=gray,
        font=body,
    )

    box_w, box_h = 300, 150
    y = 210
    xs = [80, 440, 800, 1160, 1520]
    labels = [
        ("R", "Clinical target reality", "patient state, workflow, outcome"),
        ("A", "Abstraction", "capture, crop, code, summarize"),
        ("L", "Language artifact", "photo, waveform, note, plot, video"),
        ("S", "Simulation map", "declared relation from L back to R"),
        ("P", "Permission", "audit, narrow, stress-test, allow"),
    ]
    colors = [light, pale_amber, light, pale_amber, light]
    for i, (symbol, label, sub) in enumerate(labels):
        x = xs[i]
        draw.rounded_rectangle([x, y, x + box_w, y + box_h], radius=16, fill=colors[i], outline=teal, width=3)
        draw.text((x + 24, y + 24), symbol, fill=teal, font=title)
        draw.text((x + 85, y + 28), label, fill=navy, font=h2)
        _wrapped_text(draw, (x + 24, y + 84), sub, box_w - 48, body, gray, 28)
        if i < len(labels) - 1:
            ax0 = x + box_w + 12
            ax1 = xs[i + 1] - 14
            cy = y + box_h // 2
            draw.line([ax0, cy, ax1, cy], fill=teal, width=5)
            draw.polygon([(ax1, cy), (ax1 - 18, cy - 11), (ax1 - 18, cy + 11)], fill=teal)

    draw.text((80, 430), "Diagram audit results", fill=navy, font=h2)
    columns = [("Diagram", 430), ("Runtime lesson", 690), ("Gate", 290), ("Permission", 330)]
    table_x, table_y = 80, 480
    row_h = 82
    x = table_x
    for name, width in columns:
        draw.rectangle([x, table_y, x + width, table_y + row_h], fill=(235, 240, 244), outline=line)
        draw.text((x + 14, table_y + 26), name, fill=navy, font=body)
        x += width

    short_rows = [
        ("Feynman exchange", "Latent or reconstructed content remains virtual until validated.", "real/virtual", "ABSTAIN"),
        ("Lattice duality", "Coarse-graining can preserve one invariant while flipping another.", "invariant", "STRESS-TEST"),
        ("Max/GHZ rotation", "Same picture can map to different realities under different S.", "map identity", "AUDIT"),
        ("Simulation clock", "Every L-to-R transfer resets validation.", "transfer reset", "ABSTAIN"),
        ("Prisoner's Dilemma", "Noisy interaction should not be treated as intentional defection.", "noise/context", "AUDIT"),
    ]
    for r, values in enumerate(short_rows, start=1):
        y0 = table_y + r * row_h
        fill = (253, 253, 253) if r % 2 else (247, 250, 250)
        x = table_x
        for value, (_, width) in zip(values, columns, strict=True):
            draw.rectangle([x, y0, x + width, y0 + row_h], fill=fill, outline=line)
            font = small if width >= 330 else tiny
            _wrapped_text(draw, (x + 14, y0 + 14), value, width - 28, font, (38, 49, 59), 23)
            x += width

    draw.rounded_rectangle([80, 940, 1820, 1040], radius=14, fill=(250, 249, 246), outline=amber, width=3)
    draw.text((105, 960), "Operational invariant", fill=amber, font=h2)
    _wrapped_text(
        draw,
        (405, 958),
        "A compelling multimodal artifact may support explanation, audit, simulation, or hypothesis formation. It does not become hard patient-outcome evidence unless provenance, consent, endpoint, transport, and clinician-authority gates all pass.",
        1360,
        body,
        navy,
        30,
    )

    image.save(path)
    return path


def run() -> dict[str, object]:
    RESULTS.mkdir(parents=True, exist_ok=True)
    row_dicts = rows()
    counts = permission_counts()
    csv_path = RESULTS / "picture_language_diagram_audit.csv"
    json_path = RESULTS / "picture_language_diagram_audit_summary.json"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row_dicts[0]))
        writer.writeheader()
        writer.writerows(row_dicts)

    figure = plot_runtime_map()
    summary = {
        "experiment": "picture_language_diagram_audit",
        "clinical_status": "synthetic diagrammatic analogy only",
        "diagram_count": len(DIAGRAMS),
        "source_families": sorted({item.source_family for item in DIAGRAMS}),
        "permission_counts": counts,
        "hard_outcome_permission_count": sum(
            1 for item in DIAGRAMS if "HARD_OUTCOME" in item.permission or "ALLOW" in item.permission
        ),
        "transfer_reset_diagram_count": sum(item.transfer_resets_validation for item in DIAGRAMS),
        "virtual_state_warning_count": sum(item.virtual_state_warning for item in DIAGRAMS),
        "noise_sensitive_interaction_count": sum(item.noise_sensitive_interaction for item in DIAGRAMS),
        "all_diagrams_audit_or_stress_only": all(
            item.permission
            in {
                "PROOF_STATUS_OR_PROVENANCE_AUDIT_ONLY",
                "ABSTAIN_PROVENANCE",
                "STRESS_TEST_BOUNDARY",
                "WORKFLOW_AUDIT_ONLY",
                "CONSENT_STRATEGY_AUDIT_ONLY",
                "UNIVERSALITY_AUDIT_ONLY",
            }
            for item in DIAGRAMS
        ),
        "simulation_clock_resets_validation": next(
            item.transfer_resets_validation for item in DIAGRAMS if item.diagram_id == "simulation_clock"
        ),
        "feynman_virtual_state_warning": next(
            item.virtual_state_warning for item in DIAGRAMS if item.diagram_id == "feynman_virtual_exchange"
        ),
        "prisoners_dilemma_noise_note": next(
            item.noise_sensitive_interaction
            for item in DIAGRAMS
            if item.diagram_id == "iterated_prisoners_dilemma_noise"
        ),
        "csv": str(csv_path.relative_to(ROOT)),
        "figure": str(figure.relative_to(ROOT)),
        "interpretation": (
            "The diagrams are useful as simulation, proof-status, cooperation, and workflow artifacts, "
            "but none authorizes a hard patient-outcome claim. Every multimodal transfer must preserve "
            "the simulation map, provenance, context, consent, and authority boundary."
        ),
        "rows": row_dicts,
    }
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
