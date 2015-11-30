"""
from elasticsearch import Elasticsearch
import re
"""
import xlrd
locatio="C:/Users/DELL PC/Desktop/ttm/Project 2014-15.xlsx"
book = xlrd.open_workbook(locatio)
sheet = book.sheet_by_index(0)
jsonobj={}
for row in range (5,20):
    data=sheet.cell_value(row,10)
    jsonobj["Title"]=data
    data=sheet.cell_value(row,9)
    jsonobj["Domain"]=data
    data=sheet.cell_value(row,8)
    jsonobj["Enrollment_No.3"]=data
    data=sheet.cell_value(row,7)
    jsonobj["Enrollment_No.2"]=data
    data=sheet.cell_value(row,3)
    jsonobj["Enrollment_No.1"]=data
    data=sheet.cell_value(row,5)
    jsonobj["Fculty_Name"]=data
    print jsonobj
