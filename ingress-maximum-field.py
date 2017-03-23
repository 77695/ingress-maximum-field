# -*- coding: utf-8 -*-
import sympy.geometry as geo
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
      print("Name = [%s], Latlng = [%0.4f, %0.4f]"%(p['label'],float(p['latlng'][0]),float(p['latlng'][1])))
  def __init__(self,fnJson,centerPOName=''):
    print ('Reading data from "%s"'%fnJson)
    with open(fnJson,'r') as fsJson:
      '''Read data from file'''
      rawJsonStr=fsJson.read()
      rawJson=eval(rawJsonStr,{},{})
      rawPOs=rawJson['portals']['idOthers']['bkmrk']
      kRawPOs=rawPOs.keys()
      self.POs=[]
      for k in kRawPOs:
        PO={}
        PO['label']=rawPOs[k]['label']
        while self.__hasSamePO(PO['label']):PO['label']+='A'
        PO['latlng']=rawPOs[k]['latlng'].split(',')
        PO['latlng']=geo.Point2D(float(PO['latlng'][0]),float(PO['latlng'][1]))
        PO['nKey']=0
        if PO['label']!=centerPOName:
          self.POs.append(PO)
        else:
          self.POs.insert(0,PO)
      self.__printAllPO()


          
      
filedSolver=MaxFieldSolver('example.json','不明觉厉机器')
  
