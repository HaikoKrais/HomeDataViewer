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

See details and more explanations at: http://kraisnet.de/index.php/gebaeudedaten-erfassen-und-mit-kivy-visualisieren-2/18-gebaeudedaten-erfassen-und-mit-kivy-visualisieren
'''

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.clock import Clock
import json
import urllib.request
from time import gmtime, strftime, mktime, strptime
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import matplotlib.dates as dt
from datetime import datetime
from kivy.uix.settings import SettingsWithSidebar

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
        self.current='scrn1'

    def goto_scrn2(self):
        '''switches to screen 2'''
        self.current='scrn2'

    def goto_scrn3(self):
        '''switches to screen 3'''
        self.current='scrn3'
        
    def goto_scrn4(self):
        '''switches to screen 4'''
        self.current='scrn4'

        
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
        Clock.schedule_interval(self.update,60)

    def update(self, dt):
        '''
        calls funtions to update the screen.

        Args:
            dt (int): interval in seconds in which the funtion will be called

        Returns:
            (float): Scaled value.
        '''
        self.ids.widget1.show_data('data.json')
                
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
        Clock.schedule_interval(self.update,1800)

    def update(self, dt):
        '''
        calls funtions to update the screen.

        Args:
            dt (int): interval in seconds in which the funtion will be called

        Returns:
            (float): Scaled value.
        '''        
        self.ids.widget1.download_data()
        self.ids.widget1.show_current_weather()
        self.ids.widget1.show_forecast()
        

class Scrn4(Screen):
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
        Clock.schedule_interval(self.update,600)

    def update(self, dt):
        '''
        calls funtions to update the screen.

        Args:
            dt (int): interval in seconds in which the funtion will be called

        Returns:
            (float): Scaled value.
        '''  
        self.ids.widget1.update_plot()

class Two_Scales_Widget(BoxLayout):
    '''
    Two donut style gauges showing values from a json file.

    Attributes:
    The attributes are bound by name to propertis in the kv file. Updating them will automatically update the displayed data in the visualisation

        num1 (NumericProperty, float):
            Angle of the first donut style gauge. Calculated from the actual value val1 and the limits.
            Initially set to 150.
        num2 (NumericProperty, float):
            Angle of the second donut style gauge. Calculated from the actual value val2 and the limits.
            Initially set to 150.
        val1 (StringProperty, str):
            Value of the first donut style gauge.
        val2 (StringProperty, str):
            Value of the second donut style gauge.
        val3 (StringProperty, str):
            Copntains the time code of the measurement.
        unit1 (StringProperty, str):
            Unit of val1. Initially set to °C
        unit2 (StringProperty, str):
            Unit of val2. Initially set to %rH
    '''
    
    num1 = NumericProperty(150)
    num2 = NumericProperty(150)
    val1 = StringProperty('--')
    val2 = StringProperty('--')
    val3 = StringProperty('--')
    unit1= StringProperty('°C')
    unit2= StringProperty('%rH')

    def show_data(self, filename):
        '''Reads limits for the settings and values from a json file and updates the bound properties of the class.

        The data is read from a json file. The data needs to be stored in the file as a dict which contains the following keys:
        - temperature
        - humidity
        - time_code

        Args:
            filename (str): Path to the file which contains the data to display.

        Returns:
            Nothing.
        '''

        #read limits for scales from settings
        num1_low = float(App.get_running_app().config.get('Two Scales Widget','temp_lower_limit'))
        num1_high = float(App.get_running_app().config.get('Two Scales Widget','temp_upper_limit'))
        num2_low = float(App.get_running_app().config.get('Two Scales Widget','humidity_lower_limit'))
        num2_high = float(App.get_running_app().config.get('Two Scales Widget','humidity_upper_limit'))
        
        #opens a json file and reads temperature and humidity
        with open(filename, 'r') as read_file:
            data=json.load(read_file)
            self.val1 = str(data['temperature'])
            self.val2 = str(data['humidity'])
            self.val3 = data['time_code']
            self.num1 = self.fit_to_scale(data['temperature'], num1_low, num1_high)
            self.num2 = self.fit_to_scale(data['humidity'], num2_low, num2_high)

    def fit_to_scale(self, value, minimum, maximum):
        '''scales the given value between the set max and min limits into an angle for the doughnut style gauge.

        Args:
            value (float): Value that shall be scaled.
            minimum (float): Minimum for scaling.
            maximum (float): Maximum for scaling.

        Returns:
            (float): Scaled value.
        '''
        
        return ((value - minimum) / (maximum - minimum) * 300) - 150

class WeatherWidget(RelativeLayout):
    '''Shows current weather and 5 day forecast based on OpenWeatherMap API.

        Attributes:
        The attributes are bound by name to propertis in the kv file. Updating them will automatically update the displayed data in the visualisation
        
        city (StringProperty, str):
            Name of the city.
            Initially set to --.
        country (StringProperty, str):
            Country code according to ISO where the city is located in.
            Initially set to --.
        temperature (StringProperty, str):
            Current temperature.
            Initially set to --.
        humidity (StringProperty, str):
            Current humidity.
            Initially set to --.
        pressure (StringProperty, str):
            Current humidity.
            Initially set to --.
        wind_speed (StringProperty, str):
            Current wind speed.
            Initially set to --.
        wind_direction (StringProperty, str):
            Current wind direction.
            Initially set to --.
        last_update (StringProperty, str):
            Time at which the data has been updated last from OpenWeatherMap.
            Initially set to --.
        notification  (StringProperty, str):
            Error string. Shows exceptions, like no data available.
            Initially set to --.
        image_source (StringProperty, str):
            url of the icon showing the current weather conditions.
            Initially set to --.
    '''

    city = StringProperty('--')
    country = StringProperty('--')
    temperature = StringProperty('--')
    humidity = StringProperty('--')
    pressure = StringProperty('--')
    wind_speed = StringProperty('--')
    wind_direction = StringProperty('--')
    last_update = StringProperty('--')
    notification = StringProperty('')
    image_source = StringProperty('')
    
    def get_http_to_json(self, url, file_name, *args, **kwargs):
        '''download json data from an url and save it as a .json file.

        Args:
            url (str): url where the data will be downloaded from.
            file_name (str): name of the file where the data will be stored. The file ending (.json) will be added automatically.
            *args (): not used. For further development.
            **kwargs (): not used. For further development.

        Returns:
            Nothing.
        '''
        
        #open the url and decode the json data
        try:
            with urllib.request.urlopen(url) as f:
                data = json.loads(f.read().decode('utf-8'))

                #build the file name to save the file
                my_filename = file_name + '.json'
                    
                #save the file
                with open(my_filename, 'w') as write_file:
                    json.dump(data, write_file)

        except urllib.error.HTTPError as e:
            print(e.code, e.read())
            self.notification = 'Internetverbindung prüfen'

        except urllib.error.URLError as e:
            print(e.reason)
            self.notification = 'Internetverbindung prüfen'

    def download_data(self, *args, **kwargs):
        '''download current weather and 5 day forecast data.

        Args:
            *args (): not used. For further development.
            **kwargs (): not used. For further development.

        Returns:
            (float): Scaled value.
        '''
        
        my_city = App.get_running_app().config.get('Weather Widget', 'city')
        
        now_url = 'http://api.openweathermap.org/data/2.5/weather?q={}de&APPID=YOUR_API_KEY_HERE'.format(my_city) 
        forecast_url = 'http://api.openweathermap.org/data/2.5/forecast?q={}&APPID=YOUR_API_KEY_HERE'.format(my_city)

        self.get_http_to_json(now_url, 'now')
        self.get_http_to_json(forecast_url, 'forecast')


    def show_current_weather(self, *args, **kwargs):
        '''update displayed data for current weather.

        The data is read from a json file with the name now.json. The data is stored as described in the OpenWeatherMap API.
        https://openweathermap.org/api/one-call-api?gclid=EAIaIQobChMI1bGR2-Dd6AIVxuN3Ch1sWAgGEAAYAiAAEgK6E_D_BwE
        The keys are read using the dictionary get() method because OpenWeatherMap does not always provide all data.
        Keys which are not available will be read as 'nn'

        Args:
            *args (): not used. For further development.
            **kwargs (): not used. For further development.

        Returns:
            (float): Scaled value.

        Raises:
            FileNotFoundError: Raised if no now.json file is found
        '''

        #Read data from json files and update bound properties
        try:          
            with open('now.json', 'r') as read_file:
                data=json.load(read_file)

            self.city = data.get('name','nn')
            self.country = data.get('sys').get('country','nn')
            self.temperature = '{:.1f}'.format(data.get('main').get('temp') - 273.15)
            self.humidity = str(data.get('main').get('humidity','nn'))
            self.pressure = str(data.get('main').get('pressure','nn'))
            self.image_source = 'http://openweathermap.org/img/w/' + data['weather'][0]['icon'] + '.png'
            self.wind_speed = str(data.get('wind').get('speed','nn'))
            self.wind_direction = str(data.get('wind').get('deg','nn'))
            self.last_update = str(gmtime(data.get('dt')))

        #if the file does not exist print an error message
        except FileNotFoundError as e:
            print(e)
            self.notification = 'Keine Wetterdaten vorhanden' 
    
    def show_forecast(self, *args, **kwargs):
        '''update displayed data for 5 day forecast.

        The data is read from a json file with the name forecast.json. The data is stored as described in the OpenWeatherMap API.
        https://openweathermap.org/api/one-call-api?gclid=EAIaIQobChMI1bGR2-Dd6AIVxuN3Ch1sWAgGEAAYAiAAEgK6E_D_BwE

        Args:
            *args (): not used. For further development.
            **kwargs (): not used. For further development.

        Returns:
            (float): Scaled value.

        Raises:
            FileNotFoundError: Raised if forecast.json cannot be found
        '''

        #Read data from json files and update bound properties
        try:
            with open('forecast.json', 'r') as read_file:
                data=json.load(read_file)
                self.forecast=data

            #first remove previous forecast 
            self.ids['grid'].clear_widgets()

            #add latest info
            for count in self.forecast['list']:

                #the time is formatted using strftime to display only the days name and hh:mm 
                self.ids['grid'].add_widget(Label(text=strftime('%a %H:%M',gmtime(count['dt'])), font_size='30sp'))
                #temperature will be rounded to two decimals
                self.ids['grid'].add_widget(Label(text='{:.0f}'.format(count['main']['temp'] - 273.15) + '°C', font_size='30sp'))
                self.ids['grid'].add_widget(AsyncImage(source='http://openweathermap.org/img/w/' + count['weather'][0]['icon'] + '.png'))                

        #if the file does not exist print an error message
        except FileNotFoundError as e:
            print(e)
            self.notification = 'Keine Wetterdaten vorhanden'

class TwoPlotsWidget(FigureCanvasKivyAgg):
    '''Displays two datetimeplots with shared x-axis.

        Attributes:
            timestamp (datetime):
                list of datetime values for the timeseries
            temperature (float):
                list of temperature values corresponding with timestamp
            humidity (float):
                list of humidity values corresponding with timestamp

        The attributes are bound by name to propertis in the kv file. Updating them will automatically update the displayed data in the visualisation
            units (ObjectProperty, str):
                list of string. Holding the units of the y-axis.
                Initially set to --.
            titles (ObjectProperty, str):
                list of string. Holding the titles for the plots.
                Initially set to --.
            ax_colors (ObjectProperty, str):
                List, setting the color of the plot.
                Initially set to green.
                Other parameters to change to different colors can be found in the matplotib documentation https://matplotlib.org/2.1.1/api/_as_gen/matplotlib.pyplot.plot.html
            notification  (StringProperty, str):
                Error string. Shows exceptions, like no data available.
                Initially set to --.
    '''
    
    plt.style.use('dark_background')
    
    timestamp = []
    temperature = []
    humidity = []
    units = ObjectProperty(['--','--'])
    titles = ObjectProperty(['--','--'])
    ax_colors = ObjectProperty(['g','g'])
    notification = StringProperty('')

    def __init__(self, **kwargs):
        '''__init__ takes the figure the backend is going to work with'''
        super(TwoPlotsWidget, self).__init__(plt.gcf(), **kwargs)

    def update_plot(self, *args, **kwargs):
        '''
        reads the latest data, updates the figure and plots it.

        The data is read from a json file with the name graph.json.
        The data is stored as a lsit of dicts with the following structure and a minimum of two elements:

        [
        {"time_code": "2019-03-01 00:02:38", "temperature": "23", "humidity": "42"}, 
        {"time_code": "2019-03-02 00:02:38", "temperature": "24", "humidity": "55"}, 
        {"time_code": "2019-03-03 00:02:38", "temperature": "22", "humidity": "40"}
        ]

        The graph is scaled automatically on the y-Axis. The x-Axis has major ticks for 1 day and minor ticks of 12 hours
        
        Args:
            *args (): not used. For further development.
            **kwargs (): not used. For further development.

        Returns:
            Nothing.
        '''

        #Read the data to show from a file and store it
        with open('graph.json', 'r') as read_file:
            data = json.load(read_file)

        for index in data:
            self.timestamp.append(datetime.fromtimestamp(mktime(strptime(index['time_code'],'%Y-%m-%d %H:%M:%S'))))
            self.temperature.append(float(index['temperature']))
            self.humidity.append(float(index['humidity']))

        data = [self.temperature, self.humidity]

        #Clear the figure
        myfigure = plt.gcf()
        myfigure.clf()

        #Add two subplots to the figure with a shared x axis
        axes = myfigure.subplots(2,1, sharex=True)

        #Add the data to the axes and modify their axis
        for n in range(len(axes)):
            axes[n].plot_date(self.timestamp, data[n], self.ax_colors[n], xdate=True)             
            axes[n].set_ylabel(self.units[n])
            axes[n].set_title(self.titles[n])
            plt.ylim(min(data[n])-2,max(data[n])+2)
            axes[n].xaxis.set_minor_locator(dt.HourLocator(byhour=range(0,24,12)))   #show minor ticks with a step width of 12 hours
            axes[n].xaxis.set_minor_formatter(dt.DateFormatter('%H:%M'))
            axes[n].xaxis.set_major_locator(dt.DayLocator(bymonthday=range(0,31,1))) #show major ticks witha step widht of 1 day
            axes[n].xaxis.set_major_formatter(dt.DateFormatter('%d-%B'))
            axes[n].xaxis.set_tick_params(which='major', pad=15)                     #set spacing between major and minor labels

        #the axis labels for the first subplot are made invisible
        plt.setp(axes[0].get_xticklabels(which='both'), visible=False)

        #draw the figure
        myfigure.canvas.draw_idle()
        
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
        self.config.read('mysettings.ini')
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
        
        settings.add_json_panel('Weather Widget', self.config, 'settings_weather_widget.json')
        settings.add_json_panel('Two Scales Widget', self.config, 'settings_two_scales_widget.json')

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
    MyVisuApp().run()
    
