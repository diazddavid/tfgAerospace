# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 09:50:48 2018

@author: ILTALLER
"""

stringToParse = "probando codigo para parsear strings y ver si funciona"

auxStr = stringToParse
spacePositions = []

while True:
    pos = auxStr.find(" ")
    if pos != -1:
        lastPos = len(spacePositions)
        if lastPos != 0:
            posToInsert = pos + spacePositions[lastPos - 1] + 1
        else:
            posToInsert = pos
        spacePositions.append(posToInsert)
        pos = pos + 1
        auxStr = auxStr[pos:]
    else:
        break
    
newStr = ""
print(len(spacePositions))


#toInsert = []
#for counter in range(1,numN + 1):
#    maxValue = counter*10
#    toInsert.append(min(spacePositions, key= lambda x:abs(x-maxValue)))
#    
#    
#for index in range(0,len(stringToParse)):
#    newStr = newStr + stringToParse[index]
#    if index in toInsert:
#        newStr = newStr + "\n"
        
print(newStr)

clolumns = [1,2,3,4]
prueba = [0.3 for x in clolumns]
print(prueba)