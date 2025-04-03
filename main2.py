from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import json
import random

from kivy.config import Config
Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '700')

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_mode = 'random'
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Bereichsauswahl oben
        self.range_label = Label(text="Zahlenbereich auswählen (optional)", font_size=24)
        self.layout.add_widget(self.range_label)

        range_layout = BoxLayout(size_hint=(1, 0.25), spacing=10)
        self.range_start = TextInput(hint_text='von', input_filter='int', font_size=22, size_hint_y=1, text='0')
        self.range_end = TextInput(hint_text='bis', input_filter='int', font_size=22, size_hint_y=1, text='1000')
        range_layout.add_widget(self.range_start)
        range_layout.add_widget(self.range_end)
        self.layout.add_widget(range_layout)

        # Reihenfolgeauswahl
        self.info = Label(text="Reihenfolge wählen", font_size=24)
        self.layout.add_widget(self.info)

        self.random_btn = Button(text="Zufällig", on_press=self.set_random, font_size=22, size_hint_y=0.2)
        self.asc_btn = Button(text="Aufsteigend", on_press=self.set_ascending, font_size=22, size_hint_y=0.2)
        self.desc_btn = Button(text="Absteigend", on_press=self.set_descending, font_size=22, size_hint_y=0.2)

        self.layout.add_widget(self.random_btn)
        self.layout.add_widget(self.asc_btn)
        self.layout.add_widget(self.desc_btn)

        # Zeitangabe
        self.time_label = Label(text="Countdown-Zeit pro Begriff (in Sekunden)", font_size=24)
        self.layout.add_widget(self.time_label)

        self.time_input = TextInput(
            hint_text="z.B. 10", 
            input_filter='int', 
            multiline=False, 
            font_size=24,
            size_hint=(1, 0.25),
            text="2"
        )
        self.layout.add_widget(self.time_input)

        # Startbutton
        self.start_btn = Button(text="▶️ Start", size_hint=(1, 0.3), font_size=28)
        self.start_btn.bind(on_press=self.start_training)
        self.layout.add_widget(self.start_btn)

        self.add_widget(self.layout)

    def set_random(self, instance):
        self.selected_mode = 'random'
        self.info.text = "Reihenfolge: Zufällig"

    def set_ascending(self, instance):
        self.selected_mode = 'ascending'
        self.info.text = "Reihenfolge: Aufsteigend"

    def set_descending(self, instance):
        self.selected_mode = 'descending'
        self.info.text = "Reihenfolge: Absteigend"

    def start_training(self, instance):
        countdown_time = self.time_input.text
        if not countdown_time.isdigit():
            self.info.text = "Bitte gültige Zeit eingeben!"
            return
        countdown = int(countdown_time)

        start = self.range_start.text
        end = self.range_end.text
        if start and end and start.isdigit() and end.isdigit():
            start = int(start)
            end = int(end)
        else:
            start = None
            end = None

        trainer_screen = self.manager.get_screen('trainer')
        trainer_screen.setup(self.selected_mode, countdown, start, end)
        self.manager.current = 'trainer'

class TrainerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.progress = ProgressBar(max=10)
        self.layout.add_widget(self.progress)

        self.display_label = Label(font_size=50, font_name='Roboto')
        self.layout.add_widget(self.display_label)

        self.image_display = Image(size_hint=(1, 0.6))
        self.layout.add_widget(self.image_display)

        self.btn_layout = BoxLayout(size_hint=(1, 0.2))
        self.btn_correct = Button(text='✅ Richtig', on_press=self.mark_correct, font_size=24)
        self.btn_wrong = Button(text='❌ Falsch', on_press=self.mark_wrong, font_size=24)
        self.btn_layout.add_widget(self.btn_correct)
        self.btn_layout.add_widget(self.btn_wrong)
        self.layout.add_widget(self.btn_layout)

        self.add_widget(self.layout)

    def setup(self, mode, countdown, start, end):
        with open('data/begriffe.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Bereich filtern
        if start is not None and end is not None:
            data = [d for d in data if int(d['id']) >= start and int(d['id']) <= end]

        # Sortierung anwenden
        if mode == 'random':
            random.shuffle(data)
        elif mode == 'ascending':
            data.sort(key=lambda x: int(x['id']))
        elif mode == 'descending':
            data.sort(key=lambda x: int(x['id']), reverse=True)

        self.data = data
        self.countdown_time = countdown
        self.fehler_liste = []
        self.next_round()

    def next_round(self):
        if self.data:
            self.entry = self.data.pop(0)
            self.countdown = self.countdown_time
            self.display_label.text = f"Zahl: {self.entry['id']}"
            self.image_display.source = ""
            Clock.schedule_interval(self.update_progress, 1)
        else:
            self.display_label.text = "Fertig!"
            self.image_display.source = ""
            self.btn_layout.disabled = True
            self.save_fehler()

    def update_progress(self, dt):
        self.countdown -= 1
        self.progress.value = self.countdown_time - self.countdown
        if self.countdown <= 0:
            Clock.unschedule(self.update_progress)
            self.show_solution()

    def show_solution(self):
        self.display_label.text = f"{self.entry['begriff']}"
        self.image_display.source = self.entry['bild']

    def mark_correct(self, instance):
        self.next_round()

    def mark_wrong(self, instance):
        self.fehler_liste.append(self.entry)
        self.next_round()

    def save_fehler(self):
        with open('fehler.json', 'w', encoding='utf-8') as f:
            json.dump(self.fehler_liste, f, indent=4, ensure_ascii=False)

class MemoryApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(TrainerScreen(name='trainer'))
        return sm

if __name__ == '__main__':
    MemoryApp().run()
