CREATE Table Employee (
EmployeeID INT NOT NULL AUTO_INCREMENT,
Email VARCHAR(50) NOT NULL,
FirstName  VARCHAR(50) NOT NULL,
LastName  VARCHAR(50) NOT NULL,
Password  VARCHAR(100) NOT NULL,
PointsToGive  INT NOT NULL,
PointsReceived  INT NOT NULL,
PRIMARY KEY (EmployeeID));

CREATE Table Transaction (
TransactionID INT NOT NULL AUTO_INCREMENT,
GivenByEmployeeID INT NOT NULL,
GivenToEmployeeID INT NOT NULL,
PointsGiven INT NOT NULL,
Comments VARCHAR(500),
TransactionDate DATETIME NOT NULL,
PRIMARY KEY (TransactionID),
FOREIGN KEY (GivenByEmployeeID) REFERENCES Employee(EmployeeID),
FOREIGN KEY (GivenToEmployeeID) REFERENCES Employee(EmployeeID));

CREATE Table Reward (
RewardID INT NOT NULL AUTO_INCREMENT,
RewardName VARCHAR(50) NOT NULL,
RewardCost INT NOT NULL,
PRIMARY KEY (RewardID));

CREATE Table Redemption (
RedemptionID INT NOT NULL AUTO_INCREMENT,
EmployeeID INT NOT NULL,
RewardID INT NOT NULL,
RedemptionDate DATETIME NOT NULL,
Received TINYINT NOT NULL DEFAULT '0',
PRIMARY KEY (RedemptionID),
FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID),
FOREIGN KEY (RewardID) REFERENCES Reward(RewardID));

CREATE Table Admin (
AdminID INT NOT NULL AUTO_INCREMENT,
Email VARCHAR(50) NOT NULL,
Password  VARCHAR(100) NOT NULL,
PRIMARY KEY (AdminID));

COMMIT;


# Stored Procedure
USE `epms`;
DROP procedure IF EXISTS `PointsReset`;

DELIMITER $$
USE `epms`$$
CREATE PROCEDURE PointsReset ()
BEGIN
	UPDATE Employee SET PointsToGive = 1000;
END$$

DELIMITER ;