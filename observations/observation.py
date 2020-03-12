'''
module with a number of observation classes.

The Obs class is a subclass of a pandas DataFrame with
additional attributes and methods. The specific classes (GroundwaterObs,
WaterlvlObs, ...) are subclasses of the Obs class.

The subclasses of a dataframe can have additional attributes and methods.
Additional attributes have to be defined in the '_metadata' attribute. In order
to keep the subclass methods and attributes when selecting or slicing an object
you need the '_constructor' method.


More information about subclassing pandas DataFrames can be found here:
http://pandas.pydata.org/pandas-docs/stable/development/extending.html#extending-subclassing-pandas

'''

import warnings

import numpy as np
from pandas import DataFrame, Series


from .io import io_dino


class Obs(DataFrame):
    """class for point observations.

    An Obs object is a subclass of a pandas.DataFrame and allows for additional
    attributes and methods.
    pandas can be found here:
    http://pandas.pydata.org/pandas-docs/stable/development/extending.html#extending-subclassing-pandas

    Parameters
    ----------
    x : int or float
        x coordinate of observation point
    y : int or float
        y coordinate of observation point
    name : str
        name
    meta : dictionary
        metadata
    filename : str
        filename with data of observation point

    """
    # temporary properties
    _internal_names = DataFrame._internal_names + ['none']
    _internal_names_set = set(_internal_names)

    # normal properties
    _metadata = ['x', 'y', 'name',
                 'meta',
                 'filename']

    def __init__(self, *args, **kwargs):
        """ constructor of Obs class

        *args must be input for the pandas.DataFrame constructor,
        **kwargs can be one of the attributes listed in _metadata or
        keyword arguments for the constructor of a pandas.DataFrame.
        """
        self.x = kwargs.pop('x', np.nan)
        self.y = kwargs.pop('y', np.nan)
        self.name = kwargs.pop('name', '')
        self.meta = kwargs.pop('meta', {})
        self.filename = kwargs.pop('filename', '')

        super(Obs, self).__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return Obs

    def to_collection_dict(self):
        """get dictionary with registered attributes and their values
        of an Obs object.

        This method can be used to create a dataframe from a collection
        of Obs objects.

        Returns
        -------
        d : dictionary
            dictionary with Obs information
        """
        d = {}
        for att in self._metadata:
            d[att] = getattr(self, att)

        d['obs'] = self

        return d


class GroundwaterObs(Obs):
    """class for groundwater quantity point observations

    Subclass of the Obs class. Can have the following attributes:
        - locatie: 2 filters at one piezometer should have the same 'locatie'
        - filternr: 2 filters at one piezometer should have a different 'filternr'.
        a higher filter number is preferably deeper than a lower filter number.
        - bovenkant_filter: top op the filter in m NAP
        - onderkant_filter: bottom of the filter in m NAP
        - maaiveld: surface level in m NAP
        - meetpunt: ? in m NAP
        - metadata_available: boolean indicating if metadata is available for
        the measurement point.

    """

    _metadata = Obs._metadata + \
        ['locatie', 'filternr',
         'bovenkant_filter', 'onderkant_filter',
         'maaiveld', 'meetpunt', 'metadata_available'
         ]

    def __init__(self, *args, **kwargs):
        """
        *args must be input for the pandas.DataFrame constructor,
        **kwargs can be one of the attributes listed in _metadata or
        keyword arguments for the constructor of a pandas.DataFrame.

        if the pandas.DataFrame has a column 'stand_m_tov_nap' a lot of
        plotting and other methods will work automatically without changing
        the default arguments.
        """
        self.locatie = kwargs.pop('locatie', '')
        self.filternr = kwargs.pop('filternr', '')
        self.maaiveld = kwargs.pop('maaiveld', np.nan)
        self.meetpunt = kwargs.pop('meetpunt', np.nan)
        self.bovenkant_filter = kwargs.pop('bovenkant_filter', np.nan)
        self.onderkant_filter = kwargs.pop('onderkant_filter', np.nan)
        self.metadata_available = kwargs.pop('metadata_available', np.nan)

        super(GroundwaterObs, self).__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return GroundwaterObs
    
    @classmethod
    def from_dino(cls, fname=None, name=None, filternr=1.,
                  tmin="1900-01-01", tmax="2040-01-01", 
                  **kwargs):
        """read dino data from a file or from the server

        Parameters
        ----------
        fname : str, optional
            dino csv filename
        name : str, optional
            name of the peilbuis, i.e. B57F0077
        filternr : float, optional
            filter_nr of the peilbuis, i.e. 1.
        tmin : str
            start date in format YYYY-MM-DD
        tmax : str
            end date in format YYYY-MM-DD
        kwargs : key-word arguments
            if fname is not None these arguments are passed to 
                io_dino.read_dino_groundwater_csv  
            if fname is None these arguements are passed to  
                to dino.findMeetreeks
        """
        
        if fname is None and name is None:
            raise ValueError('specify name or fname to read dino file')
            
        #read dino csv file
        elif fname is not None: 
            measurements, obs_att, meta_ts = io_dino.read_dino_groundwater_csv(
                                             fname, **kwargs)
        
            return cls(measurements, meta=meta_ts, **obs_att)
        #download dino data from server
        elif name is not None:
            measurements, meta = io_dino.download_dino_groundwater(name,
                                                               filternr,
                                                               tmin, tmax,
                                                               **kwargs)
            
            obs_att = {}
            for key in cls._metadata:
                if key in meta.keys():
                    obs_att[key] = meta.pop(key)
                    
            for key in obs_att:
                meta[key] = Series(name=key)
                meta[key].loc[measurements.index[0]] = obs_att[key]
                meta[key].loc[measurements.index[-1]] = obs_att[key]
            
            return cls(measurements, **obs_att, meta=meta)
            

    @classmethod
    def from_dino_server(cls, name, filternr=1.,
                         tmin="1900-01-01", tmax="2040-01-01",
                         **kwargs):
        """download dino data from the server.

        Parameters
        ----------
        name : str, optional
            name of the peilbuis, i.e. B57F0077
        filternr : float, optional
            filter_nr of the peilbuis, i.e. 1.
        tmin : str
            start date in format YYYY-MM-DD
        tmax : str
            end date in format YYYY-MM-DD
        kwargs : key-word arguments
            these arguments are passed to dino.findMeetreeks functie

        
        """
        
        warnings.warn("this method will be removed in future versions, use from_dino instead", DeprecationWarning)

        measurements, meta = io_dino.download_dino_groundwater(name,
                                                               filternr,
                                                               tmin, tmax,
                                                               **kwargs)
        obs_att = {}
        for key in cls._metadata:
            if key in meta.keys():
                obs_att[key] = meta.pop(key)
                
        for key in obs_att:
            meta[key] = Series(name=key)
            meta[key].loc[measurements.index[0]] = obs_att[key]
            meta[key].loc[measurements.index[-1]] = obs_att[key]
        
        return cls(measurements, **obs_att, meta=meta)
            
        

    @classmethod
    def from_dino_file(cls, fname=None, **kwargs):
        """read a dino csv file.
        Parameters
        ----------
        name : str, optional
            name of the peilbuis, i.e. B57F0077
        fname : str, optional
            dino csv filename
        kwargs : key-word arguments
            these arguments are passed to io_dino.read_dino_groundwater_csv
        """
        warnings.warn("this method will be removed in future versions, use from_dino instead", DeprecationWarning)

        if fname is not None:
            # read dino csv file

            measurements, obs_att, meta_ts = io_dino.read_dino_groundwater_csv(
                                             fname, **kwargs)
        
            
            return cls(measurements, meta=meta_ts, **obs_att)
        else:
            raise ValueError(
                'specify either the name or the filename of the measurement point')


    @classmethod
    def from_artdino_file(cls, fname=None, **kwargs):
        """read a dino csv file.

        Parameters
        ----------
        name : str, optional
            name of the peilbuis, i.e. B57F0077
        fname : str, optional
            dino csv filename
        kwargs : key-word arguments
            these arguments are passed to io_dino.read_dino_groundwater_csv
        """

        if fname is not None:
            # read dino csv file

            measurements, meta = io_dino.read_artdino_groundwater_csv(
                fname, **kwargs)

            return cls(measurements, meta=meta, **meta)
        else:
            raise ValueError(
                'specify either the name or the filename of the measurement point')

    @classmethod
    def from_wiski(cls, fname, **kwargs):

        from .io import io_wiski

        header, data = io_wiski.read_wiski_file(fname, **kwargs)
        metadata = {}
        if 'Station Site' in header.keys():
            metadata['locatie'] = header['Station Site']
            header['locatie'] = header['Station Site']

        if 'x' in header.keys():
            metadata['x'] = header['x']
        if "y" in header.keys():
            metadata['y'] = header['y']
        if 'name' in header.keys():
            metadata['name'] = header['name']

        return cls(data, meta=header, **metadata)

    @classmethod
    def from_pystore_item(cls, item):
        """Create GroundwaterObs DataFrame from Pystore item

        Parameters
        ----------
        item : pystore.item.Item
            Pystore item

        Returns
        -------
        GroundwaterObs
            GroundwaterObs DataFrame

        """

        df = item.to_pandas()
        try:
            x = item.metadata["x"]
            y = item.metadata["y"]
        except KeyError:
            x = np.nan
            y = np.nan
        item.metadata["datastore"] = item.datastore
        return cls(df, x=x, y=y, meta=item.metadata)

    def get_modellayer(self, ml, zgr=None, verbose=False):
        """Add modellayer to meta dictionary

        Parameters
        ----------
        ml : flopy.modflow.mf.Modflow
            modflow model
        zgr : np.3darray, optional
            array containing model layer elevation
            information (the default is None, which
            gets this information from the dis object)
        verbose : boolean, optional
            Print additional information to the screen (default is False).

        """
        from .modflow import get_pb_modellayer
        modellayer = get_pb_modellayer(np.array([self.x]) - ml.modelgrid.xoffset,
                              np.array([self.y]) - ml.modelgrid.yoffset,
                              np.array([self.bovenkant_filter]),
                              np.array([self.onderkant_filter]),
                              ml, zgr, verbose=verbose)[0]

        return modellayer

class GroundwaterQualityObs(Obs):
    """class for groundwater quality (grondwatersamenstelling)
    point observations.

    Subclass of the Obs class

    """

    _metadata = Obs._metadata + \
        ['locatie', 'filternr', 'maaiveld', 'metadata_available']

    def __init__(self, *args, **kwargs):

        self.locatie = kwargs.pop('locatie', '')
        self.filternr = kwargs.pop('filternr', '')
        self.maaiveld = kwargs.pop('maaiveld', np.nan)
        self.metadata_available = kwargs.pop('metadata_available', np.nan)

        super(GroundwaterQualityObs, self).__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return GroundwaterQualityObs

    @classmethod
    def from_dino_file(cls, fname, **kwargs):
        """read ad dino file with groundwater quality data

        Parameters
        ----------
        fname : str
            dino txt filename
        kwargs : key-word arguments
            these arguments are passed to io_dino.read_dino_groundwater_quality_txt
        """

        measurements, meta = io_dino.read_dino_groundwater_quality_txt(
            fname, **kwargs)

        return cls(measurements, meta=meta, **meta)


class WaterlvlObs(Obs):
    """class for water level point observations.

    Subclass of the Obs class

    """

    _metadata = Obs._metadata + \
        ['locatie', 'metadata_available'
         ]

    def __init__(self, *args, **kwargs):

        self.locatie = kwargs.pop('locatie', '')
        self.metadata_available = kwargs.pop('metadata_available', np.nan)

        super(WaterlvlObs, self).__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return WaterlvlObs

    @classmethod
    def from_dino_file(cls, fname, **kwargs):
        '''read a dino file with waterlvl data

        Parameters
        ----------
        fname : str
            dino csv filename
        kwargs : key-word arguments
            these arguments are passed to io_dino.read_dino_waterlvl_csv
        '''

        measurements, meta = io_dino.read_dino_waterlvl_csv(fname, **kwargs)

        return cls(measurements, meta=meta, **meta)

    @classmethod
    def from_waterinfo(cls, fname, **kwargs):
        """
        Read data from waterinfo csv-file or zip.

        Parameters
        ----------
        fname : str
            path to file (file can zip or csv)

        Returns
        -------
        df : WaterlvlObs
            WaterlvlObs object

        Raises
        ------
        ValueError
            if file contains data for more than one location
        """
        from .io import io_waterinfo
        from pyproj import Proj, transform

        df = io_waterinfo.read_waterinfo_file(fname)

        if len(df["MEETPUNT_IDENTIFICATIE"].unique()) > 1:
            raise ValueError("File contains data for more than one location!"
                             " Use ObsCollection.from_waterinfo()!")

        metadata = {}
        x, y = transform(Proj(init='epsg:25831'),
                         Proj(init='epsg:28992'),
                         df['X'].iloc[-1],
                         df['Y'].iloc[-1])
        metadata["name"] = df["MEETPUNT_IDENTIFICATIE"].iloc[-1]
        metadata["x"] = x
        metadata["y"] = y

        return cls(df, meta=metadata, **metadata)


class ModelObs(Obs):
    """class for model point results.

    Subclass of the Obs class
    """

    _metadata = Obs._metadata + \
        ['model']

    def __init__(self, *args, **kwargs):

        self.model = kwargs.pop('model', '')

        super(ModelObs, self).__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return ModelObs


class KnmiObs(Obs):
    """class for KNMI timeseries.

    Subclass of the Obs class
    """

    _metadata = Obs._metadata + \
        ['station']

    def __init__(self, *args, **kwargs):

        self.station = kwargs.pop('station', np.nan)

        super(KnmiObs, self).__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return KnmiObs

    @classmethod
    def from_knmi(cls, stn, variable, startdate=None, enddate=None,
                  fill_missing_obs=True, verbose=False):
        from .io import io_knmi

        ts, meta = io_knmi.get_knmi_timeseries_stn(stn, variable,
                                                   startdate, enddate,
                                                   fill_missing_obs,
                                                   verbose=verbose)
        return cls(ts, meta=meta, station=meta['station'], x=meta['x'],
                   y=meta['y'], name=meta['name'])

    @classmethod
    def from_nearest_xy(cls, x, y, variable, startdate=None, enddate=None,
                        fill_missing_obs=True, verbose=False):
        from .io import io_knmi

        ts, meta = io_knmi.get_knmi_timeseries_xy(x, y, variable,
                                                  startdate, enddate,
                                                  fill_missing_obs,
                                                  verbose=verbose)

        return cls(ts, meta=meta, station=meta['station'], x=meta['x'],
                   y=meta['y'], name=meta['name'])

    @classmethod
    def from_obs(cls, obs, variable, startdate=None, enddate=None,
                 fill_missing_obs=True, verbose=False):

        from .io import io_knmi

        x = obs.x
        y = obs.y

        if startdate is None:
            startdate = obs.index[0]
        if enddate is None:
            enddate = obs.index[-1]

        ts, meta = io_knmi.get_knmi_timeseries_xy(x, y, variable,
                                                  startdate, enddate,
                                                  fill_missing_obs,
                                                  verbose=verbose)

        return cls(ts, meta=meta, station=meta['station'], x=meta['x'],
                   y=meta['y'], name=meta['name'])
