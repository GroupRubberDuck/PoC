from flask import Blueprint, render_template, request, redirect
from werkzeug.wrappers import Response

from .dt import DECISION_TREE
from .adapters import D3JSNodeAdapter

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
