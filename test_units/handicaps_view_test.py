# handicaps_view.py
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView

kv = '''
<HandicapsWidget>:
    MDRecycleView:
        id: rv
        viewclass: 'HandicapItemRow'
        data: [{'handicap_name': 'Test ' + str(x), 'stufe': 'Stufe ' + str(x), 'index': x, 'ausgewaehlt': x == 1} for x in range(3)]
        
        RecycleBoxLayout:
            default_size: None, dp(60)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'

<HandicapItemRow>:
    orientation: 'horizontal'
    size_hint_y: None
    height: '60dp'
    md_bg_color: [0.2, 0.2, 0.2, 1] if self.index % 2 == 0 else [0.15, 0.15, 0.15, 1]
    line_color: [1, 0.65, 0, 1] if self.ausgewaehlt else (0, 0, 0, 0)
    padding: '10dp'

    MDLabel:
        text: root.handicap_name
        size_hint_x: 0.3
        color: 1, 1, 1, 1
        
    MDLabel:
        text: root.stufe
        size_hint_x: 0.2
        color: 1, 1, 1, 1
'''

class HandicapItemRow(MDBoxLayout):
    index = NumericProperty(0)
    handicap_name = StringProperty("")
    stufe = StringProperty("")
    ausgewaehlt = BooleanProperty(False)

class HandicapsWidget(MDBoxLayout):
    pass

class TestApp(MDApp):
    def build(self):
        Builder.load_string(kv)
        return HandicapsWidget()

if __name__ == '__main__':
    TestApp().run()