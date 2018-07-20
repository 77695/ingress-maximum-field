# -*- coding: utf-8 -*-
import json
import math
import turtle
import Tkinter as tk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import os
class MaxFieldSolver:
  def __writeLn(self,s):
    print s
  def __hasSamePO(self,s):
    for poCur in self.POs:
      if poCur['label']==s:
        return True
    return False
  def __printAllPO(self):
    for p in self.POs:
      print("Name = [%s], Latlng = [%f, %f]"%(p['label'],(p['latlng'][0]),(p['latlng'][1])))
  def __sub2p(self,p1,p2):
    x1,y1=p1
    x2,y2=p2
    return [x1-x2,y1-y2]
  def __x2l(self,p1,p2):
    x1,y1=p1
    x2,y2=p2
    return x1*y2-x2*y1
  def __crossSegAndLn(self,l1,l2):
    p1=l1[0]
    p2=l1[1]
    q1=l2[0]
    q2=l2[1]
    p1_q1=self.__sub2p(p1,q1)
    q2_q1=self.__sub2p(q2,q1)
    p2_q1=self.__sub2p(p2,q1)
    p1_q1xq2_q1=self.__x2l(p1_q1,q2_q1)
    q2_q1xp2_q1=self.__x2l(q2_q1,p2_q1)
    if p1_q1xq2_q1*q2_q1xp2_q1>0:return True
    else:return False
  def __cross2Ln(self,l1,l2):
    s1=self.__crossSegAndLn(l1,l2)
    s2=self.__crossSegAndLn(l2,l1)
    if s1 and s2: return True
    else:return False
  def __linkAble(self,po1,po2):
    p1,p2=self.POs[po1]['latlng'],self.POs[po2]['latlng']
    lP1P2=[p1,p2]
    for l in self.links:
      if self.__cross2Ln(lP1P2,l):
        return False
    return lP1P2
  def __link(self,po1,po2):
    p1,p2=self.POs[po1]['latlng'],self.POs[po2]['latlng']
    lP1P2=self.__linkAble(po1,po2)
    if not lP1P2:return False
    self.links.append(lP1P2)
    self.POs[po2]['nKey']+=1
    self.resAll.append(self.POs[po1]['label']+' =====> '+self.POs[po2]['label'])
    return True
  def __distLn(self,l):
    p1,p2=l[0],l[1]
    y,x=self.__sub2p(p1,p2)
    y*=2
    s=math.sqrt(x*x+y*y)
    return s
  def __angLn(self,l):
    p1,p2=l[0],l[1]
    y,x=self.__sub2p(p1,p2)
    s=self.__distLn(l)
    ang = math.acos(x/s)
    if y>0:ang=math.pi-ang+math.pi
    return ang
  def __set_angle(self):
    self.POs[0]['angle']=0
    for i in xrange(1,len(self.POs)):
      lnPo=[self.POs[i]['latlng'],self.POs[0]['latlng']]
      self.POs[i]['angle']=self.__angLn(lnPo)
  def __set_dist(self, startIdx=0):
    for i in xrange(startIdx+1):
      self.POs[i]['dist']=-1
    for i in xrange(startIdx+1,len(self.POs)):
      lnPo=[self.POs[i]['latlng'],self.POs[startIdx]['latlng']]
      self.POs[i]['dist']=self.__distLn(lnPo)
  def __sortPOs(self):
    self.POs[0]['angle']=-9999999
    self.__set_angle()
    self.POs=sorted(self.POs,key=lambda x:x['angle'])
  def __sortPOs_greedy_min_dist(self):
    for i in xrange(len(self.POs)-1):
      self.__set_dist(i)
      min_dist_idx = -1
      for j in xrange(len(self.POs)):
        if self.POs[j]['dist'] > 0 and (min_dist_idx<0 or self.POs[j]['dist']<self.POs[min_dist_idx]['dist']):
          min_dist_idx = j
      self.POs[i+1], self.POs[min_dist_idx] = self.POs[min_dist_idx], self.POs[i+1]
  def __sortPOs_dist(self):
    self.__set_dist()
    self.POs=sorted(self.POs,key=lambda x:x['dist'])
  def __readFromJson(self,fnJson,centerPOName):
    print ('Reading data from "%s"'%fnJson)
    with open(fnJson,'r') as fsJson:
      rawJson=json.load(fsJson,encoding='utf-8')
      rawPOs=rawJson['portals']['idOthers']['bkmrk']
      kRawPOs=rawPOs.keys()
      self.POs=[]
      for k in kRawPOs:
        PO={}
        PO['label']=rawPOs[k]['label']
        while self.__hasSamePO(PO['label']):PO['label']+='A'
        PO['latlng']=rawPOs[k]['latlng'].split(',')
        PO['latlng']=[float(PO['latlng'][0]),float(PO['latlng'][1])]
        PO['nKey']=0
        if PO['label']!=centerPOName.decode('utf8'):
          self.POs.append(PO)
        else:
          self.POs.insert(0,PO)
      self.__set_angle()
      for i in range(len(self.POs)):
        self.POs[i]['label'] += '[{}]'.format(round(self.POs[i]['angle']/math.pi*180,2))
  def __nameOfRes(self,res):
    return res.split(' ===')[0]
  def __printKey(self,res):
    namePO=self.__nameOfRes(res)
    for po in self.POs:
      if po['label']==namePO:
        print '#Keys of',namePO,"=",po['nKey']
  def __printResWithKey(self):
    print 'Target of all:',self.POs[0]['label'],'#Keys','=',self.POs[0]['nKey']
    self.__printKey(self.resAll[0])
    print self.resAll[0]
    for i in xrange(1,len(self.resAll)):
      if self.__nameOfRes(self.resAll[i])!=self.__nameOfRes(self.resAll[i-1]):
        self.__printKey(self.resAll[i])
      print self.resAll[i]
  def proc2(self):
    self.links=[]
    self.resAll=[]
    self.__sortPOs()
    st,ed=1,len(self.POs)-1
    for i in xrange(st,ed+1):
      self.__link(i,0)
      for j in xrange(st,i):
        self.__link(i,j)
  def plot_all_POs_dot(self):
    for po in self.POs:
      self.ax.plot(po['latlng'][1], po['latlng'][0], 'o', color='black', markersize=3)
  def plot_all_path(self):
    for i in xrange(len(self.POs)-1):
      self.ax.plot([self.POs[i]['latlng'][1], self.POs[i+1]['latlng'][1]], [self.POs[i]['latlng'][0], self.POs[i+1]['latlng'][0]], color='blue')
  def __init__(self,fnJson,centerPOName=''):
    self.__readFromJson(fnJson,centerPOName)
    self.init_window()
##    self.__printAllPO()
    self.proc2()
    self.__printResWithKey()
  def init_window(self):
    root = tk.Tk()
    root.wm_title('Ingress Maximum Field')
    root.geometry("600x1024")
    self.tk_list_POs = tk.Listbox(root, width=40, height=20, selectmode='multiple')

    self.tk_list_POs.pack(side = tk.TOP)
    def __refesh_list():
      while self.tk_list_POs.size() != 0:
        self.tk_list_POs.delete(0, self.tk_list_POs.size())
      for PO in self.POs:
        self.tk_list_POs.insert(tk.END,PO['label'])
    def __sel_item(idx_item):
      self.tk_list_POs.select_set(idx_item) #This only sets focus on the first item.
      self.tk_list_POs.event_generate("<<ListboxSelect>>")
    def __refresh_canvas():
      self.ax.clear()
      self.plot_all_path()
      self.plot_all_POs_dot()
      self.canvas.show()
    def __list_key_bind(event):
      if len(self.tk_list_POs.curselection())<1:
        return
      cur_sels = self.tk_list_POs.curselection()
      if event.char == 'q':
        for cur_sel in cur_sels:
          if cur_sel > 0:
            self.POs[cur_sel], self.POs[cur_sel-1] = self.POs[cur_sel-1], self.POs[cur_sel]
            __refesh_list()
        for cur_sel in cur_sels:
          __sel_item(cur_sel-1)
        print 'up'
      elif event.char == 'w':
        for cur_sel in cur_sels[::-1]:
          if cur_sel < len(self.POs) - 1:
            self.POs[cur_sel], self.POs[cur_sel+1] = self.POs[cur_sel+1], self.POs[cur_sel]
            __refesh_list()
        for cur_sel in cur_sels:
          __sel_item(cur_sel+1)
        print 'down'
      elif event.char == 'd':
        self.POs.remove(self.POs[cur_sel])
        __refesh_list()
        print 'delete'
      __refresh_canvas()
    self.tk_list_POs.bind("<Key>", __list_key_bind)

    tk_tips = tk.Label(root, text='Select Order of Potols\n(using \'q\' and \'w\' on keyboard)')
    tk_tips.pack(side=tk.BOTTOM)
    self.__sortPOs_greedy_min_dist()


    fig = Figure()
    self.ax = fig.add_subplot(111)
    self.plot_all_path()
    self.plot_all_POs_dot()
    
    
    self.canvas = FigureCanvasTkAgg(fig, root)
    self.canvas.show()
    self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    



    __refesh_list()
    
    root.mainloop()


          
      
filedSolver=MaxFieldSolver('example.json','不明觉厉机器')

filedSolver.proc2()
  
