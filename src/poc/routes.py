import json
from flask import Blueprint, request, make_response, current_app, jsonify
from pydantic import ValidationError
from bson.objectid import ObjectId
from typing import Any
from fpdf import FPDF

from .models import DeviceConfig
from .dt import DECISION_TREE, Result, Node
from .adapters import D3JSNodeAdapter

bp = Blueprint("main", __name__)

REQUIREMENTS = (
    "ACM-1",
    "ACM-2",
)


def _get_device(device_id: str) -> DeviceConfig | None:
    """Recupera e valida un device da MongoDB dato il suo id.
    Ritorna None se non trovato."""
    devices_collection = current_app.db["devices"]
    device_dict = devices_collection.find_one({"_id": ObjectId(device_id)})
    if device_dict is None:
        return None
    return DeviceConfig(**device_dict)

def valuta_albero(req_name: str, choices: dict) -> str:
    """Attraversa l'albero decisionale in base alle scelte per trovare il risultato finale."""
    if req_name not in DECISION_TREE:
        return "Da valutare"
    
    current_node = DECISION_TREE[req_name]
    
    # Navighiamo l'albero finché siamo su un Nodo (domanda)
    while isinstance(current_node, Node):
        if current_node.name not in choices:
            # L'utente non ha ancora risposto a questa domanda
            return "Da valutare"
        
        # Prendiamo la risposta dell'utente (True = Yes, False = No)
        risposta_yes = choices[current_node.name]
        
        # Scendiamo al ramo successivo
        current_node = current_node.yes_child if risposta_yes else current_node.no_child
        
    # Se il ciclo finisce, significa che current_node è una foglia (Result)
    if current_node == Result.PASS:
        return "Conforme"
    elif current_node == Result.FAIL:
        return "Non conforme"
    elif current_node == Result.NA:
        return "Non applicabile"
    
    return "Da valutare"

def _build_report_data(
    device: DeviceConfig,
) -> tuple[list[dict[str, Any]], list[str], list[str], bool]:
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

    # Conformità del dispositivo: AND di tutti i valori presenti nel dt di ogni asset
    compliant: bool = True
    for asset in device.assets:
        for col_vals in asset.dt.values():
            for val in col_vals.values():
                if val is False:
                    compliant = False
                    break

    return assets, columns, rows, compliant

@bp.route("/api/report/<device_id>", methods=["GET"])
def api_report_data(device_id: str):
    """API: Fornisce i dati strutturati per la tabella del report a schermo"""
    device = _get_device(device_id)
    if not device:
        return jsonify({"error": "Dispositivo non trovato"}), 404

    # Usiamo la tua funzione Core già esistente!
    assets, columns, rows, all_assessed = _build_report_data(device)

    return jsonify({
        "device_info": device.info.model_dump(),
        "assets": assets,
        "columns": columns,
        "rows": rows,
        "all_assessed": all_assessed
    })

@bp.route("/api/report/<device_id>/export", methods=["GET"])
def api_export_report(device_id: str):
    """API: Genera e restituisce il file PDF del report"""
    device = _get_device(device_id)
    if not device:
        return jsonify({"error": "Dispositivo non trovato"}), 404

    assets, columns, rows, all_assessed = _build_report_data(device)

    COLOR_HEADER_BG = (44, 62, 80)
    COLOR_HEADER_TEXT = (255, 255, 255)
    COLOR_ROW_LABEL = (240, 242, 245)
    COLOR_TRUE_BG = (230, 249, 236)
    COLOR_TRUE_TEXT = (30, 126, 52)
    COLOR_FALSE_BG = (253, 236, 234)
    COLOR_FALSE_TEXT = (192, 57, 43)
    COLOR_NA_BG = (240, 240, 240)
    COLOR_NA_TEXT = (136, 136, 136)
    COLOR_BORDER = (221, 225, 231)
    COLOR_CARD_TITLE = (26, 26, 46)
    COLOR_BADGE_BG = (59, 125, 238)

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

    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Length"] = len(pdf_bytes)
    response.headers["Content-Disposition"] = (
        f"attachment; filename=report_{device_id}.pdf"
    )
    
    return response

@bp.route("/api/dashboard/<device_id>", methods=["GET"])
def api_dashboard(device_id: str):
    try:
        device = current_app.db["devices"].find_one({"_id": ObjectId(device_id)})
    except Exception:
        return jsonify({"error": "ID non valido"}), 400

    if not device:
        return jsonify({"error": "Non trovato"}), 404

    device["_id"] = str(device["_id"])
    
    device_status_globale = "Conforme"

    for i, asset in enumerate(device["assets"]):
        asset_status = "Conforme"
        
        # Controlliamo TUTTI i requisiti definiti (ACM-1, ACM-2, ecc.)
        for req_name in REQUIREMENTS:
            # Prendiamo le risposte dell'utente (se non ci sono, usiamo dict vuoto {})
            choices = asset["dt"].get(req_name, {})
            
            # Interroghiamo il motore logico
            stato_requisito = valuta_albero(req_name, choices)
            
            # Logica di aggregazione per l'Asset
            if stato_requisito == "Da valutare":
                asset_status = "Da valutare"
            elif stato_requisito == "Non conforme" and asset_status != "Da valutare":
                asset_status = "Non conforme"
                
        # Logica di aggregazione per il Device globale
        if asset_status == "Da valutare":
            device_status_globale = "Da valutare"
        elif asset_status == "Non conforme" and device_status_globale != "Da valutare":
            device_status_globale = "Non conforme"

        asset["aggregated_status"] = asset_status

    return jsonify({
        "device": device,
        "device_status": device_status_globale
    })

@bp.route("/api/import", methods=["POST"])
def api_import_device():
    """Adapter di input: riceve il file e lo invia al Core (DeviceConfig)"""
    if "file" not in request.files:
        return jsonify({"error": "Nessun file inviato."}), 400
        
    file = request.files["file"]
    
    try:
        # Carichiamo il contenuto del file
        data = json.load(file)
        
        # CHIAMATA AL CORE: Validazione con il modello Pydantic (models.py)
        # Se i dati sono sbagliati, Pydantic solleva ValidationError
        device_config = DeviceConfig(**data)
        
        # Salvataggio tramite Adapter di Persistenza (MongoDB)
        result = current_app.db["devices"].insert_one(device_config.model_dump())
        
        # Risposta di successo con l'ID per il frontend
        return jsonify({
            "message": "Importazione completata",
            "device_id": str(result.inserted_id)
        }), 201

    except ValidationError as e:
        return jsonify({"error": "Schema JSON non valido", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/api/dt/<device_id>/<int:asset_index>/<requirement>", methods=["GET"])
def api_get_tree(device_id, asset_index, requirement):
    """API: Fornisce i dati dell'albero formattati per D3.js e la navigazione"""
    device = _get_device(device_id)
    if not device:
        return jsonify({"error": "Device non trovato"}), 404
    
    try:
        asset = device.assets[asset_index]
        choices = asset.dt.get(requirement, {})
    except IndexError:
        return jsonify({"error": "Asset non trovato"}), 404

    adapter = D3JSNodeAdapter(DECISION_TREE[requirement], choices)
    
    try:
        req_index = REQUIREMENTS.index(requirement)
        prev_req = REQUIREMENTS[req_index - 1] if req_index > 0 else None
        next_req = REQUIREMENTS[req_index + 1] if req_index < len(REQUIREMENTS) - 1 else None
    except ValueError:
        prev_req, next_req = None, None

    return jsonify({
        "tree_data": adapter.asdict(),
        "asset_name": asset.name,
        "requirement": requirement,
        "prev_req": prev_req,  # Inviato a Vue
        "next_req": next_req   # Inviato a Vue
    })

@bp.route("/api/dt/update", methods=["POST"])
def api_update_tree():
    """API: Salva una scelta (Yes/No) fatta nell'albero"""
    data = request.json
    device_id = data.get("device_id")
    asset_index = int(data.get("asset_index")) 
    requirement = data.get("requirement")
    node_name = data.get("node_name")
    value = bool(data.get("value"))

    devices_collection = current_app.db["devices"]
    
    # Aggiornamento mirato su MongoDB usando la notazione a punti di Mongo
    update_path = f"assets.{asset_index}.dt.{requirement}.{node_name}"
    
    devices_collection.update_one(
        {"_id": ObjectId(device_id)},
        {"$set": {update_path: value}}
    )
    
    return jsonify({"status": "success"})