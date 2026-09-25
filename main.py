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

API_KEY = "88e3203983def48b718621901e3ee9986537f903"

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

        btn_search.bind(on_press=self.rechercher)

        root.add_widget(btn_search)

        # ----------------------------------------------------
        # ZONE DES RESULTATS
        # ----------------------------------------------------

        self.scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )

        self.resultats_box = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            padding=[dp(3), dp(3)]
        )

        self.resultats_box.bind(
            minimum_height=self.resultats_box.setter("height")
        )

        self.scroll.add_widget(self.resultats_box)

        root.add_widget(self.scroll)

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

        self.btn_excel.bind(on_press=self.exporter_excel)

        root.add_widget(self.btn_excel)

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
                    f"Erreur API HTTP {response.status_code}\n\n"
                    f"{response.text[:1000]}"
                )

                return

            data = response.json()

            self.resultats = data.get("organic", [])

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

            bloc = BorderedBox(
                orientation="vertical",
                padding=dp(12),
                spacing=dp(6),
                size_hint_y=None
            )

            label = Label(
                text=(
                    f"[b]{i}. {titre}[/b]\n\n"
                    f"[color=666666]{lien}[/color]\n\n"
                    f"{description}"
                ),
                markup=True,
                color=BLACK,
                font_size=dp(15),
                halign="left",
                valign="top",
                size_hint_y=None
            )

            # Largeur dynamique pour le retour à la ligne
            label.text_size = (
                self.scroll.width - dp(35),
                None
            )

            label.bind(
                texture_size=lambda instance, value:
                setattr(
                    instance,
                    "height",
                    value[1] + dp(10)
                )
            )

            bloc.add_widget(label)

            # hauteur du bloc
            bloc.height = dp(130)

            self.resultats_box.add_widget(bloc)

    # ========================================================
    # MESSAGE
    # ========================================================

    def afficher_message(self, message):

        self.resultats_box.clear_widgets()

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

        label.bind(
            texture_size=lambda instance, value:
            setattr(
                instance,
                "height",
                value[1] + dp(30)
            )
        )

        self.resultats_box.add_widget(label)

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

            # En-têtes
            sheet.append([
                "N°",
                "Titre",
                "URL",
                "Description"
            ])

            # Résultats
            for i, resultat in enumerate(
                self.resultats,
                start=1
            ):

                sheet.append([
                    i,
                    resultat.get("title", ""),
                    resultat.get("link", ""),
                    resultat.get("snippet", "")
                ])

            # Ajustement des colonnes
            sheet.column_dimensions["A"].width = 8
            sheet.column_dimensions["B"].width = 45
            sheet.column_dimensions["C"].width = 70
            sheet.column_dimensions["D"].width = 90

            # Chemin local de l'application
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

            workbook.save(fichier)

            self.afficher_message(
                "✅ Export Excel réussi !\n\n"
                f"Fichier enregistré localement :\n\n"
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
