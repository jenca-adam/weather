from setuptools import setup
setup(name='weather2',
    version='1.3.6',
    author='Adam Jenca',
    description='Access weather forecast',
    long_description=
'''
# weather - Access weather forecast
## Installation
```
pip install weather
```
## Usage
```python
import weather
forecast=weather.forecast()
forecast.today['6:00'].temp # Get temperature in current location at 6.00
```
### Different places
If you want to get forecast from different place, pass `forecast` an argument.
```python
import weather
forecast=weather.forecast('New York')
forecast.tommorow['11:00'].precip # Get precipitation in New York at 11.00
```
### Different sources
`weather` supports multiple weather sources:
1. [Yr.No] (https://yr.no)
1. [Google] (https://google.com)
1. [7timer!] (https://7timer.info)
If you want to get weather from different source, pass `forecast` argument called `source`.
```python
weather.forecast(source='yrno')
weather.forecast(source='google')
weather.forecast(source='7timer')
```
### Weather properties
#### 1. `wind`
Instance of `Wind()`
Properties:
##### 1. `speed`
       Integer
       Speed in m/s
##### 2. `direction`
Instance of Direction()
Properties:
###### 1. `angle`
Integer
Angle in degrees
###### 2. `direction`
String
Angle in compass point ( 'N','NE','E','SE','S','SW','W', or 'NW' )
#### 2. `temp`
      Float/Integer
      Temperature in °C or °F (not °K)(default °C, see 'Changing units')
#### 3. `humid`(yr.no only, other services will return None)
      Float/Integer
      Humidity in %.
#### 4. `precip`(7timer will return bool)
      Float/Integer
      Precipitation amount in milimeters
### Changing units
```python
weather.forecast('New york', unit=weather.CELSIUS)#or weather.FAHRENHEIT
```
### CLI
Just run `weather`:
    ```[user@localhost ~] weather```
If you want to get all avaliable switches, use `weather -h`:

```python

usage: weather [-h] [--city CITY] [--country COUNTRY] [-d] [-s SERVICE]

Python app for getting weather forecast

optional arguments:
  -h, --help            show this help message and exit
  --city CITY           City for forecast (if not passed, using current location)
  --country COUNTRY     Country for forecast (see above)
  -d, --debug           Debug
  -s SERVICE, --service SERVICE
                        Service to use (e.g. "yrno","7timer","google"). Implied with "average"(try to optimise the service)

``` 
That says basically enough to use it.

### License

`weather` is licensed under *GPL license*

''',
    long_description_content_type='text/markdown',
    classifiers=[
                "Development Status :: 4 - Beta",
                "Environment :: Console",
                "Intended Audience :: Developers",
                "Intended Audience :: End Users/Desktop",
                "License :: OSI Approved :: GNU General Public License (GPL)",
                "Operating System :: OS Independent",
                "Programming Language :: Python",
                "Programming Language :: Python :: 3",
                ],
    entry_points={
    'console_scripts': [
        'weather = weather:main',
    ]},
    author_email="jenca.adam@gmail.com",
    url="https://github.com/jenca-adam/weather",
    packages=['weather'],
    install_requires=['urllib3','bs4','httplib2','geopy','selenium','colorama','lxml','langdetect','termcolor','tabulate','termutils','getchlib','unitconvert']


    
)

       
