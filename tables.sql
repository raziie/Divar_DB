create database Divar;
show databases;

# entity
CREATE TABLE divar.Creator(
    CreatorID int NOT NULL, 
    IsActive boolean,
    PRIMARY KEY(CreatorID)
);

# entity
CREATE TABLE divar.NormalUser(
    UserID int NOT NULL,
    CreatorID int NOT NULL,
    FirstName varchar(255),
    LastName varchar(255),
	RegisteredAt DATETIME NOT NULL,
    Email varchar(255) NOT NULL,
    Phone varchar(255) NOT NULL,
    Country varchar(255),
    State varchar(255),
    City varchar(255) NOT NULL,
    Street varchar(255),
    House_num int,
    PRIMARY KEY (UserID),
    FOREIGN KEY(CreatorID) REFERENCES Creator(CreatorID)
);

# entity
CREATE TABLE divar.AdminUser(
    UserID int NOT NULL,
    FirstName varchar(255),
    LastName varchar(255),
	RegisteredAt DATETIME NOT NULL,
    Email varchar(255) NOT NULL,
    Phone varchar(255) NOT NULL,
    Country varchar(255),
    State varchar(255),
    City varchar(255) NOT NULL,
    Street varchar(255),
    House_num int,
    PRIMARY KEY (UserID),
    FOREIGN KEY(UserID) REFERENCES NormalUser(UserID)
);

# entity
CREATE TABLE divar.Business(
    BusinessID int NOT NULL,
    UserID int NOT NULL,
    CreatorID int NOT NULL,
    BusName varchar(255) NOT NULL,
    Category varchar(255),
    RegistrationNum int NOT NULL,
    Country varchar(255),
    State varchar(255),
    City varchar(255) NOT NULL,
    Street varchar(255),
    HouseNum int,
    PRIMARY KEY(UserID, BusinessID),
    FOREIGN KEY(UserID) REFERENCES NormalUser(UserID),
    FOREIGN KEY(CreatorID) REFERENCES Creator(CreatorID)
);

# entity
CREATE TABLE divar.Advertise(
    AdID int NOT NULL,
    CreatorID int NOT NULL,
    Title varchar(255) not null,
    Price varchar(255) not null,
    Descriptions varchar(255),
    Subtitle varchar(255),
    Country varchar(255),
    State varchar(255),
    City varchar(255) NOT NULL,
    Street varchar(255),
    HouseNum int,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY(CreatorID, AdID),
    FOREIGN KEY(CreatorID) REFERENCES Creator(CreatorID)
);

# MN relation
CREATE TABLE divar.Visit(
    UserID int NOT NULL,
    CreatorID int NOT NULL,
    AdID int NOT NULL,
    PRIMARY KEY(UserID, CreatorID, AdID),
    FOREIGN KEY(UserID) REFERENCES NormalUser(UserID),
    FOREIGN KEY(CreatorID, AdID) REFERENCES Advertise(CreatorID, AdID)
);

# multivalue adj
CREATE TABLE divar.Images(
	AdID int NOT NULL,
    CreatorID int NOT NULL,
    ImagePath varchar(255) NOT NULL,
    PRIMARY KEY(ImagePath,CreatorID, AdID),
    FOREIGN KEY(CreatorID, AdID) REFERENCES Advertise(CreatorID, AdID)
);

# weak entity
CREATE TABLE divar.AdStatus(
	AdID int NOT NULL,
    CreatorID int NOT NULL,
    StatusComment varchar(255),
    State ENUM('DELETED','CONFIRMED','REJECTED', 'NONE') NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY(CreatorID, AdID),
    FOREIGN KEY(CreatorID, AdID) REFERENCES Advertise(CreatorID, AdID)
);

# MN relation
CREATE TABLE divar.ModifyStatus(
	UserID int NOT NULL,
    CreatorID int NOT NULL,
    AdID int NOT NULL,
    PRIMARY KEY(UserID, CreatorID, AdID),
    FOREIGN KEY(UserID) REFERENCES AdminUser(UserID),
    FOREIGN KEY(CreatorID, AdID) REFERENCES Advertise(CreatorID, AdID)
);

# weak entity
CREATE TABLE divar.AdReport(
	ReportNum int NOT NULL,
    CreatorID int NOT NULL,
    AdID int NOT NULL,
    UserID int NOT NULL,
    Category varchar(255) NOT NULL,
    Content varchar(255),
    PRIMARY KEY(ReportNum, CreatorID, AdID),
    FOREIGN KEY(CreatorID, AdID) REFERENCES Advertise(CreatorID, AdID),
    FOREIGN KEY(UserID) REFERENCES NormalUser(UserID)
);

# MN relation
CREATE TABLE divar.CheckReport(
	ReportNum int NOT NULL,
    CreatorID int NOT NULL,
    AdID int NOT NULL,
    UserID int NOT NULL,
	PRIMARY KEY(ReportNum, CreatorID, AdID, UserID),
    FOREIGN KEY(ReportNum) REFERENCES AdReport(ReportNum),
    FOREIGN KEY(CreatorID, AdID) REFERENCES Advertise(CreatorID, AdID),
    FOREIGN KEY(UserID) REFERENCES AdminUser(UserID)
);

# entity
CREATE TABLE divar.GeneralCat(
	AdID int NOT NULL,
    CreatorID int NOT NULL,
    PRIMARY KEY(CreatorID, AdID),
    FOREIGN KEY(CreatorID, AdID) REFERENCES Advertise(CreatorID, AdID)
);

# entity
CREATE TABLE divar.TransportationCat(
	AdID int NOT NULL,
    CreatorID int NOT NULL,
    Brand varchar(255),
    VehicleType varchar(255),
    VehicleEngine varchar(255),
    PRIMARY KEY(CreatorID, AdID),
    FOREIGN KEY(CreatorID, AdID) REFERENCES Advertise(CreatorID, AdID)
);

# entity
CREATE TABLE divar.HomeCat(
	AdID int NOT NULL,
    CreatorID int NOT NULL,
    Factory varchar(255),
    Size varchar(255),
    Material varchar(255),
    PRIMARY KEY(CreatorID, AdID),
    FOREIGN KEY(CreatorID, AdID) REFERENCES Advertise(CreatorID, AdID)
);

# entity
CREATE TABLE divar.RealCat(
	AdID int NOT NULL,
    CreatorID int NOT NULL,
    Meterage varchar(255),
    TitleDeed varchar(255),
    ConstructedAt DATETIME NOT NULL,
    PRIMARY KEY(CreatorID, AdID),
    FOREIGN KEY(CreatorID, AdID) REFERENCES Advertise(CreatorID, AdID)
);

# entity
CREATE TABLE divar.DigitalCat(
	AdID int NOT NULL,
    CreatorID int NOT NULL,
    Brand varchar(255),
    Model varchar(255),
    Battery varchar(255),
    PRIMARY KEY(CreatorID, AdID),
    FOREIGN KEY(CreatorID, AdID) REFERENCES Advertise(CreatorID, AdID)
);

desc divar.NormalUser; 
desc divar.AdminUser; 
desc divar.Business; 
desc divar.Creator;
desc divar.Advertise;
show tables from Divar;
drop table Divar.AdminUser;
drop database Divar;