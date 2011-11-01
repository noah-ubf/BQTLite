import wx.html
import re

_POST_RESIZE_EVENT = wx.NewEventType()

class _PostResizeEvent(wx.PyEvent):
    def __init__(self):
        wx.PyEvent.__init__(self)
        self.SetEventType(_POST_RESIZE_EVENT)

def EVT_POST_RESIZE(win, func):
    win.Connect(-1, -1, _POST_RESIZE_EVENT, func)

class exHtmlWindow(wx.html.HtmlWindow):
  linkClicked = None
  path = ''
  scrollpos = {}
  mode = 'text'
  busy = False
  ctrlDown = False
  fontSize = 3
  content = ''

  def __init__(self, parent, id, pos, size):
    wx.html.HtmlWindow.__init__(self,parent,id, pos, size)
    self.Bind (wx.EVT_SCROLLWIN, self.OnScroll)
    self.Bind (wx.EVT_SCROLLWIN_LINEUP, self.OnScrollUp)
    self.Bind (wx.EVT_SCROLLWIN_LINEDOWN, self.OnScrollDown)
    self.Bind (wx.EVT_SIZE, self.OnSize)
    EVT_POST_RESIZE(self, self.post_resize)
    self.Bind (wx.EVT_KEY_DOWN, self.OnKeyDown)
    self.Bind (wx.EVT_KEY_UP, self.OnKeyUp)

  def SetLinkClicked(self, func):
    self.linkClicked = func
  
  def OnLinkClicked(self, link):
    if(self.linkClicked):
      self.linkClicked(link)
    else:
      self.OutputHTML('Clicked:', link.GetHref())
    
  def OutputHTML(self, title, text, mode):
    self.saveScrollPos()
    content = ''
    if isinstance(text, basestring):
      content = text
    else:
      for part in text:
        content = content + part + '<br>'
    content = re.sub('\[', '<font color="gray"><i>[', re.sub('\]', ']</i></font>', content))
    if(title):
      content = "<h1>" + title + "</h1>" + content
    self.content = content
    fSize = str(int(self.fontSize/3))
    if(self.fontSize>0): fSize = '+' + fSize
    content = '<FONT size=' + fSize + '>' + content + '</FONT>'
    self.SetPage("<html><body>"+content+"</body></hmtl>")
    self.setMode(mode)
    self.restoreScrollPos()

  def setPath(self, path):
    self.path = path

  def OnCopy(self, event):
    clipdata = wx.TextDataObject()
    text = self.SelectionToText()
    clipdata.SetText(text)
    if wx.TheClipboard.Open():
      wx.TheClipboard.SetData(clipdata)
      wx.TheClipboard.Close()
	
  def getScrollPos(self):
    r = self.GetScrollRange(wx.VERTICAL)
    p = self.GetViewStart()[1]
    return int(p*10000/(r+1))

  def setScrollPos(self, scrollpos):
    r = self.GetScrollRange(wx.VERTICAL)
    p = int(scrollpos*(r+1)/10000)
    return self.Scroll(0, p)

  def saveScrollPos(self):
    self.scrollpos[self.mode] = self.getScrollPos()

  def restoreScrollPos(self):
    if(not self.mode in self.scrollpos):
      self.scrollpos[self.mode] = 0
    self.setScrollPos(self.scrollpos[self.mode])

  def clearScrollPos(self):
    self.scrollpos[self.mode] = 0
  
  def setMode(self, mode):
    self.mode = mode
    return self
  
  def getMode(self):
    return self.mode

  def OnKeyDown(self, event):
    if(event.GetKeyCode()==wx.WXK_CONTROL):
      self.ctrlDown = True
    event.Skip()

  def OnKeyUp(self, event):
    if(event.GetKeyCode()==wx.WXK_CONTROL):
      self.ctrlDown = False
    event.Skip()

  def OnScroll(self, event):
    event.Skip()
    self.saveScrollPos()

  def OnScrollUp(self, event):
    if(self.busy): return
    self.busy = True
    if(self.ctrlDown):
      if(self.fontSize<15):
        self.fontSize = self.fontSize + 1
        if(int(self.fontSize/3)*3==self.fontSize):
          fSize = str(int(self.fontSize/3))
          if(self.fontSize>0): fSize = '+' + fSize
          content = '<FONT size=' + fSize + '>' + self.content + '</FONT>'
          self.SetPage("<html><body>"+content+"</body></hmtl>")
          self.restoreScrollPos()
    else:
      event.Skip()
    self.busy = False

  def OnScrollDown(self, event):
    if(self.busy): return
    self.busy = True
    if(self.ctrlDown):
      if(self.fontSize>0):
        self.fontSize = self.fontSize - 1
        if(int(self.fontSize/3)*3==self.fontSize):
          fSize = str(int(self.fontSize/3))
          if(self.fontSize>0): fSize = '+' + fSize
          content = '<FONT size=' + fSize + '>' + self.content + '</FONT>'
          self.SetPage("<html><body>"+content+"</body></hmtl>")
          self.restoreScrollPos()
    else:
      event.Skip()
    self.busy = False

  def OnSize(self, event):
    wx.PostEvent(self, _PostResizeEvent())
    event.Skip()

  def post_resize(self, evt):
    self.restoreScrollPos()

  def scale(self, percentage):
    font = self.GetFont()
    if(font.IsUsingSizeInPixels()):
      font.SetPixelSize(int(font.GetPixelSize() + percentage))
      #font.SetPixelSize(int(font.GetPixelSize() * percentage / 100.0))
      #wx.MessageBox(str(int(font.GetPixelSize() * percentage / 100.0)), 'Font size', wx.OK | wx.ICON_INFORMATION, None)
    else:
      font.SetPointSize(int(font.GetPointSize() + percentage))
      #wx.MessageBox(str(int(font.GetPointSize() * percentage / 100.0)), 'Font size', wx.OK | wx.ICON_INFORMATION, None)
    self.SetFont(font)        
