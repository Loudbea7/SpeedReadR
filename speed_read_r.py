import os
import sys
import more_itertools

if sys.__stdout__ is None or sys.__stderr__ is None:
    os.environ['KIVY_NO_CONSOLELOG'] = '1'

import time
import mimetypes
import hashlib
import webbrowser
import ast
from pathlib import Path
from typing import Union
from threading import Thread
from wakepy import keep

from kivymd.app import MDApp
from kivy.factory import Factory as F
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock, mainthread
from kivy.config import Config
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.behaviors.toggle_behavior import MDToggleButton
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.button import MDRectangleFlatIconButton
from kivymd.uix.pickers import MDColorPicker
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.filemanager import MDFileManager

from database.text_parser import Parsex
from database.utils import create_db_and_tables, clear_database, create_settings_text, create_readme, create_path
from database.dao.settings_dao import SettingsDAO
from database.dao.active_dao import ActiveDAO
from database.dao.theme_dao import ThemeDAO
from database.dao.bookshelf_dao import BookshelfDAO

# clear_database() # Warning! Database will be wiped!
create_db_and_tables()

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

BASE_PATH = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

class BookListLabel(MDLabel):
    pass

class BookButton(MDRectangleFlatIconButton):
    pass

class BookButtonDelete(MDRectangleFlatIconButton):
    pass

class ContentNavigationDrawer(MDScrollView):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()
    pass

class MDNavigationDrawer2(MDNavigationDrawer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class MyToggleButton(MDRectangleFlatButton, MDToggleButton):
    pass

class RootScreen(F.Screen):
    pass

class SettingsScreen(F.Screen):
    pass

class ReaderScreen(F.Screen):
    pass

class BooksScreen(F.Screen):
    pass

class ClipScreen(F.Screen):
    pass

class DonationsScreen(F.Screen):
    pass

class ThemesScreen(F.Screen):
    pass


# kv = "speed_read.kv"
# Builder.load_file(kv)

''' Build main app '''
class Speed_Read_RApp(MDApp):    
    def build(self):
        self.icon = "assets/64x64.png"
        
        config_files = os.scandir(path="config/")
        if not "settings.txt" in config_files:
            try:
                create_settings_text()
            except:
                self.snack(self, "Error: Could not create settings file")
        
        self.create_settings()
        
        self.root_screen = RootScreen()
        
        # Playing reader
        self.play = False
        
        # Playing settings
        self.play_sett = False

        # Milisecond times
        self.timed = {}

        # Currently posting settings
        self.posting = False

        # The bookshelf only loads when is not loaded (first time open)
        # and when button reload is clicked
        self.bookshelf_loaded = False

        # screen cleans only if a book has been loaded
        self.book_loaded = False

        # list of words of the opened book
        self.word_index = ""

        # Check if double click command comes twice and filter one.
        self.old_index = None

        self.screen_manager = self.root_screen.screen_manager
        self.settings_screen = SettingsScreen(name="sett")
        self.reader_screen = ReaderScreen(name="reader")
        self.books_screen = BooksScreen(name="books")
        self.clipboard_screen = ClipScreen(name="clipboard")
        self.donations_screen = DonationsScreen(name="donations")
        self.themes_screen = ThemesScreen(name="themes")
        
        properties = [
            "reader_text_size",
            "blink_toggle",
            "blink_fade",
            "bg_text_size",
            "l_w_delay",
            "comma_delay",
            "pointer", "wpm",
            "progress_bar",
            "dot_delay",
            "blink_delay",
            "blink_interval",
            "accel",
            "blink_fade_toggle",
            "blink_color",
            "s1",
            "pager_sett_l",
            "pager_sett",
            "pager_sett_r",
            "create_readme",
            "missing_book"
            ]

        for p in properties:
            exec(f"self.root_screen.{p} = self.settings_screen.{p}")
        
        create_path(self.active_dao.get_active().path)

        files = []
        for entry in os.scandir(os.path.abspath(self.active_dao.get_active().path)):
            if entry.is_file():
                files.append(entry.name)
        
        if self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).create_readme and "Readme.txt" not in files:
            try:
                create_readme(os.path.abspath(self.active_dao.get_active().path))
            except:
                self.snack(self, 'Error: Could not create "Readme.txt"')
        
        self.screen_manager.add_widget(self.settings_screen)
        self.screen_manager.add_widget(self.reader_screen)
        self.screen_manager.add_widget(self.books_screen)
        self.screen_manager.add_widget(self.clipboard_screen)
        self.screen_manager.add_widget(self.donations_screen)
        self.screen_manager.add_widget(self.themes_screen)

        self.set_dark(self, "load")
        self.set_theme(self, "")
        self.set_hue(self, "")

        Window.bind(on_key_down=self._keydown)
        Window.bind(on_key_up=self._keyup)
        
        Clock.schedule_once(self._set_slot, 1)

        self.update_WPM()

        if self.active_dao.get_active().book != "":
            self.open_book(self.active_dao.get_active().book)

            self.select_screen("reader", self.active_dao.get_active().book)

        # Set size_hints param for fullscreen button
        # (needs to be pressed once to activate)
        self.full_screen()
        
        return self.root_screen
    
    def resource_path(self, relative_path):
        return os.path.join(BASE_PATH, relative_path)
        # if sys.platform.startswith("win32"):
        #     """ Get absolute path to resource, works for dev and for PyInstaller """
        #     # base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            
        #     return os.path.join(BASE_PATH, relative_path)
        #     return os.path.join(base_path, relative_path)
        # if sys.platform.startswith("darwin"):
        #     pass
        
        # if sys.platform.startswith("linux"):
        #     # base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        #     # return (base_path+"/"+relative_path) # First image wasn't loading ?
            
        #     return os.path.join(BASE_PATH, relative_path)
        #     return os.path.join(base_path, relative_path)
        # else:
        #     pass

    def create_settings(self):
        self.settings_dao = SettingsDAO()
        self.active_dao = ActiveDAO()
        self.theme_dao = ThemeDAO()
        self.bookshelf_dao = BookshelfDAO()

    def select_screen(self, screen, name, *kwargs):
        self.screen_manager.current = screen
        self.create_toolbar(screen, name)
    
    def create_toolbar(self, title, name):
        if "toolbar" not in dir(self.root_screen):
            toolbar = MDTopAppBar(title="Speed Read-R / " + name,
            id="topbar",
            pos_hint={'top': 1},
            left_action_items=[["menu", lambda x: self.nav_drawer_open()]]
                )
            self.root_screen.add_widget(toolbar)
            self.root_screen.toolbar = toolbar
        elif name == "":
            toolbar = self.root_screen.toolbar
            toolbar.title = "Speed Read-R / " + self.active_dao.get_active().book
        else:
            toolbar = self.root_screen.toolbar
            toolbar.title = "Speed Read-R / " + name
    
    def nav_drawer_open(self):
        nav_drawer = self.root_screen.nav_drawer
        
        self.root_screen.content_navigation.words_readed.text = str(self.active_dao.get_active().total)
        
        self.root_screen.content_navigation.show_path.text = "..."+str(
            os.path.abspath(self.active_dao.get_active().path)[-18:])
        
        nav_drawer.set_state("open")
        
    def post_slot(self, *kwargs):
        exec(f"self.settings_screen.{self.active_dao.get_active().setting_active}.state = 'down'")
    
    def _set_slot(self, *kwargs):
        self.set_slot(self.active_dao.get_active().setting_active)
        
        self.update_WPM()
    
    def keep_button_up(self, *kwargs):
        if kwargs[1] == "normal" and kwargs[2] == "normal":
            self.settings_screen.ids[kwargs[0]].state = "down"

    @mainthread
    def update_WPM(self, *kwargs):
        if self.screen_manager.current == "sett":
            self.settings_screen.ids.wpm.text = str(
                self.settings_dao.get_setting(
                slot=self.active_dao.get_active().setting_active).wpm)
        self.reader_screen.ids.display_wpm.text = str(
            self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).wpm)
    
    def set_slot(self, slot, *kwargs):
        self.active_dao.update_active(setting_active=slot)
        
        self.post_settings(slot)

        self.reader_sett_set_size(slot)

        self.set_timed()

        self.show_pointer()

    @mainthread
    def set_cursor(self):
        self.reader_screen.grid_pager.children[0].focus = True

        self.reader_screen.grid_pager.children[0].cursor = self.reader_screen.grid_pager.children[0].get_cursor_from_index(
            self.bookshelf_dao.get_book_title(self.active_dao.get_active().book).indx)
        

    def post_settings(self, *kwargs):
        self.posting = True

        text_sett = [
            "reader_text_size",
            "accel",
            "l_w_delay",
            "comma_delay",
            "blink_delay",
            "bg_text_size",
            "wpm",
            "dot_delay",
            "blink_interval",
            "blink_fade"
            ]

        for key in set(self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active)):
            from kivy.app import App
            try:
                if key[0] in text_sett:
                    exec(f"self.settings_screen.{key[0]}.text = str({key[1]})")
            except Exception as e:
                # print("Error in post_settings: ", e)
                self.snack(self, "Error: Could not post settings")
        
        self.settings_screen.pointer.active = self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).pointer
        
        self.settings_screen.blink_toggle.active = self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).blink_toggle
        
        self.settings_screen.progress_bar.active = self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).progress_bar
        
        self.settings_screen.blink_fade_toggle.active = self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).blink_fade_toggle

        self.settings_screen.blink_color.md_bg_color = ast.literal_eval(
            self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).blink_color)
        
        self.settings_screen.create_readme.active = self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).create_readme

        self.settings_screen.missing_book.active = self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).missing_book
        
        self.posting = False

    def reader_sett_set_size(self, *kwargs):
        self.settings_screen.ids.pager_sett_l.font_size = self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).reader_text_size
        
        self.settings_screen.ids.pager_sett.font_size = self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).reader_text_size
        
        self.settings_screen.ids.pager_sett_r.font_size = self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).reader_text_size
        
        self.reader_screen.ids.pager_l.font_size = self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).reader_text_size
        
        self.reader_screen.ids.pager.font_size = self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).reader_text_size
        
        self.reader_screen.ids.pager_r.font_size = self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).reader_text_size

    def show_pointer(self, *kwargs):
        if self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).pointer == True:
            self.settings_screen.ids.marker_sett.text = "|"
            self.reader_screen.ids.marker.text = "|"
        else:
            self.settings_screen.ids.marker_sett.text = " "
            self.reader_screen.ids.marker.text = " "
    
    def set_dark(self, obj, load, *kwargs):
        if load == "load":
            self.theme_cls.theme_style = self.theme_dao.read_theme()[0].dark
        else:
            self.theme_dao.update_theme(
                dark="Dark" if self.theme_cls.theme_style != "Dark" else "Light")

            self.theme_cls.theme_style = self.theme_dao.read_theme()[0].dark

    def set_theme(self, obj, theme, *kwargs):
        if theme != "":
            self.theme_cls.primary_palette = theme
            self.theme_dao.update_theme(color=theme)
            self.snack(self, "Restart the app to properly apply changes")
        else:
            self.theme_cls.primary_palette = self.theme_dao.read_theme()[0].color

    def set_hue(self, obj, hue, *kwargs):
        if hue != "":
            self.theme_cls.primary_hue = hue
            self.theme_dao.update_theme(hue=hue)
            self.snack(self, "Restart the app to properly apply changes")
        else:
            self.theme_cls.primary_hue = self.theme_dao.read_theme()[0].hue

    def open_color_picker(self):
        color_picker = MDColorPicker(size_hint=(0.45, 0.85),
        type_color="RGBA")
        color_picker.open()
        color_picker.bind(
            on_select_color=self.on_select_color,
            on_release=self.get_selected_color,
        )

    def update_color(self, color: list) -> None:
        self.settings_dao.update_settings(
            slot=self.active_dao.get_active().setting_active, blink_color=color)
        self.settings_screen.ids.blink_colorr.md_bg_color = color
    
    def get_selected_color(self,
        instance_color_picker: MDColorPicker,
        type_color: str,
        selected_color: Union[list, str],
        ):
        self.update_color(selected_color[:-1] + [1])
    
    def on_select_color(self, instance_gradient_tab, color: list) -> None:
        ...

    ''' Donations links '''
    def copy_clipboard(self, obj, site, *kwargs):
        erc20 = "0x7c7C32E8400a2B9EecAD55f94f4F734bA520687f"
        btc = "bc1ql8vsr57vctxeqqm0ayer04j6lqgsc6gtpytley"
        bnb = "bnb1aheerja9dlfs6tsda5gq6aj3vzxhm2rjm4e620"
        
        match site:
            case "bitcoin":
                Clipboard.copy(btc)
                self.snack(self, "Address BTC copied to clipboard")
            case "bnb":
                Clipboard.copy(bnb)
                self.snack(self, "Address BNB copied to clipboard")
            case "crypto":
                Clipboard.copy(erc20)
                self.snack(self, "Address ERC20 copied to clipboard")
            case "coindrop":
                webbrowser.open('https://coindrop.to/loudbeat')
            case "kofi":
                webbrowser.open('https://ko-fi.com/loudbeat')
            case "coffee":
                webbrowser.open('https://www.buymeacoffee.com/loudbeat')
            case "ig":
                webbrowser.open('https://www.instagram.com/loudbeat/')

    def snack(self, obj, pop_text, *kwargs):
        Snackbar(
            text=pop_text,
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=.7
            ).open()

    def _keydown(self, obj, key, *args):
        pass
        
    ''' Catch up keypress 
    S = speed up +10 wpm,
    D = decrease -10 wpm,
    F = toggle fullscreen reader,
    Space = Play/Pause reader and settings reader'''
    def _keyup(self, obj, key, *args):
        sm = self.screen_manager.current
        
        if key == 32 and sm == "reader":
            if self.play:
                self.reader_screen.ids.p_button.icon = "play-circle"
                self.play = False
            else:
                self.play = True
                self.reader_screen.ids.p_button.icon = "pause-circle"
                Thread(target = self.play_reader).start()
        
        if key == 32 and sm == "sett":
            if self.play_sett:
                self.play_sett = False
            else:
                self.play_sett = True
                Thread(target = self.play_reader_sett).start()
        
        if key == 115:
            Thread(target = self.speed_up).start()
        
        if key == 100:
            Thread(target = self.speed_down).start()
        
        if key == 102:
            Thread(target = self.full_screen).start()
            

    def speed_up(self):
        self.settings_dao.update_settings(
            slot=self.active_dao.get_active().setting_active, wpm=self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).wpm + 10)
        
        self.set_timed()
        
        self.update_WPM(self)

    def speed_down(self):
        self.settings_dao.update_settings(
            slot=self.active_dao.get_active().setting_active, wpm=self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).wpm - 10)
        
        self.set_timed()
        
        self.update_WPM(self)

    ''' Convert settings decimal to millisecond '''
    def set_timed(self):
        self.timed["l_w_delay"] = self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).l_w_delay / 1000
        
        self.timed["dot_delay"] = self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).dot_delay / 1000
        
        self.timed["comma_delay"] = self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).comma_delay / 1000
        
        self.timed["blink_delay"] = self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).blink_delay / 1000
        
        if self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).l_w_delay > 0:
            self.timed["step"] = 60 / self.settings_dao.get_setting(
                slot=self.active_dao.get_active().setting_active).wpm / (self.settings_dao.get_setting(
                slot=self.active_dao.get_active().setting_active).l_w_delay / 10)

        if self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).l_w_delay <= 0:
            self.timed["step"] = 60 / self.settings_dao.get_setting(
                slot=self.active_dao.get_active().setting_active).wpm

    def full_screen(self, *kwargs):
        self.reader_screen.fullscreen_button.dispatch("on_release")

    def blink(self, start_time, blink_color, blinker):
        if self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).blink_fade_toggle == True and blink_color[3] > 0:
            blink_color[3] = 1 - ((time.time() - start_time) / self.settings_dao.get_setting(
                slot=self.active_dao.get_active().setting_active).blink_fade)

        elif self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).blink_fade_toggle == True and blink_color[3] < 0:
            blink_color[3] = 0
        
        label_color = self.reader_screen.ids.pager_l.color
        
        if blinker == "sett":
            self.settings_screen.ids.pager_sett_l.color = blink_color
            self.settings_screen.ids.pager_sett_l.text = "—"
            self.settings_screen.ids.pager_sett.color = blink_color
            self.settings_screen.ids.pager_sett.text = "."
            self.settings_screen.ids.pager_sett_r.color = blink_color
            self.settings_screen.ids.pager_sett_r.text = "—   "
            
            time.sleep(self.timed["blink_delay"])
            
            self.settings_screen.ids.pager_sett_l.color = label_color
            self.settings_screen.ids.pager_sett.color = [0.62,0.15,0.04,1]
            self.settings_screen.ids.pager_sett_r.color = label_color

        if blinker == "player":
            self.reader_screen.ids.pager_l.color = blink_color
            self.reader_screen.ids.pager_l.text = "—"
            self.reader_screen.ids.pager.color = blink_color
            self.reader_screen.ids.pager.text = "."
            self.reader_screen.ids.pager_r.color = blink_color
            self.reader_screen.ids.pager_r.text = "—   "
            
            time.sleep(self.timed["blink_delay"])
            
            self.reader_screen.ids.pager_l.color = label_color
            self.reader_screen.ids.pager.color = [0.62,0.15,0.04,1]
            self.reader_screen.ids.pager_r.color = label_color
        
        return blink_color


    def save_settings(self, key, value, *kwargs):
        if self.posting != True:
            if key != "create_readme":
                
                exec(f"self.settings_dao.update_settings(slot=self.active_dao.get_active().setting_active, {key}={value})")
                
                self.set_timed()
            else:
                self.settings_dao.create_readme_settings(readme=value)
        self.update_WPM(self)

    def load_books(self, *kwargs):
        if self.bookshelf_loaded:
            self.unload_bookshelf(self)
        
        bookshelf = self.bookshelf_dao.read_bookshelf()
        
        files = []
        for entry in os.scandir(os.path.abspath(self.active_dao.get_active().path)):
            if entry.is_file():
                files.append(entry.name)
        
        for i in range(len(bookshelf)):
            if bookshelf[i].title in files:

                delete_b = BookButtonDelete(
                    id= str(bookshelf[i].title),
                    on_release = lambda x=bookshelf[i].title, *args: self.delete_book(x, *args))
                
                title = BookListLabel(text=str(bookshelf[i].title), halign="left")
                data = BookListLabel(text=str(bookshelf[i].progress) + "%", halign="center", size_hint_x= .3)
                
                open_b = BookButton(
                    id= str(bookshelf[i].title),
                    on_release = lambda x=bookshelf[i].title, *args: self.open_book(x, *args))

                self.books_screen.books_grid_2.add_widget(delete_b)
                self.books_screen.books_grid_2.add_widget(title)
                self.books_screen.books_grid_2.add_widget(data)
                self.books_screen.books_grid_2.add_widget(open_b)
            
            elif bookshelf[i].title not in files and self.settings_dao.get_setting(
                slot=self.active_dao.get_active().setting_active).missing_book:
                delete_b = BookButtonDelete(
                    id= str(bookshelf[i].title),
                    on_release = lambda x=bookshelf[i].title, *args: self.delete_book(x, *args))
                
                title = BookListLabel(text=str(
                    bookshelf[i].title), strikethrough=True, halign="left")
                data = BookListLabel(text=str(
                    bookshelf[i].progress) + "%", halign="center", size_hint_x= .3)
                
                open_b = BookButton(
                    id= str(bookshelf[i].title),
                    disabled = True,
                    on_release = lambda x=bookshelf[i].title, *args: self.open_book(x, *args))

                self.books_screen.books_grid_2.add_widget(delete_b)
                self.books_screen.books_grid_2.add_widget(title)
                self.books_screen.books_grid_2.add_widget(data)
                self.books_screen.books_grid_2.add_widget(open_b)

            self.bookshelf_loaded = True

    def reload_bookshelf(self, *kwargs):
        files = []
        new_books = 0

        for entry in os.scandir(os.path.abspath(self.active_dao.get_active().path)):
            if entry.is_file():
                files.append(entry.name)
        
        open_library = self.bookshelf_dao.read_bookshelf()
        
        suported = [
            "text/plain",
            "application/rtf",
            "text/markdown",
            "application/epub+zip",
            "application/pdf",
            "application/x-tex",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ]
            # "text/vtt"
            # "text/rtf",
            # "application/vnd.amazon.mobi8-ebook",
            # "application/vnd.oasis.opendocument.text",
            # "application/vnd.palm",
            # "application/postscript",
            # "application/xhtml+xml",
            # "text/html",
            # "application/msword",

        for book in files:
            book_type = mimetypes.guess_type(os.path.join(
                os.path.abspath(self.active_dao.get_active().path), book))[0]
            
            if book_type in suported:
                book_hash = md5(os.path.join(os.path.abspath(
                    self.active_dao.get_active().path), book))
                old = False
                
                for bk in open_library:
                    if bk.hash == book_hash:
                        old = True
                        
                        # Renamed file
                        if bk.title != book:
                            self.bookshelf_dao.update_title(hash=book_hash, title=book)
                            
                            break
                    
                    if bk.title == book:
                        old = True
                        
                        # Modified file
                        if bk.hash != book_hash:
                            self.bookshelf_dao.update_hash(title=book, hash=book_hash)
                            break

                if not old:
                    self.bookshelf_dao.create_bookshelf(
                        title=book, hash=book_hash, type=book_type, indx=0, progress=0)

                    new_books += 1

        if new_books >= 1:
            self.snack(self, str(new_books)+" new book/s found")

        else:
            self.snack(self, "Error: No book found")
            
        self.unload_bookshelf(self)
        
        self.load_books(self)


    def unload_bookshelf(self, *kwargs):
        # Delete all elements from books_grid_2
        row = [i for i in self.books_screen.books_grid_2.children]
        
        for row1 in row:
            self.books_screen.books_grid_2.remove_widget(row1)
        self.bookshelf_loaded = False

    def delete_book(self, book):
        self.bookshelf_dao.delete_book(title=book.id)

        self.reload_bookshelf()

    def clear_bookshelf(self):
        files = []
        for entry in os.scandir(os.path.abspath(self.active_dao.get_active().path)):
            if entry.is_file():
                files.append(entry.name)
        
        bookshelf = self.bookshelf_dao.read_bookshelf()

        for i in range(len(bookshelf)):
            if bookshelf[i].title not in files:
                self.bookshelf_dao.delete_book(title=bookshelf[i].title)
        
        self.reload_bookshelf()

    ''' Save text from quick text on a new file and open it on the reader '''
    def save_clip(self, obj, title, new_text, *kwargs):
        iter = 0
        
        if os.path.exists(os.path.join(os.path.abspath(
            self.active_dao.get_active().path), title)+".txt"):
            while os.path.exists(os.path.join(os.path.abspath(
                self.active_dao.get_active().path), title)+"_"+str(iter)+".txt"):
                iter +=1
            title = title+"_"+str(iter)
        
        title = title+".txt"
        
        with open(os.path.join(os.path.abspath(
            self.active_dao.get_active().path), title), "w") as new_t:
            new_t.write(new_text)

        clip_type = mimetypes.guess_type(os.path.join(
            os.path.abspath(self.active_dao.get_active().path), title))[0]
        clip_hash = md5(os.path.join(os.path.abspath(
            self.active_dao.get_active().path), title))

        self.bookshelf_dao.update_bookshelf(
            title=title, hash=clip_hash, type=clip_type, indx=0, progress=0)
        
        self.active_dao.update_active(book=title)
        
        self.open_book(title)

        
    def file_manager_open(self):
        self.file_manager = FixFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            selector="folder")
        
        self.file_manager.show(os.path.expanduser(
            os.path.abspath(self.active_dao.get_active().path)))
        
        self.manager_open = True

    def select_path(self, books_pathx):
        try:
            self.active_dao.update_active(path=os.path.relpath(books_pathx, BASE_PATH))
        
        except:
            self.snack(self, "Error: Can't load directory")
            # sys.exit("Can't load directory path settings")
        
        self.root_screen.content_navigation.show_path.text = "..."+str(
            os.path.abspath(self.active_dao.get_active().path)[-18:])
        
        self.exit_manager()
        
        self.snack(self, books_pathx)
    
    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''
        self.manager_open = False
        self.file_manager.close()
    
    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True
    
    ''' Generate iterator '''
    def reader(self, text):
        for words in text.split():
            yield words
    
    ''' Open selected book,
    parse text,
    load text into reader,
    set progress,
    cursor position,
    display title on top bar. '''
    def open_book(self, *kwargs):
        # Clear reader if loaded
        if self.book_loaded:
            self.clear_reader(self)
        
        # Use last book open if didn't passed a new one.
        if type(kwargs[0]) == str:
            pass
        else:
            self.active_dao.update_active(book=kwargs[0].id)

        book = self.bookshelf_dao.get_book_title(title=self.active_dao.get_active().book)
        
        path = os.path.abspath(self.active_dao.get_active().path)
        
        true_path = os.path.join(path, book.title)
        
        # Check if file exists
        if os.path.exists(true_path) == False:
            self.snack(self, "Error: File not found")
            return
        
        # Match open book type
        match book.type:
            case "text/plain":
                self.texted_book = Parsex.text(true_path)
            case "application/epub+zip":
                self.texted_book = Parsex.ebook(true_path)
            case "application/pdf":
                self.texted_book = Parsex.pdf(true_path)
            case "text/markdown":
                self.texted_book = Parsex.md(true_path)
            case "application/rtf":
                self.texted_book = Parsex.rtf(true_path)
            case "application/x-tex":
                self.texted_book = Parsex.text(true_path)
            case "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                self.texted_book = Parsex.docx(true_path)

        # Create iterator
        try:
            self.word_iter = more_itertools.seekable(self.reader(self.texted_book))
        except:
            self.snack(self, "Error: Could not proccess text")
            return
        
        try:
            self.open_book_length = more_itertools.ilen(self.word_iter)
        except:
            self.snack(self, "Error: Could not proccess text length")
            self.open_book_length = 0
        
        # Word count readed text
        self.index = more_itertools.ilen(
            more_itertools.seekable(self.reader(
            self.texted_book[:self.bookshelf_dao.get_book_title(
            title=self.active_dao.get_active().book).indx])))

        # Position iterator index
        self.word_iter.seek(self.index)
        
        self.reader_screen.book_length.text = f"/{self.open_book_length}"
        
        if self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).progress_bar:
            if self.index == 0:
                self.reader_screen.p_bar.value = 0
                self.reader_screen.index.text = str(self.index)
            
            else:
                self.bookshelf_dao.update_param(
                    title=self.active_dao.get_active().book, indx=self.bookshelf_dao.get_book_title(
                    title=self.active_dao.get_active().book).indx, progress=(
                    int(self.index / self.open_book_length * 100)))
                
                self.reader_screen.p_bar.value = self.bookshelf_dao.get_book_title(
                    title=self.active_dao.get_active().book).progress
                
                self.reader_screen.index.text = str(self.index)
        
        else:
            self.reader_screen.p_bar.value = 0
            self.reader_screen.index.text = str(0)

        # Split current word and show in prompter
        chunk = splitter(self.word_iter.peek(), len(self.word_iter.peek()))
        self.reader_screen.pager_l.text = str(chunk[0])
        self.reader_screen.pager.text = str(chunk[1])
        self.reader_screen.pager_r.text = str(chunk[2])
        
        tf = TextInput(
            font_size = self.settings_dao.get_setting(slot= self.active_dao.get_active().setting_active).bg_text_size,
            multiline = True,
            readonly = True,
            text = str(self.texted_book),
            background_color = [0,0,0,0],
            foreground_color = ([.15,.15,.15,1] if self.theme_cls.theme_style != "Dark" else "gray"),
            allow_copy = True,
            on_double_tap = lambda *x: self.click_text())

        self.reader_screen.grid_pager.add_widget(tf)
        self.book_loaded = True

        self.select_screen("reader", self.active_dao.get_active().book)

        self.set_cursor()

        Clock.schedule_once(
            lambda x: self.reader_screen.grid_pager.children[0].select_text(
            self.bookshelf_dao.get_book_title(
            title=self.active_dao.get_active().book).indx, self.bookshelf_dao.get_book_title(
            title=self.active_dao.get_active().book).indx+len(
            self.word_iter.peek())
            ))

    def clear_reader(self, *kwargs):
        if self.book_loaded:
            self.reader_screen.grid_pager.clear_widgets(children=None)
            self.book_loaded = False

    ''' Set new position for the reader. '''
    def click_text(self, *kwargs):
        new_index = self.reader_screen.ids.grid_pager.children[0].cursor_index(
            self.reader_screen.ids.grid_pager.children[0].cursor)
        
        if new_index != self.old_index:
            self.old_index = new_index
            
            while self.texted_book[new_index-1] != " ":
                if self.texted_book[new_index-1] == "\n" or new_index == 0:
                    break
                new_index = new_index - 1
            
            # Get new index
            self.index = more_itertools.ilen(more_itertools.seekable(
                self.reader(self.texted_book[:new_index])))

            self.bookshelf_dao.update_param(
                title=self.active_dao.get_active().book, indx=new_index, progress=(
                int(self.index / self.open_book_length * 100)))
            
            if self.settings_dao.get_setting(
                slot=self.active_dao.get_active().setting_active).progress_bar:
                self.reader_screen.ids.p_bar.value = self.bookshelf_dao.get_book_title(
                    title=self.active_dao.get_active().book).progress
                
                self.reader_screen.ids.index.text = str(self.index)

            # Change reader to new index
            self.word_iter.seek(self.index)

            chunk = splitter(self.word_iter.peek(), len(self.word_iter.peek()))
            self.reader_screen.ids.pager_l.text = str(chunk[0])
            self.reader_screen.ids.pager.text = str(chunk[1])
            self.reader_screen.ids.pager_r.text = str(chunk[2])

    ''' Iterate through words while self.play == True '''
    def play_reader(self, *args):
        self.playing = False

        # Acceleration
        start_acc = False
        
        # Blinking
        start_blink = False
        
        # Posted words count
        self.p_words = 0

        if self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).accel > 0:
            start_acc = True
            acceleration = time.time()
        
        if self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).blink_toggle:
            start_blink = True
            start_blink_t = time.time()
            loop_blink_t = time.time()
            blink_color = ast.literal_eval(
                self.settings_dao.get_setting(
                slot=self.active_dao.get_active().setting_active).blink_color)
        
        play_start = time.time()

        try:
            with keep.presenting() as k:
                if self.play:
                    self.playing = True
                while self.playing and self.index < self.open_book_length:
                    length = len(self.word_iter.peek())
                    chunk = splitter(self.word_iter.peek(), length)
                    
                    self.reader_screen.pager_l.text = str(chunk[0])
                    self.reader_screen.pager.text = str(chunk[1])
                    self.reader_screen.pager_r.text = str(chunk[2])

                    Clock.schedule_once(
                        lambda x: self.reader_screen.grid_pager.children[0].select_text(
                        self.bookshelf_dao.get_book_title(
                        title=self.active_dao.get_active().book).indx, (
                        self.bookshelf_dao.get_book_title(
                        title=self.active_dao.get_active().book).indx + length))
                        )

                    self.reader_screen.grid_pager.children[0].cursor = self.reader_screen.grid_pager.children[0].get_cursor_from_index(
                        self.bookshelf_dao.get_book_title(title=self.active_dao.get_active().book).indx)
                    
                    if self.play != True:
                        break
                    
                    delay(self.word_iter.peek(), length, self.timed)
                    
                    # Accelerate until set acceleration time reached
                    if start_acc == True:
                        if time.time()-acceleration < int(
                            self.settings_dao.get_setting(
                            slot=self.active_dao.get_active().setting_active).accel):
                            accel(acceleration, self.settings_dao.get_setting(
                                slot=self.active_dao.get_active().setting_active).accel)
                        else:
                            start_acc = False
                    
                    # Blinking if active
                    if start_blink == True:
                        if time.time() - loop_blink_t > int(
                            self.settings_dao.get_setting(
                            slot=self.active_dao.get_active().setting_active).blink_interval):
                            blink_color = self.blink(start_blink_t, blink_color, "player")
                            loop_blink_t = time.time()
                    
                    # Get indx of next word
                    self.indx = self.bookshelf_dao.get_book_title(
                        title=self.active_dao.get_active().book).indx + length
                    try:
                        while self.texted_book[
                            self.indx] == " " or self.texted_book[
                                self.indx] == "\n" or self.texted_book[
                                    self.indx].isprintable() == False:
                        # while self.texted_book[self.indx] == " " or self.texted_book[self.indx].isprintable() == False:
                            self.indx += 1
                    
                    except IndexError:
                        # If error or EOF reached, save words read and stop player.
                        self.active_dao.update_active(total=self.active_dao.get_active().total+self.p_words)
                        
                        self.reader_screen.p_button.dispatch("on_release")

                        self.snack(self, "Index Error!")
                        break
                    
                    # Get index of next word
                    self.index += 1
                    next(self.word_iter)
                    
                    # Set currently played words
                    self.p_words += 1

                    # Update progress
                    self.bookshelf_dao.update_param(
                        title=self.active_dao.get_active().book, indx=self.indx, progress=int(
                        self.index / self.open_book_length * 100))

                    if self.settings_dao.get_setting(
                        slot=self.active_dao.get_active().setting_active).progress_bar:
                        self.reader_screen.p_bar.value = self.bookshelf_dao.get_book_title(
                            title=self.active_dao.get_active().book).progress
                        
                        self.time_left(self, self.open_book_length, play_start)
                        
                        self.reader_screen.index.text = str(self.index)
                
            
            # Update read words count
            self.active_dao.update_active(total=self.active_dao.get_active().total+self.p_words)
        
        except KeyboardInterrupt:
            pass
        
        # Stop player
        self.play = False
    
    ''' Open settings.txt,
    read settings,
    Iterate through words,
    update settings reader. '''
    def play_reader_sett(self, *args):
        self.playing_sett = False

        # Acceleration
        start_acc = False

        # Blinking
        start_blink = False
        
        if self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).accel > 0:
            start_acc = True
            acceleration = time.time()
        
        if self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).blink_toggle:
            start_blink = True
            start_blink_t = time.time()
            loop_blink_t = time.time()
            blink_color = ast.literal_eval(
                self.settings_dao.get_setting(
                slot=self.active_dao.get_active().setting_active).blink_color)
        
        indx_sett = 0
        play_settings = ""
        
        if os.path.exists(os.path.join(os.path.abspath("config"), "settings.txt")) == False:
            self.snack(self, "Error: Settings file not found")
            return
        
        # Open settings text
        with open("./config/settings.txt", "r") as st:
            play_settings = st.read()
        
        # Listed words
        play_words = play_settings.split()
        
        # Total length
        play_length = len(play_words)

        # First render
        chunk_sett = splitter(play_words[indx_sett], len(play_words[indx_sett]))
        
        self.root_screen.pager_sett_l.text = str(chunk_sett[0])
        self.root_screen.pager_sett.text = str(chunk_sett[1])
        self.root_screen.pager_sett_r.text = str(chunk_sett[2])
        
        try:
            with keep.presenting() as k:
                if self.play_sett:
                    self.playing_sett = True
                while self.playing_sett:
                    # Current word length
                    length = len(play_words[indx_sett])

                    # Split current word for prompter
                    chunk_sett = splitter(play_words[indx_sett], length)

                    self.root_screen.pager_sett_l.text = str(chunk_sett[0])
                    self.root_screen.pager_sett.text = str(chunk_sett[1])
                    self.root_screen.pager_sett_r.text = str(chunk_sett[2])

                    if self.play_sett != True:
                        break

                    delay(play_words[indx_sett], length, self.timed)
                    
                    indx_sett +=1

                    if start_acc == True:
                        if time.time()-acceleration < int(
                            self.settings_dao.get_setting(
                            slot=self.active_dao.get_active().setting_active).accel):
                            accel(acceleration, self.settings_dao.get_setting(
                                slot=self.active_dao.get_active().setting_active).accel)
                        else:
                            start_acc = False
                    
                    if start_blink == True:
                        if time.time() - loop_blink_t > int(self.settings_dao.get_setting(
                            slot=self.active_dao.get_active().setting_active).blink_interval):
                            blink_color = self.blink(start_blink_t, blink_color, "sett")
                            loop_blink_t = time.time()
                    
                    # Loop text if EOF is reached.
                    if indx_sett == play_length:
                        indx_sett = 0
        
        except KeyboardInterrupt:
            pass
        
        self.play_sett = False

    ''' Calculate average time left from (current speed/remaining length) and
    (current played words/elapsed time) '''
    def time_left(self, obj, word_count, play_start, *kwargs):
        words_left = word_count - self.index
        
        if self.settings_dao.get_setting(
            slot=self.active_dao.get_active().setting_active).blink_toggle:
            
            # Calculate time left based on formula
            time_left = words_left / int(self.settings_dao.get_setting(
                slot=self.active_dao.get_active().setting_active).wpm) * 100 / 60

            # Calculate remaining blinks delay.
            blinks_left = time_left / self.settings_dao.get_setting(
                slot=self.active_dao.get_active().setting_active).blink_interval

            delay_blinks_left = blinks_left * (self.settings_dao.get_setting(
                slot=self.active_dao.get_active().setting_active).blink_delay / 1000)
            
            time_left += delay_blinks_left
            
            # Calculate time left based on execution
            execution_left = (time.time() - play_start)/ self.p_words * words_left + delay_blinks_left

        
        # Calculate time left without blinks
        else:
            execution_left = (time.time() - play_start)/ self.p_words * words_left

            time_left = words_left / int(self.settings_dao.get_setting(
                slot=self.active_dao.get_active().setting_active).wpm) * 100 / 60
        
        # Average two time left results.
        t_left = (time_left + execution_left/60)/2

        hours = t_left / 60
        minutes = t_left % 60
        seconds = (minutes % 1) * 60

        t = f"{str(int(hours)).zfill(2)}:{str(int(minutes)).zfill(2)}:{str(int(seconds)).zfill(2)}"
        
        self.reader_screen.ids.time_left.text = t


class FixFileManager(MDFileManager):
    def back(self) -> None:
        """Returning to the branch down in the directory tree."""

        if self.current_path[-1:] == "/" or self.current_path[-1:] == "\\":
            self.current_path = self.current_path[:-1]

        path, end = os.path.split(self.current_path)

        if self.current_path and path == self.current_path:
            self.show_disks()
        else:
            if not end:
                self.close()
                self.exit_manager(1)
            else:
                self.show(path)

""" Hash the files to reference it by its content
and know if they were modified to reset the index,
otherwise can get index out of range error."""
def md5(filename):
    h  = hashlib.md5()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()

''' Split words into left/center/right depending on length '''
def splitter(word, length):
    if length <= 1:
        return ["", word, ""]
    elif length <= 5:
        return [word[:1], word[1:2], word[2:]]
        # 2nd 
    elif length <= 9:
        return [word[:2], word[2:3], word[3:]]
        # 3rd
    elif length <= 13:
        return [word[:3], word[3:4], word[4:]]
        # 4th
    elif length <= 17:
        return [word[:4], word[4:5], word[5:]]
        # 5th
    elif length <= 21:
        return [word[:5], word[5:6], word[6:]]
        # 6th
    else:
        return [word[:6], word[6:7], word[7:]]
        # 7th

def delay(word, length, timed):
    tot = 0

    # Dot delay
    if word[-1:] == ".":
        tot += timed["dot_delay"]
    
    # Comma delay
    if word[-1:] == ",":
        tot += timed["comma_delay"]
    
    # Word Length delay
    if timed["l_w_delay"] > 0:
        step_count = timed["step"] * length

        tot += step_count + (1 / step_count / 1000)
    
    # Word per minute delay
    if timed["l_w_delay"] <=0:
        tot += timed["step"]
    
    time.sleep(tot)
    
    return

def accel(secs, acc_amount):
    # Elapsed time
    t1 = time.time() - secs
    
    # Add delay if elapsed time is lesser than selected acceleration time.
    if t1 < int(acc_amount):
        d = (int(acc_amount) - t1) * 10 / 1000
        time.sleep(d)

def main():
    Speed_Read_RApp().run()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        
