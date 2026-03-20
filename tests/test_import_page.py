import io
import pytest


class TestImportFile:
    def _assert_error_response(self, client, response, expected_message):
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/")
        with client.session_transaction() as sess:
            messages = dict(sess.get("_flashes", []))
        assert any(expected_message in m for m in messages.values())

    def test_no_file_error(self, client):
        response = client.post("/", data={}, content_type="multipart/form-data")
        self._assert_error_response(client, response, "Nessun file inviato")

    def test_empty_file_error(self, client):
        form_data = {"file_json": (io.BytesIO(b""), "")}
        response = client.post("/", data=form_data, content_type="multipart/form-data")
        self._assert_error_response(client, response, "Nessun file selezionato")

    def test_empty_file_format_error(self, client):
        form_data = {"file_json": (io.BytesIO(b"x" * 1024), "dispositivo.bin")}
        response = client.post("/", data=form_data, content_type="multipart/form-data")
        self._assert_error_response(
            client, response, "Il file deve avere estensione .json"
        )

    def test_too_big_error(self, client):
        form_data = {
            "file_json": (io.BytesIO(b"x" * (1024 * 1024 + 1)), "dispositivo.json")
        }
        response = client.post("/", data=form_data, content_type="multipart/form-data")
        self._assert_error_response(
            client, response, "Il file supera la dimensione massima consentita di 1 MB."
        )

    def test_invalid_file_error(self, client):
        form_data = {"file_json": (io.BytesIO(b"{"), "dispositivo.json")}
        response = client.post("/", data=form_data, content_type="multipart/form-data")
        self._assert_error_response(
            client,
            response,
            "Errore: Il file caricato non è un JSON valido o è malformato.",
        )

    def test_valid_file(self, client):
        form_data = {
            "file_json": (
                io.BytesIO(
                    b'{"info":{"name":"Test device","os":"Linux Embedded","description":"Test description"},"assets":[{"name":"A1","description":"A1","type":"security","dt":{"ACM-1":{"DN-1":false,"DN-2":false,"DN-3":false,"DN-4":false},"ACM-2":{"DN-1":false}}}]}'
                ),
                "dispositivo.json",
            )
        }
        response = client.post("/", data=form_data, content_type="multipart/form-data")
        assert response.status_code == 302
        assert response.headers["Location"].startswith("/dashboard/")
