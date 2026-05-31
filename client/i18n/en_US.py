TRANSLATIONS: dict[str, str] = {
    # Main window
    "app.window_title": "Game Save Cloud",
    "menu.file": "File(&F)",
    "menu.file.add_game": "Add Game...",
    "menu.file.exit": "Exit",
    "menu.language": "Language(&L)",
    "menu.language.zh_CN": "中文",
    "menu.language.en_US": "English",
    "menu.settings": "Settings(&S)",
    "menu.settings.server_config": "Server Configuration...",

    # Status bar
    "status.disconnected": "Disconnected",
    "status.connected": "Connected",
    "status.retrying": "Connection failed, retrying in {seconds}s ({retry_count}/{max_retries})",
    "status.max_retries": "Disconnected - Server unavailable (max retries reached)",
    "status.error_prefix": "Error: {message}",
    "status.server_config_done": "Server configured: {host}:{port}",
    "status.connecting": "Connecting to {host}:{port}...",

    # Sync status labels (unified)
    "sync.synced": "Synced",
    "sync.syncing": "Syncing",
    "sync.not_synced": "Not Synced",
    "sync.error": "Error",
    "sync.unknown": "Unknown",

    # Detail panel
    "detail.default_title": "Select a game to view details",
    "detail.no_icon": "No Icon",
    "detail.loading": "Loading...",
    "detail.change_path": "Change Path",
    "detail.local_path": "Local Path:",
    "detail.game_name": "Game Name:",
    "detail.last_sync": "Last Sync:",
    "detail.no_saves": "No Saves",
    "detail.save_operations": "Save Operations",
    "detail.upload": "Upload Save",
    "detail.download": "Download Save",
    "detail.change_icon": "Change Icon",
    "detail.delete_game": "Delete Game",
    "detail.upload_success": "Save uploaded successfully",
    "detail.download_complete": "Save download complete",
    "detail.uploading": "Uploading save...",
    "detail.downloading": "Downloading save...",
    "detail.backup_skip": "Backup exists for today, skipping backup...",
    "detail.backup_created": "Backed up to {backup_name}.zip, downloading...",
    "detail.path_updated": "Save directory updated",
    "detail.unknown_name": "Unknown",
    "detail.change_path_title": "Select new save directory",

    # File dialogs
    "dialog.change_icon.title": "Select New Icon",
    "dialog.change_icon.filter": "Images (*.png *.jpg *.jpeg *.bmp *.gif)",

    # Error messages
    "error.dialog_title": "Error",
    "error.upload_failed": "Upload Failed",
    "error.no_save_path": "Local save path not set",
    "error.path_not_exist": "Local save path does not exist:\n{path}",
    "error.file_too_large": "Save file is too large to sync",
    "error.pack_failed": "Packaging failed: {error}",
    "error.backup_failed": "Backup failed: {error}",
    "error.server_no_saves": "No saves on server",
    "error.save_file_empty": "Save file is empty",
    "error.unzip_failed": "Extraction failed: {error}",

    # Settings dialog
    "dialog.settings.title": "Server Configuration",
    "dialog.settings.description": "Configure cloud save server address",
    "dialog.settings.host_placeholder": "e.g. 127.0.0.1 or my-server.local",
    "dialog.settings.host_label": "Host Address:",
    "dialog.settings.port_label": "Port:",
    "dialog.settings.language_label": "Language / 语言:",
    "dialog.settings.restart_required": "Restart required to apply language change",

    # Add game dialog
    "dialog.add_game.title": "Add Game",
    "dialog.add_game.description": "Add a new game to the cloud save list",
    "dialog.add_game.name_placeholder": "Enter game name",
    "dialog.add_game.name_label": "Game Name:",
    "dialog.add_game.path_placeholder": "Select local save folder",
    "dialog.add_game.path_label": "Local Save Path:",
    "dialog.add_game.browse": "Browse...",
    "dialog.add_game.icon_preview": "100x200\nIcon Preview",
    "dialog.add_game.choose_icon": "Choose Icon...",
    "dialog.add_game.clear_icon": "Clear Icon",
    "dialog.add_game.validation_required": "Please enter a game name",
    "dialog.add_game.browse_path_title": "Select Local Save Folder",
    "dialog.add_game.browse_icon_title": "Select Game Icon",

    # Game list view
    "view.add_game": "Add Game",
    "view.refresh": "Refresh",

    # Delete confirmation
    "dialog.confirm_delete.title": "Confirm Deletion",
    "dialog.confirm_delete.message": "Are you sure you want to delete this game?\nSave files will remain on the server.",
}
