import os
import requests

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Line, RoundedRectangle

from openpyxl import Workbook


# ============================================================
# CONFIGURATION
# ============================================================

API_KEY = "88e3203983def48b718621901e3ee9986537f903cb82eddf65495d4b252eee713b7fec3db44ef74d"

ORANGE = (1.0, 0.45, 0.0, 1)
BLACK = (0, 0, 0, 1)
WHITE = (1, 1, 1, 1)
LIGHT_ORANGE = (1.0, 0.92, 0.82, 1)
GREY = (0.35, 0.35, 0.35, 1)


# ============================================================
# WIDGET AVEC CONTOUR
# ============================================================

class BorderedBox(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:

            Color(*WHITE)

            self.background = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]
            )

            Color(*BLACK)

            self.border = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dp(10)
                ),
                width=1.2
            )

        self.bind(
            pos=self.update_graphics,
            size=self.update_graphics
        )

    def update_graphics(self, *args):

        self.background.pos = self.pos
        self.background.size = self.size

        self.border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(10)
        )


# ============================================================
# APPLICATION
# ============================================================

class SearchApp(App):

    def build(self):

        Window.clearcolor = WHITE

        self.resultats = []

        # ----------------------------------------------------
        # CONTENEUR PRINCIPAL
        # ----------------------------------------------------

        root = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(12)
        )

        # ----------------------------------------------------
        # TITRE
        # ----------------------------------------------------

        titre = Label(
            text="[b]GOOGLE SCRAPER[/b]",
            markup=True,
            font_size=dp(25),
            color=BLACK,
            size_hint_y=None,
            height=dp(45)
        )

        root.add_widget(titre)

        # ----------------------------------------------------
        # CHAMP DE RECHERCHE
        # ----------------------------------------------------

        search_box = BorderedBox(
            orientation="horizontal",
            padding=dp(4),
            size_hint_y=None,
            height=dp(62)
        )

        self.input = TextInput(
            hint_text="Entrez votre recherche...",
            multiline=False,
            font_size=dp(18),
            foreground_color=BLACK,
            hint_text_color=GREY,
            background_color=WHITE,
            cursor_color=ORANGE,
            padding=[dp(12), dp(15)]
        )

        search_box.add_widget(self.input)

        root.add_widget(search_box)

        # ----------------------------------------------------
        # BOUTON RECHERCHER
        # ----------------------------------------------------

        btn_search = Button(
            text="🔎  RECHERCHER",
            size_hint_y=None,
            height=dp(55),
            font_size=dp(17),
            bold=True,
            color=WHITE,
            background_normal="",
            background_color=ORANGE
        )

        btn_search.bind(
            on_press=self.rechercher
        )

        root.add_widget(btn_search)

        # ----------------------------------------------------
        # EN-TÊTE DES RÉSULTATS
        # ----------------------------------------------------

        self.resultats_info = Label(
            text="Résultats de recherche",
            color=BLACK,
            font_size=dp(15),
            bold=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(35)
        )

        self.resultats_info.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        root.add_widget(
            self.resultats_info
        )

        # ----------------------------------------------------
        # ZONE SCROLLABLE DES RÉSULTATS
        # ----------------------------------------------------

        self.scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8),
            scroll_type=["bars", "content"]
        )

        self.resultats_box = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None,
            padding=[
                dp(3),
                dp(5),
                dp(3),
                dp(10)
            ]
        )

        self.resultats_box.bind(
            minimum_height=
            self.resultats_box.setter("height")
        )

        self.scroll.add_widget(
            self.resultats_box
        )

        root.add_widget(
            self.scroll
        )

        # ----------------------------------------------------
        # BOUTON EXPORT EXCEL
        # ----------------------------------------------------

        self.btn_excel = Button(
            text="📊  EXPORTER LES RÉSULTATS VERS EXCEL",
            size_hint_y=None,
            height=dp(58),
            font_size=dp(15),
            bold=True,
            color=BLACK,
            background_normal="",
            background_color=LIGHT_ORANGE,
            disabled=True
        )

        self.btn_excel.bind(
            on_press=self.exporter_excel
        )

        root.add_widget(
            self.btn_excel
        )

        return root

    # ========================================================
    # RECHERCHE SERPER
    # ========================================================

    def rechercher(self, instance):

        recherche = self.input.text.strip()

        if not recherche:

            self.afficher_message(
                "Veuillez saisir une recherche."
            )

            return

        self.afficher_message(
            "Recherche en cours..."
        )

        url = "https://google.serper.dev/search"

        headers = {
            "X-API-KEY": API_KEY,
            "Content-Type": "application/json"
        }

        payload = {
            "q": recherche
        }

        try:

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=15
            )

            if response.status_code != 200:

                self.afficher_message(
                    f"Erreur API HTTP "
                    f"{response.status_code}\n\n"
                    f"{response.text[:1000]}"
                )

                return

            data = response.json()

            self.resultats = data.get(
                "organic",
                []
            )

            if not self.resultats:

                self.afficher_message(
                    "Aucun résultat trouvé."
                )

                self.btn_excel.disabled = True

                return

            self.afficher_resultats()

            self.btn_excel.disabled = False

        except Exception as e:

            self.afficher_message(
                "Erreur pendant la recherche :\n\n"
                + str(e)
            )

    # ========================================================
    # AFFICHAGE DES RESULTATS
    # ========================================================

    def afficher_resultats(self):

        self.resultats_box.clear_widgets()

        nombre = len(self.resultats)

        self.resultats_info.text = (
            f"Résultats : {nombre}    "
            f"|    Faites défiler pour parcourir les résultats"
        )

        for i, resultat in enumerate(
            self.resultats,
            start=1
        ):

            titre = resultat.get(
                "title",
                "Sans titre"
            )

            lien = resultat.get(
                "link",
                ""
            )

            description = resultat.get(
                "snippet",
                ""
            )

            # ------------------------------------------------
            # BLOC DU RESULTAT
            # ------------------------------------------------

            bloc = BorderedBox(
                orientation="vertical",
                padding=[
                    dp(12),
                    dp(10),
                    dp(12),
                    dp(10)
                ],
                spacing=dp(7),
                size_hint_y=None
            )

            # ------------------------------------------------
            # TITRE
            # ------------------------------------------------

            label_titre = Label(
                text=f"[b]{i}. {titre}[/b]",
                markup=True,
                color=BLACK,
                font_size=dp(16),
                halign="left",
                valign="top",
                size_hint_y=None
            )

            # ------------------------------------------------
            # URL
            # ------------------------------------------------

            label_lien = Label(
                text=f"[color=666666]{lien}[/color]",
                markup=True,
                color=GREY,
                font_size=dp(13),
                halign="left",
                valign="top",
                size_hint_y=None
            )

            # ------------------------------------------------
            # DESCRIPTION
            # ------------------------------------------------

            label_description = Label(
                text=description,
                color=BLACK,
                font_size=dp(14),
                halign="left",
                valign="top",
                size_hint_y=None
            )

            # ------------------------------------------------
            # LARGEUR DES TEXTES
            # ------------------------------------------------

            def ajuster_largeur(instance, width):

                largeur = max(
                    dp(100),
                    width - dp(30)
                )

                label_titre.text_size = (
                    largeur,
                    None
                )

                label_lien.text_size = (
                    largeur,
                    None
                )

                label_description.text_size = (
                    largeur,
                    None
                )

                self.maj_
