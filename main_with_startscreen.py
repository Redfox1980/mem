
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
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        self.info = Label(text="Reihenfolge wählen und Zeit eingeben", font_size=32)
        layout.add_widget(self.info)

        self.random_btn = Button(text="Zufällige Reihenfolge", on_press=self.set_random)
        self.asc_btn = Button(text="Aufsteigend", on_press=self.set_ascending)
        self.desc_btn = Button(text="Absteigend", on_press=self.set_descending)
        self.range_btn = Button(text="Bereich auswählen", on_press=self.set_range)

        layout.add_widget(self.random_btn)
        layout.add_widget(self.asc_btn)
        layout.add_widget(self.desc_btn)

        range_layout = BoxLayout(size_hint=(1, 0.2))
        self.range_start = TextInput(hint_text='von', input_filter='int')
        self.range_end = TextInput(hint_text='bis', input_filter='int')
        range_layout.add_widget(self.range_start)
        range_layout.add_widget(self.range_end)
        layout.add_widget(range_layout)
        layout.add_widget(self.range_btn)

        self.time_input = TextInput(hint_text="Countdown in Sekunden", input_filter='int', multiline=False, size_hint=(1, 0.3))
        layout.add_widget(self.time_input)

        self.add_widget(layout)

    def set_random(self, instance):
        self.start_training('random')

    def set_ascending(self, instance):
        self.start_training('ascending')

    def set_descending(self, instance):
        self.start_training('descending')

    def set_range(self, instance):
        self.start_training('range')

    def start_training(self, mode):
        countdown_time = self.time_input.text
        if not countdown_time.isdigit():
            self.info.text = "Bitte eine gültige Countdown-Zeit eingeben!"
            return
        countdown = int(countdown_time)

        start = self.range_start.text
        end = self.range_end.text
        if mode == 'range':
            if not (start.isdigit() and end.isdigit()):
                self.info.text = "Bitte gültigen Bereich eingeben!"
                return
            start, end = int(start), int(end)
        else:
            start = end = None

        trainer_screen = self.manager.get_screen('trainer')
        trainer_screen.setup(mode, countdown, start, end)
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
        self.btn_correct = Button(text='✅ Richtig', on_press=self.mark_correct)
        self.btn_wrong = Button(text='❌ Falsch', on_press=self.mark_wrong)
        self.btn_layout.add_widget(self.btn_correct)
        self.btn_layout.add_widget(self.btn_wrong)
        self.layout.add_widget(self.btn_layout)

        self.add_widget(self.layout)

    def setup(self, mode, countdown, start, end):
        with open('data/begriffe.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        if mode == 'random':
            random.shuffle(data)
        elif mode == 'ascending':
            data.sort(key=lambda x: int(x['id']))
        elif mode == 'descending':
            data.sort(key=lambda x: int(x['id']), reverse=True)
        elif mode == 'range':
            data = [d for d in data if int(d['id']) >= start and int(d['id']) <= end]

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
