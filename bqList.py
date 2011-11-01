#!/bin/env python
# -*- coding: UTF-8 -*-

import wx
import os
import glob
import re
import fileinput
import codecs
import getpass

standardBooks = ('Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', \
'Joshua', 'Judges', 'Ruth', '1Samuel', '2Samuel', '1Kings', '2Kings', \
'1Chron', '2Chron', 'Ezra', 'Nehemiah', 'Esther', 'Job', 'Psalms', 'Proverbs', \
'Ecclesia', 'Songs', 'Isaiah', 'Jeremiah', 'Lamentations', 'Ezekiel', \
'Daniel', 'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah', \
'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah', 'Malachi',\
'Matthew', 'Mark', 'Luke', 'John', 'Acts', \
'Romans', '1Corinthians', '2Corinthians', 'Galatians', 'Ephesians', \
'Philippians', 'Colossians', '1Thessalonians', '2Thessalonians', \
'1Timothy', '2Timothy', 'Titus', 'Philemon', 'Hebrews', \
'James', '1Peter', '2Peter', '1John', '2John', '3John', 'Jude', 'Revelation', \
'1Esdras', '2Esdras', '1Maccabees', '2Maccabees', 'Tobit', 'Judith', 'Wisdom', \
'Sirach', 'Susanna', 'Baruch', 'Epistle', 'Azariah', 'Manasseh', 'Bel')


class MyBibleList:

  bibleList = []
  commentaryList = []
  otherList = []

  path = ''

  strongGreek = None
  strongHebrew = None
  
  history = []
  searchResults = []
  
  def loadList(self, path):
    self.path = path
    filelist = glob.glob(path + '/*/[bB][iI][bB][lL][eE][qQ][tT].[iI][nN][iI]')
    #filelist = filelist + glob.glob(path + '/*/BIBLEQT.INI')
    filelist = filelist + glob.glob(path + '/Commentaries/*/[bB][iI][bB][lL][eE][qQ][tT].[iI][nN][iI]')
    #filelist = filelist + glob.glob(path + '/Commentaries/*/bibleqt.ini')
    s = ''
    for item in filelist:
      if(os.path.getsize(item)<5):
        pass
      else:
        bib = MyBible(item)
        #if(bib.DesiredFontCharset!='204'):
        #  s = s + bib.path + ':' + bib.DesiredFontCharset + '\n'
        if(re.search('/Commentaries/[^/]+/[^/]+$', item)):
          self.commentaryList.append(bib)
        elif(bib.Bible):
          self.bibleList.append(bib)
        else:
          self.otherList.append(bib)
    #wx.MessageBox(s, "Charsets", wx.ICON_ERROR | wx.OK)
    self.bibleList.sort(key=lambda obj: obj.BibleName)
    self.commentaryList.sort(key=lambda obj: obj.BibleName)
    self.otherList.sort(key=lambda obj: obj.BibleName)
    self.loadStrongs()
    self.loadHistory()
    return 0

  def loadStrongs(self):
    self.strongGreek = None
    self.strongHebrew = None
    grk = self.loadStrongFrom(self.path, 'greek')
    heb = self.loadStrongFrom(self.path, 'hebrew')
    if(grk): self.strongGreek = grk
    if(heb): self.strongHebrew = heb

  def loadStrongFrom(self, path, name):
    str = MyStrongLexicon(path, name)
    if(str.loaded): return str
    return None

  def loadHistory(self):
    try:
      f = open(self.getSettingsPath() + '/bibleqt_history.ini', 'r')
    except:
      return
    history = f.read().split('\r\n')
    f.close()
    for item in history:
      #go rststrong 5 12 15 0 $$$RSTs \xc2\xf2\xee\xf0\xee\xe7\xe0\xea\xee\xed\xe8\xe5 12:15\r
      if(item):
        parts = item.split('$$$')
        newHistoryItem = {'command':parts[0], 'title':unicode(parts[1], 'utf8')}
        self.history.append(newHistoryItem)
    #wx.MessageBox(str(history), "Good", wx.ICON_ERROR | wx.OK)

  def getStrongText(self, number, isHeb=False):
    if(isHeb):
      lexicon = self.strongHebrew
    else:
      lexicon = self.strongGreek
    return lexicon.getByNumber(number)

  def getBibleList(self):
    return self.bibleList

  def getCommentaryList(self):
    return self.commentaryList

  def getOtherList(self):
    return self.otherList

  def getDictionaryList(self):
    pass

  def getModule(self, path):
    for item in self.bibleList:
      if(item.path.lower() == path.lower()):
        return item
    for item in self.commentaryList:
      if(item.path.lower() == path.lower()):
        return item
    for item in self.otherList:
      if(item.path.lower() == path.lower()):
        return item
    return None

  def getModuleByShortPath(self, path):
    res = self.getModule(self.path + '/' + path)
    if(res): return res
    res = self.getModule(self.path + '/Commentaries/' + path)
    if(res): return res
    return None

  def pushHistory(self, command, title):
    newHistoryItem = {'command':'go ' + command, 'title': title}
    item = newHistoryItem
    for i in range(0, len(self.history)):
      item2 = self.history[i]
      self.history[i] = item
      item = item2
      if(item['title'] == newHistoryItem['title']):
        return
    if(len(self.history)<99):
      self.history.append(item);
        

  def historyToText(self):
    res = ''
    for i in range(0, len(self.history)):
      res = res + self.history[i]['command'] + '$$$' + self.history[i]['title'] + '\r\n'
    return res

  def saveHistory(self):
    try:
      f = open(self.getSettingsPath() + '/bibleqt_history.ini', 'w')
      history = f.write(self.historyToText().encode('utf8'))
      f.close()
    except:
      pass    

  def getSettingsPath(self):
    user = getpass.getuser()
    return self.path + '/users/' + user
    
class MyStrongLexicon:
  path = ''
  name = ''
  title = ''
  keys = {}
  maxNum = -1
  loaded = False

  def __init__(self, path, name):
    self.path = path
    self.name = name
    self.keys = {}
    self.loaded = False
    try:
     f = open(path + '/Strongs/' + name + '.idx', 'rb')
    except:
      return None
    if(not f): return None
    line = f.readline()
    self.title = unicode(line, 'cp1251')
    line = f.readline()
    while(line):
      key = int(line)
      self.maxNum = key
      line = f.readline()
      self.keys[key] = int(line)
      line = f.readline()
    f.close()
    self.loaded = True

  def getByNumber(self, number):
    if(not self.loaded): return ('','')
    fullName = self.path + '/Strongs/' + self.name + '.htm'
    if(number in self.keys):
      start = self.keys[number]
      if(number<=self.maxNum):
        for i in range(number+1,self.maxNum):
          if(i in self.keys):
            end = self.keys[i]
            break
      else:
        end = os.path.size(fullName)+1
      f = open(fullName, 'rb')
      f.seek(start)
      text = unicode(f.read(end-start), 'cp1251')
      f.close()
      text = re.sub(' ([0-9]{1,5})', ' <a href="strong:\\1">\\1</a>', text)
      return (self.title, text)
    else:
      return (self.title, '')
  
class MyBible:
  path = ''  
  fullPath = ''
  fullyLoaded = False

  BibleName = ''
  BibleShortName = ''
  Bible = False
  OldTestament = False
  NewTestament = False
  Apocrypha = False
  Greek = False
  StrongNumbers = False
  HTMLFilter = ''
  Alphabet = ''
  DesiredFontName = ''
  DesiredFontCharset = ''
  ChapterSign = ''
  VerseSign = ''
  ChapterZero = False
  Copyright = ''
  BookQty = 0

  PathName = []
  FullName = []
  ShortName = []
  ChapterQty = []

  ini = []
  content = ''
  currentBook = None
  currentChapter = None
  files = {}

  chapters = []
  verses = []
  
  searchResults = []

  def __init__(self, path):
    self.path = os.path.dirname(path)
    self.fullPath = path
    self.fullyLoaded = False
    self.BibleName = os.path.basename(self.path)
    f = open(path, 'rb')
    self.ini = f.read()
    f.close()
    set_Bible = False
    for line in self.ini.split('\n'):
      uline = unicode(line, 'cp1251')
      tmpRe = re.search('^([^=/# ]+)\s*=\s*(.*\S)\s*$', uline)
      if(tmpRe):
        left = tmpRe.groups()[0]
        right = tmpRe.groups()[1]
        #wx.MessageBox(right, left, wx.OK | wx.ICON_INFORMATION, None)
        sright = ''
        if(right):
          sright = right#.decode('string-escape')
        if(left=='BibleName'): self.BibleName = sright
        if(left=='DesiredFontCharset'): self.DesiredFontCharset = sright
        if(left=='Bible'): 
          self.Bible = right == 'Y'
          set_Bible = True
      if(self.BibleName and set_Bible and self.DesiredFontCharset):
        return

  def getEncoding(self):
    if(self.DesiredFontCharset=='162'): return 'windows-1254'
    if(self.DesiredFontCharset=='129'): return 'EUC-KR'
    if(self.DesiredFontCharset=='201'): return 'windows-1252'
    return 'cp1251'

  def loadModule(self):
    if(self.fullyLoaded):
      return True
    f = open(self.fullPath, 'rb')
    encoding = self.getEncoding()
    #self.BibleName = os.path.basename(self.path)
    for line in self.ini.split('\n'):
      uline = unicode(line, encoding)
      tmpRe = re.search('^([^=/# ]+)\s*=\s*(.*\S)\s*$', uline)
      if(tmpRe):
        left = tmpRe.groups()[0]
        right = tmpRe.groups()[1]
        #wx.MessageBox(right, left, wx.OK | wx.ICON_INFORMATION, None)
        sright = ''
        if(right):
          sright = right
        if(left=='BibleShortName'): self.BibleShortName = sright
        #if(left=='Bible'): self.Bible = right == 'Y'
        if(left=='OldTestament'): self.OldTestament = right == 'Y'
        if(left=='NewTestament'): self.NewTestament = right == 'Y'
        if(left=='Apocrypha'): self.Apocrypha = right == 'Y'
        if(left=='Greek'): self.Greek = right == 'Y'
        if(left=='StrongNumbers'): self.StrongNumbers = right == 'Y'
        if(left=='HTMLFilter'): self.HTMLFilter = sright
        if(left=='Alphabet'): self.Alphabet = sright
        if(left=='DesiredFontName'): self.DesiredFontName = sright
        if(left=='ChapterSign'): self.ChapterSign = sright
        if(left=='VerseSign'): self.VerseSign = sright
        if(left=='ChapterZero'): self.ChapterZero = right == 'Y'
        if(left=='Copyright'): self.Copyright = sright
        if(left=='BookQty'): self.BookQty = int(right)
        if(left=='PathName'): self.PathName = self.PathName + [sright]
        if(left=='FullName'): self.FullName = self.FullName + [sright]
        if(left=='ShortName'): self.ShortName = self.ShortName + [sright.split(' ')]
        if(left=='ChapterQty'): self.ChapterQty = self.ChapterQty + [int(right)]
    self.files = {}
    filelist = glob.glob(self.path+'/*')
    for item in filelist:
      it = os.path.basename(item)
      self.files[it.lower()] = it
    self.fullyLoaded = True
    return True

  def loadBook(self, bookNumber):
    if(self.currentBook == bookNumber): return True
    key = str(self.PathName[bookNumber]).lower()
    if not key in self.files: return False
    encoding = self.getEncoding()
    fname = self.files[key]
    try:
      f = open(self.path + '/' + fname, 'rb')
    except:
      wx.MessageBox('Can\'t open the book', 'Error', wx.OK | wx.ICON_INFORMATION, None)
      return False
    #self.content= unicode(f.read(), encoding).replace('<', '\n<')\
    #                                         .replace('>', '>\n')\
    #                                         .split('\n')
    self.content= re.sub('(<[^>]*)\r\n', '\\1', unicode(f.read(), encoding)).split('\n')
    f.close()
    self.currentBook = bookNumber

    chapters = []
    verses = []
    chNum = -1
    for i in range(len(self.content)):
      if(re.search(self.ChapterSign, self.content[i])):
        if(chNum>=0):
          verses[chNum].append(i)
        chNum = chNum + 1
        chapters.append(i)
        verses.append([i])
      if(chNum>=0 and self.VerseSign and re.search(self.VerseSign, self.content[i])):
        verses[chNum].append(i)
    chapters.append(len(self.content))
    self.chapters = chapters
    self.verses = verses
    #wx.MessageBox(str(self.chapters), self.footer, wx.OK | wx.ICON_INFORMATION, None)
    return True
      
  def getChapterLines(self, chapterNumber):
    chNum = -1
    chText = ''
    chzero = 1
    if(self.ChapterZero): chzero = 0
    if(chapterNumber>=chzero and chapterNumber<=len(self.chapters)-chzero):
      start = self.verses[chapterNumber-chzero][1]
      end = self.chapters[chapterNumber-chzero+1]
      return self.content[start:end]
    return ''

  def getChapter(self, chapterNumber, strongsOn=False):
    chNum = -1
    chText = ''
    chzero = 1
    if(self.ChapterZero): chzero = 0
    lines = self.getChapterLines(chapterNumber)
    s = ''
    regexp = re.compile('<[/]?(table|tr|td|p|sup|dl|dt|dd|big|small)( [^>]*)?>', re.IGNORECASE)
    regexp2 = re.compile('<img ([^>]*)src=\s*"([^"]*)"([^>]*)>', re.IGNORECASE)
    regexp3 = re.compile('<img ([^>]*)src=([^ "]+)([^>]*)>', re.IGNORECASE)
    for i in range(0, len(lines)):
      s = regexp.sub('', lines[i])
      s = regexp2.sub('<img src="' + self.path + '/\\2" \\1 \\3>(\\2)', s)
      s = regexp3.sub('<img src="' + self.path + '/\\2" \\1 \\3>(\\2)', s)
      chText = chText + '<p>' + s + '</p>\r\n'
    if(self.DesiredFontName):
      chText = '<font face="' + self.DesiredFontName + '">' + chText + '</font>'
    return chText

  def getVerse(self, chapterNumber, verseNumber):
    chapter = self.getChapter(chapterNumber).split('\r\n')
    vnum = -1
    for i in range(len(chapter)):
      if(vnum==-1):
        if(re.search(self.ChapterSign, chapter[i])):
          vnum = 0
        continue
      if(re.search('\D' + str(verseNumber) + '\D', chapter[i])):
        regexp = re.compile('<[/]?(table|tr|td|p|sup)( [^>]*)?>', re.IGNORECASE)
        return regexp.sub('', chapter[i])
    return ''

  def getSearchInChapter(self, chapterNumber, words):
    chapter = self.getChapterLines(chapterNumber)
    result = ''
    for i in range(len(chapter)):
      flag = True
      for j in range(len(words)):
        if(words[j]==''): continue
        if(chapter[i].find(words[j])<0):
          flag = False
      if(flag):
        item = chapter[i]
        result = result + item
    return result

  def getBookCount(self):
    pass
  def getBookList(self):
    pass
  def getChapterRange(self, book):
    if(self.ChapterZero): return range(0, self.ChapterQty[book])
    return range(1, self.ChapterQty[book]+1)

  def getVerseCount(self, chapterNumber):
    pass

  def getPrevChapter(self, book, chapter):
    chzero = 1
    if(self.ChapterZero): chzero = 0
    if(chapter==chzero):
      if(book==0): return None
      return(book - 1,self.ChapterQty[book-1]-1+chzero)
    return (book, chapter - 1)

  def getNextChapter(self, book, chapter):
    chzero = 1
    if(self.ChapterZero): chzero = 0
    if(chapter==self.ChapterQty[book]-1+chzero):
      if(book==self.BookQty-1): return None
      return (book + 1, chzero)
    return (book, chapter + 1)

  def getOrderNumber(self, absInd):
    # by short book name:
    for i in range(0, len(self.ShortName)):
      if(standardBooks[absInd] in self.ShortName[i]):
        return i
    # if does not work:
    if(not self.Bible): return -1
    ind = absInd
    if(self.OldTestament):
      if(absInd>=0 and absInd<39):
        return ind
    else:
      ind = ind - 39
    if(self.NewTestament):
      if(absInd>=39 and absInd<66):
        return ind
    else:
      ind = ind - 27
    if(self.Apocrypha):
      if(absInd>=66 and ind<self.BookQty):
        return ind
    return -1
  
  def getAbsoluteIndex(self, orderNum):
    if(not self.Bible): return -1
    # by short book name:
    for i in range(0, len(standardBooks)):
      if(standardBooks[i] in self.ShortName[orderNum]):
        return i
    # if does not work:
    startIndex = 0
    if(self.OldTestament):
      if(orderNum<39):
        return orderNum
      orderNum = orderNum - 39
    startIndex = startIndex + 39
    if(self.NewTestament):
      if(orderNum < 27):
        return orderNum + startIndex
      orderNum = orderNum - 27
    startIndex = startIndex + 27
    if(self.Apocrypha):
      return orderNum + startIndex
    return -1

  def isOT(self, bookNum):
    absNum = self.getAbsoluteIndex(bookNum)
    if(absNum>=0 and absNum<=39): return True
    return False
  
  def search(self, searchString, options):
    words = searchString.lower().split(' ')
    searchResults = []
    saveCurrentBook = self.currentBook
    saveContent = self.content
    saveChapters = self.chapters
    saveVerses = self.verses
    chzero = 1
    if(self.ChapterZero): chzero = 0
    
    for i in range(self.BookQty):
    #for i in range(saveCurrentBook, saveCurrentBook+1):
      if(i==saveCurrentBook):
        self.currentBook = saveCurrentBook
        self.content = saveContent
        self.chapters = saveChapters
        self.verses = saveVerses
      else:
        self.loadBook(i)
      for ch in range(0, len(self.chapters)-1):
      #for ch in range(0, 1):
        for v in range(1, len(self.verses[ch])):
          s = ''
          for ln in range(self.verses[ch][v-1], self.verses[ch][v]):
            s = s + self.content[ln]
          regexp = re.compile('<[/]?(table|tr|td|p|sup)( [^>]*)?>', re.IGNORECASE)
          s = regexp.sub('', s)
          sLower = s.lower()
          flag = True
          for w in range(len(words)):
            if(words[w]==''): continue
            if(sLower.find(words[w])<0):
              flag = False
          if(flag):
            item = (i+1, ch+1, v-1, \
                    self.ShortName[i][0]+' '+str(ch+chzero)+':'+str(v-1),\
                    s)
            searchResults.append(item)
    self.currentBook = saveCurrentBook
    self.content = saveContent
    self.chapters = saveChapters
    self.verses = saveVerses
    self.searchResults = searchResults

  def searchCount(self):
    return len(self.searchResults)

  def getSearchPage(self, page, pageSize):
    if((page-1)*pageSize > self.searchCount()):
      return []
    if(page*pageSize < self.searchCount()):
      return self.searchResults[(page-1)*pageSize:page*pageSize]
    return self.searchResults[(page-1)*pageSize:]

class MyVerseCollection:
  list = ()
  
  def clear(self):
    self.list = ()
  
  def add(self, module, book, chapter, verses):
    item = {'module':module, 'book':book, 'chapter':chapter, 'verses':verses}
    self.list.append(item)

  def getPage(self, page, pageLen):
    if(len(self.list)<(page-1)*pageLen): return ()
    return self.list[(page-1)*pageLen : page*pageLen]


  
if __name__ == '__main__':
  Bibles = MyBibleList()
  Bibles.loadList('/home/noah/Files/Soft-Win/BibleQuote')
  for item in Bibles.getBibleList():
    print '-' + item.BibleName
