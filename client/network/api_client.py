import json
import re
from typing import Optional

from PySide2.QtCore import QObject, Signal, QUrl
from PySide2.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from client.i18n import tr


class ApiError(Exception):
    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


class ApiClient(QObject):
    games_loaded = Signal(list)
    game_loaded = Signal(object)
    game_created = Signal(object)
    game_deleted = Signal(int)
    saves_loaded = Signal(list)
    save_uploaded = Signal(object)
    save_upload_completed = Signal(int)
    save_downloaded = Signal(int)
    icon_loaded = Signal(int, object)
    error_occurred = Signal(str, int)
    health_checked = Signal(bool)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._nam = QNetworkAccessManager(self)
        self._base_url = "http://127.0.0.1:3000"

    def set_server(self, host: str, port: int) -> None:
        self._base_url = f"http://{host}:{port}"

    def health_check(self) -> None:
        req = QNetworkRequest(self._build_url("/api/health"))
        reply = self._nam.get(req)
        self._handle_reply(reply, lambda data: self.health_checked.emit(True),
                           lambda msg, code: self.health_checked.emit(False))

    def list_games(self) -> None:
        req = QNetworkRequest(self._build_url("/api/games"))
        reply = self._nam.get(req)
        self._handle_reply(reply,
                           lambda data: self.games_loaded.emit(data.get("games", [])),
                           lambda msg, code: self.error_occurred.emit(msg, code))

    def get_game(self, game_id: int) -> None:
        req = QNetworkRequest(self._build_url(f"/api/games/{game_id}"))
        reply = self._nam.get(req)
        self._handle_reply(reply,
                           lambda data: self.game_loaded.emit(data),
                           lambda msg, code: self.error_occurred.emit(msg, code))

    def create_game(self, name: str, local_save_path: str) -> None:
        body = json.dumps({"name": name, "local_save_path": local_save_path}).encode()
        req = QNetworkRequest(self._build_url("/api/games"))
        req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        reply = self._nam.post(req, body)
        self._handle_reply(reply,
                           lambda data: self.game_created.emit(data),
                           lambda msg, code: self.error_occurred.emit(msg, code))

    def update_game(self, game_id: int, name: Optional[str] = None, local_save_path: Optional[str] = None) -> None:
        body = {}
        if name is not None:
            body["name"] = name
        if local_save_path is not None:
            body["local_save_path"] = local_save_path
        req = QNetworkRequest(self._build_url(f"/api/games/{game_id}"))
        req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        body_bytes = json.dumps(body).encode()
        reply = self._nam.put(req, body_bytes)
        self._handle_reply(reply,
                           lambda data: self.game_loaded.emit(data),
                           lambda msg, code: self.error_occurred.emit(msg, code))

    def delete_game(self, game_id: int) -> None:
        req = QNetworkRequest(self._build_url(f"/api/games/{game_id}"))
        reply = self._nam.deleteResource(req)
        self._handle_reply(reply,
                           lambda _: self.game_deleted.emit(game_id),
                           lambda msg, code: self.error_occurred.emit(msg, code))

    def upload_icon(self, game_id: int, file_path: str) -> None:
        from PySide2.QtCore import QFile, QMimeDatabase
        from PySide2.QtNetwork import QHttpMultiPart, QHttpPart
        f = QFile(file_path)
        if not f.open(QFile.ReadOnly):
            self.error_occurred.emit(f"Cannot open icon file: {file_path}", 0)
            return
        multi = QHttpMultiPart(QHttpMultiPart.FormDataType)
        part = QHttpPart()
        mime = QMimeDatabase().mimeTypeForFile(file_path).name()
        part.setHeader(QNetworkRequest.ContentTypeHeader, mime)
        part.setHeader(QNetworkRequest.ContentDispositionHeader,
                       f'form-data; name="file"; filename="{file_path.rsplit("/", 1)[-1]}"')
        part.setBodyDevice(f)
        f.setParent(multi)
        multi.append(part)
        self._multi = multi  # prevent GC
        req = QNetworkRequest(self._build_url(f"/api/games/{game_id}/icon"))
        reply = self._nam.put(req, multi)
        self._handle_reply(reply,
                           lambda data: self.game_loaded.emit(data),
                           lambda msg, code: self.error_occurred.emit(msg, code))

    def download_icon(self, game_id: int) -> None:
        from PySide2.QtGui import QPixmap
        req = QNetworkRequest(self._build_url(f"/api/games/{game_id}/icon"))
        reply = self._nam.get(req)
        def on_ok(data):
            pix = QPixmap()
            pix.loadFromData(reply.readAll())
            self.icon_loaded.emit(game_id, pix)
        def on_err(msg, code):
            if code == 404:
                return  # game has no icon, silently ignore
            self.error_occurred.emit(msg, code)
        self._handle_reply(reply, on_ok, on_err)

    def upload_save(self, game_id: int, file_path: str, version: str = "1.0") -> None:
        from PySide2.QtCore import QFile
        from PySide2.QtNetwork import QHttpMultiPart, QHttpPart
        f = QFile(file_path)
        if not f.open(QFile.ReadOnly):
            self.error_occurred.emit(f"Cannot open save file: {file_path}", 0)
            return
        multi = QHttpMultiPart(QHttpMultiPart.FormDataType)
        part = QHttpPart()
        part.setHeader(QNetworkRequest.ContentDispositionHeader,
                       f'form-data; name="file"; filename="{file_path.rsplit("/", 1)[-1]}"')
        part.setBodyDevice(f)
        f.setParent(multi)
        multi.append(part)
        version_part = QHttpPart()
        version_part.setHeader(QNetworkRequest.ContentDispositionHeader,
                               'form-data; name="version"')
        version_part.setBody(version.encode())
        multi.append(version_part)
        self._multi = multi  # prevent GC
        req = QNetworkRequest(self._build_url(f"/api/games/{game_id}/saves"))
        reply = self._nam.post(req, multi)
        self._handle_reply(reply,
                           lambda data: self.save_uploaded.emit(data),
                           lambda msg, code: self.error_occurred.emit(msg, code))

    def list_saves(self, game_id: int) -> None:
        req = QNetworkRequest(self._build_url(f"/api/games/{game_id}/saves"))
        reply = self._nam.get(req)
        self._handle_reply(reply,
                           lambda data: self.saves_loaded.emit(data.get("saves", [])),
                           lambda msg, code: self.error_occurred.emit(msg, code))

    def download_save(self, save_id: int, game_id: int) -> None:
        req = QNetworkRequest(self._build_url(f"/api/saves/{save_id}/download"))
        reply = self._nam.get(req)
        def on_ok(data):
            from PySide2.QtWidgets import QFileDialog
            content_disposition = reply.header(QNetworkRequest.ContentDispositionHeader)
            filename = "save.dat"
            if content_disposition:
                match = re.search(r'filename="?([^"]+)"?', content_disposition)
                if match:
                    filename = match.group(1)
            target, _ = QFileDialog.getSaveFileName(
                None, "Save Download Location", filename,
                "All Files (*)"
            )
            if target:
                with open(target, "wb") as f:
                    f.write(reply.readAll())
        def on_err(msg, code):
            self.error_occurred.emit(msg, code)
        self._handle_reply(reply, on_ok, on_err)

    def delete_save(self, save_id: int) -> None:
        req = QNetworkRequest(self._build_url(f"/api/saves/{save_id}"))
        reply = self._nam.deleteResource(req)
        self._handle_reply(reply,
                           lambda _: None,
                           lambda msg, code: self.error_occurred.emit(msg, code))

    def upload_game_save(self, game_id: int, zip_path: str) -> None:
        from PySide2.QtCore import QFile
        from PySide2.QtNetwork import QHttpMultiPart, QHttpPart
        f = QFile(zip_path)
        if not f.open(QFile.ReadOnly):
            self.error_occurred.emit(f"Cannot open zip file: {zip_path}", 0)
            return
        multi = QHttpMultiPart(QHttpMultiPart.FormDataType)
        part = QHttpPart()
        part.setHeader(QNetworkRequest.ContentDispositionHeader,
                       'form-data; name="file"; filename="save.zip"')
        part.setBodyDevice(f)
        f.setParent(multi)
        multi.append(part)
        self._multi = multi  # prevent GC
        req = QNetworkRequest(self._build_url(f"/api/games/{game_id}/save"))
        reply = self._nam.put(req, multi)
        self._handle_reply(reply,
                           lambda data: self.save_upload_completed.emit(game_id),
                           lambda msg, code: self.error_occurred.emit(msg, code))

    def download_game_save(self, game_id: int, local_save_path: str) -> None:
        import json as _json
        req = QNetworkRequest(self._build_url(f"/api/games/{game_id}/save/download"))
        reply = self._nam.get(req)
        def on_finished():
            import zipfile
            import tempfile
            import os
            err = reply.error()
            status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute) or 0
            if err != QNetworkReply.NoError:
                if status == 404:
                    self.error_occurred.emit(tr("error.server_no_saves"), 404)
                else:
                    try:
                        msg = _json.loads(reply.readAll().data().decode()).get("detail", reply.errorString())
                    except Exception:
                        msg = reply.errorString()
                    self.error_occurred.emit(msg, status)
                reply.deleteLater()
                return
            try:
                content = bytes(reply.readAll())
                if not content:
                    self.error_occurred.emit(tr("error.save_file_empty"), 0)
                    reply.deleteLater()
                    return
                tmp_path = tempfile.mktemp(suffix=".zip")
                with open(tmp_path, "wb") as f:
                    f.write(content)
                os.makedirs(local_save_path, exist_ok=True)
                with zipfile.ZipFile(tmp_path, 'r') as zf:
                    zf.extractall(local_save_path)
                os.unlink(tmp_path)
                self.save_downloaded.emit(game_id)
            except Exception as e:
                self.error_occurred.emit(tr("error.unzip_failed", error=e), 0)
            reply.deleteLater()
        reply.finished.connect(on_finished)

    def _build_url(self, path: str) -> QUrl:
        return QUrl(f"{self._base_url}{path}")

    def _handle_reply(self, reply: QNetworkReply, on_success, on_error):
        def on_finished():
            err = reply.error()
            status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute) or 0
            if err != QNetworkReply.NoError:
                try:
                    body = json.loads(reply.readAll().data().decode())
                    msg = body.get("detail", reply.errorString())
                except Exception:
                    msg = reply.errorString()
                on_error(msg, status)
            else:
                try:
                    raw = reply.readAll().data().decode()
                    data = json.loads(raw) if raw else {}
                    on_success(data)
                except json.JSONDecodeError:
                    on_success({})
            reply.deleteLater()
        reply.finished.connect(on_finished)
