# Follow-Ups

*Note: The following are optional, unimplemented extensions.*

1. **How would you handle a distributed hotel management system across multiple properties?**
   - *Answer*: Introduce a `PropertyID` or `HotelID` to all entities. Use a partitioned database where data is sharded by `HotelID` since operations rarely cross properties.

2. **How would you implement late checkout fees automatically?**
   - *Answer*: Introduce a scheduled job (e.g., cron or an external scheduler) that scans active `Stay` records past the checkout time and automatically posts a `Charge` to their `Folio`.

3. **What happens if the power goes out or the system crashes during a check-in?**
   - *Answer*: Ensure database transactions are ACID compliant. The room assignment, stay creation, and key generation should be wrapped in a single database transaction. For physical keys, the key encoder must acknowledge success before committing the transaction.

4. **How would you handle group billing (e.g., a wedding party where one master folio pays for all rooms)?**
   - *Answer*: Introduce a `MasterFolio` or `GroupFolio` entity. Individual `Stay` records can have a pointer to the `MasterFolio` where all (or specific) charges are routed instead of their individual folios.
