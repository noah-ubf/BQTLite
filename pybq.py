#!/bin/env python
# -*- coding: UTF-8 -*-

import wx
import os
import sys
import shutil
import re
import math
from bqList import MyBibleList
from exhtml import exHtmlWindow

class MyApp(wx.App):

  path = None

  def __init__(self, *args, **kwds):
    wx.App.__init__ (self, *args, **kwds)

  def OnInit(self):
    self.path = os.path.realpath(os.path.dirname(sys.argv[0]))
    #self.path = '/home/noah/Files/Soft-Win/BibleQuote'
    self.SetAppName('BQTlite')
    self.SetClassName('BQT reader lite')
    frame = MyFrame("BQT reader lite", (150, 72), (667, 740))
    frame.Show()
    self.SetTopWindow(frame)
    return True

class MyFrame(wx.Frame):

  path = ''
  strongs = False
  page = None
  findPanel = None
  sizer = None
  bibles = None
  activeModule = None
  compareModule = None
  buttonz = {}
  searchField = None
  strongsOn = False
  currentBook = -1
  currentChapter = -1
  fullScreen = False

  def buttonData(self):
    return (("RST", self.OnModule, 'module', 130, 'Module', ''),
    ("Genesis", self.OnBook, 'book', 200, 'Book', ''),
    ("<", self.PrevChapter, None, 20, 'Previous chapter', ''),
    ("1", self.OnChapter, 'chapter', 40, 'Chapter', ''),
    (">", self.NextChapter, None, 20, 'Next chapter', ''),
    ("#", self.ToggleStrongs, 'strongs', 30, 'Toggle Strong numbers', ''),
    ("H", self.OnHistory, 'history', 30, 'History', 'HistoryButton.bmp'),
    ("S", self.OnFind, 'find', 30, 'Search', 'SearchButton.bmp'),
    ("-Compare-", self.OnCompare, 'compare', 130, 'Compare translation with...', ''),
    ('F', self.ToggleFullScreen, None, 30, 'Toggle fullscreen', 'FullScreen.bmp'))

  def createButtonBar(self, panel, yPos = 0):
    xPos = 0
    height = 0
    for eachLabel, eachHandler, eachName, eachWidth, eachHint, eachPic in self.buttonData():
      pos = (xPos, yPos)
      button = self.buildOneButton(panel, eachLabel, eachHandler, pos, eachHint, eachPic, height)
      if(eachName):
        self.buttonz[eachName] = button
      if(eachWidth):
        button.SetSize((eachWidth, -1))
      xPos += button.GetSize().width
      if(button.GetSize().height>height): 
        height=button.GetSize().height
    return height

  def buildOneButton(self, parent, label, handler, position=(0,0), hint='', img='', height=0):
    if(img and os.path.exists(self.path + '/GLYPHS/' + img)):
      image1 = wx.Image(self.path + '/GLYPHS/' + img,\
                        wx.BITMAP_TYPE_ANY).ConvertToBitmap()
      button = wx.BitmapButton(parent, id=-1, bitmap=image1,
          pos=position, size = (height, height))
    elif(img and os.path.exists(self.path + '/help/buttons/' + img)):
      image1 = wx.Image(self.path + '/help/buttons/' + img,\
                        wx.BITMAP_TYPE_ANY).ConvertToBitmap()
      button = wx.BitmapButton(parent, id=-1, bitmap=image1,
          pos=position, size = (height, height))
    else:
      button = wx.Button(parent, -1, label, position)
    self.Bind(wx.EVT_BUTTON, handler, button)
    if(hint):
      button.SetToolTip(wx.ToolTip(hint))
    return button

  def createTabs(self):
    # create notebook
    notebook = wx.Notebook( self, -1, (0,40), (500,500))
    # create pages
    ctrl = wx.Panel( notebook, -1 )
    # add pages
    notebook.AddPage( wx.TextCtrl( notebook, -1 ), "Page 1", False, -1 )
    notebook.AddPage( ctrl, "Page 2 Will be Selected", True, -1 )
    self.page = wx.html.HtmlWindow(ctrl, -1, (0,0), (200, 200))
    return notebook

  def __init__(self, title, pos, size):
    self.path = os.path.realpath(os.path.dirname(sys.argv[0]))
    #self.path = '/home/noah/Files/Soft-Win/BibleQuote'
    self.bibles = MyBibleList()
    wx.Frame.__init__(self, None, -1, title, pos, size)
    #self.createMenuBar()
    self.panel = wx.Panel(self, -1)
    self.panel.SetBackgroundColour("Yellow")
    height = self.createButtonBar(self.panel)
    #notebook = self.createTabs()
    self.page = exHtmlWindow(self, -1, (0,0), (100,100))
    self.page.SetLinkClicked(self.OnLinkClicked)
    self.findPanel = wx.Panel(self, -1)
    self.searchField = wx.TextCtrl(self.findPanel, -1, '', (0,0))
    self.findButton = wx.Button(self.findPanel, -1, 'Find', (100,0))
    self.Bind(wx.EVT_BUTTON, self.OnSearchStart, self.findButton)
    self.findPanel.Hide()
    self.CreateStatusBar()
    self.SetStatusText("Ready")
    self.strongs = False
    self.bibles.loadList(self.path)
    self.__do_layout()
    if(len(self.bibles.history)>0):
      history0 = self.bibles.history[0]
      self.bibleGo(history0['command'][3:])
    else:
      self.OnModule(None)
    self.Bind (wx.EVT_CLOSE, self.OnClose)
    favicon = wx.Icon(self.path + '/favicon.ico', wx.BITMAP_TYPE_ICO, 16, 16)
    self.SetIcon(favicon)

    import gobject
    gobject.threads_init()
    import pygtk
    pygtk.require('2.0')
    import gtk, gtk.gdk
    self.taskBarIcon = favicon
    

  def __do_layout(self):
    self.sizer = wx.FlexGridSizer(3, 1, 0, 0)
    self.sizer.Add(self.panel, 1, flag = wx.EXPAND)
    self.sizer.Add(self.findPanel, 2, flag = wx.EXPAND)
    self.sizer.Add(self.page, 3, flag = wx.EXPAND)
    self.sizer.AddGrowableRow(2)
    self.sizer.AddGrowableCol(0)
    self.SetSizer(self.sizer)
    searchSizer = wx.FlexGridSizer(1, 2, 0, 0)
    searchSizer.Add(self.searchField, 1, flag = wx.EXPAND)
    searchSizer.Add(self.findButton, 2, flag = wx.EXPAND)
    searchSizer.AddGrowableCol(0)
    self.findPanel.SetSizer(searchSizer)
    self.Layout()

  def arrangeControls(self):
    if(self.page.getMode()=='search'):
      self.findPanel.Show()
    else:
      self.findPanel.Hide()
    if(not self.activeModule or not self.activeModule.Bible \
       or not self.activeModule.StrongNumbers):
      self.strongsOn = False
    if(self.strongsOn):
      self.buttonz['strongs'].SetForegroundColour('Green')
    else:
      self.buttonz['strongs'].SetForegroundColour('Black')
    if(self.activeModule):
      self.buttonz['module'].SetLabel(self.activeModule.BibleShortName)
      self.buttonz['book'].SetLabel(self.activeModule.FullName[self.currentBook])
      self.buttonz['chapter'].SetLabel(str(self.currentChapter))
      statusText = self.activeModule.BibleName
    else:
      self.buttonz['module'].SetLabel('')
      self.buttonz['book'].SetLabel('')
      self.buttonz['chapter'].SetLabel('')
      statusText = 'Select a module'
    if(self.compareModule):
      statusText = statusText + ' | ' + self.compareModule.BibleName
      self.buttonz['compare'].SetLabel(self.compareModule.BibleShortName)
    else:
      self.buttonz['compare'].SetLabel('-Compare-')
    statusText = statusText + ' | ' + 'Mode: ' +self.page.getMode()
    if(self.page.ctrlDown):
      statusText = statusText + ' [Ctrl]'
    self.SetStatusText(statusText)
    self.Layout()

  def OnCopy(self, event):
    self.page.OnCopy(event)
    event.Skip()
		
  def OnOptions(self, event): pass

  def OnQuit(self, event):
    self.Close()

  def OnClose(self, event):
    try:
      self.bibles.saveHistory()
    except:
      pass
    self.Destroy()

  def OnAbout(self, event):
    wx.MessageBox("BQT reader light (very light)\nWritten by Noah for the sake of learning Python.",
        "BQT reader light", wx.OK | wx.ICON_INFORMATION, self)

  def OnLinkClicked(self, link):
    tmpRe = re.search('^([^:]+):(.*)$', link.GetHref())
    if(tmpRe):
      if(tmpRe.groups()[0]=='module'):
        path = tmpRe.groups()[1]
        if(self.activeModule and self.activeModule.path == path):
          self.ShowChapter(self.currentChapter)
        else:
          oldModule = self.activeModule
          self.activeModule = self.bibles.getModule(path)
          self.activeModule.loadModule()
          if(oldModule and oldModule.Bible and self.activeModule.Bible):
            #wx.MessageBox('[0]', "Module", wx.ICON_ERROR | wx.OK)
            newBookInd = self.activeModule.getOrderNumber(oldModule.getAbsoluteIndex(self.currentBook))
            #wx.MessageBox('[1]', "Module", wx.ICON_ERROR | wx.OK)
            if(newBookInd>=0):
              #wx.MessageBox('[2] book:'+str(newBookInd), "Module", wx.ICON_ERROR | wx.OK)
              if(self.activeModule.loadBook(newBookInd)):
                self.currentBook = newBookInd
                self.ShowChapter(self.currentChapter)
                #wx.MessageBox('[3]', "Module", wx.ICON_ERROR | wx.OK)
            else:
              pass
              #wx.MessageBox('Could not find the book', "Module", wx.ICON_ERROR | wx.OK)
          else:
            self.ChooseBook(path)
      elif(tmpRe.groups()[0]=='book'):
        book = int(tmpRe.groups()[1])
        self.activeModule.loadBook(book)
        self.buttonz['book'].SetLabel(self.activeModule.FullName[book])
        self.ChooseChapter(book)
      elif(tmpRe.groups()[0]=='chapter'):
        chapter = int(tmpRe.groups()[1])
        self.ShowChapter(chapter)
        self.buttonz['chapter'].SetLabel(str(chapter))
      elif(tmpRe.groups()[0]=='strong'):
        number = tmpRe.groups()[1]
        self.ShowStrong(number)
      elif(tmpRe.groups()[0]=='go'):
        self.bibleGo(tmpRe.groups()[1])
      elif(tmpRe.groups()[0]=='searchpage'):
        page = int(tmpRe.groups()[1])
        self.ShowSearchPage(page)
      elif(tmpRe.groups()[0]=='compare'):
        path = tmpRe.groups()[1]
        if(self.activeModule.path == path):
          path = ''
        self.OnCompareChoise(path)
      else:
        self.page.OutputHTML('Unknown command:', link.GetHref(), 'error')
      self.arrangeControls()

  def OnModule(self, event):
    title = 'Choose a module:'
    return self.ShowModuleList(title, 'module', True, False)
    
  def ShowModuleList(self, title, mode, showOthers, showNothing):
    if(self.page.getMode()==mode):
      self.ShowChapter(self.currentChapter)
      return
    self.page.saveScrollPos()
    modList = self.bibles.getBibleList()
    content = ''
    if(showNothing):
      content = content + '<a href="' + mode + ':">Unselect</a>'
    if(len(modList)):
      content = content + '<h2>Bibles:</h2>' + self.ProcessList(modList, mode)
    modList = self.bibles.getCommentaryList()
    if(len(modList)):
      content = content + '<h2>Commentaries:</h2>' + self.ProcessList(modList, mode)
    if(showOthers):
      modList = self.bibles.getOtherList()
      if(len(modList)):
        content = content + '<h2>Other books:</h2>' + self.ProcessList(modList, mode)
    if(content == ''):
      title = 'Could not find modules'
    self.page.OutputHTML(title, content, mode)
    self.arrangeControls()

  def ProcessList(self, modList, mode):
    content = '<ul>'
    for mod in modList:
      label = mod.BibleName
      link = mode+ ':' + mod.path
      content = content + '<li> <a href="' + link + '">' + label + '</a>'
    content = content + '</ul>'
    return content

  def ChooseBook(self, path):
    if(not self.activeModule): return
    self.page.setPath(path)
    if(self.activeModule.BookQty>1):
      content = '<table><tr><td valign=top><ul>'
      cnt = int((len(self.activeModule.FullName)-1)/3)+1
      for i in range(len(self.activeModule.FullName)):
        content = content + '<li><a href="book:' + str(i) + '">' + \
                  self.activeModule.FullName[i] + '</a>'
        if(i+1==cnt or i+1==cnt+cnt):
          content = content + '</ul></td><td valign=top><ul>'
      content = content + '</ul></td></tr></table>'
      self.page.OutputHTML('', content, 'book')
      self.arrangeControls()
    else:
      self.activeModule.loadBook(0)
      self.currentBook = 0
      self.ChooseChapter(0)
    return

  def ChooseChapter(self, book):
    if(not self.activeModule): return
    self.currentBook = int(book)
    content = ''
    chRange = self.activeModule.getChapterRange(book)
    if(len(chRange)>1):
      for i in chRange:
        content = content + '<a href="chapter:' + str(i) + \
                  '"><font size="7">&nbsp;' + str(i) + \
                  '&nbsp;</font></a> '
      self.page.OutputHTML('', content, 'chapter')
      self.arrangeControls()
    else:
      self.ShowChapter(chRange[0])
    return

  def transformContent(self, text, strongPrfx, module):
    if(module.StrongNumbers):
      if(self.strongsOn):
        text = re.sub(' ([0-9]{1,5})', ' <a href="strong:' + strongPrfx +\
                      '\\1"><small>\\1</small></a>', text)
      else:
        text = re.sub(' [0-9]{1,5}', '', text)
    #text = text.replace('<','<br>[[').replace('>',']]<br>')
    text = re.sub('<p( [^>]*)?>', '', text)
    text = text.replace('</p>','<br>')
    return text  
    
  def ShowChapter(self, chapter):
    if(not self.activeModule): return
    self.currentChapter = int(chapter)
    content = self.activeModule.getChapter(chapter)
    prfx = ''
    if(self.activeModule.isOT(self.currentBook)): prfx = '0'
    content = self.transformContent(content, prfx, self.activeModule)
    absInd = self.activeModule.getAbsoluteIndex(self.currentBook)
    newBookInd = self.activeModule.getOrderNumber(absInd)
    title = ''
    if(self.compareModule):
      self.compareModule.loadModule()
      newBookInd = self.compareModule.getOrderNumber(absInd)
      if(newBookInd>=0 and self.compareModule.loadBook(newBookInd)):
        content2 = self.compareModule.getChapter(chapter)
        if(content2):
          content2 = self.transformContent(content2, prfx, self.compareModule)
          prc = int(len(content)*100./(len(content)+len(content2)))
          content = '<table><tr><td width='+str(prc)+'% valign=top>' + content + '</td>' +\
                    '<td width='+str(100-prc)+'% valign=top>' + content2 + '</td></tr></table>'  
    self.page.OutputHTML('', content, 'text')
    self.page.restoreScrollPos()

    chzero = 0
    if(self.activeModule.ChapterZero): chzero = 1
    command = os.path.basename(self.activeModule.path).lower()\
             + ' ' + str(self.currentBook + 1)\
             + ' ' + str(self.currentChapter + chzero)
    title = self.activeModule.BibleShortName\
             + ' ' + self.activeModule.ShortName[self.currentBook][0]\
             + ' ' + str(self.currentChapter)
    self.bibles.pushHistory(command, title)
    self.arrangeControls()
    self.page.SetFocus()

  def OnBook(self, event):
    if(not self.activeModule): return
    if(self.page.getMode()=='book'): 
      self.ShowChapter(self.currentChapter)
      return
    self.ChooseBook(self.activeModule.path)

  def OnChapter(self, event):
    if(not self.activeModule): return
    if(self.page.getMode()=='chapter'): 
      self.ShowChapter(self.currentChapter)
      return
    self.page.setMode('chapter')
    self.ChooseChapter(self.currentBook)
        
  def PrevChapter(self, event):
    if(not self.activeModule): return
    if(self.page.getMode()!='text'): return 
    ch = self.activeModule.getPrevChapter(self.currentBook, self.currentChapter)
    if(ch):
      self.activeModule.loadBook(ch[0])
      self.currentBook = ch[0]
      self.ShowChapter(ch[1])
      self.page.clearScrollPos()
      self.arrangeControls()
   
  def NextChapter(self, event):
    if(not self.activeModule): return
    if(self.page.getMode()!='text'): return 
    ch = self.activeModule.getNextChapter(self.currentBook, self.currentChapter)
    if(ch):
      self.activeModule.loadBook(ch[0])
      self.currentBook = ch[0]
      self.ShowChapter(ch[1])
      self.page.clearScrollPos()
      self.arrangeControls()

  def ToggleStrongs(self, event):
    if(not self.activeModule): return
    if(1 or self.page.getMode()!='strong'):
      #if(not self.page.getMode() in ('text','strong')): return
      if(self.strongsOn):
        self.strongsOn = False
      else:
        self.strongsOn = True
    self.ShowChapter(self.currentChapter)
    self.arrangeControls()

  def ShowStrong(self, number):
    isHeb = False
    if(number[0]=='0'):
      isHeb = True
      number = number[1:]
    if(number[0]=='0'):
      number = number[1:]
    number = int(number)
    res = self.bibles.getStrongText(number, isHeb)
    title = res[0]
    content = res[1]
    self.page.OutputHTML(title, content, 'strong')
    self.arrangeControls()
      
  def OnHistory(self, event):
    if(self.page.getMode()=='history'): 
      self.ShowChapter(self.currentChapter)
      return
    content = ''
    for item in self.bibles.history:
      content = content + '<a href="go:' + item['command'][3:] +'">' + item['title'] + '</a><br>'
    title = 'History:'
    self.page.OutputHTML(title, content, 'history')
    self.arrangeControls()

  def OnFind(self, event):
    if(not self.activeModule): return
    self.page.setMode('search')
    if(self.findPanel.IsShown()):
      self.ShowChapter(self.currentChapter)
    else:
      self.ShowSearchPage(1)
    self.arrangeControls()

  def OnSearchStart(self, event):
    if(not self.activeModule or self.searchField.GetValue()==''): return
    self.activeModule.search(self.searchField.GetValue(), [])
    self.ShowSearchPage(1)
    
  def ShowSearchPage(self, page):
    pageSize = 20
    searchCount = self.activeModule.searchCount()
    found = self.activeModule.getSearchPage(page, pageSize)
    title = str(searchCount) + ' results'
    content = ''
    for i in range(len(found)):
      content = content + '<hr><a href="go:- ' + \
                              str(found[i][0]) + ' ' + \
                              str(found[i][1]) + ' ' + \
                              str(found[i][2]) + '">' + \
                              found[i][3] + '</a> ' + \
                              self.transformContent(found[i][4], '', self.activeModule)
    pageCount = int(searchCount / pageSize) + 1
    content = content + '<hr>'
    for i in range(1, pageCount+1):
      if(i == page):
        content = content + ' <FONT size="+2">' + str(i) + '</FONT> '
      else:
        content = content + ' <a href="searchpage:' + str(i) + '"><FONT size="+2">' + str(i) + '</FONT></a> '
    self.page.OutputHTML(title, content, 'search')

  def bibleGo(self, command):
    where = command.split(' ')
    if(not self.activeModule or where[0]!='-'): 
      newModule = self.bibles.getModuleByShortPath(where[0])
      if(not newModule):
        wx.MessageBox("Could not open the module: \n" + command, "Error", wx.ICON_ERROR | wx.OK)
        return
      self.activeModule = newModule
      self.activeModule.loadModule()
      self.buttonz['module'].SetLabel(self.activeModule.BibleShortName)
    currentBook = int(where[1])-1
    self.activeModule.loadBook(currentBook)
    self.currentBook = currentBook
    self.buttonz['book'].SetLabel(self.activeModule.FullName[currentBook])
    
    #wx.MessageBox(where[2], "Chapter", wx.ICON_ERROR | wx.OK)
    currentChapter = int(where[2])
    if(self.activeModule.ChapterZero):
      currentChapter = currentChapter - 1
    self.currentChapter = currentChapter
    self.buttonz['chapter'].SetLabel(str(currentChapter))
    self.ShowChapter(currentChapter)
    self.arrangeControls()

  def OnCompare(self, event):
    title = 'Choose a module to compare:'
    return self.ShowModuleList(title, 'compare', False, True)

  def OnCompareChoise(self, path):
    if(path):
      self.compareModule = self.bibles.getModule(path)
    else:
      self.compareModule = None
    self.ShowChapter(self.currentChapter)

  def ToggleFullScreen(self, event):
    if self.fullScreen:
      self.fullScreen = False
    else:
      self.fullScreen = True
    self.ShowFullScreen(self.fullScreen, style=wx.FULLSCREEN_ALL)
    self.page.SetFocus()

if __name__ == '__main__':
  app = MyApp(False)
  app.MainLoop()
