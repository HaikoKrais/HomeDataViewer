# -*- coding: utf-8 -*-
'''
Visualizes temperature and humidity in rooms and provides a weather forecast.

Classes:
    MyScreens: Used to switch between the screens which provide the different contents
    Scrn1: Start screen of the app. Provides navigation to the other screens
    Scrn2: Shows temperatrue and humidity. Uses Two_Scales_Widget
    Two_Scales_Widget: Widget providing functions to get temperature and humidity of a room and to visualize it
    Scrn3: Shows the current weather at a selectable location as well as a five day forecast. Uses Weather_Widget
    Weather_Widget: Widget providing functions to get and visualize the weather and forecast for a location
    Scrn4: Shows the temperature and humidity graph of the last 24 hours. Uses TwoPlotWidgets
    TwoPlotsWidget: Matplotlib Backend visualizing two graphs with shared x-Axis
    Scrn5: Shows a corona widget displaying current and cumulative infections

See details and more explanations at: http://kraisnet.de/index.php/gebaeudedaten-erfassen-und-mit-kivy-visualisieren-2/18-gebaeudedaten-erfassen-und-mit-kivy-visualisieren
'''

import json
import os
from datetime import datetime
from time import mktime, strptime
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.settings import SettingsWithSidebar
from TwoScalesWidgetApp import TwoScalesWidget as TwoScalesWidget
from WeatherWidgetApp import WeatherWidget as WeatherWidget
from TwoPlotsSharedXWidgetApp import TwoPlotsSharedXWidget as TwoPlotsSharedXWidget
from CoronaWidgetApp import CoronaWidget as CoronaWidget
from PollenWidgetApp import PollenWidget as PollenWidget
from kivy.resources import resource_add_path


class MyScreens(ScreenManager):
    '''
    The ScreenManager MyScreens takes care of changing between the available screens
    The functions goto_screen_1 .... can be called by all elements on the screens
    '''

    def __init__(self, **kwargs):
        '''__init__() can perform actions on instantiation. None so far'''
        super(MyScreens, self).__init__(**kwargs)

    def goto_scrn1(self):
        '''Switches to screen 1'''
        self.current = 'scrn1'

    def goto_scrn2(self):
        '''switches to screen 2'''
        self.current = 'scrn2'

    def goto_scrn3(self):
        '''switches to screen 3'''
        self.current = 'scrn3'

    def goto_scrn4(self):
        '''switches to screen 4'''
        self.current = 'scrn4'

    def goto_scrn5(self):
        '''switches to screen 5'''
        self.current = 'scrn5'

    def goto_scrn6(self):
        '''switches to screen 5'''
        self.current = 'scrn6'


class Scrn1(Screen):
    '''
    Shows the start screen

    Attributes:
        None
    '''
    pass


class Scrn2(Screen):
    '''
    Shows the screen containing the temperature and humidity widget

    Attributes:
        None
    '''

    def __init__(self, **kwargs):
        '''
        Start updating the screen regularly.

        A clock will call the update function in a selectable interval.
        Put all functions you want to update into the update function

        Args:
            **kwargs (): not used. For further development.

        Returns:
            Nothing.
        '''
        super(Scrn2, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 60)
        Clock.schedule_once(self.update)

    def update(self, dt):
        '''
        calls funtions to update the screen.

        Args:
            dt (int): interval in seconds in which the funtion will be called

        Returns:
            (float): Scaled value.
        '''
        low1 = float(App.get_running_app().config.get('Two Scales Widget', 'temp_lower_limit'))
        high1 = float(App.get_running_app().config.get('Two Scales Widget', 'temp_upper_limit'))
        low2 = float(App.get_running_app().config.get('Two Scales Widget', 'humidity_lower_limit'))
        high2 = float(App.get_running_app().config.get('Two Scales Widget', 'humidity_upper_limit'))

        fileDir = os.path.dirname(os.path.abspath(__file__))
        absFilename = os.path.join(fileDir, 'data.json')

        self.ids.widget1.show_data(filename=absFilename, low1=low1, high1=high1, low2=low2, high2=high2)


class Scrn3(Screen):
    def __init__(self, **kwargs):
        '''
        Start updating the screen regularly.

        A clock will call the update function in a selectable interval.
        Put all functions you want to update into the update function

        Args:
            **kwargs (): not used. For further development.

        Returns:
            Nothing.
        '''
        super(Scrn3, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 1800)
        Clock.schedule_once(self.update)

    def update(self, dt):
        '''
        calls funtions to update the screen.

        Args:
            dt (int): interval in seconds in which the funtion will be called

        Returns:
            (float): Scaled value.
        '''
        city = App.get_running_app().config.get('Weather Widget', 'city')
        self.ids.widget1.download_current_weather(city=city)
        self.ids.widget1.download_forecast(city=city)


class Scrn4(Screen):

#TODO: Make a proper App out of this script

    timestamp = ListProperty([])
    temperature = ListProperty([])
    humidity = ListProperty([])

    def __init__(self, **kwargs):
        super(Scrn4, self).__init__(**kwargs)
        '''
        Start updating the screen regularly.

        A clock will call the update function in a selectable interval.
        Put all functions you want to update into the update function

        Args:
            **kwargs (): not used. For further development.

        Returns:
            Nothing.
        '''
        Clock.schedule_interval(self.update, 600)
        Clock.schedule_once(self.update)

    def update(self, dt):
        '''
        calls funtions to update the screen.

        Args:
            dt (int): interval in seconds in which the funtion will be called

        Returns:
            (float): Scaled value.
        '''

        # Read the data to show from a file and store it
        fileDir = os.path.dirname(os.path.abspath(__file__))
        absFilename = os.path.join(fileDir, 'seven_day_data.json')

        try:
            with open(absFilename, 'r') as read_file:
                data = json.load(read_file)
        except FileNotFoundError:
            print('File not found for temperature and humidity graph')
            return

        self.timestamp.clear()
        self.temperature.clear()
        self.humidity.clear()

        for index in data:
            self.timestamp.append(datetime.fromtimestamp(mktime(strptime(index['time_code'], '%Y-%m-%d %H:%M:%S'))))
            self.temperature.append(float(index['temperature']))
            self.humidity.append(float(index['humidity']))

        self.ids.widget1.update_plot()


class Scrn5(Screen):
    def __init__(self, **kwargs):
        super(Scrn5, self).__init__(**kwargs)
        '''
        Shows the corona widget.

        A clock will call the update function in a selectable interval.
        Put all functions you want to update into the update function.
        During init is the update() function called. This will download the current dataset from
        the ECDC. The data ist updated once a day. So the interval should be large enough.

        Args:
            **kwargs (): not used. For further development.

        Returns:
            Nothing.
        '''
        Clock.schedule_interval(self.update, 86400)
        Clock.schedule_once(self.update)

    def update(self, dt):
        '''
        calls funtions to update the screen.

        Args:
            dt (int): interval in seconds in which the funtion will be called

        Returns:
            (float): Scaled value.
        '''

        self.ids['wdgt1'].download_data_infection()
        self.ids['wdgt1'].download_data_vaccination()


class Scrn6(Screen):
    def __init__(self, **kwargs):
        super(Scrn6, self).__init__(**kwargs)
        '''
        Shows the corona widget.

        A clock will call the update function in a selectable interval.
        Put all functions you want to update into the update function.
        During init is the update() function called. This will download the current dataset from
        the ECDC. The data ist updated once a day. So the interval should be large enough.

        Args:
            **kwargs (): not used. For further development.

        Returns:
            Nothing.
        '''
        Clock.schedule_interval(self.update, 86400)
        Clock.schedule_once(self.update)

    def update(self, dt):
        '''
        calls funtions to update the screen.

        Args:
            dt (int): interval in seconds in which the funtion will be called

        Returns:
            (float): Scaled value.
        '''

        self.ids['wdgt1'].download_dataset(url='https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json')


class MyVisuApp(App):
    def build(self):
        '''
        overwrites the build() function.

        The appearance of the settings is set here.
        Choose from the available layouts: https://kivy.org/doc/stable/api-kivy.uix.settings.html#different-panel-layouts
        The preset values for the settings are loaded by the config.read() function

        Args:
            None

        Returns:
            class MyScreens().
        '''

        self.settings_cls = SettingsWithSidebar

        fileDir = os.path.dirname(os.path.abspath(__file__))
        absFilename = os.path.join(fileDir, 'mysettings.ini')
        self.config.read(absFilename)
        return MyScreens()

    def build_settings(self, settings):
        '''
        overwrites the build_settings() function.

        Add all necessary panels here by loading from the corresponding file.

        Args:
            settings

        Returns:
            Nothing.
        '''

        fileDir = os.path.dirname(os.path.abspath(__file__))
        absFilename1 = os.path.join(fileDir, 'settings_weather_widget.json')
        absFilename2 = os.path.join(fileDir, 'settings_two_scales_widget.json')
        settings.add_json_panel('Weather Widget', self.config, absFilename1)
        settings.add_json_panel('Two Scales Widget', self.config, absFilename2)

    def on_config_change(self, config, section, key, value):
        '''
        overwrites the on_config_change() function.

        define actions that shall happen when specific entries in the configuration change here.

        Args:
            config (kivy.config.ConfigParser):
                current configuration.
            section (str):
                name of the section where the key belongs to.
            key (str):
                key as specified in the json panels.
            value ():
                value of the key. return value depending on the type of variable.

        Returns:
            class MyScreens().
        '''
        app = self.get_running_app()

        if key == 'city':
            app.root.ids['scrn3'].update(1)
        if section == 'Two Scales Widget':
            app.root.ids['scrn2'].update(1)


if __name__ == '__main__':
    resource_add_path(r'C:\Users\49172\PycharmProjects')
    MyVisuApp().run()
