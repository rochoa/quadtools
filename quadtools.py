from math import radians, floor, log, tan, cos, pi as PI


def quadkey(lon, lat, zoom):
    '''Get the quad key at a zoom level for a longitude and latitude pair.
    It truncates the longitude at -180/180 and the latitude at -90/90.

    >>> quadkey(-3.7, 42.4, 1)
    '0'
    >>> quadkey(-3.7, 42.4, 5)
    '03133'
    >>> quadkey(-180, 90, 3)
    '022'
    >>> quadkey(-200, 90, 3)
    '022'
    >>> quadkey(-200, 99, 3)
    '022'
    '''
    lon = min(max(lon, -180), 180)
    lat = min(max(lat, -90), 90)

    lat = radians(lat)
    n = 2.0 ** zoom
    x = int(floor((lon + 180.0) / 360.0 * n))
    y = int(floor((1.0 - log(tan(lat) + (1.0 / cos(lat))) / PI) / 2.0 * n))

    qk = ''
    for z in range(zoom, 0, -1):
        digit = 0
        mask = 1 << (z - 1)
        if x & mask:
            digit += 1
        if y & mask:
            digit += 2
        qk += str(digit)
    return qk


def parent(quadkey):
    '''Get the parent quadkey containing the given quadkey

    >>> parent('01')
    '0'
    >>> parent('031332')
    '03133'
    '''
    return quadkey[:-1]


def children(quadkey):
    '''Get the quadkey's four children.

    >>> children('01')
    ['010', '011', '012', '013']
    '''
    return [f'{quadkey}{quadrant}' for quadrant in QUADRANTS]


def siblings(quadkey):
    '''Get a list with all the siblings for the quadkey, includes itself.

    >>> siblings('011')
    ['010', '011', '012', '013']
    '''
    return children(parent(quadkey))


def neighbors(quadkey):
    '''Get the neighbors.
    Returns a list with NW, N, NE, W, itself, E, SW, S, and SE quadkeys.
    For edge quadkeys, it will return None for invalid neighbors.

    >>> neighbors('032')
    ['021', '030', '031', '023', '032', '033', '201', '210', '211']
    >>> neighbors('020')
    [None, '002', '003', None, '020', '021', None, '022', '023']
    >>> neighbors('000')
    [None, None, None, None, '000', '001', None, '002', '003']
    '''
    north_n = _neighbors(quadkey, Direction.North)
    south_n = _neighbors(quadkey, Direction.South)
    return [
        _neighbors(north_n, Direction.West), north_n, _neighbors(north_n, Direction.East),
        _neighbors(quadkey, Direction.West), quadkey, _neighbors(quadkey, Direction.East),
        _neighbors(south_n, Direction.West), south_n, _neighbors(south_n, Direction.East)
    ]


class Direction:
    North = 0
    South = 1
    West = 2
    East = 3


V_LOOKUP = {
    '0': '2',
    '1': '3',
    '2': '0',
    '3': '1'
}
H_LOOKUP = {
    '0': '1',
    '1': '0',
    '2': '3',
    '3': '2'
}
LOOKUP = {
    Direction.North: V_LOOKUP,
    Direction.South: V_LOOKUP,
    Direction.West: H_LOOKUP,
    Direction.East: H_LOOKUP,
}
NEXT_QUADRANTS = {
    Direction.North: {'2', '3'},
    Direction.South: {'0', '1'},
    Direction.West: {'1', '3'},
    Direction.East: {'0', '2'},
}
QUADRANTS = ['0', '1', '2', '3']


def _neighbors(quadkey, direction):
    '''Get the neighbor for the given direction.

    Returns None if it crosses the north, south, or meridian boundaries.

    >>> _neighbors('02', Direction.North)
    '00'
    >>> _neighbors('00', Direction.South)
    '02'
    >>> _neighbors('00', Direction.East)
    '01'
    >>> _neighbors('03', Direction.West)
    '02'
    >>> _neighbors('032', Direction.West)
    '023'
    >>> _neighbors('000', Direction.West) is None
    True
    >>> _neighbors('000', Direction.North) is None
    True
    >>> _neighbors('000', Direction.South)
    '002'
    '''
    if not quadkey:
        return None
    zoom = len(quadkey)
    partial = LOOKUP[direction][quadkey[-1]]
    i = -1
    while quadkey[i] not in NEXT_QUADRANTS[direction]:
        i -= 1
        if -i > zoom:
            return None
        partial = LOOKUP[direction][quadkey[i]] + partial
    return quadkey[:i] + partial
