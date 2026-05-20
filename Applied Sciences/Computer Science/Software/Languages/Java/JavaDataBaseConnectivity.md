---
title: "Definition"
domain: "Applied Sciences"
subdomain: "Computer Science > Languages > Java"
tags: [sciences-appliquées, informatique, java]
date: "2026-02-16"
---

# Definition

JDB is a java module linking the database to a web interface. The module contains interfaces, classes and exceptions.

![Objects](file:///./img/Untitle.png)


## Drivers

Every application use a driver to communicate with a database, we have to link the driver to the application via the `Class` class and the method `forName(String path)`.

### Exemple

```java
Class.forName("linktotheDrive");
```


## Connection

To connect, we have to link the database to the application with the method `getConnection` get from `DriverManager` and which take the url of the database, the username and the password.

**The connection have to be on a `try` element.**

```java
Connection con = null;
try{
	con = DriverManager.getConnection(url,nom,mdp);
}catch(Exception e){
	System.out.println(e.getMessage());
}
finally{
try {con.close();} catch(Exception e2) {} // Not the best but there's no other way
}
```

> Always close the connection with the method `close()`


# Statements

A statement is used to send queries to the database. They exists multiple statements.

## Statement

The statement is use to send queries to the database. It is very basic and does not fit for complex queries (It can be possible but it is complex) .

To send a select to a database we use `executeQuery(String query)`

For the rest we use `executeUpdate(String query)`

```java
Statement statement= con.createStatement();
String query = "";
statement.executeQuery(query);
statement.executeUpdate(query);
```

## Prepare Statement

This method is used when our query is missing some elements. For exemple if we want to compare a column with a value enter by the user or we want to insert values with a variable in it. We replace the missing elements with questions marks.

To send a select to a database we use `executeQuery()`

For the rest we use `executeUpdate()`

```java
String query = "INSERT INTO table VALUES (?,?,?)";
PreparedStatement ps = con.prepareStatement(query);
for (int i = 10; i <= 20; i++) {
	ps.setint(1, i);
	ps.setString(2, "Durand" + i);
	ps.setString(3, "paul" + i);
	ps.executeUpdate();
}
```

## Batch

The batch method is often used when we want to insert a lot of data in a table.

```java
Statement stmt = con.createStatement();
stmt.addBatch("INSERT INTO table VALUES('name0','surname0',0) ");
stmt.addBatch("INSERT INTO table VALUES('name1','surname1',1) ");
int[] count = stmt.executeBatch();
```


# Result Set

The `executeQuery()` method returns a `ResultSet` of the query.

The `ResultSet` contains the methods:

- `next()`
- `getXXX(String nameofthecolumn)`
- `getXXX(int numberofthecolumn)`

Where XXX equals the type of the column.

```java
ResultSet rs = statement.executeQuery(query);
while (rs.next()) {
String n = rs.getString("name"); 
String p = rs.getString(numberofthecolumn); 
System.out.println(n + " " + p + " " + a);
}
```


# Table infos

In JDBC we can get table infos with the interface`DatabaseMetaData`.

To get table infos we use the method `getMetaData()` from the table `ResulSetMetaData`.

The table `ResulSetMetaData` comes with a list of methods :

|Type|Method|
|---|---|
|[https://docs.oracle.com/javase/7/docs/api/java/lang/String.html](https://docs.oracle.com/javase/7/docs/api/java/lang/String.html)|[https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#getCatalogName(int)](https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#getCatalogName(int))(int column)Gets the designated column's table's catalog name.|
|int|[https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#getColumnCount()()Returns](https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#getColumnCount()()Returns) the number of columns in this ResultSet object.|
|int|[https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#getColumnDisplaySize(int)](https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#getColumnDisplaySize(int))(int column)Indicates the designated column's normal maximum width in characters.|
|[https://docs.oracle.com/javase/7/docs/api/java/lang/String.html](https://docs.oracle.com/javase/7/docs/api/java/lang/String.html)|[https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#getColumnLabel(int)](https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#getColumnLabel(int))(int column)Gets the designated column's suggested title for use in printouts and displays.|
|[https://docs.oracle.com/javase/7/docs/api/java/lang/String.html](https://docs.oracle.com/javase/7/docs/api/java/lang/String.html)|[https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#getColumnName(int)](https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#getColumnName(int))(int column)Get the designated column's name.|
|int|[https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#getColumnType(int)](https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#getColumnType(int))(int column)Retrieves the designated column's SQL type.|
|[https://docs.oracle.com/javase/7/docs/api/java/lang/String.html](https://docs.oracle.com/javase/7/docs/api/java/lang/String.html)|[https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#getColumnTypeName(int)](https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#getColumnTypeName(int))(int column)Retrieves the designated column's database-specific type name.|
|[https://docs.oracle.com/javase/7/docs/api/java/lang/String.html](https://docs.oracle.com/javase/7/docs/api/java/lang/String.html)|[https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#getSchemaName(int)](https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#getSchemaName(int))(int column)Get the designated column's table's schema.|
|[https://docs.oracle.com/javase/7/docs/api/java/lang/String.html](https://docs.oracle.com/javase/7/docs/api/java/lang/String.html)|[https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#getTableName(int)](https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#getTableName(int))(int column)Gets the designated column's table name.|
|boolean|[https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#isAutoIncrement(int)](https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#isAutoIncrement(int))(int column)Indicates whether the designated column is automatically numbered.|
|boolean|[https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#isCaseSensitive(int)](https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#isCaseSensitive(int))(int column)Indicates whether a column's case matters.|
|boolean|[https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#isDefinitelyWritable(int)](https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#isDefinitelyWritable(int))(int column)Indicates whether a write on the designated column will definitely succeed.|
|int|[https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#isNullable(int)](https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#isNullable(int))(int column)Indicates the nullability of values in the designated column.|
|boolean|[https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#isReadOnly(int)](https://docs.oracle.com/javase/7/docs/api/java/sql/ResultSetMetaData.html#isReadOnly(int))(int column)Indicates whether the designated column is definitely not writable.|

### _Exemple_

```java
ResultSet rs = stmt.executeQuery(query);
ResultSetMetaData rsmd = rs.getMetaData();
int nbCols = rsmd.getColumnCount();
System.out.println("This table contains" + nbCols + " columns.");
```


# Transactions

By default each query get immediately a result after the `execute` method being executed. This approach can be conflictual. If a query return an error by the half of his execution, this may cause some problems. To counter this, we can choose the manner to commit our queries (manually or automatically) via the method `setAutoCommit(boolean result)`. If an error occur during the process we have to rollback, we use then the `rollback()` method.

If several queries work on the same table this can cause validity problems. To protect yourself, we have to set the transaction isolation protocol. With the method `setTransactionIsolation(int valueoftheisolation)`.

|Name|Role|Value|
|---|---|---|
|Connection.TRANSACTION_READ_UNCOMMITTED|Does not guarantee anything.|1|
|Connection.TRANSACTION_READ_COMMITTED|Guarantees that a data has been committed previously by someone.|2|
|Connection.TRANSACTION_REPEATABLE_READ|Guarantees that the data cannot change if a second read is done in the same transaction.|4|
|Connection.TRANSACTION_SERIALIZABLE|If a transaction tries to do an operation not compatible with the first one, it is blocked.|8|

### _Exemple_

```java

Connection con = null;
try{
	con.setTransactionIsolation(Connection.TRANSACTION_REPEATABLE_READ);
	con.setAutoCommit(false);
	Statement stmt = con.createStatement();
	stmt.executeUpdate("UPDATE table SET column = 1");
	stmt.executeUpdate(query);
	con.commit();
	con.close();
}catch(Exception e){
	try{con.rollback()}catch(Exeption e2){}
	System.out.println(e.getMessage());
}finally{
	try{con.close()}catch(Exeption e3){}
}

```
