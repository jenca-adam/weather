# weather - Access weather forecast
## Installation
```
pip install weather2
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
`weather` supports two weather sources:
1. [Yr.No](https://yr.no)
1. [7timer!](https://7timer.info)
If you want to get weather from different source, pass `forecast` argument called `source`.
```python
weather.forecast(service='yrno')
weather.forecast(service='7timer')
```
### Weather properties
<ol>
  <li>
    <p><code>wind</code>: Instance of <code>Wind()</code></p>
    Properties:
    <ol>
      <li>
        <p><code>speed</code>: Integer</p>
        Speed in m/s
      </li>
      <li>
        <p><code>direction</code>: Instance of <code>Direction()</code></p>
        Properties:
        <ol>
          <li>
            <p><code>angle</code>: Integer</p>
            Angle in degrees
          </li>
          <li>
            <p><code>direction</code>: String</p>
            Angle in compass point (<code>'N'</code>,<code>'NE'</code>,<code>'E'</code>,<code>'SE'</code>,<code>'S'</code>,<code>'SW'</code>,
            <code>'W'</code>, or <code>'NW'</code>)
          </li>
        </ol>
      </li>
    </ol>
  </li>
  <li>
    <p><code>temp</code>: Float/Integer</p>
      Temperature in °C or °F (not °K) (default °C, see 'Changing units')
  </li>
  <li>
    <p><code>humid</code> (<code>yr.no</code> only, other services will return <code>None</code>): Float/Integer</p>
      Humidity in %.
  </li>
  <li>
    <p><code>precip</code> (<code>7timer</code> will return <code>bool</code>): Float/Integer</p>
      Precipitation amount in milimeters
</ol>

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
                   [-u] [-a]

Python app for getting weather forecast

options:
  -h, --help            show this help message and exit
  --city CITY           City for forecast (if not passed, using current
                        location)
  --country COUNTRY     Country for forecast (see above)
  -d, --debug           Debug
  -s SERVICE, --service SERVICE
                        Service to use ("yrno" or "7timer"). Implied with
                        "average"(try to optimise the service)
  -u, --ugly            Toggle JSON output
  -a, --api             Just print the data (implies JSON output)

``` 
That says basically enough to use it.

### License

`weather` is licensed under *MIT license*
