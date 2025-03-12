CREATE DATABASE foodies_restaurant;

USE foodies_restaurant;

CREATE TABLE Customer(
    Customer_Id INT PRIMARY KEY AUTO_INCREMENT,
    Customer_name VARCHAR(50),
    Email_Address VARCHAR(50),
    Phone_number VARCHAR(15)
);

INSERT INTO Customer(Customer_name, Email_Address, Phone_number) 
VALUES ("Sale", "sale867@gmail.com", "098766544"), 
       ("Maki", "maki123@gmail.com", "123456");
select * from Customer;
CREATE TABLE Reservation(
    Reservation_id INT PRIMARY KEY AUTO_INCREMENT,
    Customer_Id INT,
    FOREIGN KEY(Customer_Id) REFERENCES Customer(Customer_Id) ON DELETE CASCADE,
    Reservation_Date DATE NOT NULL,
    No_of_people INT,
    Reservation_Time TIME
);


INSERT INTO Reservation (Customer_Id, Reservation_Date, No_of_people, Reservation_Time) 
VALUES (1, "2025-02-03", 4, "14:00:00");

CREATE TABLE Order_Details(
    Order_Id INT PRIMARY KEY AUTO_INCREMENT,
    Customer_Id INT,
    FOREIGN KEY(Customer_Id) REFERENCES Customer(Customer_Id) ON DELETE CASCADE,
    Total_Amount DECIMAL(10,2), 
    Order_Date DATE,
    Order_Status VARCHAR(20) NOT NULL
);
select * from Order_Details;

INSERT INTO Order_Details(Customer_Id, Total_Amount, Order_Date, Order_Status) 
VALUES (1, 1200.00, "2025-02-04", "Pending");


CREATE TABLE Menu(
    Menu_Id INT PRIMARY KEY AUTO_INCREMENT,
    Item_name VARCHAR(40) NOT NULL,
    Item_price DECIMAL(10,2), 
    Item_Availability TINYINT(1)
);


INSERT INTO Menu(Item_name, Item_price, Item_Availability) 
VALUES ("pizza", 600.00, 1); 

select * from Menu;

CREATE TABLE Order_Items(
    Order_Item_Id INT PRIMARY KEY AUTO_INCREMENT,
    Order_Id INT,
    FOREIGN KEY(Order_Id) REFERENCES Order_Details(Order_Id) ON DELETE CASCADE,
    Menu_Id INT,
    FOREIGN KEY(Menu_Id) REFERENCES Menu(Menu_Id),
    Quantity INT DEFAULT 1 
);

select * from Order_Items;
INSERT INTO Order_Items(Order_Id, Menu_Id, Quantity) 
VALUES (1, 1, 2);

CREATE TABLE FAQs(
    FAQs_Id INT PRIMARY KEY AUTO_INCREMENT,
    Question_Text TEXT,
    Answer TEXT
);


SELECT C.Customer_Id, C.Customer_name, C.Email_Address, C.Phone_number,
       MAX(R.Reservation_id) AS Latest_Reservation_Id,
       MAX(R.Reservation_Date) AS Latest_Reservation_Date, 
       MAX(R.No_of_people) AS No_of_people, 
       MAX(R.Reservation_Time) AS Latest_Reservation_Time
FROM Customer C
LEFT JOIN Reservation R ON C.Customer_Id = R.Customer_Id
GROUP BY C.Customer_Id;

SELECT C.Customer_Id, C.Customer_name, C.Email_Address, C.Phone_number,
       O.Order_Id, O.Total_Amount, O.Order_Date, O.Order_Status 
FROM Customer C
JOIN Order_Details O ON C.Customer_Id = O.Customer_Id;

SELECT OI.Order_Id, OI.Menu_Id, OI.Quantity, (OI.Quantity * M.Item_price) AS Total_Price
FROM Order_Items OI
JOIN Menu M ON OI.Menu_Id = M.Menu_Id;





