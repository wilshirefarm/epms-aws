from datetime import datetime
from db.db import *

def isBroke(giverEmail, pointsToGive):
    #check that user has enough points to give
    availablePointsSql = "SELECT PointsToGive from Employee where Email = '" + giverEmail + "'"
    availablePoints = readData(availablePointsSql)
    if availablePoints[0][0] < pointsToGive:
        return True
    else:
        return False


def isRealRecipient(recipient):
    # check that recipient exists
    recipientEmailSql = "SELECT Email from Employee where Email = '" + recipient + "'"
    recipientEmail = readData(recipientEmailSql)
    if len(recipientEmail) ==0:
        return False
    else:
        return True

def initiateTransfer(giverEmail, recipient, PointsGiven, comments):
    #do the transfer
    #return true if transfer was successful else return false
    try:
        giverEmployeeId = readData("SELECT EmployeeId from Employee where Email = '" + giverEmail + "'")
        recipientEmployeeId = readData("SELECT EmployeeId from Employee where Email = '" + recipient + "'")
        values = "(" + str(giverEmployeeId[0][0]) + "," + str(recipientEmployeeId[0][0]) + "," + str(PointsGiven) + "," + comments + ", \'" + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "\')"
        print(giverEmployeeId, recipientEmployeeId, values)
        updateData("INSERT into Transaction (GivenByEmployeeId,GivenToEmployeeId,PointsGiven,Comments,TransactionDate) values" + values)
        updateData("UPDATE Employee SET PointsToGive = PointsToGive -" + str(PointsGiven)+ " WHERE EmployeeId = "+str(giverEmployeeId[0][0]))
        updateData("UPDATE Employee SET PointsReceived = PointsReceived +" + str(PointsGiven)+ " WHERE EmployeeId = "+str(recipientEmployeeId[0][0]))
        return True
        
    except Exception as e:
        print(e)
        return False
