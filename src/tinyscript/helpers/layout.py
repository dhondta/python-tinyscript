# -*- coding: UTF-8 -*-
"""CLI layout objects.

"""
from .common import lazy_load_module, lazy_object
from .termsize import get_terminal_size

for _m in ["terminaltables", "textwrap"]:
    lazy_load_module(_m)


__all__ = __features__ = ["BorderlessTable", "NameDescription"]


def __init_tables():
    class _NoBorder(terminaltables.AsciiTable):
        """ AsciiTable with no border. """
        def __init__(self, *args, **kwargs):
            super(_NoBorder, self).__init__(*args, **kwargs)
            self.outer_border = False
            self.inner_column_border = False
            self.inner_heading_row_border = False
        
        def __str__(self):
            t = self.table
            return "\n" + t + "\n" if len(t) > 0 else ""
    
    class BorderlessTable(_NoBorder):
        """ Custom table with no border. """
        def __init__(self, data, title=None, title_ul_char="=", header_ul_char="-", header=True, indent=3):
            if len(data) == 0:
                raise ValueError("Invalid data ; should be a non-empty")
            self.data = data
            if data is None or not isinstance(data, list) or not all(isinstance(r, list) for r in data):
                raise ValueError("Invalid data ; should be a non-empty list of lists")
            if header:
                # add a row with underlining for the header row
                data.insert(1, [len(_) * header_ul_char for _ in data[0]])
            if len(data) < 2:
                raise ValueError("Invalid data ; should be a non-empty")
            # now insert an indentation column
            if (indent or 0) > 0:
                for row in data:
                    row.insert(0, max(0, indent - 3) * " ")
            # then initialize the AsciiTable
            super(BorderlessTable, self).__init__(data)
            # wrap the text for every column that has a width above the average
            n_cols, sum_w, c_widths = len(self.column_widths), sum(self.column_widths), []
            try:
                width, _ = get_terminal_size()
            except TypeError:
                width = 80
            width -= n_cols * 2  # take cell padding into account
            max_w = round(float(width) / n_cols)
            rem = width - sum(w for w in self.column_widths if w <= max_w)
            c_widths = [w if w <= max_w else max(round(float(w) * width / sum_w), max_w) for w in self.column_widths]
            if sum(c_widths) >= width:
                c_widths[c_widths.index(max(c_widths))] -= sum(c_widths) - width
            for row in self.table_data:
                for i, v in enumerate(row):
                    if len(str(v)) > 0:
                        row[i] = "\n".join(textwrap.wrap(str(v), c_widths[i]))
            # configure the title
            self.title_ = title  # define another title to format it differently
            self.title_ul_char = title_ul_char
        
        def __str__(self):
            return self.table
        
        @property
        def table(self):
            t = self.title_
            s = ("\n{}\n{}\n".format(t, len(t) * self.title_ul_char) if t is not None else "") + "\n{}\n"
            return s.format(super(BorderlessTable, self).table)
    
    class NameDescription(_NoBorder):
        """ Row for displaying a name-description pair, with details if given. """
        indent = 4
        
        def __init__(self, name, descr, details=None, nwidth=16):
            # compute the name column with to a defined width
            n = "{n: <{w}}".format(n=name, w=nwidth)
            # then initialize the AsciiTable, adding an empty column for indentation
            super(NameDescription, self).__init__([[" " * max(0, self.indent - 3), n, ""]])
            # now wrap the text of the last column
            max_w = self.column_max_width(-1)
            self.table_data[0][2] = "\n".join(textwrap.wrap(descr, max_w))
            self._details = details
        
        def __str__(self):
            s = super(NameDescription, self).__str__()
            if self._details:
                s += str(NameDescription(" ", self._details, nwidth=self.indent-2))
            return s
    
    return _NoBorder, BorderlessTable, NameDescription
_NoBorder, BorderlessTable, NameDescription = lazy_object(__init_tables)

