# Tech events in SG!

Auto finds free tech events in SG.
Tested on Python 3.6+

### Endpoints:
- Subscribe to the ics calendar: https://webuild-events.herokuapp.com/cal
- List of events: https://webuild-events.herokuapp.com/events
- List of groups: https://webuild-events.herokuapp.com/groups
- List of filtered groups: https://webuild-events.herokuapp.com/filtered_groups
- List of filtered events: https://webuild-events.herokuapp.com/filtered_events

### Development
```
$ pip install -r requirements.txt
```

### Run
```
$ python main.py
```

### Test run 
Generates a list of upcoming tech events in JSON
```
$ python test.py
```

### Deployment
Auto-deployed on git pushes to heroku
