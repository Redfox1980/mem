
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
from kivy.uix.button import Button

from kivy.config import Config
Config.set('graphics', 'width', '600')   # Breite in Pixel
Config.set('graphics', 'height', '800')  # Höhe in Pixel

import json
import random
import os

class MemoryTrainer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.load_data()
        self.progress = ProgressBar(max=3)
        self.add_widget(self.progress)

        self.display_label = Label(font_size=50, font_name='Roboto')
        self.add_widget(self.display_label)

        self.image_display = Image(size_hint=(1, 0.6))
        self.add_widget(self.image_display)

        self.btn_layout = BoxLayout(size_hint=(1, 0.2))
        self.btn_correct = Button(text='✅ Richtig', on_press=self.mark_correct)
        self.btn_wrong = Button(text='❌ Falsch', on_press=self.mark_wrong)
        self.btn_layout.add_widget(self.btn_correct)
        self.btn_layout.add_widget(self.btn_wrong)
        self.add_widget(self.btn_layout)

        self.fehler_liste = []
        self.next_round()

    def load_data(self):
        with open('data/begriffe.json', 'r', encoding='utf-8') as f:
            self.data = json.load(f)
            random.shuffle(self.data)

    def next_round(self):
        if self.data:
            self.entry = self.data.pop()
            self.countdown = 3
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
        self.progress.value = 3 - self.countdown
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
        return MemoryTrainer()

if __name__ == '__main__':
    MemoryApp().run()
