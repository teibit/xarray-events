import xarray as xr, pandas as pd

from typing import Union
from pathlib import Path

@xr.register_dataset_accessor('events')

class EventsAccessor:
    """xarray accessor with extended events-handling functionality.
    
    An xarray accessor that extends its functionality to handle events in high-level way. This API makes it easy to load events into an existing Dataset from a variety of sources and perform selections on the events that yield versions of the Datasets satisfying a set of specified constraints.
    
    Attributes:
            _ds (xr.Dataset): The Dataset to be accessed whose class-level functionality is to be extended.
    
    """
    
    def __init__(self, ds) -> None:
        """
        Arguments:
            ds (xr.Dataset): The Dataset to be accessed whose class-level functionality is to be extended.
        """
        self._ds = ds
    
    def load(self, source: Union[type(pd.DataFrame()), type(Path())]) -> self:
        """Set the events as an attribute of _ds.
        
        Depending on the source where the events are to be found, fetch and load them accordingly.
        
        The events will ultimately be represented as a dictionary where the key is the type of event and the value is a DataFrame containing it. Hence, regardless of how they're represented, this method aims to make it fit in this format.
        
        Arguments:
            source (DataFrame/PosixPath): A DataFrame or Path specifying where the events are to be loaded from.
        
        Returns:
            self, which is the modified ds now including events accessed by ds.events from the outside.
        
        Usage:
            First method that should be called on a Dataset upon using this API.
            
        """
        
        def split_events(events):
            return {
                event_types[event_type_id]: event_df.loc[:, lambda df: df.notna().any()]
                for event_type_id, event_df in events.groupby('event_type_id')
            }
        
        # a DataFrame is the ultimate way of representing the events before splitting them
        if type(source) == type(pd.DataFrame()):
            self._ds = self._ds.assign_attrs(_events = split_events(source))
        
        # if a Path is given, fetch the data depending on the file extension, convert it into a DataFrame and split the events
        elif type(source) == type(Path()):
            if source.suffix == '.csv':
                pass
            pass
        
        else:
            print('Unsupported events source')
        
        return self
    
    def sel(self, constraints: dict, event_types: dict = None) -> dict:
        """Perform a selection on _ds based on a set of constraints in the events.
        
        Given a set of constraints specified in a dictionary, select the events that satisfy all of them and then return, for each of them, a new version of _ds. This new _ds will have its dimensions constrained by the specified attributes that literally match the specified constraints.
        
        Arguments:
            constraints (dict): A dictionary that specifies a list of constraints in a dictionary. A key is an attribute from the DataFrame storing the events and a values is a list of potential values.
            event_types (dict): A dictionary that if specified establishes a correspondance between events and their IDs. A key is the event_type_id and a value is the event name.
        
        Returns:
            datasets (dict): A dictionary that specifies, for each event, the resulting constrained Dataset.
        
        Usage:
            Call strictly after having called load(...) on a Dataset. This ensures that ds.events exists and has the appropriate format that this method expects.
        
        """
        
        # self.types is a dict that stores, for each event name, the attributes that we extract from the source
        self.types = dict({k:list(v.columns) for k,v in zip(self._ds._events,self._ds._events.values())})
        
        # self.matching_dims is a dict that filters self.types to only contain values that match dimensions of self._ds literally
        self.matching_dims = {k: list(filter(lambda x: x in self._ds.dims, v)) for k,v in self.types.items()}
        
        # drop values from self.matching_dims for which no constraint was specified
        self.matching_dims = {k:list(filter(lambda x: x in constraints, v)) for k,v in self.matching_dims.items()}
        
        # if one of the specified constraints in the selection is event_type_id then filter self.matching_dims and self._ds._events to only contain the specified events
        if 'event_type_id' in constraints and event_types != None:
            
            self.matching_dims = {k:v for k,v in self.matching_dims.items() if k in [event_types[x] for x in constraints['event_type_id']]}
        
            self._ds = self._ds.assign_attrs(_events = {k:self._ds._events[k] for k in [event_types[x] for x in constraints['event_type_id']]})
        
        # apply specified constraints to self._ds._events
        events = self._ds._events
        
        for col,vals in constraints.items():
            for k,v in events.items():
                events = {k:v[v[col].isin(vals)] for k,v in events.items()}
        
        self._ds = self._ds.assign_attrs(_events = events)
        
        # datasets is a selection on self._ds applying each specified matching constrain and also setting self._ds._events accordingly
        datasets = {key:self._ds.sel({k:constraints[k] for k in val}).assign_attrs(_events = self._ds._events[key]) for key,val in self.matching_dims.items()}
        
        # filter datasets to not contain empty events after having applied all conditions
        datasets = {k:v for k,v in datasets.items() if not v._events.empty}
        
        return datasets
