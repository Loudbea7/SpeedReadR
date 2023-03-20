from kivymd.app import MDApp
from kivy.factory import Factory as F
from kivy.core.window import Window
import sys
import os
import time
import mimetypes
import hashlib
import sqlite3
from os import listdir
from os import path
from pathlib import Path
from kivy.properties import ObjectProperty
from kivy.core.window import Window

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.navigationdrawer import MDNavigationDrawer

from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivymd.toast import toast
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.behaviors.toggle_behavior import MDToggleButton
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.button import MDRectangleFlatIconButton
from kivymd.uix.pickers import MDColorPicker
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivy.core.clipboard import Clipboard
from typing import Union
from kivymd.uix.filemanager import MDFileManager
from threading import Thread
from kivy.clock import Clock, mainthread
import webbrowser
from kivy.config import Config
import ast
import zlib
import base64

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import zipfile
from pypdf import PdfReader
from markdown import markdown
from striprtf.striprtf import rtf_to_text



global_settings = {}
timed = {}
books_path = ""
current_slot = ""
active = ""

# if function posting is loading the values, the save function won't work until it finishes
posting = False

# The bookshelf only loads when is not loaded (first time open) and when button reload is clicked
bookshelf_loaded = False

# screen cleans only if a book has been loaded
book_loaded = False

# Last opened book
current_book = ""

# Load database of opened book
open_book = None

texted_book = ""

db = None
con = None

# Clicking on the text triggers the function twice, it filters the repetition.
old_index = None

# list of words of the opened book
word_index = None

# Current index, number of characters
indx = None
# Current index, number of word indexed to play
index = None

play = False
play_sett = False

# played words since play.
p_words = 0

# Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

class BookListLabel(MDLabel):
    pass

class BookButton(MDRectangleFlatIconButton):
    pass

class ContentNavigationDrawer(MDScrollView):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()
    pass

class MDNavigationDrawer2(MDNavigationDrawer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    # screen_manager = ObjectProperty()
    # nav_drawer = ObjectProperty()
    # def on_state(self, *args):
        # print("state", self.state)

        # app = App.get_running_app()
        # if self.state == "open":
            # show_path()
            # print('Updating the show_path!', self.children)
            # print('Updating the show_path!', dir(self.ids))
            # print('Updating the show_path!', app.ids.show_path)
            # print('Updating the show_path!', self.root_screen.ids.show_path)
            # self.show_path.text = "..."+str(books_path[-18:])

            # self.root_screen.show_path.text = "..."+str(books_path[-18:])
            # app.root_screen.toolbar.opacity = 0

        # elif self.state == "close":
        #     app.root_screen.toolbar.opacity = 1

class MyToggleButton(MDRectangleFlatButton, MDToggleButton):
    pass
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self

class RootScreen(F.Screen):
    pass

# class MainScreen(MDScreen):
    # def on_enter(self):
    #     print('Entering the Main Screen!')
    #     Clock.schedule_once(self.update_show_path, 3)

    # def update_show_path(self, *kwargs):
    #     print('Updating the show_path!')
    #     self.root_screen.show_path.text = "..."+str(books_path[-18:])
    # pass


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


kv = "speed_read.kv"
Builder.load_file(kv)

''' Build main app '''
class Speed_Read_R(MDApp):    
    def build(self):
        self.root_screen = RootScreen()
        self.screen_manager = self.root_screen.screen_manager
        self.settings_screen = SettingsScreen(name="sett",
            )
        self.reader_screen = ReaderScreen(name="reader")
        self.books_screen = BooksScreen(name="books")
        self.clipboard_screen = ClipScreen(name="clipboard")
        self.donations_screen = DonationsScreen(name="donations")
        self.themes_screen = ThemesScreen(name="themes")
        
        properties = ["reader_text_size", "blink_toggle", "blink_fade", "bg_text_size", "l_w_delay", "comma_delay", "pointer", "wpm", "progress_bar", "dot_delay", "blink_delay", "blink_interval", "accel", "blink_fade_toggle", "blink_color", "s1", "pager_sett_l", "pager_sett", "pager_sett_r"]

        for p in properties:
            # exec(f"self.main_screen.{p} = self.settings_screen.{p}")
            exec(f"self.root_screen.{p} = self.settings_screen.{p}")
        
        # self.root_screen.add_widget(self.screen_manager)
        # self.screen_manager.add_widget(self.main_screen)
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
        # on window size, set the size of the text
        # def _on_window_resize(window, width, height):
        #     print('hey')
        # Window.bind(on_resize=_on_window_resize)
        print("setting slot")
        Clock.schedule_once(self._set_slot, 2)
        print("slot setted")
        print('building app again')
        # path = os.path.join(os.getcwd(), "speed_read_r.kv")
        # Builder.load_file(path)
        print("update wpm")
        self.update_WPM()
        print("wpm updated")
        if current_book:
            print("opening current book")
            self.open_book(current_book)
            print("current book opened")

            # self.set_cursor()
            # self.reader_screen.grid_pager.children[0].focus = True

            # self.reader_screen.grid_pager.children[0].cursor = self.reader_screen.grid_pager.children[0].get_cursor_from_index(indx)

        # self.create_toolbar("Title")
        # self.select_screen("reader")
        print("returning root_screen")
        return self.root_screen
        # return self.screen_manager
        # return self.main_screen

    def select_screen(self, screen, name, *kwargs):
        print("SELF: ", self)
        # print("OBJ: ", obj)
        print("SCREEN: ", screen)
        # self.screen_manager.current = screen
        self.screen_manager.current = screen
        self.create_toolbar(screen, name)
    
    def create_toolbar(self, title, name):
        # if "toolbar" not in dir(self.main_screen):
        # print(self.screen_manager.current)
        print("TITLE: ", title)
        if "toolbar" not in dir(self.root_screen):
            print("Creating toolbar")
            toolbar = MDTopAppBar(title="Speed Read-R / " + name,
            id="topbar",
            pos_hint={'top': 1},
            left_action_items=[["menu", lambda x: self.nav_drawer_open()]]
                )
            self.root_screen.add_widget(toolbar)
            self.root_screen.toolbar = toolbar
        elif name == "":
            toolbar = self.root_screen.toolbar
            toolbar.title = "Speed Read-R / " + current_book
        else:
            print("Modifying toolbar")
            # toolbar = self.main_screen.toolbar
            toolbar = self.root_screen.toolbar
            toolbar.title = "Speed Read-R / " + name
    
    def nav_drawer_open(self):
        # nav_drawer = self.root.children[0].ids.nav_drawer
        nav_drawer = self.root_screen.nav_drawer
        # print("WTF", self.root_screen.nav_drawer.show_path)
        self.root_screen.content_navigation.show_path.text = "..."+str(books_path[-18:])
        nav_drawer.set_state("open")
        pass










    def post_slot(self, *kwargs):
        global current_slot
        exec(f"self.settings_screen.{current_slot}.state = 'down'")
    

    # def build(self):
    #     self.screen_manager = F.ScreenManager()
    #     self.main_screen = MainScreen(name='Test')
    #     self.screen_manager.add_widget(self.main_screen)
    #     print(self.main_screen.show_path)
    #     Builder.load_string(kv)
    #     def print_some_property(*args):
    #         print(self.main_screen.show_path.text)
    #     Clock.schedule_once(print_some_property, 3)
    #     return self.screen_manager
    
    def _set_slot(self, *kwargs):
        print('Setting the slot!')
        self.set_slot(current_slot)
        self.update_WPM()
    
    def keep_button_up(self, *kwargs):
        if kwargs[1] == "normal" and kwargs[2] == "normal":
            self.settings_screen.ids[kwargs[0]].state = "down"

    @mainthread
    def update_WPM(self, *kwargs):
        global global_settings
        global current_slot
        if self.root_screen.ids.screen_manager.current == "sett":
            self.settings_screen.ids.wpm.text = str(global_settings[current_slot]["wpm"])
        self.reader_screen.ids.display_wpm.text = str(global_settings[current_slot]["wpm"])
    
    def set_slot(self, slot, *kwargs):
        global global_settings
        global current_slot
        try:
            db.execute("UPDATE active SET setting_active = ?", [slot])
            con.commit()
            current_slot = slot
        except:
            print("Config File Error (set_slot)")
        print('Starting post_settings')
        self.post_settings(slot)
        print('Finished post_settings')

        print('Starting reader_sett_set_size')
        self.reader_sett_set_size(slot)
        print('Finished reader_sett_set_size')

        print('Starting set_timed')
        set_timed()
        print('Finished set_timed')

        print('Starting show_pointer')
        self.show_pointer()
        print('Finished show_pointer')

    @mainthread
    def set_cursor(self):
        self.reader_screen.grid_pager.children[0].focus = True

        self.reader_screen.grid_pager.children[0].cursor = self.reader_screen.grid_pager.children[0].get_cursor_from_index(indx)
        

    def post_settings(self, *kwargs):
        global posting
        global global_settings
        global current_slot
        posting = True
        switches = ["pointer", "progress_bar", "blink_toggle", "blink_fade_toggle", "blink_color"]
        
        # for key in settings:
        for key in set(global_settings[current_slot]) - {"active", "blink_color"}:
        # for key in settings if key != "active" else ...:
            # if value == digit, write ids[key].root
            # else
            print(key)
            print(type(key))
            from kivy.app import App
            try:
                if key not in switches:
                    # if str(global_settings[current_slot][key]).isdigit():
                    # self.main_screen.ids[key].text = str(int(global_settings[current_slot][key]))
                    # var = App.get_running_app().root.get_screen('Main Screen').ids['show_path']
                    print("posting text setting = ", key)
                    # print("1) What is this: ", var, type(var))
                    # print('I am going to execute this: ', f"self.main_screen.{key}.text = str(int(global_settings[current_slot][key]))")
                    exec(f"self.settings_screen.{key}.text = str(int(global_settings[current_slot][key]))")
                else:
                    # print("POSTING TEXT SETTING: ", "True" if global_settings[current_slot][key] == "1" or global_settings[current_slot][key] == "True" else "False")
                    # self.main_screen.ids[key].active = (True if global_settings[current_slot][key] == "1" or global_settings[current_slot][key] == "True" else False)
                    # var = App.get_running_app().root.get_screen('Main Screen').ids['blink_colorr']
                    print("posting Switch setting = ", key)
                    # print("2) What is this: ", var, type(var))
                    # print('I am going to execute this: ', f"self.main_screen.{key}.active = (True if global_settings[current_slot][key] == '1' or global_settings[current_slot][key] == 'True' else False)")
                    exec(f"self.settings_screen.{key}.active = (True if global_settings[current_slot][key] == '1' or global_settings[current_slot][key] == 'True' or global_settings[current_slot][key] == True else False)")
            except Exception as e:
                print("Error in post_settings: ", e)
        
        self.settings_screen.blink_color.md_bg_color = ast.literal_eval(global_settings[current_slot]["blink_color"])
        posting = False

        print('Finished posting settings!')

    def reader_sett_set_size(self, *kwargs):
        print("starting 1")
        self.settings_screen.ids.pager_sett_l.font_size = global_settings[current_slot]["reader_text_size"]
        print("starting 2")
        self.settings_screen.ids.pager_sett.font_size = global_settings[current_slot]["reader_text_size"]
        print("starting 3")
        self.settings_screen.ids.pager_sett_r.font_size = global_settings[current_slot]["reader_text_size"]
        print("starting 4")
        self.reader_screen.ids.pager_l.font_size = global_settings[current_slot]["reader_text_size"]
        print("starting 5")
        self.reader_screen.ids.pager.font_size = global_settings[current_slot]["reader_text_size"]
        print("starting 6")
        self.reader_screen.ids.pager_r.font_size = global_settings[current_slot]["reader_text_size"]
        print("starting 7")

    def show_pointer(self, *kwargs):
        global global_settings
        global current_slot
        if global_settings[current_slot]["pointer"] == True or global_settings[current_slot]["pointer"] == "True" or global_settings[current_slot]["pointer"] == "1":
            self.settings_screen.ids.marker_sett.text = "|"
            self.reader_screen.ids.marker.text = "|"
        else:
            self.settings_screen.ids.marker_sett.text = " "
            self.reader_screen.ids.marker.text = " "
    
    def set_dark(self, obj, load, *kwargs):
        if load == "load":
            self.theme_cls.theme_style = str(db.execute("SELECT dark FROM theme WHERE id = 1").fetchall()[0][0])
        else:
            db.execute("UPDATE theme SET dark = ? WHERE id = 1", ["Dark" if self.theme_cls.theme_style != "Dark" else "Light"])
            con.commit()

            self.theme_cls.theme_style = "Dark" if self.theme_cls.theme_style != "Dark" else "Light"

    def set_theme(self, obj, theme, *kwargs):
        if theme != "":
            self.theme_cls.primary_palette = theme
            db.execute("UPDATE theme SET color = ? WHERE id = 1", [theme])
            con.commit()
            self.snack(self, "Restart the app to properly apply changes")
        else:
            self.theme_cls.primary_palette = str(db.execute("SELECT color FROM theme WHERE id = 1").fetchall()[0][0])

    def set_hue(self, obj, hue, *kwargs):
        if hue != "":
            self.theme_cls.primary_hue = hue
            db.execute("UPDATE theme SET hue = ?  WHERE id = 1", [hue])
            con.commit()
            self.snack(self, "Restart the app to properly apply changes")
        else:
            self.theme_cls.primary_hue = str(db.execute("SELECT hue FROM theme WHERE id = 1").fetchall()[0][0])

    def open_color_picker(self):
        color_picker = MDColorPicker(size_hint=(0.45, 0.85),
        type_color="RGBA")
        color_picker.open()
        color_picker.bind(
            on_select_color=self.on_select_color,
            on_release=self.get_selected_color,
        )

    def update_color(self, color: list) -> None:
        global db
        global con
        global current_slot
        db.execute("UPDATE settings SET blink_color = ? WHERE active = ?",[str(color), current_slot])
        con.commit()
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
        quote = "0x177d49b81dED8Ff0CC59e8c1cc4F297e273f53D7"
        match site:
            # it will open google window in your browser
            case "crypto":
                Clipboard.put(quote, 'TEXT')
                self.snack(self, "Address copied to clipboard")
            case "coindrop":
                webbrowser.open('https://coindrop.to/loudbeat')
            case "kofi":
                webbrowser.open('https://ko-fi.com/loudbeat')
            case "coffee":
                webbrowser.open('https://www.buymeacoffee.com/loudbeat')
            case "ig":
                webbrowser.open('https://www.instagram.com/loudbeat/')
            case "paypal":
                webbrowser.open('https://www.paypal.com/donate/?hosted_button_id=6LUSPTKGZFWCJ')

    def snack(self, obj, pop_text, *kwargs):
        Snackbar(
            text=pop_text,
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=.7
            ).open()

    def _keydown(self, obj, key, *args):
        pass
        
    ''' Catch up keypress S = speed up +10 wpm, D = decrease -10 wpm, F = toggle fullscreen reader, Space = Play/Pause reader and settings reader'''
    def _keyup(self, obj, key, *args):
        global play
        global play_sett
        print("key pressed: ", key)
        sm = self.screen_manager.current
        print(sm)
        if key == 32 and sm == "reader":
            if play:
                self.reader_screen.ids.p_button.icon = "play-circle"
                play = False
            else:
                play = True
                self.reader_screen.ids.p_button.icon = "pause-circle"
                Thread(target = self.play_reader).start()
        if key == 32 and sm == "sett":
            if play_sett:
                play_sett = False
            else:
                play_sett = True
                Thread(target = self.play_reader_sett).start()
        if key == 115:
            Thread(target = self.speed_up).start()
        if key == 100:
            Thread(target = self.speed_down).start()
        if key == 102:
            Thread(target = self.full_screen).start()
            

    def speed_up(self):
        global global_settings
        global current_slot
        global db
        global con
        
        global_settings[current_slot]["wpm"] = int(global_settings[current_slot]["wpm"]) + 10
        
        Clock.schedule_once(
            lambda x: db.execute("UPDATE settings SET wpm = ? WHERE active = ?", [global_settings[current_slot]["wpm"], current_slot])
            )
        Clock.schedule_once(
            lambda x: con.commit()
            )
        
        set_timed()
        
        self.update_WPM(self)

    def speed_down(self):
        global global_settings
        global current_slot
        global db
        global con
        
        global_settings[current_slot]["wpm"] = int(global_settings[current_slot]["wpm"]) - 10
        
        Clock.schedule_once(
            lambda x: db.execute("UPDATE settings SET wpm = ? WHERE active = ?", [global_settings[current_slot]["wpm"], current_slot])
            )
        Clock.schedule_once(
            lambda x: con.commit()
            )
        
        set_timed()
        
        self.update_WPM(self)

    def full_screen(self, *kwargs):
        self.reader_screen.fullscreen_button.dispatch("on_release")

    def blink(self, start_time, blink_color, blinker):
        global timed
        global global_settings
        global current_slot
        
        if (global_settings[current_slot]["blink_fade_toggle"] == True or global_settings[current_slot]["blink_fade_toggle"] == "True" or global_settings[current_slot]["blink_fade_toggle"] == "1") and blink_color[3] > 0:
            blink_color[3] = 1 - ((time.time() - start_time) / int(global_settings[current_slot]["blink_fade"]))
        elif (global_settings[current_slot]["blink_fade_toggle"] == True or global_settings[current_slot]["blink_fade_toggle"] == "True" or global_settings[current_slot]["blink_fade_toggle"] == "1") and blink_color[3] < 0:
            blink_color[3] = 0
        else:
            # blink_color[3] = 0
            pass
        
        label_color = self.root.ids.pager_l.color
        if blinker == "sett":
            self.settings_screen.ids.pager_sett_l.color = blink_color
            self.settings_screen.ids.pager_sett_l.text = "—"
            self.settings_screen.ids.pager_sett.color = blink_color
            self.settings_screen.ids.pager_sett.text = "."
            self.settings_screen.ids.pager_sett_r.color = blink_color
            self.settings_screen.ids.pager_sett_r.text = "—   "
            
            time.sleep(timed["blink_delay"])
            
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
            
            time.sleep(timed["blink_delay"])
            
            self.reader_screen.ids.pager_l.color = label_color
            self.reader_screen.ids.pager.color = [0.62,0.15,0.04,1]
            self.reader_screen.ids.pager_r.color = label_color
        
        return blink_color


    def save_settings(*kwargs):
        global global_settings
        global current_slot
        global posting
        global con
        if posting:
            pass
        else:
            query = "UPDATE settings SET {} = ? WHERE active = ?".format(kwargs[1])

            db.execute(query, [kwargs[2], current_slot])
            con.commit()
            global_settings[current_slot][kwargs[1]] = kwargs[2]
            set_timed()

    def load_books(self, *kwargs):
        global bookshelf_loaded
        global books_path
        if bookshelf_loaded:
            pass
        else:
            bookshelf = db.execute("SELECT title, hash, type, indx, progress FROM bookshelf ORDER BY title").fetchall()

            for book in bookshelf:
                title = BookListLabel(text=str(book[0]), halign="left")
                data = BookListLabel(text=str(book[4]) + "%", halign="center", size_hint_x= .3)
                
                open_b = BookButton(
                    id= book[0],
                    on_release = lambda  x=book[0], *args: self.open_book(x, *args))

                self.books_screen.books_grid_2.add_widget(title)
                self.books_screen.books_grid_2.add_widget(data)
                self.books_screen.books_grid_2.add_widget(open_b)

            bookshelf_loaded = True

    def reload_bookshelf(self, *kwargs):
        global books_path
        global db
        global con
        
        files = listdir(books_path)
        
        open_library = db.execute("SELECT title, hash, type FROM bookshelf").fetchall()
        
        new_books = 0
        
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
            book_type = mimetypes.guess_type(books_path+book)[0]
            if book_type in suported:
                book_hash = md5(books_path+book)
                old = False
                
                for b in range(len(open_library)):
                    if open_library[b][1] == book_hash:
                        old = True
                        # Renamed file
                        if open_library[b][0] != book:
                            db.execute("UPDATE bookshelf SET title = ? WHERE hash = ?", [book, book_hash])
                
                for b in range(len(open_library)):
                    if open_library[b][0] == book:
                        old = True
                        # Modified file
                        if open_library[b][1] != book_hash:
                            db.execute("UPDATE bookshelf SET hash = ?, indx = 0 WHERE title = ?", [book_hash, book])

                if not old:
                    db.execute("INSERT INTO bookshelf (title, hash, type, indx, progress, marker) VALUES(?, ?, ?, ?, ?, ?)", (book, book_hash, book_type, 0, 0, "(0, 0)"))
                    con.commit()

                    new_books += 1

        if new_books >= 1:
            self.snack(self, str(new_books)+" new book/s found")
            self.unload_bookshelf(self)
            self.load_books(self)
        else:
            self.snack(self, "No book found")

    def unload_bookshelf(self, *kwargs):
        # Delete all elements from books_grid_2
        global bookshelf_loaded
        # if bookshelf_loaded:
        # row = [i for i in self.main_screen.books_grid_2.children]
        row = [i for i in self.root_screen.books_grid_2.children]
        for row1 in row:
            # self.main_screen.books_grid_2.remove_widget(row1)
            self.root_screen.books_grid_2.remove_widget(row1)
        bookshelf_loaded = False

    ''' Save text from quick text on a new file and open it on the reader '''
    def save_clip(self, obj, title, new_text, *kwargs):
        global books_path
        global current_book
        global con
        global db
        iter = 0
        if os.path.exists(books_path+title+".txt"):
            while os.path.exists(books_path+title+"_"+str(iter)+".txt"):
                iter +=1
            title = title+"_"+str(iter)
        title = title+".txt"
        with open(books_path+title, "w") as new_t:
            new_t.write(new_text)

        clip_type = mimetypes.guess_type(books_path+title)[0]
        clip_hash = md5(books_path+title)
        db.execute("INSERT INTO bookshelf (title, hash, type, indx, progress, marker) VALUES(?, ?, ?, ?, ?, ?)", (title, clip_hash, clip_type, 0, 0, "(0, 0)"))
        con.commit()
        current_book = title
        self.open_book(current_book)

        
    def file_manager_open(self):
        global books_path
        self.file_manager = FixFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            selector="folder")
        # self.file_manager.show("/home/loudbeat/VSCode/speed_read_rsvp/Books/")
        self.file_manager.show(os.path.expanduser(books_path))
        # print(os.path.expanduser(books_path))
        # self.file_manager.show(os.path.expanduser("~"))
        self.manager_open = True
    




    def select_path(self, books_pathx):
        global books_path
        global con
        '''It will be called when you click on the file name
        or the catalog selection button.

        :type path: str;
        :param path: path to the selected directory or file;
        '''

        try:
            db.execute("UPDATE active SET path = ?", [books_pathx])
            con.commit()
            books_path = books_pathx
        except:
            sys.exit("Can't load directory path settings")
        
        # self.main_screen.show_path.text = "..."+str(books_path[-18:])
        self.root_screen.show_path.text = "..."+str(books_path[-18:])
        
        self.exit_manager()
        
        toast(books_pathx)
    
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

    ''' Open selected book, parse text, load text into reader, set progress, cursor position, display title on top bar. '''
    def open_book(self, *kwargs):
        global books_path
        global book_loaded
        global open_book
        global texted_book
        global word_index
        global current_book
        global global_settings
        global current_slot
        global indx
        global index
        global con
        book_name = ""

        if book_loaded:
            self.clear_reader(self)
        if type(kwargs[0]) == str:
            book_name = current_book
        else:
            book_name = kwargs[0].id
        pages = ""

        book = db.execute("SELECT * FROM bookshelf WHERE title = ?", (book_name,)).fetchall()
        db.execute("UPDATE active SET book = ?", [book_name])
        con.commit()
        bk = ["id", "title", "hash", "type", "indx", "progress", "marker"]
        open_book = {}
        try:
            for b in range(len(bk)-1):
                open_book[bk[b+1]] = book[0][b+1]
        except:
            return

        match open_book["type"]:
            case "text/plain":
                texted_book = Parsex.text(books_path+book_name) # Read text
            case "application/epub+zip":
                texted_book = Parsex.ebook(books_path+book_name) # Read text
            case "application/pdf":
                texted_book = Parsex.pdf(books_path+book_name) # Read text
            case "text/markdown":
                texted_book = Parsex.md(books_path+book_name) # Read text
            case "application/rtf":
                texted_book = Parsex.rtf(books_path+book_name) # Read text
            case "application/x-tex":
                texted_book = Parsex.text(books_path+book_name) # Read text
            case "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                texted_book = Parsex.docx(books_path+book_name) # Read text

        try:
            open_book["length"] = len(texted_book.split())
        except:
            open_book["length"] = 0

        word_index = texted_book.split()
        
        indx = int(open_book["indx"])
        cut = texted_book[:open_book["indx"]]
        index = len(cut.split())
        
        self.reader_screen.book_length.text = f"/{open_book['length']}"
        if global_settings[current_slot]["progress_bar"] == True or global_settings[current_slot]["progress_bar"] == "1":
            if index == 0:
                open_book["progress"] = 0
                self.reader_screen.p_bar.value = open_book["progress"]
                self.reader_screen.index.text = str(0)
            else:
                open_book["progress"] = index / open_book["length"] * 100
                self.reader_screen.p_bar.value = open_book["progress"]
                self.reader_screen.index.text = str(index)
        else:
            self.reader_screen.p_bar.value = 0
            self.reader_screen.index.text = str(0)

        chunk = splitter(word_index[index], len(word_index[index]))
        self.reader_screen.pager_l.text = str(chunk[0])
        self.reader_screen.pager.text = str(chunk[1])
        self.reader_screen.pager_r.text = str(chunk[2])
        
        tf = TextInput(
            font_size = global_settings[current_slot]["bg_text_size"],
            multiline = True,
            readonly = True,
            text = str(texted_book),
            background_color = [0,0,0,0],
            foreground_color = ([.15,.15,.15,1] if self.theme_cls.theme_style != "Dark" else "gray"),
            allow_copy = True,
            on_double_tap = lambda *x: self.click_text())

        self.reader_screen.grid_pager.add_widget(tf)
        book_loaded = True

        # self.screen_manager.current = "reader"
        self.select_screen("reader", book_name)

        # self.root_screen.topbar.title = "Speed Read-R / " + book_name
        
        # self.reader_screen.grid_pager.children[0].focus = True
        self.set_cursor()

        Clock.schedule_once(
            lambda x: self.reader_screen.grid_pager.children[0].select_text(indx, indx+len(word_index[index])
            ))

    def clear_reader(self, *kwargs):
        global book_loaded
        
        if book_loaded:
            self.reader_screen.grid_pager.clear_widgets(children=None)
            book_loaded = False

    ''' Set new position for the reader. '''
    def click_text(self, *kwargs):
        global old_index
        global current_book
        global texted_book
        global global_settings
        global current_slot
        global indx
        global index
        global con
        global db
        
        new_index = self.reader_screen.ids.grid_pager.children[0].cursor_index(self.reader_screen.ids.grid_pager.children[0].cursor)
        
        if new_index != old_index:
            old_index = new_index
            while texted_book[new_index-1] != " ":
                if texted_book[new_index-1] == "\n" or new_index == 0:
                    break
                new_index = new_index - 1
            indx = new_index
            
            db.execute("UPDATE bookshelf SET indx = ? WHERE title = ?", [indx, current_book])
            con.commit()
            
            cut = texted_book[:indx]
            index = len(cut.split())
            open_book["progress"] = index / open_book["length"] * 100
            
            db.execute("UPDATE bookshelf SET progress = ? WHERE title = ?", [int(open_book["progress"]), current_book])
            con.commit()
            
            if global_settings[current_slot]["progress_bar"]:
                self.reader_screen.ids.p_bar.value = open_book["progress"]
                self.reader_screen.ids.index.text = str(index)

            chunk = splitter(word_index[index], len(word_index[index]))
            self.reader_screen.ids.pager_l.text = str(chunk[0])
            self.reader_screen.ids.pager.text = str(chunk[1])
            self.reader_screen.ids.pager_r.text = str(chunk[2])

    ''' Iterate through words while play = True'''
    def play_reader(self, *args):
        global play
        global texted_book
        global word_index
        global current_book
        global global_settings
        global current_slot
        global indx
        global index
        global p_words
        start_acc = False
        start_blink = False
        print("STARTING READER")
        word_count = len(word_index)
        if int(global_settings[current_slot]["accel"]) > 0:
            start_acc = True
            acceleration = time.time()
        if global_settings[current_slot]["blink_toggle"] == True or global_settings[current_slot]["blink_toggle"] == "True" or global_settings[current_slot]["blink_toggle"] == "1":
            start_blink = True
            # start_acc = True
            start_blink_t = time.time()
            loop_blink_t = time.time()
            blink_color = ast.literal_eval(global_settings[current_slot]["blink_color"])
        play_start = time.time()

        try:
            while play and index < word_count:
                length = len(word_index[index])
                chunk = splitter(word_index[index], length)
                self.reader_screen.pager_l.text = str(chunk[0])
                self.reader_screen.pager.text = str(chunk[1])
                self.reader_screen.pager_r.text = str(chunk[2])

                Clock.schedule_once(
                    lambda x: self.reader_screen.grid_pager.children[0].select_text(indx, indx+length)
                    )

                self.reader_screen.grid_pager.children[0].cursor = self.reader_screen.grid_pager.children[0].get_cursor_from_index(indx)
                
                delay(word_index[index], length)
                
                if start_acc == True:
                    if time.time()-acceleration < int(global_settings[current_slot]["accel"]):
                        accel(acceleration)
                    else:
                        start_acc = False
                if start_blink == True:
                    if time.time() - loop_blink_t > int(global_settings[current_slot]["blink_interval"]):
                        blink_color = self.blink(start_blink_t, blink_color, "player")
                        loop_blink_t = time.time()
                
                indx += length
                while texted_book[indx] == " " or texted_book[indx] == "\n":
                    indx += 1
                index += 1
                
                open_book["progress"] = index / open_book["length"] * 100

                self.update_progress(int(indx), int(open_book["progress"]))

                if global_settings[current_slot]["progress_bar"] == True or global_settings[current_slot]["progress_bar"] == "True" or global_settings[current_slot]["progress_bar"] == "1":
                    self.reader_screen.p_bar.value = open_book["progress"]
                    self.time_left(self, index, word_count, play_start)
                    self.reader_screen.index.text = str(index)
        
        except KeyboardInterrupt:
            pass
        
        play = False
        p_words = 0
    
    ''' Open settings.txt, read settings, Iterate through words, update settings reader. '''
    def play_reader_sett(self, *args):
        global play_sett
        global global_settings
        global current_slot
        # global books_path
        start_acc = False
        start_blink = False
        if int(global_settings[current_slot]["accel"]) > 0:
            start_acc = True
            acceleration = time.time()
        
        if global_settings[current_slot]["blink_toggle"] == True or global_settings[current_slot]["blink_toggle"] == "True" or global_settings[current_slot]["blink_toggle"] == "1":
            start_blink = True
            start_blink_t = time.time()
            loop_blink_t = time.time()
            blink_color = ast.literal_eval(global_settings[current_slot]["blink_color"])
        
        indx_sett = 0
        play_settings = ""
        
        with open("./config/settings.txt", "r") as st:
            play_settings = st.read()
        
        play_words = play_settings.split() # listed words
        
        play_length = len(play_words) # Total length

        chunk_sett = splitter(play_words[indx_sett], len(play_words[indx_sett])) # first render
        # self.main_screen.pager_sett_l.text = str(chunk_sett[0])
        # self.main_screen.pager_sett.text = str(chunk_sett[1])
        # self.main_screen.pager_sett_r.text = str(chunk_sett[2])
        self.root_screen.pager_sett_l.text = str(chunk_sett[0])
        self.root_screen.pager_sett.text = str(chunk_sett[1])
        self.root_screen.pager_sett_r.text = str(chunk_sett[2])
        try:
            while play_sett:
                length = len(play_words[indx_sett]) # current word length
                chunk_sett = splitter(play_words[indx_sett], length) # splitter
                # self.main_screen.pager_sett_l.text = str(chunk_sett[0])
                # self.main_screen.pager_sett_l.text = str(chunk_sett[0])
                # self.main_screen.pager_sett.text = str(chunk_sett[1])
                self.root_screen.pager_sett.text = str(chunk_sett[1])
                self.root_screen.pager_sett_r.text = str(chunk_sett[2])
                self.root_screen.pager_sett_r.text = str(chunk_sett[2])

                delay(play_words[indx_sett], length)
                indx_sett +=1
                if start_acc == True:
                    if time.time()-acceleration < int(global_settings[current_slot]["accel"]):
                        accel(acceleration)
                    else:
                        start_acc = False
                
                if start_blink == True:
                    if time.time() - loop_blink_t > int(global_settings[current_slot]["blink_interval"]):
                        blink_color = self.blink(start_blink_t, blink_color, "sett")
                        loop_blink_t = time.time()
                
                # Loop text
                if indx_sett == play_length:
                    indx_sett = 0
                    continue
        except KeyboardInterrupt:
            pass
        play_sett = False

    @mainthread
    def update_progress(self, indx, progress, *kwargs):
        global db
        global con
        db.execute("UPDATE bookshelf SET indx = ?, progress = ? WHERE title = ?", [indx, progress, current_book])
        con.commit()

    ''' Calculate average time left from current speed/remaining length and current played words/elapsed time. '''
    def time_left(self, obj, index, word_count, play_start, *kwargs):
        global global_settings
        global current_slot
        global p_words
        words_left = word_count - index
        
        p_words += 1
        
        execution_left = (time.time() - play_start)/ p_words * words_left
        
        time_left = words_left / int(global_settings[current_slot]["wpm"]) * 100 / 60
        
        t_left = (time_left + execution_left/60)/2
        
        hours = t_left / 60
        minutes = t_left % 60
        seconds = minutes / 60
        
        t = f"{str(int(hours)).zfill(2)}:{str(int(minutes)).zfill(2)}"
        self.reader_screen.ids.time_left.text = t


class FixFileManager(MDFileManager):
    def back(self) -> None:
        """Returning to the branch down in the directory tree."""

        if self.current_path[-1:] == "/":
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

    ''' Parse text into string according to file format. '''
class Parsex():
    def text(f_path):
        text = ""
        with open(f_path, "r") as f:
            text = f.read()
        return(return_x(text))

    def pdf(f_path):
        reader = PdfReader(f_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return(return_x(text))

    def ebook(f_path):
        text = ""
        t = ""
        book = epub.read_epub(f_path)
        items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        for i in items:
            soup = BeautifulSoup(i.get_body_content(), "html.parser")
            t = t + "\n".join([para.get_text() for para in soup.find_all("p")])
            text = t
        return(return_x(text))
    
    def md(f_path):
        with open(f_path, "r") as md_file:
            md_text = md_file.read()
            html = markdown(md_text)
            soup = BeautifulSoup(html, features="html.parser")
            text = soup.get_text()
            return(return_x(text))
    
    def docx(f_path):
        with zipfile.ZipFile(f_path, 'r') as unzipped:
            with unzipped.open('word/document.xml') as docu:
                text = BeautifulSoup(docu.read(), 'xml')
        return(return_x(text))
    
    def odt(f_path):
        return Parsex.docx(f_path)
    
    def rtf(f_path):
        rtf = ""
        with open(f_path, "r") as f:
            rtf = f.read()
            text = rtf_to_text(rtf)
        return(return_x(text))

def return_x(text):
    return text if text != None else "Couldn't extract text"


''' Convert settings digits to millisecond '''
def set_timed():
    global timed
    t = ["l_w_delay", "dot_delay", "comma_delay", "blink_delay"]
    
    for s in t:
        timed[s] = int(global_settings[current_slot][s]) / 1000
    
    if int(global_settings[current_slot]["l_w_delay"]) > 0:
        timed["step"] = 60 / int(global_settings[current_slot]["wpm"]) / (int(global_settings[current_slot]["l_w_delay"]) / 10)
    
    if int(global_settings[current_slot]["l_w_delay"]) <= 0:
        timed["step"] = 60 / int(global_settings[current_slot]["wpm"])

""" Hash the files to reference it by its content and know if they were modified to reset the index, otherwise can get index out of range error."""
def md5(filename):
    h  = hashlib.md5()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()


''' Load settings reader text if it doesn't exist. '''
def create_settings():
    comp_settings = "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"

    decoded_sett = zlib.decompress(base64.b64decode(comp_settings))

    try:
        with open("./config/settings.txt", "w") as new_settings:
            new_settings.write(decoded_sett.decode("utf-8"))
    except:
        sys.exit("Coudn't write new reader settings file")


''' Split words into left/center/right depending on length'''
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
        #4th
    elif length <= 17:
        return [word[:4], word[4:5], word[5:]]
        #4th
    else:
        return [word[:5], word[5:6], word[6:]]
        #5th

def delay(word, length):
    global global_settings
    global current_slot
    global timed
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

def accel(secs):
    global global_settings
    
    t1 = time.time() - secs # Elapsed time
    
    if t1 < int(global_settings[current_slot]["accel"]):
        d = (int(global_settings[current_slot]["accel"]) - t1) * 10 / 1000
        # print("ACC DELAY: ", d)
        time.sleep(d)
    # secs -= time.time()
    # d = secs * 3 / 1000
    # return secs


''' Load all the settings, create files if don't exist. '''
def load_settings():
    global global_settings
    global current_slot
    global books_path
    global current_book
    global db
    global con
    
    Path("./config").mkdir(parents=True, exist_ok=True)

    config_path = os.listdir(os.path.join("./config", ''))
    
    if not "settings.txt" in config_path:
        create_settings()
    
    if not "settings.db" in config_path:
        try:
            # CREATING CONFIG...
            con = sqlite3.connect("./config/settings.db")
            db = con.cursor()
            con.commit()
            
            db.execute("CREATE TABLE bookshelf(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, title TEXT, hash TEXT, type TEXT, indx INTEGER, progress INTEGER, marker TEXT)")
            con.commit()
            
            db.execute("CREATE TABLE settings(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,active TEXT, bg_text_size INTEGER, reader_text_size INTEGER, wpm INTEGER, accel INTEGER, pointer  TEXT, l_w_delay INTEGER, dot_delay INTEGER, comma_delay INTEGER, progress_bar TEXT, blink_toggle TEXT, blink_interval INTEGER, blink_delay INTEGER, blink_color TEXT, blink_fade_toggle TEXT, blink_fade INTEGER)")
            con.commit()
            
            db.execute("CREATE TABLE active(setting_active TEXT, path TEXT, book TEXT)")
            con.commit()
            
            db.execute("CREATE TABLE theme(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, dark TEXT, color TEXT, hue TEXT)")
            con.commit()
            
            for i in range(3):
                db.execute("INSERT INTO settings(active, bg_text_size, reader_text_size, wpm, accel, pointer, l_w_delay, dot_delay, comma_delay, progress_bar, blink_toggle, blink_interval, blink_delay, blink_color, blink_fade_toggle, blink_fade) Values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ("s"+str((i+1)), 18, 40, 450, 5, "True", 50, 10, 10, "True", "True", 5, 500, "[0.62, 0.15, 0.04, 1]", "True", 30))
                con.commit()
            
            def_path = path.abspath("./Books/")
            def_path = os.path.join(def_path, '')
            
            db.execute("INSERT INTO active(setting_active, path, book) VALUES(?, ?, ?)", ("s1", def_path, "Readme.txt"))
            con.commit()
            
            db.execute("INSERT INTO theme (id, dark, color, hue) VALUES('1', 'Dark', 'Purple', '200')")
            con.commit()

        except:
            sys.exit("Config file error")
            ...
        # CONFIG CREATED...
    
    # LOAD CONFIG TO MEMORY...
    try:
        con = sqlite3.connect("./config/settings.db")
        db = con.cursor()
        
        sett = ["id", "active", "bg_text_size", "reader_text_size", "wpm", "accel", "pointer", "l_w_delay", "dot_delay", "comma_delay", "progress_bar", "blink_toggle", "blink_interval", "blink_delay", "blink_color", "blink_fade_toggle", "blink_fade"]
        
        setting = db.execute("SELECT * FROM settings").fetchall()

        db.execute("UPDATE active SET setting_active = 's1'")
        con.commit()
        
        global_settings = {"s1":{},"s2":{},"s3":{}}
        
        for i in range(3):
            for j in range(len(sett)-1):
                global_settings["s"+str(i+1)][str(sett[j+1])] = setting[i][j+1]
        
        current_slot = db.execute("SELECT setting_active FROM active").fetchone()[0]
        books_path = db.execute("SELECT path FROM active").fetchone()[0]
        current_book = str(db.execute("SELECT book FROM active").fetchone()[0])
        set_timed()
        
    except Exception as e:
        print(e)
        sys.exit("Config file error")
    
    Path(books_path).mkdir(parents=True, exist_ok=True)
    
    # SETTINGS LOADED...
    # starting global variables and db fix.

def main():
    load_settings()
    Speed_Read_R().run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
