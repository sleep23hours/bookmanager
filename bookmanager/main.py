from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex

# ========== 模拟手机屏幕尺寸 ==========
Window.size = (360, 640)


class BookItem(BoxLayout):
    """单本图书的卡片组件"""

    def __init__(self, book_id, title, author, delete_callback, **kwargs):
        super().__init__(**kwargs)
        self.book_id = book_id
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 70
        self.padding = 8
        self.spacing = 10

        # 白色卡片背景
        with self.canvas.before:
            Color(0.98, 0.98, 0.98, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

        # 左侧：书名 + 作者
        info = BoxLayout(orientation='vertical', size_hint_x=0.75)
        info.add_widget(Label(
            text=title,
            font_size='16sp',
            color=(0.1, 0.1, 0.1, 1),
            halign='left',
            valign='middle',
            text_size=(200, None),
            bold=True
        ))
        info.add_widget(Label(
            text=f'作者：{author}',
            font_size='13sp',
            color=(0.4, 0.4, 0.4, 1),
            halign='left',
            text_size=(200, None)
        ))
        self.add_widget(info)

        # 右侧：删除按钮
        del_btn = Button(
            text='删除',
            size_hint_x=0.25,
            background_color=(0.9, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        del_btn.bind(on_press=lambda x: delete_callback(book_id))
        self.add_widget(del_btn)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class BookApp(App):
    """应用主类"""

    def build(self):
        self.store = JsonStore('books.json')
        self.title = '图书管理'

        # 根布局
        root = BoxLayout(orientation='vertical', padding=12, spacing=10)

        # 标题栏
        root.add_widget(Label(
            text='📚 我的图书',
            font_size='22sp',
            color=get_color_from_hex('#1976D2'),
            size_hint_y=None,
            height=50,
            bold=True
        ))

        # 输入区域
        input_box = BoxLayout(orientation='vertical', spacing=6, size_hint_y=None, height=95)
        self.title_input = TextInput(
            hint_text='书名',
            multiline=False,
            background_color=(1, 1, 1, 1),
            padding=(10, 8)
        )
        self.author_input = TextInput(
            hint_text='作者',
            multiline=False,
            background_color=(1, 1, 1, 1),
            padding=(10, 8)
        )
        input_box.add_widget(self.title_input)
        input_box.add_widget(self.author_input)
        root.add_widget(input_box)

        # 添加按钮
        add_btn = Button(
            text='+ 添加图书',
            size_hint_y=None,
            height=48,
            background_color=get_color_from_hex('#4CAF50'),
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        add_btn.bind(on_press=self.add_book)
        root.add_widget(add_btn)

        # 统计信息
        self.stats_label = Label(
            text='共 0 本图书',
            size_hint_y=None,
            height=30,
            color=(0.5, 0.5, 0.5, 1),
            font_size='13sp'
        )
        root.add_widget(self.stats_label)

        # 可滚动图书列表
        scroll = ScrollView()
        self.book_list = GridLayout(cols=1, spacing=8, size_hint_y=None, padding=(0, 5))
        self.book_list.bind(minimum_height=self.book_list.setter('height'))
        scroll.add_widget(self.book_list)
        root.add_widget(scroll)

        self.load_books()
        return root

    def add_book(self, instance):
        """添加图书"""
        title = self.title_input.text.strip()
        author = self.author_input.text.strip()

        if not title or not author:
            self.show_popup('提示', '书名和作者不能为空')
            return

        # 自动生成递增 ID
        keys = [int(k) for k in self.store.keys()]
        new_id = str(max(keys + [0]) + 1)
        self.store.put(new_id, title=title, author=author)

        self.title_input.text = ''
        self.author_input.text = ''
        self.load_books()

    def delete_book(self, book_id):
        """删除图书"""
        if self.store.exists(book_id):
            self.store.delete(book_id)
            self.load_books()

    def load_books(self):
        """加载并渲染图书列表"""
        self.book_list.clear_widgets()
        keys = sorted(self.store.keys(), key=lambda x: int(x))

        for key in keys:
            book = self.store.get(key)
            item = BookItem(
                book_id=key,
                title=book['title'],
                author=book['author'],
                delete_callback=self.delete_book
            )
            self.book_list.add_widget(item)

        self.stats_label.text = f'共 {len(keys)} 本图书'

    def show_popup(self, title, msg):
        """弹出提示框"""
        popup = Popup(
            title=title,
            content=Label(text=msg),
            size_hint=(None, None),
            size=(260, 140),
            auto_dismiss=True
        )
        popup.open()


if __name__ == '__main__':
    BookApp().run()