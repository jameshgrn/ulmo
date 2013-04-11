import os.path

import pandas

from ulmo import util


CIRS_DIR = util.get_ulmo_dir('ncdc/cirs')


def get_data(index, by_state=False, as_dataframe=False, use_file=None):
    url = _get_url(index, by_state)
    filename = url.rsplit('/', 1)[-1]
    path = os.path.join(CIRS_DIR, filename)

    with util.open_file_for_url(url, path, use_file=use_file) as f:
        data = _parse_values(f, by_state)

    if as_dataframe:
        return data
    else:
        return data.T.to_dict().values()


def _get_url(index, by_state):
    return "ftp://ftp.ncdc.noaa.gov/pub/data/cirs/drd964x.%s%s.txt" % (
        index, 'st' if by_state else '')


def _parse_values(file_handle, by_state):
    if by_state:
        id_columns = [
            ('location_code', 0, 3, None),
            #('division', 3, 3, None), # ignored in state files
            #('element', 4, 6, None),  # element is redundant
            ('year', 6, 10, None),
        ]
    else:
        id_columns = [
            ('location_code', 0, 2, None),
            ('division', 2, 4, None),
            #('element', 4, 6, None),  # element is redundant
            ('year', 6, 10, None),
        ]

    month_columns = [
        (str(n), 3 + (7 * n), 10 + (7 * n), None)
        for n in range(1, 13)
    ]

    columns = id_columns + month_columns

    data = util.parse_fwf(file_handle, columns, na_values=["-99.99"])

    month_columns = [id_column[0] for id_column in id_columns]
    melted = pandas.melt(data, id_vars=month_columns)\
        .rename(columns={'variable': 'month'})

    melted.month = melted.month.astype(int)

    locations = _states_regions_dataframe()['abbr']
    with_locations = melted.join(locations, on='location_code')

    if by_state:
        data = with_locations.rename(columns={
            'abbr': 'location',
        })
    else:
        data = with_locations.rename(columns={
            'abbr': 'state',
            'location_code': 'state_code'
        })

    return data


def _states_regions_dataframe():
    """returns a dataframe indexed by state/region code with columns for the
    name and abbrevitation (abbr) to use
    """
    STATES_REGIONS = {
        # code: (full name, abbrevation)
        1: ("Alabama", "AL"),
        2: ("Arizona", "AZ"),
        3: ("Arkansas", "AR"),
        4: ("California", "CA"),
        5: ("Colorado", "CO"),
        6: ("Connecticut", "CT"),
        7: ("Delaware", "DE"),
        8: ("Florida", "FL"),
        9: ("Georgia", "GA"),
        10: ("Idaho", "ID"),
        11: ("Illinois", "IL"),
        12: ("Indiana", "IN"),
        13: ("Iowa", "IA"),
        14: ("Kansas", "KS"),
        15: ("Kentucky", "KY"),
        16: ("Louisiana", "LA"),
        17: ("Maine", "ME"),
        18: ("Maryland", "MD"),
        19: ("Massachusetts", "MA"),
        20: ("Michigan", "MI"),
        21: ("Minnesota", "MN"),
        22: ("Mississippi", "MS"),
        23: ("Missouri", "MO"),
        24: ("Montana", "MT"),
        25: ("Nebraska", "NE"),
        26: ("Nevada", "NV"),
        27: ("New Hampshire", "NH"),
        28: ("New Jersey", "NJ"),
        29: ("New Mexico", "NM"),
        30: ("New York", "NY"),
        31: ("North Carolina", "NC"),
        32: ("North Dakota", "ND"),
        33: ("Ohio", "OH"),
        34: ("Oklahoma", "OK"),
        35: ("Oregon", "OR"),
        36: ("Pennsylvania", "PA"),
        37: ("Rhode Island", "RI"),
        38: ("South Carolina", "SC"),
        39: ("South Dakota", "SD"),
        40: ("Tennessee", "TN"),
        41: ("Texas", "TX"),
        42: ("Utah", "UT"),
        43: ("Vermont", "VT"),
        44: ("Virginia", "VA"),
        45: ("Washington", "WA"),
        46: ("West Virginia", "WV"),
        47: ("Wisconsin", "WI"),
        48: ("Wyoming", "WY"),
        101: ("Northeast Region", "ner"),
        102: ("East North Central Region", "encr"),
        103: ("Central Region", "cr"),
        104: ("Southeast Region", "ser"),
        105: ("West North Central Region", "wncr"),
        106: ("South Region", "sr"),
        107: ("Southwest Region", "swr"),
        108: ("Northwest Region", "nwr"),
        109: ("West Region", "wr"),
        110: ("National (contiguous 48 States)", "national"),

        # The following are the range of code values for the National Weather Service Regions, river basins, and agricultural regions.
        111: ("NWS: Great Plains", "nws:gp"),
        115: ("NWS: Southern Plains and Gulf Coast", "nws:spgc"),
        120: ("NWS: US Rockies and Westward", "nws:usrw"),
        121: ("NWS: Eastern Region", "nws:er"),
        122: ("NWS: Southern Region", "nws:sr"),
        123: ("NWS: Central Region", "nws:cr"),
        124: ("NWS: Western Region", "nws:wr"),
        201: ("NWS: Pacific Northwest Basin", "nws:pnwb"),
        202: ("NWS: California River Basin", "nws:crb"),
        203: ("NWS: Great Basin", "nws:gb"),
        204: ("NWS: Lower Colorado River Basin", "nws:lcrb"),
        205: ("NWS: Upper Colorado River Basin", "nws:urcb"),
        206: ("NWS: Rio Grande River Basin", "nws:rgrb"),
        207: ("NWS: Texas Gulf Coast River Basin", "nws:tgcrb"),
        208: ("NWS: Arkansas-White-Red Basin", "nws:awrb"),
        209: ("NWS: Lower Mississippi River Basin", "nws:lmrb"),
        210: ("NWS: Missouri River Basin", "nws:mrb"),
        211: ("NWS: Souris-Red-Rainy Basin", "nws:srrb"),
        212: ("NWS: Upper Mississippi River Basin", "nws:umrb"),
        213: ("NWS: Great Lakes Basin", "nws:glb"),
        214: ("NWS: Tennessee River Basin", "nws:trb"),
        215: ("NWS: Ohio River Basin", "nws:ohrb"),
        216: ("NWS: South Atlantic-Gulf Basin", "nws:sagb"),
        217: ("NWS: Mid-Atlantic Basin", "nws:mab"),
        218: ("NWS: New England Basin", "nws:neb"),
        220: ("NWS: Mississippi River Basin & Tributaties (N. of Memphis, TN",
              "nws:mrb&t"),

        # below( codes are weighted by area)
        250: ("Area: Spring Wheat Belt", "area:swb"),
        255: ("Area: Primary Hard Red Winter Wheat Belt", "area:phrwwb"),
        256: ("Area: Winter Wheat Belt", "area:wwb"),
        260: ("Area: Primary Corn and Soybean Belt", "area:pcsb"),
        261: ("Area: Corn Belt", "area:cb"),
        262: ("Area: Soybean Belt", "area:sb"),
        265: ("Area: Cotton Belt", "area:cb"),

        # below( codes are weighted by productivity)
        350: ("Prod: Spring Wheat Belt", "prod:swb"),
        356: ("Prod: Winter Wheat Belt", "prod:wwb"),
        361: ("Prod: Corn Belt", "prod:cb"),
        362: ("Prod: Soybean Belt", "prod:sb"),
        365: ("Prod: Cotton Belt", "prod:cb"),

        # below( codes are for percent productivity in the Palmer Z Index categories)
        450: ("% Prod: Spring Wheat Belt", "%prod:swb"),
        456: ("% Prod: Winter Wheat Belt", "%prod:wwb"),
        461: ("% Prod: Corn Belt", "%prod:cb"),
        462: ("% Prod: Soybean Belt", "%prod:sb"),
        465: ("% Prod: Cotton Belt", "%prod:cb"),
    }
    return pandas.DataFrame(STATES_REGIONS).T.rename(columns={0: 'name', 1: 'abbr'})
