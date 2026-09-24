/*==========================================================================
  02_load_data.sql

  Purpose : Populates TeraTestingDB with representative data, including
            deliberate edge-case rows referenced by evals/cases/*.yaml
            (see inline comments marked EDGE CASE).

  Notes   :
    - Uses one INSERT ... VALUES statement per row. Teradata does not
      support the multi-row VALUES(...),(...) syntax used by some other
      RDBMS, so single-row INSERTs are the portable, correct form here.
==========================================================================*/

DATABASE TeraTestingDB;

/*--------------------------------------------------------------------------
  Customer  (15 rows; CustomerID 115 has zero orders -- EDGE CASE)
--------------------------------------------------------------------------*/
INSERT INTO Customer (CustomerID, CustomerName, Region, Segment, SignupDate, Email) VALUES (101, 'Acme Manufacturing',   'Northeast', 'Corporate',      DATE '2021-03-15', 'ap@acmemfg.com');
INSERT INTO Customer (CustomerID, CustomerName, Region, Segment, SignupDate, Email) VALUES (102, 'Blue Ridge Retail',    'Southeast', 'Corporate',      DATE '2020-07-01', 'buyer@blueridge.com');
INSERT INTO Customer (CustomerID, CustomerName, Region, Segment, SignupDate, Email) VALUES (103, 'Carla Nguyen',         'West',      'Consumer',       DATE '2022-01-20', 'carla.nguyen@example.com');
INSERT INTO Customer (CustomerID, CustomerName, Region, Segment, SignupDate, Email) VALUES (104, 'Delta Logistics',      'Midwest',   'Corporate',      DATE '2019-11-05', 'orders@deltalog.com');
INSERT INTO Customer (CustomerID, CustomerName, Region, Segment, SignupDate, Email) VALUES (105, 'Evan Brooks',          'Northeast', 'Consumer',       DATE '2023-05-11', 'evan.brooks@example.com');
INSERT INTO Customer (CustomerID, CustomerName, Region, Segment, SignupDate, Email) VALUES (106, 'Frontier Hardware',    'West',      'Small Business', DATE '2021-09-30', 'sales@frontierhw.com');
INSERT INTO Customer (CustomerID, CustomerName, Region, Segment, SignupDate, Email) VALUES (107, 'Grace Kim',            'Southeast', 'Consumer',       DATE '2022-08-14', 'grace.kim@example.com');
INSERT INTO Customer (CustomerID, CustomerName, Region, Segment, SignupDate, Email) VALUES (108, 'Harbor Point Cafe',    'Northeast', 'Small Business', DATE '2020-02-18', 'manager@harborpoint.com');
INSERT INTO Customer (CustomerID, CustomerName, Region, Segment, SignupDate, Email) VALUES (109, 'Ivan Petrov',          'Midwest',   'Consumer',       DATE '2023-02-27', 'ivan.petrov@example.com');
INSERT INTO Customer (CustomerID, CustomerName, Region, Segment, SignupDate, Email) VALUES (110, 'Jade Consulting Group','West',      'Corporate',      DATE '2018-06-09', 'contact@jadeconsulting.com');
INSERT INTO Customer (CustomerID, CustomerName, Region, Segment, SignupDate, Email) VALUES (111, 'Karen Ollila',         'Southeast', 'Consumer',       DATE '2021-12-01', 'karen.ollila@example.com');
INSERT INTO Customer (CustomerID, CustomerName, Region, Segment, SignupDate, Email) VALUES (112, 'Lonestar Auto Parts',  'Midwest',   'Small Business', DATE '2019-04-22', 'parts@lonestarauto.com');
INSERT INTO Customer (CustomerID, CustomerName, Region, Segment, SignupDate, Email) VALUES (113, 'Marcus Webb',          'Northeast', 'Consumer',       DATE '2022-10-03', 'marcus.webb@example.com');
INSERT INTO Customer (CustomerID, CustomerName, Region, Segment, SignupDate, Email) VALUES (114, 'Nolan & Pierce LLP',   'West',      'Corporate',      DATE '2017-08-16', 'billing@nolanpierce.com');
INSERT INTO Customer (CustomerID, CustomerName, Region, Segment, SignupDate, Email) VALUES (115, 'Olivia Chen',          'Southeast', 'Consumer',       DATE '2024-06-30', 'olivia.chen@example.com');

/*--------------------------------------------------------------------------
  Product  (15 rows; ProductID 210 has NULL Category -- EDGE CASE;
            ProductID 215 is discontinued but still referenced by an old
            order line -- EDGE CASE)
--------------------------------------------------------------------------*/
INSERT INTO Product (ProductID, ProductName, Category, UnitPrice, Discontinued) VALUES (201, 'Steel Hex Bolt 10mm',        'Hardware',         0.45,   'N');
INSERT INTO Product (ProductID, ProductName, Category, UnitPrice, Discontinued) VALUES (202, 'Cordless Drill 18V',        'Power Tools',     89.99,   'N');
INSERT INTO Product (ProductID, ProductName, Category, UnitPrice, Discontinued) VALUES (203, 'Safety Goggles',            'Safety Gear',      7.25,   'N');
INSERT INTO Product (ProductID, ProductName, Category, UnitPrice, Discontinued) VALUES (204, 'Industrial Shelving Unit',  'Storage',        149.00,   'N');
INSERT INTO Product (ProductID, ProductName, Category, UnitPrice, Discontinued) VALUES (205, 'LED Work Light',            'Lighting',        24.50,   'N');
INSERT INTO Product (ProductID, ProductName, Category, UnitPrice, Discontinued) VALUES (206, 'Copper Wire 50ft',          'Electrical',      32.10,   'N');
INSERT INTO Product (ProductID, ProductName, Category, UnitPrice, Discontinued) VALUES (207, 'Adjustable Wrench Set',     'Hardware',        18.75,   'N');
INSERT INTO Product (ProductID, ProductName, Category, UnitPrice, Discontinued) VALUES (208, 'Shop Vacuum 6-Gallon',      'Power Tools',    109.99,   'N');
INSERT INTO Product (ProductID, ProductName, Category, UnitPrice, Discontinued) VALUES (209, 'Work Gloves (Pair)',        'Safety Gear',      9.99,   'N');
INSERT INTO Product (ProductID, ProductName, Category, UnitPrice, Discontinued) VALUES (210, 'Miscellaneous Fastener Kit', NULL,             15.00,   'N');
INSERT INTO Product (ProductID, ProductName, Category, UnitPrice, Discontinued) VALUES (211, 'Extension Cord 25ft',       'Electrical',      21.40,   'N');
INSERT INTO Product (ProductID, ProductName, Category, UnitPrice, Discontinued) VALUES (212, 'Folding Workbench',         'Storage',        129.50,   'N');
INSERT INTO Product (ProductID, ProductName, Category, UnitPrice, Discontinued) VALUES (213, 'Paint Roller Set',          'Painting',        11.20,   'N');
INSERT INTO Product (ProductID, ProductName, Category, UnitPrice, Discontinued) VALUES (214, 'Ratchet Tie-Down Straps',   'Hardware',        14.60,   'N');
INSERT INTO Product (ProductID, ProductName, Category, UnitPrice, Discontinued) VALUES (215, 'Analog Shop Radio',         'Electronics',     42.00,   'Y');

/*--------------------------------------------------------------------------
  Store (5 rows)
--------------------------------------------------------------------------*/
INSERT INTO Store (StoreID, StoreName, Region, ManagerName) VALUES (301, 'Downtown Supply Co.',   'Northeast', 'Tara Whitfield');
INSERT INTO Store (StoreID, StoreName, Region, ManagerName) VALUES (302, 'Riverside Hardware',    'Southeast', 'Marcus Delgado');
INSERT INTO Store (StoreID, StoreName, Region, ManagerName) VALUES (303, 'Pacific Trade Depot',   'West',      'Susan Alvarez');
INSERT INTO Store (StoreID, StoreName, Region, ManagerName) VALUES (304, 'Heartland Builders Mart','Midwest',  'Derek Osei');
INSERT INTO Store (StoreID, StoreName, Region, ManagerName) VALUES (305, 'Online Fulfillment Center', NULL,    'Priya Raman');

/*--------------------------------------------------------------------------
  Orders (30 rows; OrderID 430 is a very old order using the discontinued
          product 215; several Cancelled/Returned/Pending statuses for
          edge-case prompts; no order references CustomerID 115)
--------------------------------------------------------------------------*/
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (401, 101, 301, DATE '2025-01-10', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (402, 102, 302, DATE '2025-01-12', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (403, 103, 305, DATE '2025-01-15', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (404, 104, 304, DATE '2025-01-18', 'Cancelled');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (405, 105, 301, DATE '2025-01-20', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (406, 106, 303, DATE '2025-01-22', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (407, 107, 302, DATE '2025-01-25', 'Returned');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (408, 108, 301, DATE '2025-02-01', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (409, 109, 304, DATE '2025-02-03', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (410, 110, 305, DATE '2025-02-05', 'Pending');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (411, 111, 303, DATE '2025-02-08', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (412, 112, 302, DATE '2025-02-10', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (413, 113, 301, DATE '2025-02-14', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (414, 114, 305, DATE '2025-02-16', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (415, 101, 302, DATE '2025-02-20', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (416, 103, 303, DATE '2025-02-22', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (417, 104, 304, DATE '2025-02-25', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (418, 106, 301, DATE '2025-03-01', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (419, 107, 302, DATE '2025-03-03', 'Cancelled');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (420, 109, 305, DATE '2025-03-05', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (421, 110, 303, DATE '2025-03-08', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (422, 111, 301, DATE '2025-03-10', 'Returned');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (423, 112, 304, DATE '2025-03-12', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (424, 113, 302, DATE '2025-03-15', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (425, 114, 301, DATE '2025-03-18', 'Pending');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (426, 102, 305, DATE '2025-03-20', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (427, 105, 303, DATE '2025-03-22', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (428, 108, 304, DATE '2025-03-25', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (429, 113, 301, DATE '2025-03-28', 'Completed');
INSERT INTO Orders (OrderID, CustomerID, StoreID, OrderDate, Status) VALUES (430, 110, 303, DATE '2022-05-04', 'Completed');

/*--------------------------------------------------------------------------
  OrderLine (~45 rows; OrderLineID 545 uses discontinued ProductID 215)
--------------------------------------------------------------------------*/
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (501, 401, 202, 1,  89.99);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (502, 401, 201, 20,  9.00);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (503, 402, 204, 2, 298.00);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (504, 403, 205, 3,  73.50);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (505, 404, 208, 1, 109.99);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (506, 405, 209, 5,  49.95);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (507, 406, 206, 2,  64.20);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (508, 406, 211, 1,  21.40);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (509, 407, 213, 4,  44.80);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (510, 408, 212, 1, 129.50);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (511, 409, 214, 6,  87.60);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (512, 410, 207, 2,  37.50);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (513, 411, 203, 10, 72.50);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (514, 412, 210, 3,  45.00);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (515, 413, 202, 1,  89.99);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (516, 413, 205, 2,  49.00);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (517, 414, 204, 1, 149.00);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (518, 415, 201, 50, 22.50);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (519, 416, 206, 3,  96.30);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (520, 417, 208, 2, 219.98);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (521, 418, 209, 8,  79.92);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (522, 419, 213, 2,  22.40);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (523, 420, 211, 4,  85.60);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (524, 421, 214, 2,  29.20);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (525, 422, 207, 1,  18.75);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (526, 423, 212, 1, 129.50);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (527, 424, 203, 6,  43.50);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (528, 425, 210, 2,  30.00);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (529, 426, 202, 1,  89.99);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (530, 427, 205, 4,  98.00);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (531, 428, 206, 2,  64.20);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (532, 429, 209, 3,  29.97);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (533, 402, 201, 10,  4.50);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (534, 403, 214, 1,  14.60);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (535, 405, 213, 2,  22.40);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (536, 408, 211, 1,  21.40);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (537, 409, 201, 15,  6.75);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (538, 411, 207, 1,  18.75);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (539, 414, 203, 4,  29.00);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (540, 416, 210, 1,  15.00);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (541, 418, 212, 1, 129.50);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (542, 420, 204, 1, 149.00);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (543, 423, 208, 1, 109.99);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (544, 426, 206, 1,  32.10);
INSERT INTO OrderLine (OrderLineID, OrderID, ProductID, Quantity, LineTotal) VALUES (545, 430, 215, 2,  84.00);

/*--------------------------------------------------------------------------
  Employee (15 rows; simple management hierarchy, EmployeeID 601 is the
            top of the hierarchy with a NULL ManagerID)
--------------------------------------------------------------------------*/
INSERT INTO Employee (EmployeeID, EmployeeName, Department, JobTitle, ManagerID) VALUES (601, 'Renee Castillo', 'Executive',  'VP of Operations',   NULL);
INSERT INTO Employee (EmployeeID, EmployeeName, Department, JobTitle, ManagerID) VALUES (602, 'Tara Whitfield', 'Retail',     'Store Manager',      601);
INSERT INTO Employee (EmployeeID, EmployeeName, Department, JobTitle, ManagerID) VALUES (603, 'Marcus Delgado', 'Retail',     'Store Manager',      601);
INSERT INTO Employee (EmployeeID, EmployeeName, Department, JobTitle, ManagerID) VALUES (604, 'Susan Alvarez',  'Retail',     'Store Manager',      601);
INSERT INTO Employee (EmployeeID, EmployeeName, Department, JobTitle, ManagerID) VALUES (605, 'Derek Osei',     'Retail',     'Store Manager',      601);
INSERT INTO Employee (EmployeeID, EmployeeName, Department, JobTitle, ManagerID) VALUES (606, 'Priya Raman',    'Fulfillment','Fulfillment Manager',601);
INSERT INTO Employee (EmployeeID, EmployeeName, Department, JobTitle, ManagerID) VALUES (607, 'Owen Fitzgerald','Retail',     'Sales Associate',    602);
INSERT INTO Employee (EmployeeID, EmployeeName, Department, JobTitle, ManagerID) VALUES (608, 'Naomi Reyes',    'Retail',     'Sales Associate',    602);
INSERT INTO Employee (EmployeeID, EmployeeName, Department, JobTitle, ManagerID) VALUES (609, 'Victor Huang',   'Retail',     'Sales Associate',    603);
INSERT INTO Employee (EmployeeID, EmployeeName, Department, JobTitle, ManagerID) VALUES (610, 'Chloe Dubois',   'Retail',     'Sales Associate',    604);
INSERT INTO Employee (EmployeeID, EmployeeName, Department, JobTitle, ManagerID) VALUES (611, 'Amara Okafor',   'Retail',     'Sales Associate',    605);
INSERT INTO Employee (EmployeeID, EmployeeName, Department, JobTitle, ManagerID) VALUES (612, 'Liam Shepherd',  'Fulfillment','Warehouse Associate',606);
INSERT INTO Employee (EmployeeID, EmployeeName, Department, JobTitle, ManagerID) VALUES (613, 'Sofia Marchetti','Finance',    'Financial Analyst',  601);
INSERT INTO Employee (EmployeeID, EmployeeName, Department, JobTitle, ManagerID) VALUES (614, 'Ethan Brar',     'IT',         'Database Administrator', 601);
INSERT INTO Employee (EmployeeID, EmployeeName, Department, JobTitle, ManagerID) VALUES (615, 'Grace Lindqvist','IT',        'Security Engineer',  601);

/*--------------------------------------------------------------------------
  DBA_Users (12 rows; 'suspended_analyst' is Suspended -- EDGE CASE;
             'former_contractor' exists here but has no matching activity
             in DBA_AccessRights -- EDGE CASE)
--------------------------------------------------------------------------*/
INSERT INTO DBA_Users (UserName, CreateDate, DefaultDatabase, PermSpaceMB, SpoolSpaceMB, AccountRole) VALUES ('dbaadmin',          DATE '2017-01-10', 'TeraTestingDB', 500000.00, 200000.00, 'DBA');
INSERT INTO DBA_Users (UserName, CreateDate, DefaultDatabase, PermSpaceMB, SpoolSpaceMB, AccountRole) VALUES ('ebrar',             DATE '2018-06-12', 'TeraTestingDB', 200000.00, 100000.00, 'DBA');
INSERT INTO DBA_Users (UserName, CreateDate, DefaultDatabase, PermSpaceMB, SpoolSpaceMB, AccountRole) VALUES ('glindqvist',        DATE '2019-02-20', 'TeraTestingDB',  50000.00,  50000.00, 'Security');
INSERT INTO DBA_Users (UserName, CreateDate, DefaultDatabase, PermSpaceMB, SpoolSpaceMB, AccountRole) VALUES ('smarchetti',        DATE '2020-03-05', 'TeraTestingDB',  20000.00,  30000.00, 'Analyst');
INSERT INTO DBA_Users (UserName, CreateDate, DefaultDatabase, PermSpaceMB, SpoolSpaceMB, AccountRole) VALUES ('jsmith_ds',         DATE '2021-04-14', 'TeraTestingDB',  30000.00,  60000.00, 'Analyst');
INSERT INTO DBA_Users (UserName, CreateDate, DefaultDatabase, PermSpaceMB, SpoolSpaceMB, AccountRole) VALUES ('asingh_dev',        DATE '2021-09-09', 'TeraTestingDB',  15000.00,  25000.00, 'Developer');
INSERT INTO DBA_Users (UserName, CreateDate, DefaultDatabase, PermSpaceMB, SpoolSpaceMB, AccountRole) VALUES ('mgarcia_ops',       DATE '2020-11-23', 'TeraTestingDB',  25000.00,  40000.00, 'Developer');
INSERT INTO DBA_Users (UserName, CreateDate, DefaultDatabase, PermSpaceMB, SpoolSpaceMB, AccountRole) VALUES ('svc_etl',           DATE '2019-08-01', 'TeraTestingDB', 100000.00, 150000.00, 'ServiceAccount');
INSERT INTO DBA_Users (UserName, CreateDate, DefaultDatabase, PermSpaceMB, SpoolSpaceMB, AccountRole) VALUES ('guest_analyst',     DATE '2023-01-05', 'TeraTestingDB',   5000.00,  10000.00, 'ReadOnly');
INSERT INTO DBA_Users (UserName, CreateDate, DefaultDatabase, PermSpaceMB, SpoolSpaceMB, AccountRole) VALUES ('suspended_analyst', DATE '2020-05-17', 'TeraTestingDB',  10000.00,  10000.00, 'Suspended');
INSERT INTO DBA_Users (UserName, CreateDate, DefaultDatabase, PermSpaceMB, SpoolSpaceMB, AccountRole) VALUES ('former_contractor', DATE '2022-02-02', 'TeraTestingDB',   5000.00,   5000.00, 'ReadOnly');
INSERT INTO DBA_Users (UserName, CreateDate, DefaultDatabase, PermSpaceMB, SpoolSpaceMB, AccountRole) VALUES ('secadmin',          DATE '2018-01-01', 'TeraTestingDB',  50000.00,  50000.00, 'Security');

/*--------------------------------------------------------------------------
  DBA_AccessRights (~20 rows; AccessID 719 grants rights on a table name
                    that does not exist in this database -- EDGE CASE,
                    representing a stale grant left over from a rename/drop)
--------------------------------------------------------------------------*/
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (701, 'jsmith_ds',   'TeraTestingDB', 'Customer',              'SELECT', 'dbaadmin', DATE '2021-04-15');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (702, 'jsmith_ds',   'TeraTestingDB', 'Orders',                'SELECT', 'dbaadmin', DATE '2021-04-15');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (703, 'jsmith_ds',   'TeraTestingDB', 'OrderLine',             'SELECT', 'dbaadmin', DATE '2021-04-15');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (704, 'asingh_dev',  'TeraTestingDB', 'Product',               'SELECT', 'dbaadmin', DATE '2021-09-10');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (705, 'asingh_dev',  'TeraTestingDB', 'Product',               'INSERT', 'dbaadmin', DATE '2021-09-10');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (706, 'asingh_dev',  'TeraTestingDB', 'Product',               'UPDATE', 'dbaadmin', DATE '2021-09-10');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (707, 'mgarcia_ops', 'TeraTestingDB', 'Orders',                'ALL',    'dbaadmin', DATE '2020-11-24');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (708, 'mgarcia_ops', 'TeraTestingDB', 'OrderLine',             'ALL',    'dbaadmin', DATE '2020-11-24');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (709, 'svc_etl',     'TeraTestingDB', 'Customer',              'INSERT', 'dbaadmin', DATE '2019-08-02');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (710, 'svc_etl',     'TeraTestingDB', 'Orders',                'INSERT', 'dbaadmin', DATE '2019-08-02');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (711, 'svc_etl',     'TeraTestingDB', 'OrderLine',             'INSERT', 'dbaadmin', DATE '2019-08-02');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (712, 'svc_etl',     'TeraTestingDB', 'Product',               'INSERT', 'dbaadmin', DATE '2019-08-02');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (713, 'guest_analyst','TeraTestingDB','Customer',              'SELECT', 'dbaadmin', DATE '2023-01-06');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (714, 'guest_analyst','TeraTestingDB','Product',               'SELECT', 'dbaadmin', DATE '2023-01-06');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (715, 'smarchetti',  'TeraTestingDB', 'Orders',                'SELECT', 'dbaadmin', DATE '2020-03-06');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (716, 'smarchetti',  'TeraTestingDB', 'OrderLine',             'SELECT', 'dbaadmin', DATE '2020-03-06');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (717, 'ebrar',       'TeraTestingDB', 'DBA_QueryLog',          'SELECT', 'dbaadmin', DATE '2018-06-13');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (718, 'glindqvist',  'TeraTestingDB', 'DBA_SecurityAuditLog',  'SELECT', 'dbaadmin', DATE '2019-02-21');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (719, 'former_contractor','TeraTestingDB','LegacyShipmentTbl', 'SELECT', 'dbaadmin', DATE '2022-02-03');
INSERT INTO DBA_AccessRights (AccessID, UserName, DatabaseName, TableName, AccessType, GrantedBy, GrantDate) VALUES (720, 'suspended_analyst','TeraTestingDB','Customer',          'SELECT', 'dbaadmin', DATE '2020-05-18');

/*--------------------------------------------------------------------------
  DBA_SecurityAuditLog (~25 rows; includes a brute-force pattern of failed
                        logons from one IP, a PERMISSION_DENIED event, and
                        a logon attempt by 'ghost_user' who does not exist
                        in DBA_Users -- EDGE CASE)
--------------------------------------------------------------------------*/
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (801, 'dbaadmin',          'LOGON',            TIMESTAMP '2025-03-01 08:00:00', '10.0.1.5',    'Y');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (802, 'jsmith_ds',         'LOGON',            TIMESTAMP '2025-03-01 08:15:00', '10.0.2.11',   'Y');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (803, 'jsmith_ds',         'LOGOFF',           TIMESTAMP '2025-03-01 17:30:00', '10.0.2.11',   'Y');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (804, 'asingh_dev',        'LOGON',            TIMESTAMP '2025-03-01 09:05:00', '10.0.2.14',   'Y');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (805, 'guest_analyst',     'LOGON',            TIMESTAMP '2025-03-01 09:10:00', '10.0.9.2',    'Y');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (806, 'guest_analyst',     'PERMISSION_DENIED',TIMESTAMP '2025-03-01 09:12:00', '10.0.9.2',    'N');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (807, 'suspended_analyst', 'FAILED_LOGON',     TIMESTAMP '2025-03-01 10:00:00', '10.0.4.7',    'N');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (808, 'unknown_user',      'FAILED_LOGON',     TIMESTAMP '2025-03-01 23:58:00', '203.0.113.44','N');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (809, 'unknown_user',      'FAILED_LOGON',     TIMESTAMP '2025-03-01 23:58:05', '203.0.113.44','N');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (810, 'unknown_user',      'FAILED_LOGON',     TIMESTAMP '2025-03-01 23:58:10', '203.0.113.44','N');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (811, 'unknown_user',      'FAILED_LOGON',     TIMESTAMP '2025-03-01 23:58:15', '203.0.113.44','N');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (812, 'unknown_user',      'FAILED_LOGON',     TIMESTAMP '2025-03-01 23:58:20', '203.0.113.44','N');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (813, 'ghost_user',        'FAILED_LOGON',     TIMESTAMP '2025-03-02 02:14:00', '198.51.100.9','N');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (814, 'ebrar',             'LOGON',            TIMESTAMP '2025-03-02 08:00:00', '10.0.1.9',    'Y');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (815, 'ebrar',             'PASSWORD_CHANGE',  TIMESTAMP '2025-03-02 08:05:00', '10.0.1.9',    'Y');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (816, 'glindqvist',        'LOGON',            TIMESTAMP '2025-03-02 08:30:00', '10.0.1.12',   'Y');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (817, 'smarchetti',        'LOGON',            TIMESTAMP '2025-03-02 09:00:00', '10.0.3.4',    'Y');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (818, 'smarchetti',        'LOGOFF',           TIMESTAMP '2025-03-02 16:45:00', '10.0.3.4',    'Y');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (819, 'mgarcia_ops',       'LOGON',            TIMESTAMP '2025-03-02 09:05:00', '10.0.2.20',   'Y');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (820, 'svc_etl',           'LOGON',            TIMESTAMP '2025-03-02 01:00:00', '10.0.0.2',    'Y');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (821, 'svc_etl',           'LOGOFF',           TIMESTAMP '2025-03-02 01:45:00', '10.0.0.2',    'Y');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (822, 'former_contractor', 'FAILED_LOGON',     TIMESTAMP '2025-03-02 14:00:00', '192.0.2.77',  'N');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (823, 'secadmin',          'LOGON',            TIMESTAMP '2025-03-02 07:55:00', '10.0.1.2',    'Y');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (824, 'secadmin',          'PERMISSION_DENIED',TIMESTAMP '2025-03-02 11:20:00', '10.0.1.2',    'N');
INSERT INTO DBA_SecurityAuditLog (LogID, UserName, EventType, EventTimestamp, SourceIP, Success) VALUES (825, 'dbaadmin',          'LOGOFF',           TIMESTAMP '2025-03-02 18:00:00', '10.0.1.5',    'Y');

/*--------------------------------------------------------------------------
  DBA_QueryLog (~25 rows; QueryID 930 is a very long-running/high-spool
               query, QueryID 931 is Aborted, QueryID 932 is run by a
               Suspended user -- all EDGE CASEs)
--------------------------------------------------------------------------*/
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (901, 'jsmith_ds',   'SELECT * FROM Orders WHERE OrderDate > DATE ''2025-01-01''',                     TIMESTAMP '2025-03-01 08:16:00', 1.20,  0.80,   1500,    45.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (902, 'jsmith_ds',   'SELECT c.Region, SUM(ol.LineTotal) FROM Customer c JOIN Orders o ON c.CustomerID = o.CustomerID JOIN OrderLine ol ON o.OrderID = ol.OrderID GROUP BY 1', TIMESTAMP '2025-03-01 08:20:00', 3.50,  2.10,   8000,   210.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (903, 'asingh_dev',  'UPDATE Product SET UnitPrice = UnitPrice * 1.05 WHERE Category = ''Hardware''',    TIMESTAMP '2025-03-01 09:06:00', 0.90,  0.60,    900,    12.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (904, 'guest_analyst','SELECT * FROM Customer',                                                          TIMESTAMP '2025-03-01 09:11:00', 0.40,  0.20,    300,     8.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (905, 'smarchetti',  'SELECT Status, COUNT(*) FROM Orders GROUP BY Status',                              TIMESTAMP '2025-03-02 09:01:00', 0.60,  0.30,    500,    10.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (906, 'mgarcia_ops', 'SELECT * FROM DBA_QueryLog WHERE ElapsedSeconds > 5',                              TIMESTAMP '2025-03-02 09:07:00', 0.75,  0.40,    600,    15.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (907, 'svc_etl',     'INSERT INTO Orders SELECT * FROM Orders_Staging',                                  TIMESTAMP '2025-03-02 01:05:00', 12.00, 9.00,  20000,   450.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (908, 'ebrar',       'SELECT DatabaseName, SUM(CurrentPermMB) FROM DBA_TableSpaceUsage GROUP BY 1',       TIMESTAMP '2025-03-02 08:10:00', 0.30,  0.15,    200,     5.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (909, 'jsmith_ds',   'SELECT p.Category, AVG(ol.LineTotal/ol.Quantity) FROM Product p JOIN OrderLine ol ON p.ProductID = ol.ProductID GROUP BY 1', TIMESTAMP '2025-03-03 10:00:00', 2.10, 1.30,   4000,   90.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (910, 'asingh_dev',  'SELECT * FROM Product WHERE Discontinued = ''Y''',                                 TIMESTAMP '2025-03-03 10:05:00', 0.20,  0.10,    150,     3.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (911, 'mgarcia_ops', 'SELECT o.OrderID FROM Orders o LEFT JOIN OrderLine ol ON o.OrderID = ol.OrderID WHERE ol.OrderLineID IS NULL', TIMESTAMP '2025-03-03 11:00:00', 0.50, 0.25, 400, 9.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (912, 'smarchetti',  'SELECT SUM(LineTotal) FROM OrderLine',                                             TIMESTAMP '2025-03-03 11:30:00', 0.35,  0.18,    300,     6.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (913, 'guest_analyst','SELECT * FROM DBA_Users',                                                         TIMESTAMP '2025-03-03 12:00:00', 0.10,  0.05,     50,     2.00, 'Failed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (914, 'jsmith_ds',   'SELECT CustomerID, COUNT(*) FROM Orders GROUP BY CustomerID HAVING COUNT(*) > 2',  TIMESTAMP '2025-03-04 09:00:00', 1.80,  1.10,   3000,    60.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (915, 'ebrar',       'COLLECT STATISTICS ON Orders COLUMN (OrderDate)',                                  TIMESTAMP '2025-03-04 07:00:00', 25.00, 18.00, 50000, 800.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (916, 'mgarcia_ops', 'DELETE FROM Orders WHERE Status = ''Cancelled'' AND OrderDate < DATE ''2020-01-01''', TIMESTAMP '2025-03-04 07:30:00', 0.60, 0.35,  500,  10.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (917, 'smarchetti',  'SELECT Region, COUNT(DISTINCT CustomerID) FROM Customer GROUP BY Region',          TIMESTAMP '2025-03-04 09:15:00', 0.45,  0.22,    350,     7.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (918, 'asingh_dev',  'ALTER TABLE Product ADD Weight DECIMAL(6,2)',                                       TIMESTAMP '2025-03-04 10:00:00', 3.00,  2.00,   2000,    40.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (919, 'jsmith_ds',   'SELECT * FROM Orders o JOIN Customer c ON o.CustomerID = c.CustomerID WHERE c.CustomerID = 115', TIMESTAMP '2025-03-05 09:00:00', 0.05, 0.02, 10, 1.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (920, 'svc_etl',     'INSERT INTO OrderLine SELECT * FROM OrderLine_Staging',                            TIMESTAMP '2025-03-05 01:00:00', 8.00,  6.00,  15000,   320.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (921, 'mgarcia_ops', 'SELECT StoreID, COUNT(*) FROM Orders GROUP BY StoreID ORDER BY 2 DESC',            TIMESTAMP '2025-03-05 09:30:00', 0.55,  0.28,    450,     9.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (922, 'ebrar',       'SELECT DatabaseName, TableName, LastStatsCollectionDate FROM DBA_TableSpaceUsage WHERE LastStatsCollectionDate IS NULL', TIMESTAMP '2025-03-05 07:45:00', 0.25, 0.12, 200, 4.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (930, 'svc_etl',     'SELECT o.*, ol.*, p.*, c.* FROM Orders o, OrderLine ol, Product p, Customer c WHERE o.OrderID = ol.OrderID', TIMESTAMP '2025-03-06 02:00:00', 612.40, 588.20, 4200000, 18500.00, 'Completed');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (931, 'asingh_dev',  'SELECT * FROM Orders CROSS JOIN OrderLine',                                        TIMESTAMP '2025-03-06 10:00:00', 45.00, 40.00, 900000,  9200.00, 'Aborted');
INSERT INTO DBA_QueryLog (QueryID, UserName, QueryText, StartTime, ElapsedSeconds, CPUTime, IOCount, SpoolUsageMB, Status) VALUES (932, 'suspended_analyst', 'SELECT * FROM Customer',                                                      TIMESTAMP '2025-03-06 03:00:00', 0.30,  0.15,    250,     5.00, 'Completed');

/*--------------------------------------------------------------------------
  DBA_TableSpaceUsage (11 rows, one per business/DBA table; 'Employee' and
                       'DBA_QueryLog' have never had stats collected --
                       EDGE CASE; 'DBA_SecurityAuditLog' shows PeakPermMB
                       greater than CurrentPermMB, indicating a purge --
                       EDGE CASE)
--------------------------------------------------------------------------*/
INSERT INTO DBA_TableSpaceUsage (DatabaseName, TableName, CurrentPermMB, PeakPermMB, RowCount, LastStatsCollectionDate) VALUES ('TeraTestingDB', 'Customer',             12.50,   12.50,    15, DATE '2025-03-01');
INSERT INTO DBA_TableSpaceUsage (DatabaseName, TableName, CurrentPermMB, PeakPermMB, RowCount, LastStatsCollectionDate) VALUES ('TeraTestingDB', 'Product',               8.20,    8.20,    15, DATE '2025-03-01');
INSERT INTO DBA_TableSpaceUsage (DatabaseName, TableName, CurrentPermMB, PeakPermMB, RowCount, LastStatsCollectionDate) VALUES ('TeraTestingDB', 'Store',                 2.10,    2.10,     5, DATE '2025-03-01');
INSERT INTO DBA_TableSpaceUsage (DatabaseName, TableName, CurrentPermMB, PeakPermMB, RowCount, LastStatsCollectionDate) VALUES ('TeraTestingDB', 'Orders',               45.60,   45.60,    30, DATE '2025-03-04');
INSERT INTO DBA_TableSpaceUsage (DatabaseName, TableName, CurrentPermMB, PeakPermMB, RowCount, LastStatsCollectionDate) VALUES ('TeraTestingDB', 'OrderLine',            78.90,   78.90,    45, DATE '2025-03-04');
INSERT INTO DBA_TableSpaceUsage (DatabaseName, TableName, CurrentPermMB, PeakPermMB, RowCount, LastStatsCollectionDate) VALUES ('TeraTestingDB', 'Employee',              6.40,    6.40,    15, NULL);
INSERT INTO DBA_TableSpaceUsage (DatabaseName, TableName, CurrentPermMB, PeakPermMB, RowCount, LastStatsCollectionDate) VALUES ('TeraTestingDB', 'DBA_Users',             3.30,    3.30,    12, DATE '2025-03-01');
INSERT INTO DBA_TableSpaceUsage (DatabaseName, TableName, CurrentPermMB, PeakPermMB, RowCount, LastStatsCollectionDate) VALUES ('TeraTestingDB', 'DBA_AccessRights',      4.75,    4.75,    20, DATE '2025-03-01');
INSERT INTO DBA_TableSpaceUsage (DatabaseName, TableName, CurrentPermMB, PeakPermMB, RowCount, LastStatsCollectionDate) VALUES ('TeraTestingDB', 'DBA_SecurityAuditLog', 15.00,   62.00,    25, DATE '2025-02-15');
INSERT INTO DBA_TableSpaceUsage (DatabaseName, TableName, CurrentPermMB, PeakPermMB, RowCount, LastStatsCollectionDate) VALUES ('TeraTestingDB', 'DBA_QueryLog',        210.00,  210.00,    25, NULL);
INSERT INTO DBA_TableSpaceUsage (DatabaseName, TableName, CurrentPermMB, PeakPermMB, RowCount, LastStatsCollectionDate) VALUES ('TeraTestingDB', 'DBA_TableSpaceUsage',   1.10,    1.10,    11, DATE '2025-03-01');
