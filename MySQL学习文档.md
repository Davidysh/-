# MySQL学习记录文档
## 1.创建数据库  
'''   
`CREATE DATABASE 'mydatabase'`  
`CHARACTER SET utf8mb4`  
`COLLATE utf8mb4_general_ci;`  ##COLLATE是设定排序的规则，如ci指的是大小写无关  
'''  
如果不知道数据库是否已经创建`CREATE DATABASE IF NOT EXISTS mydatabase;`  
或者`SHOW DATABASE LIKE 'database'`
## 2.删除数据库
`DROP DATABASE 'database'`  
如果不知道数据库是否已经存在可以加上 IF EXISTS 
## 3.数据类型
1.[数值类型](/datatype.png)  
2.[时间类型](/Timetype.png)  
3.[字符串类型](/Stringtype.png)  
4.枚举类型ENUM以及集合类型SET ##区别ENUM只能