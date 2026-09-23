import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label

API_KEY = "TA_CLE_SERPER"

class SearchApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.input = TextInput(hint_text="Entrez votre recherche", size_hint_y=None, height=50)
        self.layout.add_widget(self.input)

        btn = Button(text="Rechercher", size_hint_y=None, height=50)
        btn.bind(on_press=self.rechercher)
        self.layout.add_widget(btn)

        self.scroll = ScrollView()
        self.resultats_label = Label(text="", size_hint_y=None, halign='left', valign='top')
        self.resultats_label.bind(texture_size=self.resultats_label.setter('size'))
        self.scroll.add_widget(self.resultats_label)
        self.layout.add_widget(self.scroll)

        return self.layout

    def rechercher(self, instance):
        recherche = self.input.text
        url = "https://google.serper.dev/search"
        headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}
        payload = {"q": recherche}

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            data = response.json()
            resultats = data.get("organic", [])
            texte = ""
            for i, r in enumerate(resultats, start=1):
                texte += f"{i}. {r.get('title','')}\n{r.get('link','')}\n{r.get('snippet','')}\n\n"
            self.resultats_label.text = texte
        except Exception as e:
            self.resultats_label.text = f"Erreur : {e}"

if __name__ == "__main__":
    SearchApp().run()
