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

API_KEY = "cb82eddf65495d4b252eee713b7fec3db44ef74d"

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
            spacing=dp(10)
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
            height=dp(60)
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
        # BOUTON RECHERCHE
        # ----------------------------------------------------

        btn_search = Button(
            text="RECHERCHER",
            size_hint_y=None,
            height=dp(52),
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
        # INFORMATIONS RESULTATS
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

        self.resultats_info.text_size = (
            None,
            dp(35)
        )

        root.add_widget(
            self.resultats_info
        )

        # ----------------------------------------------------
        # SCROLL DES RESULTATS
        # ----------------------------------------------------

        self.scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8),
            scroll_type=["bars", "content"]
        )

        self.resultats_box = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=[
                dp(3),
                dp(3),
                dp(3),
                dp(10)
            ],
            size_hint_y=None
        )

        self.resultats_box.bind(
            minimum_height=self.resultats_box.setter(
                "height"
            )
        )

        self.scroll.add_widget(
            self.resultats_box
        )

        root.add_widget(
            self.scroll
        )

        # ----------------------------------------------------
        # EXPORT EXCEL
        # ----------------------------------------------------

        self.btn_excel = Button(
            text="EXPORTER LES RÉSULTATS VERS EXCEL",
            size_hint_y=None,
            height=dp(55),
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
    # RECHERCHE
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
                    f"{response.text[:500]}"
                )

                return

            data = response.json()

            self.resultats = data.get(
                "organic",
                []
            )

            if not self.resultats:

                self.btn_excel.disabled = True

                self.afficher_message(
                    "Aucun résultat trouvé."
                )

                return

            self.afficher_resultats()

            self.btn_excel.disabled = False

        except Exception as e:

            self.afficher_message(
                "Erreur pendant la recherche :\n\n"
                + str(e)
            )
    # ========================================================
    # AFFICHAGE RESULTATS
    # ========================================================

    def afficher_resultats(self):

        self.resultats_box.clear_widgets()

        nombre = len(self.resultats)

        self.resultats_info.text = (
            f"Résultats trouvés : {nombre}"
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
            # BLOC RESULTAT
            # ------------------------------------------------

            bloc = BorderedBox(
                orientation="vertical",
                padding=[
                    dp(12),
                    dp(10),
                    dp(12),
                    dp(10)
                ],
                spacing=dp(6),
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

            label_url = Label(
                text=lien,
                color=GREY,
                font_size=dp(12),
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

            def mettre_a_jour_largeur(
                widget,
                largeur
            ):

                widget.text_size = (
                    max(1, largeur - dp(24)),
                    None
                )

            # ------------------------------------------------
            # HAUTEUR AUTOMATIQUE DES TEXTES
            # ------------------------------------------------

            def mettre_a_jour_hauteur(
                widget,
                texture_size
            ):

                widget.height = (
                    texture_size[1]
                    + dp(2)
                )

            # ------------------------------------------------
            # LIENS
            # ------------------------------------------------

            label_titre.bind(
                texture_size=mettre_a_jour_hauteur
            )

            label_url.bind(
                texture_size=mettre_a_jour_hauteur
            )

            label_description.bind(
                texture_size=mettre_a_jour_hauteur
            )

            # ------------------------------------------------
            # AJOUT DES LABELS
            # ------------------------------------------------

            bloc.add_widget(
                label_titre
            )

            bloc.add_widget(
                label_url
            )

            bloc.add_widget(
                label_description
            )

            # ------------------------------------------------
            # HAUTEUR DU BLOC
            # ------------------------------------------------

            def mettre_a_jour_bloc(
                instance,
                size
            ):

                bloc.height = (
                    label_titre.height
                    + label_url.height
                    + label_description.height
                    + dp(32)
                )

            bloc.bind(
                size=mettre_a_jour_bloc
            )

            # ------------------------------------------------
            # LARGEUR DES TEXTES SELON LE BLOC
            # ------------------------------------------------

            def ajuster_textes(
                instance,
                size
            ):

                largeur = (
                    instance.width
                    - dp(24)
                )

                label_titre.text_size = (
                    max(1, largeur),
                    None
                )

                label_url.text_size = (
                    max(1, largeur),
                    None
                )

                label_description.text_size = (
                    max(1, largeur),
                    None
                )

            bloc.bind(
                size=ajuster_textes
            )

            # ------------------------------------------------
            # AJOUT AU SCROLL
            # ------------------------------------------------

            self.resultats_box.add_widget(
                bloc
            )

        # ----------------------------------------------------
        # REVENIR EN HAUT
        # ----------------------------------------------------

        self.scroll.scroll_y = 1

    # ========================================================
    # MESSAGE
    # ========================================================

    def afficher_message(self, message):

        self.resultats_box.clear_widgets()

        self.resultats_info.text = (
            "Résultats de recherche"
        )

        label = Label(
            text=message,
            color=BLACK,
            font_size=dp(17),
            halign="center",
            valign="middle",
            size_hint_y=None
        )

        label.text_size = (
            self.scroll.width - dp(30),
            None
        )

        label.height = (
            label.texture_size[1]
            + dp(30)
        )

        self.resultats_box.add_widget(
            label
        )

    # ========================================================
    # EXPORT EXCEL
    # ========================================================

    def exporter_excel(self, instance):

        if not self.resultats:

            self.afficher_message(
                "Aucun résultat à exporter."
            )

            return

        try:

            workbook = Workbook()

            sheet = workbook.active

            sheet.title = "Résultats"

            sheet.append([
                "N°",
                "Titre",
                "URL",
                "Description"
            ])

            for i, resultat in enumerate(
                self.resultats,
                start=1
            ):

                sheet.append([
                    i,
                    resultat.get(
                        "title",
                        ""
                    ),
                    resultat.get(
                        "link",
                        ""
                    ),
                    resultat.get(
                        "snippet",
                        ""
                    )
                ])

            sheet.column_dimensions[
                "A"
            ].width = 8

            sheet.column_dimensions[
                "B"
            ].width = 45

            sheet.column_dimensions[
                "C"
            ].width = 70

            sheet.column_dimensions[
                "D"
            ].width = 90

            dossier = os.path.join(
                self.user_data_dir,
                "exports"
            )

            os.makedirs(
                dossier,
                exist_ok=True
            )

            fichier = os.path.join(
                dossier,
                "resultats_google.xlsx"
            )

            workbook.save(
                fichier
            )

            self.afficher_message(
                "Export Excel réussi !\n\n"
                f"Fichier enregistré :\n\n"
                f"{fichier}"
            )

        except Exception as e:

            self.afficher_message(
                "Erreur lors de l'export Excel :\n\n"
                + str(e)
            )


# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":
    SearchApp().run()
