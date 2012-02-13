#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Line Map
"""
import Tkinter as Tk
import xml.dom.minidom

from lineinfo import LineInfo
from lineinfo import Span
from style import Style


class Point(object):
    """Position
    """
    def __init__(self, pos_x, pos_y):
        self.x = int(pos_x)
        self.y = int(pos_y)


class LineMap(Tk.Frame):
    """LineMap widget
    """
    def __init__(self, master=None, view_size=(320, 480)):
        """
        Arguments:
            master -- parent widget
        """
        Tk.Frame.__init__(self, master)
        self.pack()

        self.view_size = view_size
        self.map_size = view_size
        (view_width, view_height) = self.view_size
        (map_width, map_height) = self.map_size

        self.view = Tk.Canvas(self,
                              borderwidth=2,
                              background='#fff',
                              width=view_width,
                              height=view_height,
                              scrollregion=(0, 0,
                                            map_width + 1,
                                            map_height + 1))
        # vscroll
        self.vscroll = Tk.Scrollbar(self,
                                    command=self.view.yview,
                                    orient=Tk.VERTICAL)
        # hscroll
        self.hscroll = Tk.Scrollbar(self,
                                    command=self.view.xview,
                                    orient=Tk.HORIZONTAL)
        self.view["xscrollcommand"] = self.hscroll.set
        self.view["yscrollcommand"] = self.vscroll.set
        self.view.grid(row=0, column=0)
        self.vscroll.grid(row=0, column=1, sticky=Tk.N + Tk.S)
        self.hscroll.grid(row=1, column=0, sticky=Tk.E + Tk.W)

    def map_resize(self, line_info, style):
        map_size = self.calc_map_size(line_info, style, self.view_size)
        (canvas_width, canvas_height) = map_size
        self.view.configure(scrollregion=(0, 0,
                                          canvas_width + 1,
                                          canvas_height + 1))
        for oid in self.view.find_all():
            self.view.delete(oid)

    def draw_mark(self, center, color, mark, text):
        """
        Arguments:
            center -- center posion
            color -- mark color
            mark -- style mark
            text -- text in mark
        """
        for (radius, col) in [
            (mark.radius, color),
            (mark.radius_inside, mark.color_inside),
            ]:
            self.view.create_oval(center.x - radius, center.y - radius,
                                  center.x + radius, center.y + radius,
                                  outline=col,
                                  fill=col)
        self.view.create_text(
            center.x,
            center.y,
            font=(mark.font.family,
                  mark.font.size,
                  mark.font.weight,
                  ),
            anchor=Tk.CENTER,
            text=text,
            )

    def draw_change(self, base, changes, style):
        """
        Arguments:
            base -- current node center point
            changes -- change info list
            style -- decoration info
        """
        mark_changes = []
        text_changes = []
        for change in changes:
            if change.line.has_code():
                mark_changes.append(change)
            else:
                text_changes.append(change)
        # mark
        center = Point(
            sum([
                base.x,
                style.station.mark.radius,
                style.station.text.margin.left,
                style.change.mark.radius,
                ]),
            sum([
                base.y,
                style.station.mark.radius,
                style.change.mark.radius,
                ])
            )
        for change in mark_changes:
            self.draw_mark(center, change.line.color,
                           style.change.mark, change.line.code)
            center.x += style.change.mark.radius * 2

        # text
        if not text_changes:
            return
        change_text = u', '.join(
            ['%s' % change.line.name for change in text_changes]
            )
        corner = Point(
            sum([
                base.x,
                style.station.mark.radius,
                style.station.text.margin.left,
                ]),
            sum([
                base.y,
                style.station.mark.radius,
                ])
            )
        if mark_changes:
            corner.y += style.change.mark.radius * 2
        self.view.create_text(corner.x,
                              corner.y,
                              text="%s" % change_text,
                              anchor=Tk.NW,
                              font=(style.change.text.font.family,
                                    style.change.text.font.size,
                                    ),
                              fill=style.change.text.color,
                              )

    def draw_node(self, base, color, name, minutes, style):
        """
        Argumetns:
            base -- current node center position
            color -- station color
            name -- station name
            minutes -- station minutes
            style -- decoration info
        """
        self.draw_mark(base, color, style.station.mark, "%d" % minutes)
        mark = style.station.mark
        text = style.station.text
        self.view.create_text(
            base.x + mark.radius + text.margin.left,
            base.y,
            font=(text.font.family, text.font.size),
            anchor=Tk.W,
            text="%s" % name)

    def draw(self, line_info, style, span=Span(0, -1)):
        """
        Arguments:
            line_info -- line info
            style -- decoration info
            span -- draw station index
        """
        self.map_resize(line_info, style)
        # offset
        center_x = sum([
            style.body.padding.left,
            style.station.mark.radius,
            ])
        center_y = sum([
            style.body.padding.top,
            style.station.mark.radius,
            ])
        base_minutes = line_info.get_minutes(span.begin_idx, span.base_idx)
        base_kilos = line_info.get_kilometers(span.begin_idx, span.base_idx)

        # draw
        color = line_info.line.color
        link_length = 0
        for link in line_info.gen_links(span.begin_idx, span.end_idx):
            link_length += sum([
                style.station.mark.radius,
                style.link.between,
                self.calc_change_height(line_info, style, link.begin_idx),
                style.station.mark.radius,
                ])
        # draw link
        pos_list = [(center_x, center_y),
                    (center_x, center_y + link_length)]
        self.view.create_line(*pos_list,
                              smooth=False,
                              fill=line_info.line.color,
                              width=style.link.width)

        for station_idx in line_info.gen_stations(span.begin_idx,
                                                  span.end_idx):
            link_height = sum([
                style.station.mark.radius,
                style.link.between,
                self.calc_change_height(line_info, style, station_idx),
                style.station.mark.radius,
                ])
            # draw station
            kilo = line_info.get_kilometers(
                span.begin_idx, link.begin_idx, base_kilos)
            minutes = line_info.get_minutes(
                span.begin_idx, station_idx, base_minutes)
            node_name = line_info.get_station_name(station_idx)
            self.draw_node(Point(center_x, center_y), color, node_name,
                           minutes, style)
            # draw change
            changes = line_info.get_changes(station_idx)
            self.draw_change(Point(center_x, center_y), changes, style)

            center_y += link_height

    @classmethod
    def calc_change_height(cls, line_info, style, idx):
        """
        Arguments:
            line_info -- line info
            style -- decoration info
            idx -- station index
        """
        changes = line_info.get_changes(idx)
        mark_height = 0
        text_height = 0
        for change in changes:
            if change.line.has_code():
                mark_height = style.change.mark.radius * 2
            else:
                text_height = style.change.text.height
        return mark_height + text_height

    @classmethod
    def calc_change(cls, line_info, style, begin_idx=0, end_idx=-1):
        """
        Arguments:
            line_info -- line info
            style -- decoration info
            begin_idx -- begin index
            end_idx -- end index
        """
        idx_list = [idx for idx in line_info.gen_stations(begin_idx, end_idx)]
        total_height = sum([cls.calc_change_height(line_info, style, idx)
                            for idx in idx_list])

        return total_height

    @classmethod
    def calc_map_size(cls, line_info, style, min_size):
        """
        Arguments:
            line_info -- line info
            style -- decoration info
            min_size -- minimum width, minimum height
        """
        (min_width, min_height) = min_size
        nodes = line_info.get_stations()
        map_width = max([
            sum([
                style.body.padding.left,
                style.station.mark.radius * 2,
                style.body.padding.right,
                ]),
            min_width,
            ])
        map_height = max([
            sum([
                style.body.padding.top,
                style.station.mark.radius * 2 * len(nodes),
                cls.calc_change(line_info, style),
                style.link.between * (len(nodes) - 1),
                style.body.padding.bottom,
                ]),
            min_height,
            ])
        return (map_width, map_height)


def test():
    """open file
    """
    style = Style.load('data/style.xml')
    infos = LineInfo.load('data/0001.xml')

    line_map = LineMap()
    line_map.draw(infos, style, Span(-1, 0, -1))
    #line_map.draw(infos, style, Span(0, -1))
    line_map.mainloop()

if __name__ == "__main__":
    test()
