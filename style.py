#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Style
"""
import xml.dom
import xml.dom.minidom


__all__ = ['Style']


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


def getTextValue(element, name, default=''):
    if not element:
        return default
    child = getChild(element, name)
    if not child:
        return default
    return child.firstChild.data


def getValue(element, name, default=0):
    if not element:
        return default
    val = getTextValue(element, name, default)
    if not val:
        return default
    return int(val)


class Spacer(object):
    def __init__(self, left, top, right, bottom):
        self.left = int(left)
        self.top = int(top)
        self.right = int(right)
        self.bottom = int(bottom)

    def __unicode__(self):
        return u'%d, %d, %d, %d' % (
            self.left,
            self.top,
            self.right,
            self.bottom,
            )

    def __repr__(self):
        return u"%s(%d, %d, %d, %d)" % (
            self.__class__.__name__,
            self.left,
            self.top,
            self.right,
            self.bottom,
            )

    @staticmethod
    def create(cls, element, name):
        elem = getChild(element, name)
        left = getValue(elem, 'left')
        top = getValue(elem, 'top')
        right = getValue(elem, 'right')
        bottom = getValue(elem, 'bottom')
        return cls(left, top, right, bottom)


class Padding(Spacer):
    def __init__(self, left, top, right, bottom):
        Spacer.__init__(self, left, top, right, bottom)

    @classmethod
    def parse(cls, element):
        return Spacer.create(cls, element, 'padding')


class Margin(Spacer):
    def __init__(self, left, top, right, bottom):
        Spacer.__init__(self, left, top, right, bottom)

    @classmethod
    def parse(cls, element):
        return Spacer.create(cls, element, 'margin')


class Font(object):
    def __init__(self, family, size, weight):
        self.family = family
        self.size = size
        self.weight = weight

    @staticmethod
    def parse(element):
        el_font = getChild(element, 'font')
        family = getTextValue(el_font, 'family')
        size = getTextValue(el_font, 'size')
        weight = getTextValue(el_font, 'weight')
        return Font(family, size, weight)


class Mark(object):
    def __init__(self, radius, radius_inside, color_inside, font):
        self.radius = int(radius)
        self.radius_inside = int(radius_inside)
        self.color_inside = color_inside
        self.font = font

    @staticmethod
    def parse(element):
        el_mark = getChild(element, 'mark')
        radius = getValue(el_mark, 'radius')
        radius_inside = getValue(el_mark, 'radius-inside')
        color_inside = getTextValue(el_mark, 'color-inside')
        font = Font.parse(el_mark)
        return Mark(radius, radius_inside, color_inside, font)


class Text(object):
    def __init__(self, font, margin, color, height):
        self.font = font
        self.margin = margin
        self.color = color
        self.height = int(height)

    @staticmethod
    def parse(element):
        font = Font.parse(element)
        margin = Margin.parse(element)
        color = getTextValue(element, 'color', '#000')
        height = getValue(element, 'height')
        return Text(font, margin, color, height)


class Body(object):
    def __init__(self, padding):
        self.padding = padding

    @staticmethod
    def parse(element):
        el_body = getChild(element, 'body')
        padding = Padding.parse(el_body)
        return Body(padding)


class Station(object):
    def __init__(self, mark, text):
        self.mark = mark
        self.text = text

    @staticmethod
    def parse(element):
        el_station = getChild(element, 'station')
        mark = Mark.parse(el_station)
        text = Text.parse(el_station)
        return Station(mark, text)


class Link(object):
    def __init__(self, between, width):
        self.between = between
        self.width = width

    @staticmethod
    def parse(element):
        el_link = getChild(element, 'link')
        between = getValue(el_link, 'between', 10)
        width = getValue(el_link, 'width', 1)
        return Link(between, width)


class Change(object):
    def __init__(self, mark, text):
        self.mark = mark
        self.text = text

    @staticmethod
    def parse(element):
        el_change = getChild(element, 'change')
        mark = Mark.parse(el_change)
        text = Text.parse(el_change)
        return Change(mark, text)


class Style(object):
    def __init__(self, body, station, link, change):
        self.body = body
        self.station = station
        self.link = link
        self.change = change

    @staticmethod
    def parse(element):
        body = Body.parse(element)
        station = Station.parse(element)
        link = Link.parse(element)
        change = Change.parse(element)
        return Style(body, station, link, change)

    @staticmethod
    def load(filename):
        dom = xml.dom.minidom.parse(filename)
        return Style.parse(dom)


def test():
    style = Style.load('data/style.xml')
    print style.body.padding
    print style.station.text.margin


if __name__ == '__main__':
    test()
