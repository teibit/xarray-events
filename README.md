# xarray-events
This is an xarray accessor that extends xarray's functionality to handle events in high-level way. This API makes it easy to load events into an existing Dataset from a variety of sources and perform selections on the events that yield versions of the Datasets satisfying a set of specified constraints.

## Requirements

⚠️ ... work in progress ...

- [Python 3](https://docs.python.org/3/)
- [xarray](http://xarray.pydata.org/en/stable/index.html)
- [pandas](https://pandas.pydata.org/)

## Functionality

⚠️ ... work in progress ...

## Example

Let us describe a simple, toy example that demonstrates the functionalities of this API.

Assume we have the following Dataset with data about students in a school:

```
courses, students, terms = ['Physics', 'Maths'], ['Ever', 'Henry'], ['mid', 'final']

grades = [[[4.4,6.9],[10,3.6]],[[9.8,6.6],[5.9,8.1]]]

data_vars = {'grades': (['course', 'student', 'term'], grades)}

coordinates = {'course': (['course'], courses), 'student': (['student'], students), 'term': (['term'], terms)}

attributes = {'name': 'OU', 'campus': 'Stone town', 'department': 'Information Technologies'}

ds = xr.Dataset(data_vars, coordinates, attributes)
```

The resulting Dataset is:

```
<xarray.Dataset>
Dimensions:  (course: 2, student: 2, term: 2)
Coordinates:
  * course   (course) <U7 'Physics' 'Maths'
  * student  (student) <U5 'Ever' 'Henry'
  * term     (term) <U5 'mid' 'final'
Data variables:
    grades   (course, student, term) int64 1 2 3 4 5 6 7 8
Attributes:
    name:        OU
    campus:      Stone town
    department:  Information Technologies
```

Assume we identify the following events:

```
event_types = {1:'A', 2:'B', 3:'C', 4:'D', 5:'C'}

data = [[5,4.4,'Ever','mid'],[4,6.9,'Ever','mid'],[1,10,'Henry','mid'],[5,3.6,'Henry','mid'],[1,9.8,'Ever','final'],[4,6.6,'Ever','final'],[5,5.9,'Henry','final'],[2,8.1,'Henry','final']]

events = pd.DataFrame(data, columns=['event_type_id','grade','student','term'])
```

The resulting DataFrame is:

```
event_type_id	grade	student	term
0	5	4.4	Ever	mid
1	4	6.9	Ever	mid
2	1	10.0	Henry	mid
3	5	3.6	Henry	mid
4	1	9.8	Ever	final
5	4	6.6	Ever	final
6	5	5.9	Henry	final
7	2	8.1	Henry	final
```

From this, we wish to constrain the dataset so that we get data associated with the event in which Ever scored either an A or a C. The following query enables just that:

```
q = ds.events.load(events).sel(dict({'student':['Ever'], 'event_type_id':[1,3]}), event_types)
```

And the result, as you'd expect, is precisely:

```
{'A': <xarray.Dataset>
Dimensions:  (course: 2, student: 1, term: 2)
Coordinates:
  * course   (course) <U7 'Physics' 'Maths'
  * student  (student) <U5 'Ever'
  * term     (term) <U5 'mid' 'final'
Data variables:
    grades   (course, student, term) int64 1 2 5 6
Attributes:
    name:        OU
    campus:      Stone town
    department:  Information Technologies
    _events:        event_type_id  grade student   term\n4              1    ...}
```

Since Ever scored no Cs, only an A is displayed. We have now constrained the Dataset to show data satisfying all constraints.

Notice that the only event from which ```ds``` was constrained can be seen with ```q['A']._events``` and is:

```
   event_type_id  grade student   term
4              1    9.8    Ever  final
```
