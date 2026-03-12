from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    make_response,
    flash,
    current_app,
    url_for,
)
from werkzeug.wrappers import Response
from pydantic import ValidationError
from bson.objectid import ObjectId

from .models import DeviceConfig
from .dt import DECISION_TREE
from .adapters import D3JSNodeAdapter
from fpdf import FPDF

import json
import os

bp = Blueprint("main", __name__)

REQUIREMENTS = ("ACM-1", "ACM-2",)

def _get_device(device_id: str) -> DeviceConfig | None:
    """Recupera e valida un device da MongoDB dato il suo id.
    Ritorna None se non trovato."""
    devices_collection = current_app.db["devices"]
    device_dict = devices_collection.find_one({"_id": ObjectId(device_id)})
    if device_dict is None:
        return None
    return DeviceConfig(**device_dict)

def _build_report_data(device: DeviceConfig) -> tuple[list[dict], list[str], list[str]]:
    """Costruisce assets, columns e rows a partire da un DeviceConfig.
    Usata sia dalla route /<device_id>/report che da /<device_id>/report/export."""
    assets = [a.model_dump() for a in device.assets]
 
    # Ricava columns e rows dinamicamente dal primo asset che ha dati nel dt
    columns: list[str] = []
    rows: list[str] = []
    for asset in device.assets:
        if asset.dt:
            columns = list(asset.dt.keys())
            rows = list(next(iter(asset.dt.values())).keys())
            break
 
    return assets, columns, rows


@bp.route("/<device_id>/report")
def report(device_id: str) -> Response | str:
    device = _get_device(device_id)
    if device is None:
        flash("Dispositivo non trovato.", "error")
        return redirect(url_for("main.import_page"))
 
    assets, columns, rows = _build_report_data(device)
    return render_template(
        "report.html",
        title=f"Report — {device.info.name}",
        page_title=f"{device.info.name} — {device.info.os}",
        info=device.info.model_dump(),
        assets=assets,
        columns=columns,
        rows=rows,
        device_id=device_id,
    )



@bp.route("/<device_id>/report/export")
def report_export(device_id: str) -> Response:
    device = _get_device(device_id)
    if device is None:
        flash("Dispositivo non trovato.", "error")
        return redirect(url_for("main.import_page"))
 
    assets, columns, rows = _build_report_data(device)
 
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
 
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Length"] = len(pdf_bytes)
    response.headers["Content-Disposition"] = f"attachment; filename=report_{device_id}.pdf"
    return response


@bp.route("/<device_id>/dt/<int:asset_id>/<requirement>")
def decision_tree(device_id: str, asset_id: int, requirement: str) -> Response|str:
    devices_collection = current_app.db["devices"]
    device_dict = devices_collection.find_one({"_id": ObjectId(device_id)})

    if device_dict is None:
        flash("Dispositivo non trovato.", "error")
        return redirect(url_for("main.import_page"))

    device = DeviceConfig(**device_dict)

    if asset_id < 1 or asset_id > len(device.assets):
        flash("Asset inesistente.", "error")
        return redirect(url_for("main.import_page"))

    # Calcola il prossimo requisito da visualizzare e il prossimo asset (o dello stesso asset)
    next_req_idx = (REQUIREMENTS.index(requirement) + 1) % len(REQUIREMENTS)
    next_asset_id = asset_id
    if next_req_idx == 0:
        next_asset_id += 1

    forward_link: str = f"/{device_id}/dt/{next_asset_id}/{REQUIREMENTS[next_req_idx]}"
    if next_req_idx == 0 and next_asset_id >= len(device.assets):
        # Se il prossimo requisito è il primo (indice 0) e l'asset è l'ultimo,
        # vuol dire che si è raggiunta la fine della visualizzazione dei decision tree
        # e si può passare alla pagina di report
        forward_link = f"/{device_id}/report"

    # Calcola il precedente requisito da visualizzare e il precedente asset (o dello stesso asset)
    prev_req_idx = (REQUIREMENTS.index(requirement) - 1) % len(REQUIREMENTS)
    prev_asset_id = asset_id
    if next_req_idx == len(REQUIREMENTS) - 1:
        prev_asset_id -= 1

    back_link: str = f"/{device_id}/dt/{prev_asset_id}/{REQUIREMENTS[prev_req_idx]}"
    if prev_asset_id < 1:
        # Se l'id dell'asset precedente è < 1 si è tornati al primo asset e quindi non
        # si può più tornare indietro
        back_link = ""

    return render_template(
        "decision_tree.html",
        title=f"Decision Tree {device.assets[asset_id - 1].name} - {requirement}",
        page_title=requirement,
        assets=enumerate([a.name for a in device.assets]),
        selected_asset=asset_id,
        json_dt=D3JSNodeAdapter(
            DECISION_TREE[requirement],
            device.assets[asset_id - 1].dt[requirement],
        ).asdict(),
        back_link=back_link,
        forward_link=forward_link,
    )


@bp.route("/<device_id>/dt/<int:asset_id>/<requirement>/updatedt")
def update_decision_tree(device_id: str, asset_id: int, requirement: str) -> Response:
    """Aggiornamento del decision tree modificando la risposta ad un requisito"""
    
    # Validazione dei parametri in input
    updateKey: str = request.args.get("set", "", type=str)
    updateRawValue: str = request.args.get("value", "", type=str)
    if updateKey == "":
        return redirect(url_for("main.import_page"))
    
    devices_collection = current_app.db["devices"]

    # Per prima cosa si prende il dispositivo dal database
    device_dict = devices_collection.find_one({"_id": ObjectId(device_id)})
    if device_dict is None:
        flash("Dispositivo non trovato.", "error")
        return redirect(url_for("main.import_page"))

    # Validazione asset_id
    if asset_id < 1 or asset_id > len(device_dict["assets"]):
        flash("Asset non trovato.", "error")
        return redirect(url_for("main.import_page"))

    # Aggiornamento della risposta al requisito nel decision tree
    device_dict["assets"][asset_id - 1]['dt'][requirement][updateKey] = (
        updateRawValue == "true"
    )
    devices_collection.update_one(
        {"_id": ObjectId(device_id)}, {"$set": {"assets": device_dict["assets"]}}
    )

    # Rimanda l'utente alla visualizzazione del decision tree
    return redirect(f"/{device_id}/dt/{asset_id}/{requirement}")


@bp.route("/", methods=["GET", "POST"])
def import_page():
    if request.method == "POST":
        if "file_json" not in request.files:
            flash("Nessun file inviato al form.", "error")
            return redirect(url_for("main.import_page"))

        uploaded_file = request.files["file_json"]
        filename = uploaded_file.filename
        if filename == "":
            flash("Nessun file selezionato.", "error")
            return redirect(url_for("main.import_page"))

        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext != ".json":
            flash("Il file deve avere estensione .json", "error")
            return redirect(url_for("main.import_page"))

        if request.content_length > (1024 * 1024):
            flash("Il file supera la dimensione massima consentita di 1 MB.", "error")
            return redirect(url_for("main.import_page"))

        try:
            raw_data = json.load(uploaded_file)
            validated_device = DeviceConfig.model_validate(raw_data)
            device_dict = validated_device.model_dump()
            device_dict["status"] = "Imported"

            devices_collection = current_app.db["devices"]

            result = devices_collection.insert_one(device_dict)
            new_device_id = str(result.inserted_id)

            flash("Configurazione importata e validata con successo!", "success")
            return redirect(f"/{new_device_id}/dt/1/{REQUIREMENTS[0]}")

        except json.JSONDecodeError:
            flash(
                "Errore: Il file caricato non è un JSON valido o è malformato.", "error"
            )
            return redirect(url_for("main.import_page"))

        except ValidationError as e:
            error_messages = []
            for error in e.errors():
                field_path = " -> ".join(str(loc) for loc in error["loc"])
                error_messages.append(
                    f"Errore nel campo '{field_path}': {error['msg']}"
                )

                for msg in error_messages:
                    flash(msg, "error")

                return redirect(url_for("main.import_page"))
        except Exception as e:
            flash(f"Errore imprevisto durante la lettura: {str(e)}", "error")
            return redirect(url_for("main.import_page"))

    elif request.method == "GET":
        return render_template(
            "import.html", title="Importa Configurazione", page_title="Carica File JSON"
        )
