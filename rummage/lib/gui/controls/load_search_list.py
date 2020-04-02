"""
Load search list.

Licensed under MIT
Copyright (c) 2013 - 2015 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""
import wx
from .dynamic_lists import DynamicList
from ..localization import _
from .. import data


class SavedSearchList(DynamicList):
    """Error list."""

    def __init__(self, parent):
        """Initialization."""

        self.localize()

        super().__init__(
            parent,
            [
                self.NAME,
                self.COMMENT,
                self.SEARCH,
                self.REPLACE,
                self.FLAGS,
                self.TYPE,
                self.REPLACE_TYPE
            ]
        )

    def localize(self):
        """Translate strings."""

        self.NAME = _("Name")
        self.COMMENT = _("Comment")
        self.SEARCH = _("Search")
        self.REPLACE = _("Replace")
        self.FLAGS = _("Flags")
        self.TYPE = _("Type")
        self.REPLACE_TYPE = _("Replace Type")

    def create_image_list(self):
        """Create image list."""

        self.tint = data.RGBA(self.GetForegroundColour().Get())
        self.images = wx.ImageList(16, 16)
        self.glass = self.images.Add(data.get_bitmap('glass.png', tint=self.tint))
        self.sort_up = self.images.Add(data.get_bitmap('arrow_up.png', tint=self.tint, alpha=0.3))
        self.sort_down = self.images.Add(data.get_bitmap('arrow_down.png', tint=self.tint, alpha=0.3))
        self.AssignImageList(self.images, wx.IMAGE_LIST_SMALL)

    def get_item_text(self, item, col, absolute=False):
        """Return the text for the given item and col."""

        if not absolute:
            item = self.itemIndexMap[item]
        return self.itemDataMap[item][self.get_real_col(col)]