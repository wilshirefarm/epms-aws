from flask import Flask, render_template, request, jsonify, redirect, session, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
import re
from db.db import *
from db.transfer_points import *
from datetime import datetime
import pytz

# Initialize Flask
app = Flask(__name__)
app.secret_key = b'\x11\xae\xba\x13\xca-\xa8W\x84l\xf3\xd3\xa3x\xed\x10'

emailRegex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
numberRegex = '^\d{1-4}$'

# Set up timezone for CST
cst_timezone = pytz.timezone('US/Central')

@app.route('/', methods=('GET', 'POST'))
def login():
    if 'email' in session:
        return redirect(url_for('backToMenu'))
    elif 'admin' in session:
        return redirect(url_for('admin'))

    else:
        if request.method == 'POST':
            email = request.form['email']
            email = '\'' + str(email) + '\''
            password = request.form['password']
            error = ""

            sqlToFindUser = 'SELECT email, password from Employee where email = ' + email
            user = readData(sqlToFindUser)
            #print(user)
            if len(user) == 0:
                error = 'Incorrect Email'
            else:
                if check_password_hash(user[0][1], password) != True:
                    error = 'Incorrect Password'
                else:
                    print('Success!')
                    session.clear()
                    session['email'] = email.strip('\'')
                    return redirect(url_for('backToMenu'))

            flash(error)
        return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('redemptionHome'))

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        email = '\'' + str(email) + '\''
        firstName = request.form['firstName']
        firstName = '\'' + str(firstName) + '\''
        lastName = str(request.form['lastName'])
        lastName = '\'' + str(lastName) + '\''
        password = generate_password_hash(str(request.form['password']))
        password = '\'' + str(password) + '\''
        values = "(" + email + "," + firstName + "," + lastName + "," + password + "," + str(1000) + "," + str(0) + ")"
        error = ""

        sqlToFindUser = 'SELECT email, password from Employee where email = ' + email
        user = readData(sqlToFindUser)
        if len(user) != 0:
            error = 'You already have an account'
        else:
            sqlToCreateUser = 'INSERT INTO Employee (Email, FirstName, LastName, Password, PointsToGive, PointsReceived) VALUES ' + values
            updateData(sqlToCreateUser)
            session.clear()
            session['email'] = email.strip('\'')
            return redirect(url_for('backToMenu'))

        flash(error)
    return render_template('register.html')

@app.route('/menu', methods=['GET'])
def backToMenu():
    if 'email' in session:
        sqlToFindUser = 'SELECT EmployeeID, Email, FirstName, PointsToGive, PointsReceived FROM Employee WHERE Email = \'' + session['email'] + '\''
        user = readData(sqlToFindUser)
        firstName = user[0][2]
        return render_template('menu.html', firstName=firstName)
    else:
        return redirect(url_for('login'))

@app.route('/giftMenu', methods=['GET','POST'])
def redirectToGiftMenu():
    if 'email' in session:
        sqlToFindUser = 'SELECT EmployeeID, Email, FirstName, PointsToGive, PointsReceived FROM Employee WHERE Email = \'' + session['email'] + '\''
        user = readData(sqlToFindUser)
        employeeId = user[0][0]
        firstName = user[0][2]
        pointsToGive = user[0][3]
        pointsReceived = user[0][4]
        return render_template('gift.html', pointsToGive=pointsToGive)
    else:
        return redirect(url_for('login'))

@app.route('/gift', methods=['POST'])
def giftPoints():
    recipient = request.form['recipient']
    pointsToGive = request.form['pointsToGive']
    comments = request.form['Comments']
    giverEmail = session['email']
    comments = '\'' + str(comments) + '\''

    #validate email address
    if(not re.search(emailRegex, recipient)):
        flash('Invalid email address')
        return redirect(url_for('redirectToGiftMenu'))

    #see if email address exists
    if(not isRealRecipient(recipient)):
        flash('Recipient does not exist')
        return redirect(url_for('redirectToGiftMenu'))

    #check that giver is not same as recipient
    if(recipient == giverEmail):
        flash("Oops, did you mean to transfer points to someone else?")
        return redirect(url_for('redirectToGiftMenu'))

    #validate points and see if they're numbers and if giver has enough points
    try:
        pointsInt = int(pointsToGive)
        if (isBroke(giverEmail, pointsInt)):
            flash("Sorry, you don't have that many points to give out")
            return redirect(url_for('redirectToGiftMenu'))
        elif (pointsInt <= 0):
            flash("Please enter a number greater than 0")
            return redirect(url_for('redirectToGiftMenu'))

        else:
            #initiate transfer
            if(initiateTransfer(giverEmail, recipient, pointsInt, comments)):
                flash('Points successfully transferred!')
            else:
                flash('Internal error trying to transfer points. Please try again later')
    except:
        flash('Please enter a number for points')
        return redirect(url_for('redirectToGiftMenu'))

    return redirect(url_for('redirectToGiftMenu'))

@app.route('/history', methods=('GET', 'POST'))
def history():
    if 'email' in session:
        sqlToFindUser = 'SELECT EmployeeID, Email, FirstName, PointsToGive, PointsReceived FROM Employee WHERE Email = \'' + session['email'] + '\''
        user = readData(sqlToFindUser)
        employeeId = user[0][0]
        firstName = user[0][2]
        pointsToGive = user[0][3]
        pointsReceived = user[0][4]

        sqlToGetPointsReceived = 'SELECT CONCAT(FirstName, " ", LastName), Email, PointsGiven, TransactionDate, Comments FROM epms.Transaction JOIN epms.Employee ON GivenByEmployeeID = EmployeeID WHERE GivenToEmployeeID = ' + str(employeeId) + ' ORDER BY TransactionDate DESC'
        transactionsReceived = readData(sqlToGetPointsReceived)
        transactionsReceivedList = []
        for transaction in transactionsReceived:
            transactionsReceivedList.append((
                transaction[0], 
                transaction[1], 
                transaction[2], 
                transaction[3].strftime("%B %-d %Y, %-I:%M %p"), 
                transaction[4]))

        sqlToGetPointsGiven = 'SELECT CONCAT(FirstName, " ", LastName), Email, PointsGiven, TransactionDate, Comments FROM epms.Transaction JOIN epms.Employee ON GivenToEmployeeID = EmployeeID WHERE GivenByEmployeeID = ' + str(employeeId) + ' ORDER BY TransactionDate DESC'
        transactionsGiven = readData(sqlToGetPointsGiven)
        transactionsGivenList = []
        for transaction in transactionsGiven:
            transactionsGivenList.append((
                transaction[0], 
                transaction[1], 
                transaction[2], 
                transaction[3].strftime("%B %-d %Y, %-I:%M %p"), 
                transaction[4]))

        return render_template('history.html', firstName=firstName, pointsToGive=pointsToGive, pointsReceived=pointsReceived, transactionsReceived=transactionsReceivedList, transactionsGiven=transactionsGivenList)
    else:
        return redirect(url_for('login'))

@app.route('/redeemMenu', methods=('GET', 'POST'))
def redemptionHome():
    if 'email' in session:
        sqlToFindUser = 'SELECT EmployeeID, Email, FirstName, PointsToGive, PointsReceived FROM Employee WHERE Email = \'' + session['email'] + '\''
        user = readData(sqlToFindUser)
        employeeId = user[0][0]
        firstName = user[0][2]
        pointsToGive = user[0][3]
        pointsReceived = user[0][4]
        #print(user)

        sqlToGetRewards = 'SELECT * FROM Reward'
        rewardsFromDB = readData(sqlToGetRewards)
        rewardsDict = {}
        for reward in rewardsFromDB:
            rewardsDict[reward[0]] = (reward[1], reward[2])

        sqlToGetRedemptions = 'SELECT * FROM Redemption WHERE EmployeeID = ' + str(employeeId) + ' ORDER BY RedemptionDate DESC'
        redemptionsFromDB = readData(sqlToGetRedemptions)
        redemptions = []
        for r in redemptionsFromDB:
            redemptions.append((rewardsDict[r[2]][0], r[3].strftime("%B %-d %Y, %-I:%M %p"), rewardsDict[r[2]][1], r[4]))
        #print(redemptions)

        return render_template('redemptionHome.html', firstName=firstName, pointsReceived=pointsReceived, redemptions=redemptions)
    else:
        return redirect(url_for('login'))

@app.route('/redeem', methods=('GET', 'POST'))
def redeem():
    if 'email' in session:
        if request.method == 'GET':
            sqlToFindUser = 'SELECT Email, FirstName, PointsToGive, PointsReceived FROM Employee WHERE Email = \'' + session['email'] + '\''
            user = readData(sqlToFindUser)
            firstName = user[0][1]
            pointsToGive = user[0][2]
            pointsReceived = user[0][3]
            #print(user)

            sqlToGetRewards = 'SELECT * FROM Reward'
            rewardsFromDB = readData(sqlToGetRewards)
            rewards = []
            for r in rewardsFromDB:
                rewards.append((r[0], r[1], str(r[2]) + ' points'))
            #print(rewards)
            return render_template('redeem.html', firstName=firstName, pointsReceived=pointsReceived, rewards=rewards)

        elif request.method == 'POST':
            error = ""

            sqlToFindUser = 'SELECT EmployeeID, Email, FirstName, PointsToGive, PointsReceived FROM Employee WHERE Email = \'' + session['email'] + '\''
            user = readData(sqlToFindUser)
            employeeId = user[0][0]
            firstName = user[0][2]
            pointsToGive = user[0][3]
            pointsReceived = user[0][4]

            reward = request.form['rewardSelection'].strip('()').split(',')
            #print(reward)
            rewardId = reward[0]
            sqlToFindReward = 'SELECT * FROM Reward WHERE RewardID = ' + str(rewardId)
            row = readData(sqlToFindReward)
            rewardCost = row[0][2]

            if rewardCost > pointsReceived:
                error = 'You don\'t have enough points.'
                flash(error)
                return redirect(url_for('redeem'))

            newPointsReceived = pointsReceived - rewardCost
            values = "(" + str(employeeId) + "," + str(rewardId) + ", \'" + str(datetime.now(cst_timezone).strftime('%Y-%m-%d %H:%M:%S')) + "\')"
            print(datetime.now())
            sqlToCreateRedemption = 'INSERT INTO Redemption (EmployeeID, RewardID, RedemptionDate) VALUES ' + values
            updateData(sqlToCreateRedemption)
            sqlToUpdateEmployee = 'UPDATE Employee SET PointsReceived = ' + str(newPointsReceived) + ' WHERE EmployeeID = ' + str(employeeId)
            updateData(sqlToUpdateEmployee)

            return redirect(url_for('redemptionHome'))
    else:
        return redirect(url_for('login'))

@app.route('/admin', methods=('GET', 'POST'))
def admin():
    if 'admin' in session:
        return render_template('admin.html')
    elif 'email' in session:
        return redirect(url_for('backToMenu'))
    else:
        return redirect(url_for('adminLogin'))

@app.route('/adminLogin', methods=('GET', 'POST'))
def adminLogin():
    if 'admin' in session:
        return redirect(url_for('admin'))
    elif 'email' in session:
        return redirect(url_for('backToMenu'))

    else:
        if request.method == 'POST':
            email = request.form['email']
            email = '\'' + str(email) + '\''
            password = request.form['password']
            error = ""

            sqlToFindAdmin = 'SELECT email, password from Admin where email = ' + email
            admin = readData(sqlToFindAdmin)
            print(admin)
            if len(admin) == 0:
                error = 'Incorrect Email'
            else:
                if check_password_hash(admin[0][1], password) != True:
                    error = 'Incorrect Password'
                else:
                    print('Success!')
                    session.clear()
                    session['admin'] = email.strip('\'')
                    return redirect(url_for('admin'))

            flash(error)
        return render_template('adminLogin.html')

@app.route('/employees')
def employees():
    if 'admin' in session:
        sqlToGetEmployees = 'SELECT * from Employee'
        employees = readData(sqlToGetEmployees)
        return render_template('employees.html', employees=employees)
    elif 'email' in session:
        return redirect(url_for('backToMenu'))
    else:
        return redirect(url_for('adminLogin'))

@app.route('/redemptions')
def redemptions():
    if 'admin' in session:
        sqlToGetAllRedemptions = 'SELECT RedemptionID, Email, RewardName, RewardCost, RedemptionDate, Received FROM Redemption JOIN Employee ON Employee.EmployeeID = Redemption.EmployeeID JOIN Reward ON Reward.RewardID = Redemption.RewardID ORDER BY RedemptionDate DESC;'
        redemptions = readData(sqlToGetAllRedemptions)
        redemptionsList = []
        for redemption in redemptions:
            redemptionsList.append((
                redemption[0], 
                redemption[1], 
                redemption[2], 
                redemption[3], 
                redemption[4].strftime("%B %-d %Y, %-I:%M %p"), 
                redemption[5]))
        return render_template('redemptions.html', redemptions=redemptionsList)
    elif 'email' in session:
        return redirect(url_for('backToMenu'))
    else:
        return redirect(url_for('adminLogin'))

@app.route('/redemptions/<redemption>', methods=('GET','POST'))
def editRedemption(redemption):
    if 'admin' in session:
        if request.method == 'GET':
            sqlToGetAllRedemption = 'SELECT RedemptionID, Email, RewardName, RewardCost, RedemptionDate, Received FROM Redemption JOIN Employee ON Employee.EmployeeID = Redemption.EmployeeID JOIN Reward ON Reward.RewardID = Redemption.RewardID WHERE RedemptionID = ' + redemption + ' ORDER BY RedemptionDate DESC;'
            redemption = readData(sqlToGetAllRedemption)[0]
            return render_template('editRedemption.html', redemption=redemption)

        elif request.method == 'POST':
            received = request.form['received?']
            sqlToEditRedemption = f'UPDATE Redemption SET Received = {received} WHERE RedemptionID = {redemption};'
            updateData(sqlToEditRedemption)
            return redirect(url_for('redemptions'))

    elif 'email' in session:
        return redirect(url_for('backToMenu'))
    else:
        return redirect(url_for('adminLogin'))

@app.route('/transactions')
def transactions():
    if 'admin' in session:
        sqlToGetTransactions = 'SELECT TransactionID, e1.Email as GivenBy, e2.Email as GivenTo, PointsGiven, Comments, TransactionDate FROM Transaction JOIN Employee e1 ON e1.EmployeeID = Transaction.GivenByEmployeeID JOIN Employee e2 ON e2.EmployeeID = Transaction.GivenToEmployeeID ORDER BY TransactionDate DESC;'
        transactions = readData(sqlToGetTransactions)
        transactionsList = []
        for transaction in transactions:
            transactionsList.append((
                transaction[0], 
                transaction[1], 
                transaction[2], 
                transaction[3], 
                transaction[4], 
                transaction[5].strftime("%B %-d %Y, %-I:%M %p")))
        return render_template('transactions.html', transactions=transactionsList)
    elif 'email' in session:
        return redirect(url_for('backToMenu'))
    else:
        return redirect(url_for('adminLogin'))

@app.route('/rewards', methods=('GET', 'POST'))
def rewards():
    if 'admin' in session:
        if request.method == 'GET':
            sqlToGetRewards = 'SELECT * FROM Reward'
            rewardsFromDB = readData(sqlToGetRewards)
            rewards = []
            for r in rewardsFromDB:
                rewards.append((r[0], r[1], str(r[2]) + ' points'))
            return render_template('rewards.html', rewards=rewards)

        elif request.method == 'POST':
            if request.args['action'] == 'add':
                print('ADD')
                print(request.form)
                rewardName = request.form['rewardName']
                rewardCost = request.form['rewardCost']
                insertData('INSERT INTO Reward (RewardName, RewardCost) VALUES (\'' + rewardName + '\', ' + rewardCost + ');')
                flash('Sucessfully added reward!')
            elif request.args['action'] == 'remove':
                print('REMOVE')
                print(request.form)
                rewardSelection = eval(request.form['rewardSelection'])
                print(rewardSelection[0])
                updateData('DELETE FROM Reward WHERE RewardID = ' + str(rewardSelection[0]))
                flash('Sucessfully removed reward!')
            return redirect(url_for('rewards'))

    elif 'email' in session:
        return redirect(url_for('backToMenu'))
    else:
        return redirect(url_for('adminLogin'))


@app.route('/pointsReport')
def pointsReport():
    if 'admin' in session:
        if request.method == 'GET':
            sqlPointsGivenOutByMonth = 'SELECT EXTRACT(MONTH FROM TransactionDate), EXTRACT(YEAR FROM TransactionDate), SUM(PointsGiven) FROM epms.Transaction GROUP BY EXTRACT(MONTH FROM TransactionDate), EXTRACT(YEAR FROM TransactionDate);'
            sqlPointsRedeemedByMonth = 'SELECT EXTRACT(MONTH FROM RedemptionDate), EXTRACT(YEAR FROM RedemptionDate), SUM(RewardCost) FROM epms.Redemption JOIN epms.Reward ON Redemption.RewardID = Reward.RewardID GROUP BY EXTRACT(MONTH FROM RedemptionDate), EXTRACT(YEAR FROM RedemptionDate);'
            sqlPointsGivenOutByMonthByUser = 'SELECT EXTRACT(MONTH FROM TransactionDate), EXTRACT(YEAR FROM TransactionDate), Email, SUM(PointsGiven) FROM epms.Transaction JOIN epms.Employee ON GivenByEmployeeID = EmployeeID GROUP BY GivenByEmployeeID, EXTRACT(MONTH FROM TransactionDate), EXTRACT(YEAR FROM TransactionDate) ORDER BY SUM(PointsGiven) DESC;'
            sqlPointsReceivedByMonthByUser = 'SELECT EXTRACT(MONTH FROM TransactionDate), EXTRACT(YEAR FROM TransactionDate), Email, SUM(PointsGiven) FROM epms.Transaction JOIN epms.Employee ON GivenToEmployeeID = EmployeeID GROUP BY GivenToEmployeeID, EXTRACT(MONTH FROM TransactionDate), EXTRACT(YEAR FROM TransactionDate) ORDER BY SUM(PointsGiven) DESC;'
            sqlPointsRedeemedByMonthByUser = 'SELECT EXTRACT(MONTH FROM RedemptionDate), EXTRACT(YEAR FROM RedemptionDate), Email, SUM(RewardCost) FROM epms.Redemption JOIN epms.Reward ON Redemption.RewardID = Reward.RewardID JOIN epms.Employee ON Redemption.EmployeeID = Employee.EmployeeID WHERE RedemptionDate >= now()-interval 2 month GROUP BY Redemption.EmployeeID, EXTRACT(MONTH FROM RedemptionDate), EXTRACT(YEAR FROM RedemptionDate) ORDER BY SUM(RewardCost) DESC;'
            sqlEmployeesNotUsingAllPoints = 'SELECT Email, PointsToGive FROM epms.Employee WHERE PointsToGive != 0;'

            pointsGivenOutByMonth = readData(sqlPointsGivenOutByMonth)
            pointsRedeededByMonth = readData(sqlPointsRedeemedByMonth)
            pointsGivenOutByMonthByUser = readData(sqlPointsGivenOutByMonthByUser)
            pointsReceivedByMonthByUser = readData(sqlPointsReceivedByMonthByUser)
            pointsRedeemedByMonthByUser = readData(sqlPointsRedeemedByMonthByUser)
            employeesNotUsingAllPoints = readData(sqlEmployeesNotUsingAllPoints)

            return render_template('pointsReport.html', pointsGivenOutByMonth=pointsGivenOutByMonth, pointsRedeededByMonth=pointsRedeededByMonth, pointsGivenOutByMonthByUser=pointsGivenOutByMonthByUser, pointsReceivedByMonthByUser=pointsReceivedByMonthByUser, pointsRedeemedByMonthByUser=pointsRedeemedByMonthByUser, employeesNotUsingAllPoints= employeesNotUsingAllPoints)

    elif 'email' in session:
        return redirect(url_for('backToMenu'))
    else:
        return redirect(url_for('adminLogin'))

@app.route('/resetPoints', methods=('GET','POST'))
def resetPoints():
    if 'admin' in session:
        if request.method == 'POST':
            updateData('CALL PointsReset')
            flash("Points have been reset.")
            return redirect(url_for('admin'))
        return render_template('resetPoints.html')

    elif 'email' in session:
        return redirect(url_for('backToMenu'))
    else:
        return redirect(url_for('adminLogin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')


