"""
سجود السهو — Soudjoud As-Sahw
Application Kivy/KivyMD — version Android-safe
"""

import os
import sys

# ── Dossier racine ────────────────────────────────────────────────────────────
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except Exception:
    BASE_DIR = os.getcwd()

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ['KIVY_NO_ENV_CONFIG'] = '1'

from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizable', True)

from kivy.core.text import LabelBase
from kivy.resources import resource_add_path

# ── Dossier polices ───────────────────────────────────────────────────────────
FONTS_DIR = os.path.join(BASE_DIR, 'assets', 'fonts')
os.makedirs(FONTS_DIR, exist_ok=True)

NOTO_REGULAR = os.path.join(FONTS_DIR, 'NotoNaskhArabic-Regular.ttf')
NOTO_BOLD    = os.path.join(FONTS_DIR, 'NotoNaskhArabic-Bold.ttf')


def _is_valid_font(path):
    """Vérifie qu'un fichier de police existe et est lisible."""
    try:
        return os.path.isfile(path) and os.path.getsize(path) > 1000
    except Exception:
        return False


def _download_noto():
    """
    Télécharge NotoNaskhArabic si absent.
    Silencieux en cas d'échec — ne fait jamais crasher l'app.
    """
    if _is_valid_font(NOTO_REGULAR):
        return
    try:
        import urllib.request
        url = (
            'https://github.com/google/fonts/raw/main/ofl/notonaskharabic/'
            'NotoNaskhArabic%5Bwght%5D.ttf'
        )
        print(f'[Font] Téléchargement NotoNaskhArabic...')
        urllib.request.urlretrieve(url, NOTO_REGULAR)
        print('[Font] ✓ Téléchargé')
    except Exception as e:
        print(f'[Font] ✗ Téléchargement échoué (ignoré) : {e}')


def _find_font(preferred, fallbacks):
    """Retourne la première police valide trouvée, ou None."""
    for path in [preferred] + fallbacks:
        if _is_valid_font(path):
            print(f'[Font] Utilisation : {path}')
            return path
    return None


# Tenter le téléchargement — jamais bloquant
_download_noto()

# Chercher la meilleure police disponible
_arabic_font = _find_font(NOTO_REGULAR, [
    NOTO_BOLD,
    os.path.join(FONTS_DIR, 'NotoSansArabic-Regular.ttf'),
    '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf',
    '/usr/share/fonts/truetype/freefont/FreeSerif.ttf',
])

_arabic_bold = _find_font(NOTO_BOLD, [
    NOTO_REGULAR,
    '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf',
]) or _arabic_font

# ── Enregistrement des polices ────────────────────────────────────────────────
resource_add_path(FONTS_DIR)

if _arabic_font:
    try:
        LabelBase.register(
            name='Arabic',
            fn_regular=_arabic_font,
            fn_bold=_arabic_bold or _arabic_font,
        )
        LabelBase.register(
            name='Roboto',
            fn_regular=_arabic_font,
            fn_bold=_arabic_bold or _arabic_font,
        )
        print('[Font] Polices enregistrées OK')
    except Exception as e:
        print(f'[Font] Enregistrement échoué (ignoré) : {e}')
else:
    print('[Font] ⚠ Aucune police arabe — utilisation police par défaut')

# ── Imports app ───────────────────────────────────────────────────────────────
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window

# Import screens avec gestion d'erreur explicite
try:
    from screens.home_screen import HomeScreen
    from screens.category_screen import CategoryScreen
    from screens.schema_screen import SchemaScreen
except ImportError as e:
    print(f'[ERREUR CRITIQUE] Import screens échoué : {e}')
    print('[INFO] Vérifiez que screens/__init__.py existe')
    raise

# Chargement des fichiers .kv
for kv_name in ['home', 'category', 'schema']:
    kv_path = os.path.join(BASE_DIR, 'kv', f'{kv_name}.kv')
    if os.path.isfile(kv_path):
        Builder.load_file(kv_path)
        print(f'[KV] {kv_name}.kv chargé OK')
    else:
        print(f'[KV] ⚠ {kv_path} introuvable — ignoré')


class SoudjoudAssahwApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"

        self.theme_cls.font_styles.update({
            "H3":        ["Arabic", 48,  True,  -0.5],
            "H4":        ["Arabic", 38,  True,  -0.5],
            "H5":        ["Arabic", 30,  True,   0  ],
            "H6":        ["Arabic", 24,  True,   0.1],
            "Subtitle1": ["Arabic", 19,  False,  0.1],
            "Subtitle2": ["Arabic", 17,  True,   0.1],
            "Body1":     ["Arabic", 17,  False,  0.3],
            "Body2":     ["Arabic", 15,  False,  0.2],
            "Button":    ["Arabic", 16,  True,   1.0],
            "Caption":   ["Arabic", 14,  False,  0.3],
            "Overline":  ["Arabic", 12,  True,   1.2],
        })

        Window.clearcolor = (0.04, 0.08, 0.18, 1)

        from kivy.uix.screenmanager import ScreenManager, SlideTransition
        self.sm = ScreenManager(transition=SlideTransition())
        self.sm.add_widget(HomeScreen(name='home'))
        return self.sm

    def go_to_category(self, category_id, is_arabic):
        if self.sm.has_screen('category'):
            self.sm.remove_widget(self.sm.get_screen('category'))
        self.sm.add_widget(CategoryScreen(
            name='category',
            category_id=category_id,
            is_arabic=is_arabic,
        ))
        self.sm.current = 'category'

    def go_to_schema(self, is_arabic):
        if self.sm.has_screen('schema'):
            self.sm.remove_widget(self.sm.get_screen('schema'))
        self.sm.add_widget(SchemaScreen(name='schema', is_arabic=is_arabic))
        self.sm.current = 'schema'

    def go_back(self):
        self.sm.current = 'home'


if __name__ == '__main__':
    SoudjoudAssahwApp().run()
