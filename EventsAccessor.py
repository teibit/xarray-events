import xarray as xr

@xr.register_dataset_accessor('events')

class EventsAccessor:
    
    def __init__(self, ds):
        self._ds = ds
    
    def load(self, source):
        
        def split_events(events):
            return {
                event_types[event_type_id]: event_df.loc[:, lambda df: df.notna().any()]
                for event_type_id, event_df in events.groupby('event_type_id')
            }
        
        if type(source) == type(pd.DataFrame()):
            self._ds = self._ds.assign_attrs(_events = split_events(source))
        
        elif type(source) == type(Path()):
            if source.suffix == '.csv':
                pass
        
        else:
            print('Unsupported events source')
        
        return self
    
    def sel(self, constraints, event_types=None):
        
        # self.types is a dict that stores, for each event name, the attributes that we extract from the source
        self.types = dict({key:list(val.columns) for key,val in zip(self._ds._events,self._ds._events.values())})
        
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
