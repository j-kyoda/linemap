#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""LatLong, Station, Link, Line, LineInfo
"""
import xml.dom.minidom

__all__ = ['LineInfo', 'Span']


def getChildren(element, path):
    if not element:
        return []
    names = path.split('/')
    for name in names[:-1]:
        element = element.getElementsByTagName(name)[0]
    return element.getElementsByTagName(names[-1])


def getChild(element, path):
    if not element:
        return None
    children = getChildren(element, path)
    if not children:
        return None
    return children[0]


def getTextValue(element, path, default=''):
    if not element:
        return default
    child = getChild(element, path)
    if not child:
        return default
    return child.firstChild.data


class Span(object):
    """It keeps span.
    """
    def __init__(self, begin_idx, end_idx, base_idx=None):
        """
        Arguments:
            begin_idx -- begin station index
            end_idx -- end station index
            base_idx -- base station index
        """
        self.begin_idx = begin_idx
        self.end_idx = end_idx
        self.base_idx = base_idx
        if self.base_idx is None:
            self.base_idx = self.begin_idx


class LatLong(object):
    """It keeps position.
    """
    __slots__ = ['latitude', 'longitude']

    def __init__(self, latitude, longitude):
        """
        Arguments:
            latitude -- latitude
            longitude -- longitude
        """
        if not latitude:
            latitude = 0.0
        self.latitude = float(latitude)
        if not longitude:
            longitude = 0.0
        self.longitude = float(longitude)

    def __unicode__(self):
        return ', '.join([
            '%f' % self.latitude,
            '%f' % self.longitude,
            ])

    def __repr__(self):
        return u'%s(%f, %f)' % (
            self.__class__.__name__,
            self.latitude,
            self.longitude,
            )

    @classmethod
    def parse(cls, element):
        """create latlong from xml element
        Attributes:
            element -- station element
        """
        return LatLong(
            element.getAttribute('latitude'),
            element.getAttribute('longitude'),
            )


class Station(object):
    """It keeps station info.
    """
    __slots__ = ['idx', 'name', 'latlong', 'code']

    def __init__(self, idx, name, latlong, code):
        """
        Arguments:
            idx -- index
            name -- station name
            latlong -- LatLong object
            code -- station code
        """
        if not idx:
            idx = -1
        self.idx = int(idx)
        self.name = name
        self.latlong = latlong
        self.code = code

    def __unicode__(self):
        return u', '.join([
            '%d' % self.idx,
            self.name,
            unicode(self.latlong),
            self.code,
            ])

    def __repr__(self):
        return u"%s(%d, u'%s', %s, u'%s')" % (
            self.__class__.__name__,
            self.idx,
            self.name,
            self.latlong,
            self.code,
            )

    def has_idx(self, idx):
        """Return true if has idx, false otherwise.
        Arguments:
            idx -- index
        Returns:
            True -- It has same idx.
            False -- It does not have same idx.
        """
        if self.idx == idx:
            return True
        return False

    def has_code(self):
        """Return true if has code, false otherwise.
        Arguments:
            None
        Returns:
            True -- It has code.
            False -- It has no code.
        """
        if self.code:
            return True
        return False

    @classmethod
    def parse(cls, el_station):
        """create station from xml element
        Arguments:
            el_station -- element
        Returns:
            Station object.
        """
        return Station(
            el_station.getAttribute('idx'),
            el_station.getAttribute('name'),
            LatLong.parse(el_station),
            el_station.getAttribute('code'),
            )


class Link(object):
    """It keeps link.
    """
    __slots__ = ['begin_idx', 'end_idx', 'kilometers', 'minutes']

    def __init__(self, begin_idx, end_idx, kilometers, minutes):
        self.begin_idx = int(begin_idx)
        self.end_idx = int(end_idx)
        self.kilometers = float(kilometers)
        self.minutes = int(minutes)

    def __unicode__(self):
        return u'%d, %d, %f, %d' % (
            self.begin_idx,
            self.end_idx,
            self.kilometers,
            self.minutes,
            )

    def __repr__(self):
        return u"%s(%d, %d, %f, %d)" % (
            self.__class__.__name__,
            self.begin_idx,
            self.end_idx,
            self.kilometers,
            self.minutes,
            )

    def gen_idx(self):
        """index generator
        """
        for idx in [self.begin_idx, self.end_idx]:
            yield idx

    def reverse(self):
        """make reverse link"""
        return Link(
            self.end_idx,
            self.begin_idx,
            self.kilometers,
            self.minutes,
            )

    @classmethod
    def parse(cls, el_link):
        """make link from xml element
        Arguments:
            el_link -- element
        """
        return Link(
            el_link.getAttribute('begin-idx'),
            el_link.getAttribute('end-idx'),
            el_link.getAttribute('kilometers'),
            el_link.getAttribute('minutes'),
            )


class Line(object):
    """It keeps line.
    """
    __slots__ = ['name', 'color', 'code']

    def __init__(self, name, color, code):
        self.name = name
        self.color = color
        self.code = code

    def __unicode__(self):
        return u'%s, %s, %s' % (
            self.name,
            self.color,
            self.code,
            )

    def __repr__(self):
        return u"%s(u'%s', u'%s', u'%s')" % (
            self.__class__.__name__,
            self.name,
            self.color,
            self.code,
            )

    def has_code(self):
        """Return true if code, false otherwise.
        Arguments:
            None
        Returns:
            True -- It has code.
            False -- It has no code.
        """
        if self.code:
            return True
        return False

    @classmethod
    def parse(cls, el_line):
        """make line from xml element
        Arguments:
            el_line -- element
        """
        return Line(
            el_line.getAttribute('name'),
            el_line.getAttribute('color'),
            el_line.getAttribute('code'),
            )


class Change(object):
    """It keeps change.
    """
    __slots__ = ['idx', 'line', 'station']

    def __init__(self, idx, line, station):
        self.idx = int(idx)
        self.line = line
        self.station = station

    def __unicode__(self):
        return u'%d, %s, %s' % (
            self.idx,
            unicode(self.line),
            unicode(self.station),
            )

    def __repr__(self):
        return u"%s(%d, %s, %s)" % (
            self.__class__.__name__,
            self.idx,
            self.line.__repr__(),
            self.station.__repr__(),
            )

    def has_idx(self, idx):
        """When object has idx return True, other return False
        Arguments:
            idx -- index
        """
        if self.idx == idx:
            return True
        return False

    def has_code(self):
        """When object has code return True, other return False
        Arguments:
            None
        """
        if self.line.code and self.station.code:
            return True
        return False

    @classmethod
    def parse(cls, el_change):
        """make change from xml element
        Arguments:
            el_change -- element
        """
        return Change(
            el_change.getAttribute('idx'),
            Line.parse(getChild(el_change, 'line')),
            Station.parse(getChild(el_change, 'station')),
            )


class LineInfo(object):
    """It keeps change.
    """
    __slots__ = ['line', 'stations', 'links', 'changes']

    def __init__(self, line, stations, links, changes):
        self.line = line
        self.stations = stations
        self.links = links
        self.changes = changes

    def __unicode__(self):
        return u'%s, %s' % (
            self.line.name,
            self.line.color,
            )

    def get_stations(self, idx=None):
        """
        Arguments:
            idx -- index
        """
        if idx is None:
            return tuple(self.stations)
        while idx < 0:
            idx += len(self.stations)
        return [station for station in self.stations if station.has_idx(idx)]

    def get_station_name(self, idx):
        """
        Arguments:
            idx -- station index
        """
        stations = self.get_stations(idx)
        if not stations:
            return u''
        return stations[0].name

    def gen_links(self, begin_idx=0, end_idx=-1):
        """
        Arguments:
            begin_idx -- begin stataion index
            end_idx -- end station index
        """
        while begin_idx < 0:
            begin_idx += len(self.stations)
        while end_idx < 0:
            end_idx += len(self.stations)

        if begin_idx == end_idx:
            raise StopIteration
        links = list(self.links)
        if begin_idx > end_idx:
            links.reverse()
            links = [link.reverse() for link in links]
            for link in links:
                if link.begin_idx > begin_idx:
                    continue
                if link.begin_idx <= end_idx:
                    raise StopIteration
                yield link
            raise StopIteration
        else:
            for link in links:
                if link.begin_idx < begin_idx:
                    continue
                if link.begin_idx >= end_idx:
                    raise StopIteration
                yield link
            raise StopIteration

    def gen_stations(self, begin_idx=0, end_idx=-1):
        """
        Arguments:
            begin_idx -- begin stataion index
            end_idx -- end station index
        """
        while begin_idx < 0:
            begin_idx += len(self.stations)
        while end_idx < 0:
            end_idx += len(self.stations)

        if begin_idx == end_idx:
            raise StopIteration
        links = list(self.links)
        if begin_idx > end_idx:
            links.reverse()
            links = [link.reverse() for link in links]
            for link in links:
                if link.begin_idx > begin_idx:
                    continue
                if link.begin_idx <= end_idx:
                    raise StopIteration
                yield link.begin_idx
            yield link.end_idx
            raise StopIteration
        else:
            for link in links:
                if link.begin_idx < begin_idx:
                    continue
                if link.begin_idx > end_idx:
                    raise StopIteration
                yield link.begin_idx
            yield link.end_idx
            raise StopIteration

    def get_changes(self, idx=None):
        """
        Arguments:
            idx -- station index
        """
        if idx is None:
            return tuple(self.changes)
        return [change for change in self.changes if change.has_idx(idx)]

    def get_minutes(self, begin_idx, end_idx, base_minutes=0):
        """
        Arguments:
            begin_idx -- begin station index
            end_idx -- end station index
            base_minutes -- base minutes
        """
        return sum(
            [link.minutes for link in self.gen_links(begin_idx, end_idx)]
            ) - base_minutes

    def get_kilometers(self, begin_idx, end_idx, base_kilometers=0):
        """
        Arguments:
            begin_idx -- begin station index
            end_idx -- end station index
            base_kilometers -- base kilometers
        """
        return sum(
            [link.kilometers for link in self.gen_links(begin_idx, end_idx)]
            ) - base_kilometers

    @classmethod
    def parse(cls, dom):
        """make line from xml element

        Arguments:
            dom -- element
        """
        elm = getChild(dom, 'line-info')
        return LineInfo(
            Line.parse(elm),
            [Station.parse(el) for el in getChildren(elm, 'stations/station')],
            [Link.parse(el) for el in getChildren(elm, 'links/link')],
            [Change.parse(el) for el in getChildren(elm, 'changes/change')],
            )

    @classmethod
    def load(cls, filename):
        """load from xmlfile

        Arguments:
            filename -- lineinfo file
        """
        dom = xml.dom.minidom.parse(filename)
        return cls.parse(dom)


def test():
    """Sample
    """
    infos = LineInfo.load('data/0005.xml')

    begin_idx = -1
    end_idx = 0
    base_idx = -1

    mes = [infos.line.name, infos.line.color]
    base_minutes = infos.get_minutes(begin_idx, base_idx)
    base_kilometers = infos.get_kilometers(begin_idx, base_idx)
    for link in infos.gen_links(begin_idx, end_idx):
        mes.append(
            u'%4.1f(%2d) %s' % (
                infos.get_kilometers(begin_idx, link.begin_idx,
                                     base_kilometers),
                infos.get_minutes(begin_idx, link.begin_idx, base_minutes),
                infos.get_station_name(link.begin_idx),
                )
            )
        change_text = u'\n'.join(
            ['     ||  -> %s' % change.line.name \
             for change in infos.get_changes(link.begin_idx)])
        if change_text:
            mes.append(change_text)
        mes.append('     ||')
    mes.append(
        u'%4.1f(%2d) %s' % (
            infos.get_kilometers(begin_idx, end_idx, base_kilometers),
            infos.get_minutes(begin_idx, end_idx, base_minutes),
            infos.get_station_name(end_idx),
            )
        )

    print u'\n'.join(mes).encode('utf-8')

    print [link for link in infos.gen_links(begin_idx, end_idx)]
    print [idx for idx in infos.gen_stations(begin_idx, end_idx)]

    print len(infos.stations)
    print infos.__unicode__().encode('utf-8')
    print infos.__repr__().encode('utf-8')

    print infos.stations[0].__unicode__().encode('utf-8')
    print infos.stations[0].__repr__().encode('utf-8')

    print infos.links[0].__unicode__().encode('utf-8')
    print infos.links[0].__repr__().encode('utf-8')

    print infos.changes[0].__unicode__().encode('utf-8')
    print infos.changes[0].__repr__().encode('utf-8')


if __name__ == "__main__":
    test()
