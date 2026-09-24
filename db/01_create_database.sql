/*==========================================================================
  01_create_database.sql

  Purpose : Creates the TeraTestingDB database and all tables used by the
            Teradata "Tera" agent regression eval set.

  Domains :
    - Business / analytics : Customer, Product, Store, Orders, OrderLine,
                              Employee
    - DBA / security / ops : DBA_Users, DBA_AccessRights,
                              DBA_SecurityAuditLog, DBA_QueryLog,
                              DBA_TableSpaceUsage
                              (modeled after Teradata DBC-style system views
                              since real DBC objects cannot be created here)

  Notes   :
    - Every table declares an explicit PRIMARY INDEX (Teradata requires/
      strongly expects one; it also determines row distribution).
    - Cross-table relationships use REFERENCES ... WITH NO CHECK OPTION
      (Teradata "soft" referential integrity), which is standard practice
      in Teradata EDWs and deliberately allows a few rows that violate
      logical RI for edge-case testing (e.g. an audit-log entry for a
      user who no longer exists in DBA_Users).
==========================================================================*/

CREATE DATABASE TeraTestingDB
FROM DBC
AS PERM = 2000000000,
   SPOOL = 1000000000;

DATABASE TeraTestingDB;

/*--------------------------------------------------------------------------
  Business / analytics domain
--------------------------------------------------------------------------*/

CREATE SET TABLE Customer
(
    CustomerID      INTEGER         NOT NULL,
    CustomerName    VARCHAR(100)    NOT NULL,
    Region          VARCHAR(30),
    Segment         VARCHAR(30),
    SignupDate      DATE,
    Email           VARCHAR(100)
)
PRIMARY INDEX (CustomerID);

CREATE SET TABLE Product
(
    ProductID       INTEGER         NOT NULL,
    ProductName     VARCHAR(100)    NOT NULL,
    Category        VARCHAR(50),
    UnitPrice       DECIMAL(10,2),
    Discontinued    CHAR(1)         DEFAULT 'N'
)
PRIMARY INDEX (ProductID);

CREATE SET TABLE Store
(
    StoreID         INTEGER         NOT NULL,
    StoreName       VARCHAR(60)     NOT NULL,
    Region          VARCHAR(30),
    ManagerName     VARCHAR(100)
)
PRIMARY INDEX (StoreID);

CREATE SET TABLE Orders
(
    OrderID         INTEGER         NOT NULL,
    CustomerID      INTEGER         NOT NULL REFERENCES WITH NO CHECK OPTION Customer (CustomerID),
    StoreID         INTEGER         REFERENCES WITH NO CHECK OPTION Store (StoreID),
    OrderDate       DATE            NOT NULL,
    Status          VARCHAR(20)     NOT NULL
)
PRIMARY INDEX (OrderID);

CREATE SET TABLE OrderLine
(
    OrderLineID     INTEGER         NOT NULL,
    OrderID         INTEGER         NOT NULL REFERENCES WITH NO CHECK OPTION Orders (OrderID),
    ProductID       INTEGER         REFERENCES WITH NO CHECK OPTION Product (ProductID),
    Quantity        INTEGER         NOT NULL,
    LineTotal       DECIMAL(12,2)   NOT NULL
)
PRIMARY INDEX (OrderLineID);

CREATE SET TABLE Employee
(
    EmployeeID      INTEGER         NOT NULL,
    EmployeeName    VARCHAR(100)    NOT NULL,
    Department      VARCHAR(50),
    JobTitle        VARCHAR(50),
    ManagerID       INTEGER         REFERENCES WITH NO CHECK OPTION Employee (EmployeeID)
)
PRIMARY INDEX (EmployeeID);

/*--------------------------------------------------------------------------
  DBA / security / ops domain
--------------------------------------------------------------------------*/

CREATE SET TABLE DBA_Users
(
    UserName        VARCHAR(30)     NOT NULL,
    CreateDate      DATE            NOT NULL,
    DefaultDatabase VARCHAR(30),
    PermSpaceMB     DECIMAL(12,2),
    SpoolSpaceMB    DECIMAL(12,2),
    AccountRole     VARCHAR(30)
)
PRIMARY INDEX (UserName);

CREATE SET TABLE DBA_AccessRights
(
    AccessID        INTEGER         NOT NULL,
    UserName        VARCHAR(30)     REFERENCES WITH NO CHECK OPTION DBA_Users (UserName),
    DatabaseName    VARCHAR(30)     NOT NULL,
    TableName       VARCHAR(30),
    AccessType      VARCHAR(20)     NOT NULL,
    GrantedBy       VARCHAR(30),
    GrantDate       DATE
)
PRIMARY INDEX (AccessID);

CREATE SET TABLE DBA_SecurityAuditLog
(
    LogID           INTEGER         NOT NULL,
    UserName        VARCHAR(30),
    EventType       VARCHAR(30)     NOT NULL,
    EventTimestamp  TIMESTAMP(0)    NOT NULL,
    SourceIP        VARCHAR(45),
    Success         CHAR(1)         NOT NULL
)
PRIMARY INDEX (LogID);

CREATE SET TABLE DBA_QueryLog
(
    QueryID         INTEGER         NOT NULL,
    UserName        VARCHAR(30)     REFERENCES WITH NO CHECK OPTION DBA_Users (UserName),
    QueryText       VARCHAR(500),
    StartTime       TIMESTAMP(0)    NOT NULL,
    ElapsedSeconds  DECIMAL(10,2),
    CPUTime         DECIMAL(10,2),
    IOCount         INTEGER,
    SpoolUsageMB    DECIMAL(12,2),
    Status          VARCHAR(20)
)
PRIMARY INDEX (QueryID);

CREATE SET TABLE DBA_TableSpaceUsage
(
    DatabaseName            VARCHAR(30)     NOT NULL,
    TableName               VARCHAR(30)     NOT NULL,
    CurrentPermMB           DECIMAL(12,2),
    PeakPermMB              DECIMAL(12,2),
    RowCount                INTEGER,
    LastStatsCollectionDate DATE
)
PRIMARY INDEX (DatabaseName, TableName);
