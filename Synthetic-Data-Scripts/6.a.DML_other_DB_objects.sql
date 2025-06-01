CREATE VIEW `view_payment_data` AS
SELECT payment.paymentNumber,
       payment.orderNumber,
       payment.paymentDate,
       payment.amount,
       payment.paymentMethodID,
       customerorder.orderDate,
       customerorder.requiredDate,
       customerorder.dispatchDate,
       customerorder.orderStatusID,
       customerorder.customerNumber,
       customer.customerName,
       customer.contactFirstName,
       customer.contactLastName,
       customer.phone,
       customer.addressLine1,
       customer.addressLine2,
       customer.postalCode,
       customer.county,
       customer.subCounty,
       customer.salesRepEmployeeNumber,
       orderstatus.status,
       paymentmethod.paymentMethod
FROM payment
         INNER JOIN customerorder ON payment.orderNumber = customerorder.orderNumber
         INNER JOIN customer ON customerorder.customerNumber = customer.customerNumber
         INNER JOIN orderstatus ON customerorder.orderStatusID = orderstatus.orderStatusID
         INNER JOIN paymentmethod ON payment.paymentMethodID = paymentmethod.paymentMethodID
ORDER BY payment.paymentDate;