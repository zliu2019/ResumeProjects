
#### How to use MS SQL Server with VS Code?

Tutorial: 

https://docs.microsoft.com/en-us/sql/t-sql/lesson-1-creating-database-objects?view=sql-server-ver15

VS Code Steps:

    1/ open a new file, name it
    
    2/ press Ctrl+Shift+P or F1 to open command palette

    3a/ To create a new connect profile, press MS SQL: Manage Connection Profiles, and use localhost to create a new profile.

    3b/ Since I already created a connection profile named Zhilin-Liu from localhost, so Enter SQL connect, press MS SQL: connect. 
    
    4/ Press Zhilin-Liu
    
    5/ play!

#### Manage my databases?

Use Master

Create Database my_db_name

(Delete statements above, then ...)

Use my_db_name

Create Table:

-- Create a new table called 'TableName' in schema 'SchemaName'
-- Drop the table if it already exists
IF OBJECT_ID('SchemaName.Employees', 'U') IS NOT NULL
DROP TABLE SchemaName.Employees
GO
-- Create the table in the specified schema
CREATE TABLE SchemaName.Employees
(
    EmployeesId INT NOT NULL PRIMARY KEY, -- primary key column
    Column1 [NVARCHAR](50) NOT NULL,
    Column2 [NVARCHAR](50) NOT NULL
    -- specify more columns here
);
GO

***Schema***:

A Schema is a collection of database objects (including Tables, Views, procedures, index, etc.) associated with a database. 

The username of a database is called a Schema owner (owner of logically grouped structures of data). 

Schema always belong to a single database whereas a database can have single or multiple schemas. 

Also, it is also very similar to separate namespaces or containers, which stores database objects. It includes various database objects including your tables,  views, procedures, index, etc.

#### How to play with Transact-SQL?

Tutorial:

https://docs.microsoft.com/en-us/sql/t-sql/tutorial-writing-transact-sql-statements?view=sql-server-ver15

#### How to use Machine Learning on SQL Server with Python on rational data both on-premises and in the cloud?

Tutorial:

https://docs.microsoft.com/en-us/sql/machine-learning/?view=sql-server-ver15