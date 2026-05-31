_locale: str = "zh_CN"
_translations: dict[str, str] = {}


def tr(key: str, **kwargs) -> str:
    text = _translations.get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text


def set_locale(locale: str) -> None:
    global _locale, _translations
    _locale = locale
    if locale == "zh_CN":
        from client.i18n.zh_CN import TRANSLATIONS as t
    elif locale == "en_US":
        from client.i18n.en_US import TRANSLATIONS as t
    else:
        from client.i18n.zh_CN import TRANSLATIONS as t
    _translations = t


def get_locale() -> str:
    return _locale


def available_locales() -> list[tuple[str, str]]:
    return [("zh_CN", "中文"), ("en_US", "English")]


def sync_status_label(status_value: str) -> str:
    return tr(f"sync.{status_value}")
