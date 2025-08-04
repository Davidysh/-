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
4.枚举类型ENUM以及集合类型SET ##区别ENUM可选择一个预定义的集合
## 4.创建数据表  
`CREATE TABLE 'yourtablename'( ` ##注意括号是()   
    `column1 datatype, `   
   `column2 datatype,`    
    ···
`);`  
实例：(创建一个学生TABLE，学号/id（主键）,姓名，性别，入学时间，年龄)  
`CREATE TABLE Student(`  
    `id SMALL INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,`  ##AUTO_INCREMENT用于创建一个自增长的列  
    `name CHAR(10) NOT NULL, ` 
    `gender CHAR(1) NOT NULL,`  ##存储M/F 或者是BIT储存(0/1)  
    `enrollment DATE NOT NULL,`  
    `age TINYINT NOT NULL, `  
`);`
## 5.删除数据表
`DROP TABLE [IF EXISTS]'yourtablename';`  
仅删除表中数据`TRUNCATE TABLE 'yourtablename'`
## 6.插入数据
`INSERT INTO 'yourtablename'(column1,column2,cloumn3,...)`  
`VALUES(value1,value2,value3,...)`
实例：(插入两个学生信息)
`INSERT INTO Student`
`VALUES(NULL,'张三'，'F',2025-08-04,18)`##NULL 是用于自增长列的占位符，表示系统将为 id 列生成一个唯一的值。  
## 7.查询数据（重点中的重点）
`SELECT column1, column2,`  
`FROM table_name`  
`[WHERE condition]`  ##条件判断(如筛选掉一些NULL以及空值)  
`[ORDER BY column_name [ASC | DESC]]`  ##排序规则默认ASC升序  
`[LIMIT number];`  ##查询条数  
实例：基于你创建的Student表，编写一个SQL查询，找出所有年龄大于等于18岁的女学生，并按入学时间从新到旧排序显示。  
`SELECT name,age,gender,enrollment`  
`FROM Student`  
`WHERE age >=18 and gender = 'F'`  
`ORDER BY enrollment DESC`  
执行完搜索后进行内存的释放(在pyth中可以使用with OR cursor.close()/conn.close())先关闭游标再关闭连接
## 8.WHERE字句
1.比较 同编程‘>,<,>=,<=,<>,!=’  
2.组合 and/or  
3.模糊匹配 LIKE  
4.非 NOT;在指定集合中 IN;在指定范围中BETWEEN;是否为空 IS NULL以及IS NOT NULL  
## 9.UPDATE更新
`UPDATE table_name`  
`SET column1=value1,column2=value2`  
`[WHERE condition]`  
实例：假设有一个实表结构如下  
CREATE TABLE StudentScores (  
    student_id INT PRIMARY KEY,  
    student_name VARCHAR(50) NOT NULL,  
    math_score INT,  
    english_score INT,  
    science_score INT,  
    class VARCHAR(20),  
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
);  
题目要求
1.基础更新：将学生"王五"的数学成绩(math_score)从78分更新为85分  
UPDATE StudentScores  
SET math_score = 85, update_time = CURRENT_TIMESTAMP   
WHERE student_name = '王五'; 

2.多列更新：将"三年2班"所有学生的英语成绩(english_score)增加5分   
UPDATE StudentScores  
SET english_score = english_score + 5, update_time = CURRENT_TIMESTAMP  
WHERE class = '三年2班';  

3.条件更新：将科学成绩(science_score)低于70分的学生，科学成绩统一设置为70分  
UPDATE StudentScores  
SET science_score = 70, update_time = CURRENT_TIMESTAMP  
WHERE science_score < 70;  

4.综合更新：将"三年1班"且数学成绩高于80分的学生的英语成绩减少3分  
UPDATE StudentScores  
SET english_score = english_score - 3, update_time = CURRENT_TIMESTAMP  
WHERE math_score > 70 AND class = '三年1班';

5.带计算的更新：将所有学生的数学成绩更新为原数学成绩的105%(四舍五入取整)  
UPDATE StudentScores  
SET math_score = ROUND(math_score*1.05), update_time = CURRENT_TIMESTAMP;  

进阶挑战  
6.使用子查询更新：将科学成绩高于班级平均科学成绩的学生的英语成绩增加2分  
<!-- UPDATE StudentScores  
SET english_score = english_score + 2, update_time = CURRENT_TIMESTAMP  
WHERE science_score > AVG(science_score); ##WHERE中不能使用聚合函数除非配合GROUP BY-->
UPDATE StudentScores s  
SET english_score = english_score + 2,  
    update_time = CURRENT_TIMESTAMP  
WHERE science_score > (  
    SELECT AVG(science_score)   
    FROM StudentScores   
    WHERE class = s.class ##班级隔离  
);

7.同时更新多个表：假设有另一个表 ClassInfo 记录班级平均分，请同时更新 StudentScores和 ClassInfo 表  
！！！暂时放置

## 10.删除数据
`DELECT FROM table_name`  
`WHERE codition;`  
实例:假设有两个表
订单表(Orders)CREATE TABLE Orders (  
    order_id INT PRIMARY KEY,  
    customer_id INT NOT NULL,  
    order_date DATE NOT NULL,  
    total_amount DECIMAL(10,2) NOT NULL,  
    status VARCHAR(20) CHECK(status IN ('已完成','处理中','已取消'))
);  
客户表(Customers)CREATE TABLE Customers (  
    customer_id INT PRIMARY KEY,  
    customer_name VARCHAR(100) NOT NULL,  
    registration_date DATE NOT NULL,  
    vip_status VARCHAR(10) CHECK(vip_status IN ('普通','白银','黄金','铂金'))
);  
问题要求
1.基础删除：删除所有"已取消"状态的订单  
DELECT FROM Orders  WHERE status = '已取消';

2.子查询删除：删除所有从未下过订单的客户记录  
DELETE FROM Customers  
WHERE customer_id NOT IN (  
    SELECT DISTINCT customer_id  ##DISTINCT 去重一个客户可能有很多订单  
    FROM Orders  
);

3.关联条件删除：删除VIP等级为"普通"且最近一年内没有任何订单的客户  
DELECT FROM Customers   
WHERE vip_status = '普通' AND customer_id NOT IN(SELECT customer_id FROM Orders WHERE oder_date <= DATE_SUB(CURRENT_DATE, INTERVAL 1 YEAR))  
##DATE_SUB((date, INTERVAL expr type))函数用于从日期中减去指定的时间间隔  

4.复杂条件删除：删除总金额低于该客户平均订单金额的订单  
DELECT FROM Orders O1   
WHERE total_amount < (  
    SELECT AVG(total_amount) FROM Orders O2  
    WHERE O1.customer_id = O2.customer_id);

5.多表关联删除：删除所有订单总金额低于1000的VIP客户的订单记录  
<!-- DELETE FROM Orders
WHERE customer_id IN (  
    SELECT c.customer_id  
    FROM Customers c  
    JOIN (  
        SELECT customer_id, SUM(total_amount) as customer_total  
        FROM Orders  
        GROUP BY customer_id  
    ) o ON c.customer_id = o.customer_id  
    WHERE c.vip_status != '普通'  
    AND o.customer_total < 1000  
); ##在研究研究-->

6.存在性检查删除：删除那些客户已经不存在于客户表中的订单记录
DELECT FROM Orders
WHERE customer_id NOT IN (
    SELECT customer_id
    FROM Cutomers
);

## 11.模糊查询LIKE子句
使用%代表任意字符,类似*  
`SELECT column1, column2, ...`  
`FROM table_name`  
`WHERE column_name LIKE pattern;`  
通配符  
%: SELECT * FROM Students WHERE name LIKE '刘%';
_: SELECT * FROM Students WHERE name LIKE '_勇%';

## 12.UNION操作符
UNION 操作符用于连接两个以上的 SELECT 语句的结果组合到一个结果集合，并去除重复的行。
UNION 操作符必须由两个或多个 SELECT 语句组成，每个 SELECT 语句的列数和对应位置的数据类型必须相同。  
`SELECT column1, column2, ...`  `FROM table1`  `WHERE condition1`  
`UNION`  
`SELECT column1, column2, ...`  `FROM table2`  `WHERE condition2`  
`[ORDER BY column1, column2, ...];`  
UNION 只会选取不同的值,UNION ALL 来选取重复的值。

## 13.ORDER BY(排序) 语句
`SELECT column1, column2, ...`  
`FROM table_name`  
`ORDER BY column1(/1) [ASC | DESC], column2(/2) [ASC | DESC], ...;`  
会按照ORDER BY后排序要求的先后顺序依次排序(如按column1升序再按column2降序)
也可以用数字代替column名字  
实例:  
产品表CREATE TABLE products (  
    product_id INT PRIMARY KEY,  
    product_name VARCHAR(200) NOT NULL,  
    category VARCHAR(50),  
    price DECIMAL(10,2),  
    stock_quantity INT,  
    sales_volume INT,  
    last_restock_date DATE  
);  
订单表CREATE TABLE orders (  
    order_id INT PRIMARY KEY,  
    customer_id INT,  
    order_date DATE,  
    total_amount DECIMAL(12,2),  
    shipping_country VARCHAR(50),  
    payment_method VARCHAR(50),  
    order_status VARCHAR(20)  
);
1.按价格排序：查询所有产品信息，按价格从高到低排序，如果价格相同，则按库存数量从低到高排序。  
SELECT * FROM products ORDER BY price DESC,stock_quantity ASC  

2.订单日期排序：查询订单表中所有状态为"Completed"的订单，按订单日期从新到旧排序，如果日期相同，则按订单金额从高到低排序。  
SELECT * FROM orders,products WHERE oder_status = 'Completed' ORDER BY order_date DESC,price DESC

3.多条件排序：查询库存少于50件的产品，按类别（Category）升序排列，同一类别下按销量（Sales Volume）降序排列。  
SELECT * FROM products WHERE stock_quantity < 50 ORDER BY Category, sales_volume DESC

4.混合排序：查询最近30天内补货的产品，按补货日期（Last Restock Date）降序排列，相同日期的按价格升序排列。
SELECT * FROM products WHERE last_restock_date < DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY) ORDER BY last_restock_date DESC, price

5.动态排序：查询所有订单，要求按订单状态（Order Status）排序，排序规则为：  
"Shipped" 状态的订单排在最前面  
"Processing" 状态的订单排在中间  
"Cancelled" 状态的订单排在最后  
同一状态下的订单按订单日期降序排列。 
SELECT * FROM orders 
ORDER BY 
    CASE order_status  
      WHEN 'Shipped' THEN 1   
      WHEN 'Processing' THEN 2  
      WHEN 'Cancelled' THEN 3 
      ELSE THEN 4
    END,
    order_date DESC;

6.NULL值处理：查询所有产品，按最后补货日期（Last Restock Date）排序，但从未补货的产品（NULL值）排在最后，其余按日期降序排列。
SELECT * FROM products ORDER BY CASE last_restock_date is NULL THEN 1 ELSE 0 END, last_restock_date DESC;
SELECT * FROM products ORDER BY CASE last_restock_date DESC NULL LAST;  # 8.0.16版本以后支持

7.结合聚合函数排序：查询每个产品类别（Category）的平均价格，并按平均价格降序排列，如果平均价格相同，则按类别名称升序排列。
SELECT AVG(price) AS avg_price FROM products  
GROUP BY category  
ORDER BY avg_price

8.多表联合排序：查询订单表中金额最高的前10笔订单，并关联产品表，显示订单ID、订单日期、总金额、支付方式，按总金额降序排列，相同金额的按订单日期升序排列。
补充表CREATE TABLE order_items (  
    item_id INT PRIMARY KEY,  
    order_id INT,  
    product_id INT,  
    quantity INT,  
    unit_price DECIMAL(10,2),  
    FOREIGN KEY (order_id) REFERENCES orders(order_id),  
    FOREIGN KEY (product_id) REFERENCES products(product_id)  
);

SELECT o.order_id,o.order_date,o.total_amount,o.payment_method,p.product_name,p.category 
FROM orders o  
JOIN order_items oi ON o.order_id = oi.order_id  
JOIN products p ON oi.product_id = p.product_id  
ORDER BY o.total_amount DESC, o.order_date ASC  
LIMIT 10;


## 14.GROUP BY(分组)语句
`SELECT column1, aggregate_function(column2)`  
`FROM table_name`  
`WHERE condition`  
`GROUP BY column1;`  
TIPS:  
+ GROUP BY 子句通常与聚合函数一起使用，因为分组后需要对每个组进行聚合操作。
+ SELECT 子句中的列通常要么是分组列，要么是聚合函数的参数。
+ 可以使用多个列进行分组，只需在 GROUP BY 子句中用逗号分隔列名即可。
##  表定义
表定义  
客户表(customers)CREATE TABLE customers (  
    customer_id INT PRIMARY KEY,  
    customer_name VARCHAR(100) NOT NULL,  
    email VARCHAR(100) UNIQUE,  
    country VARCHAR(50),  
    registration_date DATE,  
    vip_status BOOLEAN DEFAULT FALSE  
);  
产品表(products)CREATE TABLE products (  
    product_id INT PRIMARY KEY,  
    product_name VARCHAR(200) NOT NULL,  
    category VARCHAR(50),  
    price DECIMAL(10,2),  
    stock_quantity INT,  
    supplier_country VARCHAR(50)  
);  
订单表(orders)CREATE TABLE orders (  
    order_id INT PRIMARY KEY,  
    customer_id INT,  
    order_date DATE,  
    total_amount DECIMAL(12,2),  
    shipping_country VARCHAR(50),  
    payment_method VARCHAR(50),  
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)  
);  
订单明细表(order_items)CREATE TABLE order_items (  
    item_id INT PRIMARY KEY,  
    order_id INT,  
    product_id INT,  
    quantity INT,  
    unit_price DECIMAL(10,2),  
    FOREIGN KEY (order_id) REFERENCES orders(order_id),  
    FOREIGN KEY (product_id) REFERENCES products(product_id)  
);  
## 15.连接使用
***INNER JOIN/JOIN***  
`SELECT column1, column2, ...`  
`FROM table1`  
`INNER JOIN table2 ON table1.column_name = table2.column_name;`
实例:
1.基本INNER JOIN查询查询所有订单信息及对应的客户姓名和邮箱  
SELECT o.order_id, o.order_date, o.total_amount,   
       o.payment_method, c.customer_name, c.email  
FROM orders o  
INNER JOIN customers c ON o.customer_id = c.customer_id;  

2.多表INNER JOIN查询查询包含产品名称的完整订单明细（需连接orders、order_items和products表）
SELECT c.customer_id, c.customer_name,   
p.product_id, p.product_name, p.price, p.supplier_country,   
o1.order_id, o1.payment_method, o1.total_amount,   
o2.quantity, o2.item_id,   
ROUND(o2.quantity * o2.unit_price) AS subtotal  
FROM orders o1
INNER JOIN customers c ON c.customer_id = o1.customer_id
INNER JOIN order_items o2 ON o2.order_id = o1.order_id
INNER JOIN products p ON p.product_id = o2.product_id

3.INNER JOIN与聚合函数统计每个客户的订单总数量和总消费金额
SELCET c.customer_name, o2.quantity,  
SUM(o2.quantity * o2.unit_price) AS subtotal  
FROM orders o1
INNER JOIN customers c ON c.customer_id = o1.customer_id  
INNER JOIN order_items o2 ON o2.order_id = o1.order_id  
GROUP BY c.customer_id, c.customer_name  
ORDER BY total_spent DESC;

4.INNER JOIN与条件筛选查询2023年来自美国(US)且单笔金额超过$100的订单详情最后按下单时间进行排序
SELECT o1.order_id, o1.total_amount,  
p.product_id, p.product_name,  
c.customer_id, c.customer_name,  
o2.quantity, o2.item_id,   
ROUND(o2.quantity * o2.unit_price, 2) AS subtotal 
FROM orders o1   
INNER JOIN customers c ON c.customer_id = o1.customer_id  
INNER JOIN order_items o2 ON o2.order_id = o1.order_id  
INNER JOIN products p ON p.product_id = o2.product_id  
WHERE o1.shipping_country = 'US'  
AND (o2.quantity * o2.unit_price) > 100   ## 不能使用别名
AND o1.order_date >= '2023-01-01'   
AND o1.order_date <= '2023-12-31'
ORDER BY o1.order_date DESC;

5.INNER JOIN与排序分页查询消费金额最高的5位客户信息及其订单总金额


***LEFT JOIN***  
`SELECT column1, column2, ...`  
`FROM table1`  
`LEFT JOIN table2 ON table1.column_name = table2.column_name;`
返回左表所有行，并包括右表中匹配的行，如果右表中没有匹配的行返回NULL

***RIGHT JOIN***  
`SELECT column1, column2, ...`  
`FROM table1`  
`RIGHT JOIN table2 ON table1.column_name = table2.column_name;`  
同左连接

