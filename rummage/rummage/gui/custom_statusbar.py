"""
Custom Status Bar.

https://gist.github.com/facelessuser/5750045

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
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
from collections import OrderedDict
import sys
import wx
import wx.lib.agw.supertooltip

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

if wx.VERSION > (2, 9, 4) and wx.VERSION < (3, 0, 3):
    def monkey_patch():
        """
        Monkey patch Supertooltips.

        Remove once WxPython gets its crap together.
        """

        import inspect
        import re
        target_line = re.compile(r'([ ]{8})(maxWidth = max\(bmpWidth\+\(textWidth\+self._spacing\*3\), maxWidth\)\n)')
        tt_source = inspect.getsourcelines(wx.lib.agw.supertooltip.ToolTipWindowBase.OnPaint)[0]
        count = 0
        found = False
        for line in tt_source:
            if not found:
                m = target_line.match(line)
                if m:
                    tt_source[count] = m.group(0)
                    found = True
                    count += 1
                    continue
            tt_source[count] = line[4:]
            count += 1
        exec(''.join(tt_source))
        wx.lib.agw.supertooltip.ToolTipWindowBase.OnPaint = OnPaint  # noqa

    monkey_patch()


class ContextMenu(wx.Menu):

    """Context Menu."""

    def __init__(self, parent, menu, pos):
        """Attach the context menu to to the parent with the defined items."""

        wx.Menu.__init__(self)
        self._callbacks = {}

        for i in menu:
            menuid = wx.NewId()
            item = wx.MenuItem(self, menuid, i[0])
            self._callbacks[menuid] = i[1]
            self.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.on_callback, item)

        parent.PopupMenu(self, pos)

    def on_callback(self, event):
        """Execute the menu item callback."""

        menuid = event.GetId()
        self._callbacks[menuid](event)
        event.Skip()


class ToolTip(wx.lib.agw.supertooltip.SuperToolTip):

    """Tooltip."""

    def __init__(self, target, message, header="", style="Office 2007 Blue", start_delay=.1):
        """Attach the defined tooltip to the target."""

        super(ToolTip, self).__init__(message, header=header)
        self.SetTarget(target)
        self.ApplyStyle(style)
        self.SetStartDelay(start_delay)
        target.tooltip = self

    def hide(self):
        """Hide the tooltip."""

        if self._superToolTip:
            self._superToolTip.Destroy()


class TimedStatusExtension(object):

    """Timed status in status bar."""

    def set_timed_status(self, text):
        """
        Set the status for a short time.

        Save the previous status for restore
        when the timed status completes.
        """

        if self.text_timer.IsRunning():
            self.text_timer.Stop()
        else:
            self.saved_text = self.GetStatusText(0)
        self.SetStatusText(text, 0)
        self.text_timer.Start(5000, oneShot=True)

    def sb_time_setup(self):
        """Setup timer for timed status."""

        self.saved_text = ""
        self.text_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.clear_text, self.text_timer)

    def clear_text(self, event):
        """Clear the status."""

        self.SetStatusText(self.saved_text, 0)

    def set_status(self, text):
        """Set the status."""

        if self.text_timer.IsRunning():
            self.text_timer.Stop()
        self.SetStatusText(text, 0)


class IconTrayExtension(object):

    """Add icon tray extension."""

    def remove_icon(self, name):
        """Remove an icon from the tray."""

        if name in self.sb_icons:
            self.hide_tooltip(name)
            self.sb_icons[name].Destroy()
            del self.sb_icons[name]
            self.place_icons(resize=True)

    def hide_tooltip(self, name):
        """Hide the tooltip."""

        if self.sb_icons[name].tooltip:
            self.sb_icons[name].tooltip.hide()

    def set_icon(
        self, name, icon, msg=None, context=None,
        click_right=None, click_left=None,
        dclick_right=None, dclick_left=None
    ):
        """
        Set the given icon in the tray.

        Attach a menu and/or tooltip if provided.
        """

        if name in self.sb_icons:
            self.hide_tooltip(name)
            self.sb_icons[name].Destroy()
        self.sb_icons[name] = wx.StaticBitmap(self, bitmap=icon)
        if msg is not None:
            ToolTip(self.sb_icons[name], msg)
        if click_left is not None:
            self.sb_icons[name].Bind(wx.EVT_LEFT_DOWN, click_left)
        if context is not None:
            self.sb_icons[name].Bind(wx.EVT_RIGHT_DOWN, lambda e: self.show_menu(name, context))
        elif click_right is not None:
            self.sb_icons[name].Bind(wx.EVT_RIGHT_DOWN, click_right)
        if dclick_left is not None:
            self.sb_icons[name].Bind(wx.EVT_LEFT_DCLICK, dclick_left)
        if dclick_right is not None:
            self.sb_icons[name].Bind(wx.EVT_RIGHT_DCLICK, dclick_right)
        self.place_icons(resize=True)

    def show_menu(self, name, context):
        """Show context menu on icon in tray."""

        self.hide_tooltip(name)
        ContextMenu(self, context, self.sb_icons[name].GetPosition())

    def place_icons(self, resize=False):
        """Calculate new icon position and icon tray size."""

        x_offset = 0
        if resize:
            if _PLATFORM in "osx":
                # OSX must increment by 10
                self.SetStatusWidths([-1, len(self.sb_icons) * 20 + 10])
            elif _PLATFORM == "windows":
                # In at least wxPython 2.9+, the first icon inserted changes the size, additional icons don't.
                # I've only tested >= 2.9.
                if len(self.sb_icons):
                    self.SetStatusWidths([-1, (len(self.sb_icons) - 1) * 20 + 1])
                else:
                    self.SetStatusWidths([-1, len(self.sb_icons) * 20 + 1])
            else:
                # Linux? Should be fine with 1, but haven't tested yet.
                self.SetStatusWidths([-1, len(self.sb_icons) * 20 + 1])
        rect = self.GetFieldRect(1)
        for v in self.sb_icons.values():
            v.SetPosition((rect.x + x_offset, rect.y))
            v.Hide()
            v.Show()
            x_offset += 20

    def on_sb_size(self, event):
        """Ensure icons are properly placed on resize."""

        event.Skip()
        self.place_icons()

    def sb_tray_setup(self):
        """Setup the status bar with icon tray."""

        self.SetFieldsCount(2)
        self.SetStatusText('', 0)
        self.SetStatusWidths([-1, 1])
        self.sb_icons = OrderedDict()
        self.Bind(wx.EVT_SIZE, self.on_sb_size)


class CustomStatusExtension(IconTrayExtension, TimedStatusExtension):

    """Custom status extension."""

    def sb_setup(self):
        """Setup the extention variant of the CustomStatusBar object."""

        self.sb_tray_setup()
        self.sb_time_setup()


class CustomStatusBar(wx.StatusBar, CustomStatusExtension):

    """Custom status bar."""

    def __init__(self, parent, name):
        """Init the CustomStatusBar object."""

        super(CustomStatusBar, self).__init__(
            parent,
            id=wx.ID_ANY,
            style=wx.STB_DEFAULT_STYLE,
            name=name
        )
        self.sb_setup()


def extend(instance, extension):
    """Extend instance with extension class."""

    instance.__class__ = type(
        b'%s_extended_with_%s' % (instance.__class__.__name__, extension.__name__),
        (instance.__class__, extension),
        {}
    )


def extend_sb(sb):
    """Extend the statusbar."""

    extend(sb, CustomStatusExtension)
    sb.sb_setup()
