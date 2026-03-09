from flask import Blueprint, render_template, request, redirect, make_response
from werkzeug.wrappers import Response

from .dt import DECISION_TREE
from .adapters import D3JSNodeAdapter
from fpdf import FPDF

bp = Blueprint("main", __name__)

# 
# Blocco di costanti temporanee
# 
CHOICES: dict[str, dict[str, bool]] = {
    "ACM-1": {"DN-1": False, "DN-2": False, "DN-3": False, "DN-4": False},
    "ACM-2": {"DN-1": False},
}
ASSETS: dict[int, str] = {
    1: "Mosquitto Client",
    2: "Mosquitto Client configuration",
    3: "wpa_supplicant",
    4: "wpa_supplicant configuration",
    5: "SSH client",
    6: "SSH client configuration",
    7: "DHCP Client",
    8: "DHCP Client configuration",
    9: "DNS Client configuration",
    10: "Mosquitto broker",
    11: "Mosquitto broker configuration",
}
REQUIREMENTS: list[str] = ["ACM-1", "ACM-2"]
# 
# Fine blocco
# 
def _build_report_data() -> tuple[list[dict], list[str], list[str]]:
    """Costruisce assets, columns e rows dai dati in memoria.
    Usata sia dalla route /report che dalla route /report/export."""
    columns: list[str] = REQUIREMENTS
    rows: list[str] = list(next(iter(CHOICES.values())).keys())
    assets = [
        {
            "name": name,
            "description": name,
            "type": "N.A.",
            "dt": {
                req: {dn: CHOICES[req][dn] for dn in CHOICES[req]}
                for req in REQUIREMENTS
            },
        }
        for name in ASSETS.values()
    ]
    return assets, columns, rows


@bp.route("/report")
def report() -> str:
    assets, columns, rows = _build_report_data()
    return render_template(
        "report.html",
        title="Report",
        page_title="Coffee Machine — Linux Embedded",
        assets=assets,
        columns=columns,
        rows=rows,
    )


@bp.route("/report/export")
def report_export() -> Response:
    assets, columns, rows = _build_report_data()
    COLOR_HEADER_BG   = (44,  62,  80)
    COLOR_HEADER_TEXT = (255, 255, 255)
    COLOR_ROW_LABEL   = (240, 242, 245)
    COLOR_TRUE_BG     = (230, 249, 236)
    COLOR_TRUE_TEXT   = (30,  126, 52)
    COLOR_FALSE_BG    = (253, 236, 234)
    COLOR_FALSE_TEXT  = (192, 57,  43)
    COLOR_NA_BG       = (240, 240, 240)
    COLOR_NA_TEXT     = (136, 136, 136)
    COLOR_BORDER      = (221, 225, 231)
    COLOR_CARD_TITLE  = (26,  26,  46)
    COLOR_BADGE_BG    = (59,  125, 238)

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.set_margins(12, 12, 12)
    page_w = pdf.w - pdf.l_margin - pdf.r_margin
    dn_col_w = 38
    acm_col_w = (page_w - dn_col_w) / len(columns)
    row_h = 7

    for asset in assets:
        pdf.add_page()

        pdf.set_fill_color(*COLOR_BADGE_BG)
        pdf.set_text_color(*COLOR_HEADER_TEXT)
        pdf.set_font("Helvetica", "B", 7)
        pdf.cell(0, 5, asset["type"].upper(), ln=True, fill=True)
        pdf.ln(1)

        pdf.set_text_color(*COLOR_CARD_TITLE)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, asset["name"], ln=True)

        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, asset["description"], ln=True)
        pdf.ln(3)

        pdf.set_fill_color(*COLOR_HEADER_BG)
        pdf.set_text_color(*COLOR_HEADER_TEXT)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_draw_color(*COLOR_BORDER)

        pdf.cell(dn_col_w, row_h, "DN / ACM", border=1, align="C", fill=True)
        for col in columns:
            pdf.cell(acm_col_w, row_h, col, border=1, align="C", fill=True)
        pdf.ln()

        for row in rows:
            pdf.set_fill_color(*COLOR_ROW_LABEL)
            pdf.set_text_color(*COLOR_CARD_TITLE)
            pdf.set_font("Helvetica", "B", 8)
            pdf.cell(dn_col_w, row_h, row, border=1, align="L", fill=True)

            pdf.set_font("Helvetica", "", 8)
            for col in columns:
                if col in asset["dt"] and row in asset["dt"][col]:
                    val = asset["dt"][col][row]
                    if val:
                        pdf.set_fill_color(*COLOR_TRUE_BG)
                        pdf.set_text_color(*COLOR_TRUE_TEXT)
                        label = "True"
                    else:
                        pdf.set_fill_color(*COLOR_FALSE_BG)
                        pdf.set_text_color(*COLOR_FALSE_TEXT)
                        label = "False"
                else:
                    pdf.set_fill_color(*COLOR_NA_BG)
                    pdf.set_text_color(*COLOR_NA_TEXT)
                    label = "N.A."

                pdf.cell(acm_col_w, row_h, label, border=1, align="C", fill=True)
            pdf.ln()

    pdf_bytes = pdf.output()
    response = make_response(bytes(pdf_bytes))
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=report.pdf"
    return response



@bp.route("/dt/<int:asset_id>/<requirement>")
def decision_tree(asset_id: int, requirement: str) -> str:
    # Calcola il prossimo requisito da visualizzare e il prossimo asset (o dello stesso asset)
    next_req_idx = (REQUIREMENTS.index(requirement) + 1) % len(REQUIREMENTS)
    next_asset_id = asset_id
    if next_req_idx == 0:
        next_asset_id += 1

    forward_link: str = f"/dt/{next_asset_id}/{REQUIREMENTS[next_req_idx]}"
    if next_req_idx == 0 and ASSETS.get(next_asset_id, None) is None:
        # Se il prossimo requisito è il primo (indice 0) e il prossimo asset non viene
        # trovato nella lista, vuol dire che si è raggiunta la fine della visualizzazione
        # dei deicision tree e si può passare alla pagina di report
        forward_link = "/report"

    # Calcola il precedente requisito da visualizzare e il precendente asset (o dello stesso asset)
    prev_req_idx = (REQUIREMENTS.index(requirement) - 1) % len(REQUIREMENTS)
    prev_asset_id = asset_id
    if next_req_idx == len(REQUIREMENTS) - 1:
        prev_asset_id -= 1

    back_link: str = f"/dt/{prev_asset_id}/{REQUIREMENTS[prev_req_idx]}"
    if prev_asset_id < 1:
        # Se l'id dell'asset precendente è < 1 si è tornati al primo asset e quindi non
        # si può più tornare indietro
        back_link = ""

    return render_template(
        "decision_tree.html",
        title=f"Decision Tree {ASSETS[asset_id]} - {requirement}",
        page_title=requirement,
        assets=ASSETS,
        selected_asset=asset_id,
        json_dt=D3JSNodeAdapter(
            DECISION_TREE[requirement],
            CHOICES[requirement],
        ).asdict(),
        back_link=back_link,
        forward_link=forward_link,
    )


@bp.route("/dt/<int:asset_id>/<requirement>/updatedt")
def update_decision_tree(asset_id: int, requirement: str) -> Response:
    updateKey: str = request.args.get("set", "", type=str)
    updateRawValue: str = request.args.get("value", "", type=str)
    if updateKey != "":
        CHOICES[requirement][updateKey] = updateRawValue == "true"

    return redirect(f"/dt/{asset_id}/{requirement}")
