#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import os

import wx


class PhotoFilmStripList(wx.ScrolledWindow):
    
    HEIGHT = 200
    BORDER = 40
    
    def __init__(self, parent, id=-1, 
                 pos=wx.DefaultPosition, size=wx.DefaultSize, 
                 style=wx.HSCROLL | wx.VSCROLL, name='PhotoFilmStripList'):
        wx.ScrolledWindow.__init__(self, parent, id, pos, size,  style, name)
        self.SetBackgroundColour(wx.BLACK)
        self.SetClientSizeWH(-1, self.HEIGHT+20)

        self.__pictures = []
        self.__selIdx   = -1
        self.__hvrIdx   = -1
        self.__buffer   = wx.EmptyBitmap(self.GetSizeTuple()[0], self.HEIGHT)
        self.__picStrip = None
        
        self.__UpdatePictures()
        
        self.SetScrollRate(1, 0)
        
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvent)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        
    def OnPaint(self, event):
        wx.BufferedPaintDC(self, self.__buffer, wx.BUFFER_VIRTUAL_AREA)
        event.Skip()
            
    def OnMouseWheel(self, event):
        rot = event.GetWheelRotation()
        linesPer = 40 #event.GetLinesPerAction()
        sp = self.GetScrollPos(wx.HORIZONTAL)
        if rot > 0:
            self.Scroll(sp - linesPer, -1)
        else:
            self.Scroll(sp + linesPer, -1)
            
    def OnMouseEvent(self, event):
        idx = self.HitTest(self.CalcUnscrolledPosition(event.GetPosition()))
        if event.Moving():
            if idx != self.__hvrIdx:
                self.__hvrIdx = idx
                self.UpdateBuffer()
        if event.Leaving():
            self.__hvrIdx = -1
            self.UpdateBuffer()
        if event.LeftDown():
            if idx != -1 and idx != self.__selIdx:
                self.Select(idx)
        event.Skip()
        
    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        sel = self.GetSelected()
        if key == wx.WXK_LEFT:
            if sel > 0:
                self.Select(sel - 1)
        
        elif key == wx.WXK_RIGHT:
            if sel < self.GetItemCount() - 1:
                self.Select(sel + 1)
        
        elif key == wx.WXK_END:
            self.Select(self.GetItemCount() - 1)
            
        elif key == wx.WXK_HOME:
            self.Select(0)

    def UpdateBuffer(self):
        dc = wx.BufferedDC(None, self.__buffer)
        dc.DrawBitmap(self.__picStrip, 0, 0)
        gcdc = wx.GCDC(dc)
        self.__DrawHighlights(gcdc)
        self.Refresh()
        
    def UpdatePictures(self):
        self.__UpdatePictures()

    def __UpdatePictures(self):
        width = self.__DrawPictures(None)
        self.__picStrip = wx.EmptyBitmap(width, self.HEIGHT)
        
        dc = wx.MemoryDC(self.__picStrip)
        width = self.__DrawPictures(dc)
        self.__DrawFilmStrip(dc, width)
        dc.SelectObject(wx.NullBitmap)
        
        self.SetVirtualSize((width, self.HEIGHT))
        self.__buffer = wx.EmptyBitmap(width, self.HEIGHT)
        self.UpdateBuffer()

    def __DrawFilmStrip(self, dc, width):
        dc.SetBrush(wx.WHITE_BRUSH)
        dc.SetPen(wx.WHITE_PEN)
        n = 0
        while 1:
            sx = (n * 32) + 10
            dc.DrawRoundedRectangle(sx, 14, 14, 20, 3)
            dc.DrawRoundedRectangle(sx, self.HEIGHT - 34, 14, 20, 3)
            if sx > width:
                break
            n += 1
            
    def __DrawPictures(self, dc):
        '''
        draws all pictures on specified dc and returns needed with of all drawn
        pictures. if dc is None nothing is drawn, but with is returned anyway.
        @param dc: A wx.DC object where the pictures are drawn to.
        @return: The width in pixels needed to draw all pictures.
        '''
        if dc is not None:
            dc.SetBackground(wx.BLACK_BRUSH)
            dc.Clear()
            font = wx.SystemSettings_GetFont(wx.SYS_ANSI_FIXED_FONT)
            font.SetPointSize(9)
            dc.SetFont(font)
            dc.SetTextForeground(wx.Color(237, 156, 0))
        sx = 10
        for idx, pic in enumerate(self.__pictures):
            pw, ph = float(pic.GetWidth()), float(pic.GetHeight())
            thumbHeight = self.HEIGHT - (2 * self.BORDER)
            thumbWidth = int(thumbHeight * (pw / ph))
            bmp = pic.GetScaledBitmap(thumbWidth, thumbHeight)

            if dc is not None:
                dc.DrawBitmap(bmp, sx, self.BORDER, True)
                labelRect = wx.Rect(sx, 0, thumbWidth, self.HEIGHT)
                dc.DrawLabel(str(idx + 1), labelRect, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_TOP)
                dc.DrawLabel(os.path.basename(pic.GetFilename()), 
                             labelRect, 
                             wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM)

            sx += thumbWidth + 10
            
        return sx

    def __DrawHighlights(self, dc):
        dc.SetPen(wx.TRANSPARENT_PEN)
        if self.__selIdx != -1:
            rect = self.GetThumbRect(self.__selIdx)
            col = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)
            dc.SetBrush(wx.Brush(wx.Color(col.Red(), col.Green(), col.Blue(), 180)))
            dc.DrawRectangleRect(rect)
        if self.__hvrIdx != -1:
            rect = self.GetThumbRect(self.__hvrIdx)
            col = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)
            color = wx.Color(col.Red(), col.Green(), col.Blue(), 80)
            dc.SetBrush(wx.Brush(color))
            dc.DrawRectangleRect(rect)

    def GetThumbRect(self, idx):
        sx = 10
        for pidx, pic in enumerate(self.__pictures):
            pw, ph = float(pic.GetWidth()), float(pic.GetHeight())
            thumbHeight = self.HEIGHT - (2 * self.BORDER)
            thumbWidth = int(thumbHeight * (pw / ph))
            
            if idx == pidx:
                rect = wx.Rect(sx, 0, thumbWidth, self.HEIGHT)
                return rect
        
            sx += thumbWidth + 10
 
    def HitTest(self, pos):
        sx = 10
        for idx, pic in enumerate(self.__pictures):
            pw, ph = float(pic.GetWidth()), float(pic.GetHeight())
            thumbHeight = self.HEIGHT - (2 * self.BORDER)
            thumbWidth = int(thumbHeight * (pw / ph))
            
            rect = wx.Rect(sx, 0, thumbWidth, self.HEIGHT)
            if rect.Contains(pos):
                return idx
        
            sx += thumbWidth + 10
        return -1
    
    def AddPicture(self, pic):
        self.__pictures.append(pic)
        self.__UpdatePictures()
        
    def InsertPicture(self, idx, pic):
        self.__pictures.insert(idx, pic)
        self.__UpdatePictures()
        
    def DeleteItem(self, idx):
        self.__pictures.pop(idx)
        if self.__selIdx >= len(self.__pictures):
            self.__selIdx = len(self.__pictures) - 1
        self.__UpdatePictures()
        
    def DeleteAllItems(self):
        self.__pictures = []
        self.__UpdatePictures()
        
    def GetItemCount(self):
        return len(self.__pictures)
    
    def GetPicture(self, idx):
        try:
            return self.__pictures[idx]
        except IndexError:
            return None
    def SetPicture(self, idx, pic):
        if idx in xrange(len(self.__pictures)):
            self.__pictures[idx] = pic
            self.__UpdatePictures()
        
    def GetPictures(self):
        return self.__pictures[:]
        
    def GetSelected(self):
        return self.__selIdx
    
    def Select(self, idx):
        if idx in xrange(len(self.__pictures)):
            evt = wx.ListEvent(wx.EVT_LIST_ITEM_SELECTED.typeId, self.GetId())
            evt.m_itemIndex = idx
            evt.m_oldItemIndex = self.__selIdx

            self.__selIdx = idx
            self.UpdateBuffer()
            
            self.GetEventHandler().ProcessEvent(evt)
            return True
        else:
            return False
        
    def SwapPictures(self, idxFrom, idxTo):
        picFrom = self.__pictures[idxFrom]
        picTo = self.__pictures[idxTo]
        self.__pictures[idxFrom] = picTo
        self.__pictures[idxTo] = picFrom
        self.__UpdatePictures()


#if __name__ == "__main__":
#    from core.Picture import Picture
#
#    
#    p1 = Picture('/home/jens/Bilder/1/CIMG0558.JPG')
#    p2 = Picture('/home/jens/Bilder/1/CIMG0559.JPG')
#    p3 = Picture('/home/jens/Bilder/1/CIMG0560.JPG')
#    p4 = Picture('/home/jens/Bilder/79.70.94.45/007.JPG')
#    
#    app = wx.PySimpleApp()
#    f = wx.Frame(None)
#    l = PhotoFilmStripList(f, style=wx.SUNKEN_BORDER)
#    l.AddPicture(p1)
#    l.AddPicture(p2)
#    l.AddPicture(p3)
#    l.AddPicture(p4)
#    f.Show()
#    app.MainLoop()
