# win_resize.py
# Copyright: Andridov andrdidov@gmail.com
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import win32gui as wg32
import win32api as wa32
import win32con

import wx
import re
import time
import argparse
import collections

from threading import Thread
from datetime import datetime, timedelta

"""
The script for positioning windows on the screen.

Requirements:
You need AutoHotkey application to enable shorcuts on Windows OS. 
run the win_resize.ahk file. This enables you to run shortcut like:
left WIN+CTRL+C

How does it work?

1. Select your window to move/resize.
2. Imagine your desktop area divided in to cells:
┌───┬───┬───┬───┬───┐
│ 1 │ 2 │ 3 │ 4 │ 5 │
├───┼───┼───┼───┼───┤
│ q │ w │ e │ r │ t │
├───┼───┼───┼───┼───┤
│ a │ s │ d │ f │ g │
├───┼───┼───┼───┼───┤
│ z │ x │ c │ v │ b │
└───┴───┴───┴───┴───┘
Press shortcut for needed cells ratio. 
Example:
    Right WIN+CTRL+D activates script with ability to move window on any of 3x3 cells.

3. Define the bounding cells by pressing appropriate keys.
4. Press Enter to commit or Esc to quit.
"""

def do_argparse():
    parser = argparse.ArgumentParser(description='win_resize conmmand line')

    parser.add_argument('-m', type=str, required=True
        , help='size of grid can be 3x3 or 4x4')

    parser.add_argument

    args, other_args = parser.parse_known_args()

    return [args, other_args]


# user defined types section
Point = collections.namedtuple("Point", ["x", "y"])
Regn = collections.namedtuple("Regn", ["x", "y", "x2", "y2"])
Rect = collections.namedtuple("Rect", ["x", "y", "width", "height"])
Metric = collections.namedtuple("Metric", [
        "desktop_width"
        , "desktop_height"
        , "window_regn"
        , "client_rect"
        , "window_width"
        , "window_height" ])


# interfaces section
class DesktopMngrInterface:

    def get_metric_info(self) -> Metric:
        """A method return base metric parameters to represent in info tab """
        pass

    def move_window(self, lt_cell, rb_cell, dimention_x, dimention_y):
        """
        A method moves window

            lt_cell - left top cell of the window
            rb_cell - right bottom cell of the window
            dimention_x - numberr of cells in row
            dimention_y - number of cells in column
        """
        pass
    


class WinMngr(DesktopMngrInterface):
    def __init__(self):
        self.__base_hwnd = wg32.GetActiveWindow()
        if not self.__base_hwnd:
            self.__base_hwnd = wg32.GetForegroundWindow()

        self.__base_rect = wg32.GetWindowRect(self.__base_hwnd)
        self.__clnt_rect = wg32.GetClientRect(self.__base_hwnd)
        self._metric = Metric(
            desktop_width=wa32.GetSystemMetrics(win32con.SM_CXMAXIMIZED)-16 
            , desktop_height=wa32.GetSystemMetrics(win32con.SM_CYMAXIMIZED)-16
            , window_regn=Regn(self.__base_rect[0], self.__base_rect[1], 
                    self.__base_rect[2], self.__base_rect[3])
            , client_rect=Rect(self.__clnt_rect[0], self.__clnt_rect[1], 
                    self.__clnt_rect[2], self.__clnt_rect[3])
            , window_width=self.__base_rect[2]-self.__base_rect[0]
            , window_height=self.__base_rect[3]-self.__base_rect[1]
            )

        self._border_x = self._metric.window_width - self.__clnt_rect[2]
        self._border_y = self._metric.window_height - self.__clnt_rect[3]


    def get_metric_info(self):
        return self._metric

    
    def move_window(self, lt_cell, rb_cell, dimention_x, dimention_y):

        cell_w = self._metric.desktop_width / dimention_x
        cell_h = self._metric.desktop_height / dimention_y

        # window area x, y, width, height
        x = int(lt_cell.x * cell_w)
        y = int(lt_cell.y * cell_h)
        w = int((rb_cell.x - lt_cell.x + 1) * cell_w)
        h = int((rb_cell.y - lt_cell.y + 1) * cell_h)

        bl = int(self._border_x / 2)
        wg32.MoveWindow(
            self.__base_hwnd, x - bl, y, w + self._border_x, h + bl, True)


class NamesPool:
    def __init__(self, mode):
        self.__mode = mode
        self.__parse_mode()

        self._cell_names = [
            '1', '2', '3', '4', '5',
            'q', 'w', 'e', 'r', 't',
            'a', 's', 'd', 'f', 'g',
            'z', 'x', 'c', 'v', 'b']

        self.__max_dimention_x = 5
        self.__max_dimention_y = 4
        self.__init_collections()


    def __parse_mode(self):
        m = re.match(r"^(\d)x(\d)$", self.__mode)
        if not m:
            raise Exception(
                f"Error: bad dimentions settled in mode attrib: {self.__mode}")
        self.__dimention_x = int(m.group(1))
        self.__dimention_y = int(m.group(2))


    def __init_collections(self):
        NameItem = collections.namedtuple("NameItem", ["name", "x", "y"])
        self.__items_list = []
        self.__active_names_list = []

        for iy in range(self.__max_dimention_y):
            if iy >= self.__dimention_y:
                break

            for ix in range(self.__dimention_x):
                name = self._cell_names[iy * self.__max_dimention_x + ix]
                self.__active_names_list.append(name)
                self.__items_list.append(NameItem(name, ix, iy))


    def items(self):
        return self.__items_list


    def dimentions(self):
        return Point(self.__dimention_x, self.__dimention_y)



class Cell(wx.Button):
    def __init__(self, p, name_point):
        super().__init__(p, label=name_point.name)
        
        self.selected = False
        self.name = name_point.name
        self.x = name_point.x
        self.y = name_point.y
        self.__init_colors()

    def __init_colors(self):
        c = self.GetBackgroundColour()
        self.__default_color = c
        self.__selected_color = (0xFF, c[1] & 0x0F, c[2] & 0x0F, c[3]) 
        self.__in_zone_color = (0xFF, c[1] & 0xA0, c[2] & 0xA0, c[3])


    def on_select_button(self, evt):
        self.selected = not self.selected
        print(f"button pressed: name={self.name}, x={self.x}, y={self.y}, value={self.selected}")
        if evt:
            evt.Skip()


    def set_colour(self, color):
        if color == 0:
            self.SetBackgroundColour(self.__default_color)
        elif color == 1:
            self.SetBackgroundColour(self.__selected_color)
        else:
            self.SetBackgroundColour(self.__in_zone_color)



class Positer:
    def __init__(self, mode, desktop_mngr):
        self._desktop_manager = desktop_mngr
        
        metic = desktop_mngr.get_metric_info()
        self.__GRID_WIN_SIZE = (
            int(metic.desktop_width / 10)
            , int(metic.desktop_height / 9.5))

        self.__cell_names = NamesPool(mode)
        self.__selected_cells = []
        self.__cells = []
        self.__init_evt_key_ids()

    
    def __init_evt_key_ids(self):
        self.__evt_key_ids = {}
        for item in self.__cell_names.items():
            self.__evt_key_ids[wx.Window.NewControlId()] = item


    def __draw_cell_panel(self, nb):
        p = wx.Panel(nb)
        sizer = wx.GridBagSizer()

        for item in self.__cell_names.items():
            c = Cell(p, item)
            p.Bind(wx.EVT_BUTTON, self.__on_colour_btn, c)
            p.Bind(wx.EVT_BUTTON, c.on_select_button, c)
            sizer.Add(c, pos=(item.y, item.x), flag = wx.EXPAND|wx.ALL)
            self.__cells.append(c)
        
        dimentions = self.__cell_names.dimentions()

        for iy in range(dimentions.y):
             sizer.AddGrowableRow(iy)
        for ix in range(dimentions.x):
            sizer.AddGrowableCol(ix)
        p.SetSizerAndFit(sizer)
        nb.AddPage(p, "Cells")


    def __draw_info_panel(self, nb):
        metric = self._desktop_manager.get_metric_info()

        # f"desktop size {(metric.desktop_width, metric.desktop_height)}\n" \
        # f"window region {metric.window_regn}\n" \
        # f"client rect {metric.client_rect}\n" \
        # f"window_width  {metric.window_width}\n" \
        # f"window_height {metric.window_height}"

        p = wx.Panel(nb)
        sizer = wx.GridBagSizer()

        lbl_desktop_size = wx.StaticText(p, -1, 
            f"Desktop size: {(metric.desktop_width, metric.desktop_height )}")
        sizer.Add(lbl_desktop_size, pos=(0, 0), flag=wx.ALIGN_LEFT)

        sizer.AddGrowableRow(0)
        sizer.AddGrowableCol(0)
        p.SetSizerAndFit(sizer)
        nb.AddPage(p, "Info")


    def __draw_options_panel(self, nb):
        # not implemented now
        pass


    def __build_gui(self):
        self.__app = wx.App(False)
        style = ( wx.CLIP_CHILDREN | wx.STAY_ON_TOP |
                  wx.NO_BORDER | wx.FRAME_SHAPED  )
        

        metric = self._desktop_manager.get_metric_info()

        x = metric.window_regn.x2 - int(metric.window_width / 2) \
            - int(self.__GRID_WIN_SIZE[0]/2)
        y = metric.window_regn.y2 - int(metric.window_height / 2) \
            - int(self.__GRID_WIN_SIZE[1]/2)

        self.__grid_win = wx.Frame(None, wx.ID_ANY, pos=(x, y), style=style)
        p = wx.Panel(self.__grid_win)

        self.c_nb = wx.Notebook(p)
        sizer = wx.GridBagSizer()

        self.__draw_cell_panel(self.c_nb)
        self.__draw_info_panel(self.c_nb)
        self.__draw_options_panel(self.c_nb)
        sizer.Add(self.c_nb, pos =(0, 0), flag = wx.EXPAND|wx.ALL)

        sizer.SetSizeHints(p)
        sizer.AddGrowableRow(0)
        sizer.AddGrowableCol(0)
        p.SetSizerAndFit(sizer)

        self.__grid_win.SetSize(self.__GRID_WIN_SIZE)

        self.__create_accel_table(self.__grid_win)

        self.__grid_win.Show(True)
        self.__app.MainLoop()
        

    def __create_accel_table(self, win):
        self.event_id_close = wx.Window.NewControlId()
        self.event_id_enter = wx.Window.NewControlId()

        win.Bind(wx.EVT_MENU, self.__on_close, id=self.event_id_close)
        win.Bind(wx.EVT_MENU, self.__on_enter, id=self.event_id_enter)
        accel_list = [
            (wx.ACCEL_CTRL, ord('Q'), self.event_id_close),
            (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, self.event_id_close),
            (wx.ACCEL_NORMAL, wx.WXK_RETURN, self.event_id_enter)]
        
        for k,v in self.__evt_key_ids.items():
            win.Bind(wx.EVT_MENU, self.__on_select_cell, id=k)
            accel_list.append((wx.ACCEL_NORMAL, ord(v.name), k))

        accel_tbl = wx.AcceleratorTable(accel_list)
        win.SetAcceleratorTable(accel_tbl)


    def __get_boundary_cells(self):
        dimention = self.__cell_names.dimentions()
        lt_x = dimention.x
        lt_y = dimention.y
        rb_x = 0
        rb_y = 0

        for c in self.__cells:
            if c.selected:
                lt_x = min(lt_x, c.x)
                lt_y = min(lt_y, c.y)
                rb_x = max(rb_x, c.x)
                rb_y = max(rb_y, c.y)

        return (Point(lt_x, lt_y), Point(rb_x, rb_y))

    
    def __on_enter(self, evt):
        dimention = self.__cell_names.dimentions()
        (lt_cell, rb_cell) = self.__get_boundary_cells()
        self._desktop_manager.move_window( 
            lt_cell, rb_cell, dimention.x, dimention.y)
        self.__on_close(evt)


    def __on_close(self, evt):
        self.__grid_win.Close()
        # do your actions on close
        if evt != None:
            evt.Skip()


    def __on_select_cell(self, evt):
        print(f"event id={evt.GetId()}")
        (name, x, y) = self.__evt_key_ids[evt.GetId()]
        for c in self.__cells:
            if name == c.name:
                c.on_select_button(None)
                break
        self.__on_colour_btn(None)
        evt.Skip()

    def __on_colour_btn(self, evt):
        (lt_cell, rb_cell) = self.__get_boundary_cells()
        for c in self.__cells:
            if c.selected:
                c.set_colour(1)
            elif c.x in range(lt_cell.x, rb_cell.x + 1) and \
                c.y in range(lt_cell.y, rb_cell.y + 1):
                c.set_colour(2)
            else:
                c.set_colour(0)
        if evt:
            evt.Skip()


    def show(self):
        self.__build_gui()
        

    def close(self):
        self.__on_close(None)



def get_mngr():
    # supports only windows for now
    # but probably 
    mngr = WinMngr()
    return mngr


dialog_closed = False;

def wait_and_close(positer):
    exit = False;
    time_expire = datetime.now() + timedelta(seconds=10)
    while not exit:
        time.sleep(0.1)
        time_now = datetime.now()

        if time_now > time_expire:
            positer.close()
            exit = True

        if dialog_closed == True:
            exit = True

def main():
    [known_args, other_args] = do_argparse()

    p = Positer(known_args.m, get_mngr())
    global dialog_closed
    thread_timer= Thread(target=wait_and_close, args=(p,))

    thread_timer.start()

    p.show()
    dialog_closed = True

    thread_timer.join()

main()
