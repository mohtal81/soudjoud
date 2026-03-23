"""
سجود السهو — Soudjoud As-Sahw
Application Kivy/KivyMD
"""

import os
import sys

# ── Dossier racine dans le path ───────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ['KIVY_NO_ENV_CONFIG'] = '1'

from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizable', True)

from kivy.core.text import LabelBase
from kivy.resources import resource_add_path

# ── Police arabe ──────────────────────────────────────────────────────────────
FONTS_DIR = os.path.join(BASE_DIR, 'assets', 'fonts')
os.makedirs(FONTS_DIR, exist_ok=True)

NOTO_REGULAR = os.path.join(FONTS_DIR, 'NotoNaskhArabic-Regular.ttf')
NOTO_BOLD    = os.path.join(FONTS_DIR, 'NotoNaskhArabic-Bold.ttf')

def _download_noto():
    """Télécharge NotoNaskhArabic si absent."""
    import urllib.request
    urls = {
        NOTO_REGULAR: (
            'https://github.com/google/fonts/raw/main/ofl/notonaskharabic/'
            'NotoNaskhArabic%5Bwght%5D.ttf'
        ),
    }
    for dest, url in urls.items():
        if not os.path.isfile(dest) or os.path.getsize(dest) < 1000:
            print(f'[Font] Téléchargement de {os.path.basename(dest)}...')
            try:
                urllib.request.urlretrieve(url, dest)
                print(f'[Font] ✓ {os.path.basename(dest)} téléchargé')
            except Exception as e:
                print(f'[Font] ✗ Échec : {e}')

def _find_font(preferred, fallbacks):
    """Cherche une police dans l'ordre de préférence."""
    for path in [preferred] + fallbacks:
        if os.path.isfile(path) and os.path.getsize(path) > 1000:
            print(f'[Font] Utilisation : {path}')
            return path
    return None

# Essaie de télécharger Noto si absent
if not os.path.isfile(NOTO_REGULAR) or os.path.getsize(NOTO_REGULAR) < 1000:
    _download_noto()

# Cherche la meilleure police disponible
_arabic_font = _find_font(NOTO_REGULAR, [
    NOTO_BOLD,
    os.path.join(FONTS_DIR, 'NotoSansArabic-Regular.ttf'),
    # Polices système Windows avec shaping arabe correct
    r'C:\Windows\Fonts\times.ttf',     # Times New Roman (supporte mieux l'arabe)
    r'C:\Windows\Fonts\tahoma.ttf',
    r'C:\Windows\Fonts\arial.ttf',
    # Linux
    '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf',
    '/usr/share/fonts/truetype/freefont/FreeSerif.ttf',
])

_arabic_bold = _find_font(NOTO_BOLD, [
    NOTO_REGULAR,
    r'C:\Windows\Fonts\timesbd.ttf',
    r'C:\Windows\Fonts\tahomabd.ttf',
    r'C:\Windows\Fonts\arialbd.ttf',
    '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf',
]) or _arabic_font

if not _arabic_font:
    print('[Font] ⚠ Aucune police arabe trouvée — texte peut être mal rendu')
    # Dernier recours : police Kivy par défaut
    _arabic_font = 'Roboto'
    _arabic_bold = 'Roboto'

# ── Enregistrement des polices ────────────────────────────────────────────────
resource_add_path(FONTS_DIR)

if _arabic_font != 'Roboto':
    LabelBase.register(
        name='Arabic',
        fn_regular=_arabic_font,
        fn_bold=_arabic_bold,
    )
    LabelBase.register(
        name='Roboto',
        fn_regular=_arabic_font,
        fn_bold=_arabic_bold,
    )

# ── App ───────────────────────────────────────────────────────────────────────
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window

from screens.home_screen import HomeScreen
from screens.category_screen import CategoryScreen
from screens.schema_screen import SchemaScreen

Builder.load_file(os.path.join(BASE_DIR, 'kv', 'home.kv'))
Builder.load_file(os.path.join(BASE_DIR, 'kv', 'category.kv'))
Builder.load_file(os.path.join(BASE_DIR, 'kv', 'schema.kv'))


class SoudjoudAssahwApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"

        # Tailles de police augmentées
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