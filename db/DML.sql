sqlToFindUser = 'SELECT email, password from Employee where email = ' + email

sqlToCreateUser = 'INSERT INTO Employee (Email, FirstName, LastName, Password, PointsToGive, PointsReceived) VALUES ' + values

sqlToFindUser = 'SELECT EmployeeID, Email, FirstName, PointsToGive, PointsReceived FROM Employee WHERE Email = \'' + session['email'] + '\''

sqlToGetPointsReceived = 'SELECT CONCAT(FirstName, " ", LastName), PointsGiven, TransactionDate, Comments FROM epms.Transaction JOIN epms.Employee ON GivenByEmployeeID = EmployeeID WHERE GivenToEmployeeID = ' + str(employeeId) + ' ORDER BY TransactionDate DESC'

sqlToGetPointsGiven = 'SELECT CONCAT(FirstName, " ", LastName), PointsGiven, TransactionDate, Comments FROM epms.Transaction JOIN epms.Employee ON GivenToEmployeeID = EmployeeID WHERE GivenByEmployeeID = ' + str(employeeId) + ' ORDER BY TransactionDate DESC'

sqlToGetRedemptions = 'SELECT * FROM Redemption WHERE EmployeeID = ' + str(employeeId) + ' ORDER BY RedemptionDate DESC'

sqlToGetRewards = 'SELECT * FROM Reward'

sqlToFindReward = 'SELECT * FROM Reward WHERE RewardID = ' + str(rewardId)

sqlToCreateRedemption = 'INSERT INTO Redemption (EmployeeID, RewardID, RedemptionDate) VALUES ' + values

sqlToUpdateEmployee = 'UPDATE Employee SET PointsReceived = ' + str(newPointsReceived) + ' WHERE EmployeeID = ' + str(employeeId)

sqlToFindAdmin = 'SELECT email, password from Admin where email = ' + email

updateData('CALL ResetPoints')

sqlPointsGivenOutByMonth = 'SELECT EXTRACT(MONTH FROM TransactionDate), EXTRACT(YEAR FROM TransactionDate), SUM(PointsGiven) FROM epms.Transaction GROUP BY EXTRACT(MONTH FROM TransactionDate), EXTRACT(YEAR FROM TransactionDate);'
 
sqlPointsRedeemedByMonth = 'SELECT EXTRACT(MONTH FROM RedemptionDate), EXTRACT(YEAR FROM RedemptionDate), SUM(RewardCost) FROM epms.Redemption JOIN epms.Reward ON Redemption.RewardID = Reward.RewardID GROUP BY EXTRACT(MONTH FROM RedemptionDate), EXTRACT(YEAR FROM RedemptionDate);'

sqlPointsGivenOutByMonthByUser = 'SELECT EXTRACT(MONTH FROM TransactionDate), EXTRACT(YEAR FROM TransactionDate), CONCAT(FirstName, " ", LastName), SUM(PointsGiven) FROM epms.Transaction JOIN epms.Employee ON GivenByEmployeeID = EmployeeID GROUP BY GivenByEmployeeID, EXTRACT(MONTH FROM TransactionDate), EXTRACT(YEAR FROM TransactionDate) ORDER BY SUM(PointsGiven) DESC;'

sqlPointsReceivedByMonthByUser = 'SELECT EXTRACT(MONTH FROM TransactionDate), EXTRACT(YEAR FROM TransactionDate), CONCAT(FirstName, " ", LastName), SUM(PointsGiven) FROM epms.Transaction JOIN epms.Employee ON GivenToEmployeeID = EmployeeID GROUP BY GivenToEmployeeID, EXTRACT(MONTH FROM TransactionDate), EXTRACT(YEAR FROM TransactionDate) ORDER BY SUM(PointsGiven) DESC;'sqlPointsRedeemedByMonthByUser = 'SELECT EXTRACT(MONTH FROM RedemptionDate), EXTRACT(YEAR FROM RedemptionDate), CONCAT(FirstName, " ", LastName), SUM(RewardCost) FROM epms.Redemption JOIN epms.Reward ON Redemption.RewardID = Reward.RewardID JOIN epms.Employee ON Redemption.EmployeeID = Employee.EmployeeID WHERE RedemptionDate >= now()-interval 2 month GROUP BY Redemption.EmployeeID, EXTRACT(MONTH FROM RedemptionDate), EXTRACT(YEAR FROM RedemptionDate) ORDER BY SUM(RewardCost) DESC;'
 
sqlEmployeesNotUsingAllPoints = 'SELECT CONCAT(FirstName, " ", LastName), PointsToGive FROM epms.Employee WHERE PointsToGive != 0;'

availablePointsSql = "SELECT PointsToGive from Employee where email = '" + giverEmail + "'"

recipientEmailSql = "SELECT Email from Employee where email = '" + recipient + "'"

giverEmployeeId = readData("SELECT EmployeeId from Employee where email = '" + giverEmail + "'")

recipientEmployeeId = readData("SELECT EmployeeId from Employee where email = '" + recipient + "'")
        
updateData("INSERT into Transaction (GivenByEmployeeId,GivenToEmployeeId,PointsGiven,Comments) values" + values)
        
updateData("UPDATE Employee SET PointsToGive = PointsToGive -" + str(PointsGiven)+ " WHERE EmployeeId = "+str(giverEmployeeId[0][0]))
        
updateData("UPDATE Employee SET PointsReceived = PointsReceived +" + str(PointsGiven)+ " WHERE EmployeeId = "+str(recipientEmployeeId[0][0]))

"UPDATE Employee SET PointsToGive = 1000;"