TRANSLATIONS: dict[str, str] = {
    # Main window
    "app.window_title": "游戏云存档",
    "menu.file": "文件(&F)",
    "menu.file.add_game": "添加游戏...",
    "menu.file.exit": "退出",
    "menu.language": "语言(&L)",
    "menu.language.zh_CN": "中文",
    "menu.language.en_US": "English",
    "menu.settings": "设置(&S)",
    "menu.settings.server_config": "服务器配置...",

    # Status bar
    "status.disconnected": "未连接",
    "status.connected": "已连接",
    "status.retrying": "连接失败，{seconds}s 后重试 ({retry_count}/{max_retries})",
    "status.max_retries": "未连接 - 服务器不可用（已达最大重试次数）",
    "status.error_prefix": "错误: {message}",
    "status.server_config_done": "已配置服务器: {host}:{port}",
    "status.connecting": "正在连接 {host}:{port}...",

    # Sync status labels (unified)
    "sync.synced": "已同步",
    "sync.syncing": "同步中",
    "sync.not_synced": "未同步",
    "sync.error": "错误",
    "sync.unknown": "未知",

    # Detail panel
    "detail.default_title": "选择游戏查看详情",
    "detail.no_icon": "暂无图标",
    "detail.loading": "加载中...",
    "detail.change_path": "修改目录",
    "detail.local_path": "本地路径:",
    "detail.game_name": "游戏名称:",
    "detail.last_sync": "上次同步:",
    "detail.no_saves": "暂无存档",
    "detail.save_operations": "存档操作",
    "detail.upload": "上传存档",
    "detail.download": "下载存档",
    "detail.change_icon": "更换图标",
    "detail.delete_game": "删除游戏",
    "detail.upload_success": "存档上传成功",
    "detail.download_complete": "存档下载完成",
    "detail.uploading": "正在上传存档...",
    "detail.downloading": "正在下载存档...",
    "detail.backup_skip": "今日已有备份，跳过备份，正在下载...",
    "detail.backup_created": "已备份到 {backup_name}.zip，正在下载...",
    "detail.path_updated": "存档目录已更新",
    "detail.unknown_name": "未知",
    "detail.change_path_title": "选择新的存档目录",

    # File dialogs
    "dialog.change_icon.title": "选择新图标",
    "dialog.change_icon.filter": "Images (*.png *.jpg *.jpeg *.bmp *.gif)",

    # Error messages
    "error.dialog_title": "错误",
    "error.upload_failed": "上传失败",
    "error.no_save_path": "未设置本地存档路径",
    "error.path_not_exist": "本地存档路径不存在:\n{path}",
    "error.file_too_large": "存档文件过大，无法同步",
    "error.pack_failed": "打包失败: {error}",
    "error.backup_failed": "备份失败: {error}",
    "error.server_no_saves": "服务器上暂无存档",
    "error.save_file_empty": "存档文件为空",
    "error.unzip_failed": "解压失败: {error}",

    # Settings dialog
    "dialog.settings.title": "服务器配置",
    "dialog.settings.description": "配置云存档服务器地址",
    "dialog.settings.host_placeholder": "例如: 127.0.0.1 或 my-server.local",
    "dialog.settings.host_label": "主机地址:",
    "dialog.settings.port_label": "端口:",
    "dialog.settings.language_label": "语言 / Language:",
    "dialog.settings.restart_required": "需要重启应用以应用语言设置",

    # Add game dialog
    "dialog.add_game.title": "添加游戏",
    "dialog.add_game.description": "添加新游戏到云存档列表",
    "dialog.add_game.name_placeholder": "输入游戏名称",
    "dialog.add_game.name_label": "游戏名称:",
    "dialog.add_game.path_placeholder": "选择本地存档文件夹",
    "dialog.add_game.path_label": "本地存档路径:",
    "dialog.add_game.browse": "浏览...",
    "dialog.add_game.icon_preview": "100x200\n图标预览",
    "dialog.add_game.choose_icon": "选择图标...",
    "dialog.add_game.clear_icon": "清除图标",
    "dialog.add_game.validation_required": "请输入游戏名称",
    "dialog.add_game.browse_path_title": "选择本地存档文件夹",
    "dialog.add_game.browse_icon_title": "选择游戏图标",

    # Game list view
    "view.add_game": "添加游戏",
    "view.refresh": "刷新",

    # Delete confirmation
    "dialog.confirm_delete.title": "确认删除",
    "dialog.confirm_delete.message": "确定要删除这个游戏吗？\n存档文件将保留在服务器上。",
}
