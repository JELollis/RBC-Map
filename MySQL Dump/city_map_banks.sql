CREATE DATABASE  IF NOT EXISTS `city_map` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `city_map`;
-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: city_map
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `banks`
--

DROP TABLE IF EXISTS `banks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `banks` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Column` varchar(255) NOT NULL,
  `Row` varchar(255) NOT NULL,
  `Name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `idx_column_row` (`Column`,`Row`)
) ENGINE=InnoDB AUTO_INCREMENT=590 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `banks`
--

LOCK TABLES `banks` WRITE;
/*!40000 ALTER TABLE `banks` DISABLE KEYS */;
INSERT INTO `banks` VALUES (1,'Cedar','1st','OmniBank'),(2,'Despair','1st','OmniBank'),(3,'Uranium','1st','OmniBank'),(4,'Fir','2nd','OmniBank'),(5,'Oppression','2nd','OmniBank'),(6,'Kracken','3rd','OmniBank'),(7,'Dogwood','4th','OmniBank'),(8,'Yew','4th','OmniBank'),(9,'Malaise','4th','OmniBank'),(10,'Flint','5th','OmniBank'),(11,'Ivory','5th','OmniBank'),(12,'Kyanite','6th','OmniBank'),(13,'Kracken','7th','OmniBank'),(14,'Larch','7th','OmniBank'),(15,'Steel','7th','OmniBank'),(16,'Olive','9th','OmniBank'),(17,'Sorrow','9th','OmniBank'),(18,'Quail','10th','OmniBank'),(19,'Squid','10th','OmniBank'),(20,'Nervous','10th','OmniBank'),(21,'Pyrites','10th','OmniBank'),(22,'Raven','11th','OmniBank'),(23,'Tapir','11th','OmniBank'),(24,'Unicorn','11th','OmniBank'),(25,'Lead','11th','OmniBank'),(26,'Malachite','11th','OmniBank'),(27,'Quail','12th','OmniBank'),(28,'Buzzard','13th','OmniBank'),(29,'Kracken','13th','OmniBank'),(30,'Bleak','14th','OmniBank'),(31,'Knotweed','15th','OmniBank'),(32,'Raven','15th','OmniBank'),(33,'Fear','15th','OmniBank'),(34,'Gypsum','15th','OmniBank'),(35,'Juniper','16th','OmniBank'),(36,'Sycamore','16th','OmniBank'),(37,'Amethyst','16th','OmniBank'),(38,'Kracken','18th','OmniBank'),(39,'Quail','18th','OmniBank'),(40,'Ruby','18th','OmniBank'),(41,'Emerald','19th','OmniBank'),(42,'Pessimism','19th','OmniBank'),(43,'Juniper','20th','OmniBank'),(44,'Umbrella','20th','OmniBank'),(45,'Ennui','20th','OmniBank'),(46,'Lead','21st','OmniBank'),(47,'Zelkova','23rd','OmniBank'),(48,'Chagrin','23rd','OmniBank'),(49,'Torment','23rd','OmniBank'),(50,'Unctuous','23rd','OmniBank'),(51,'Squid','24th','OmniBank'),(52,'Pyrites','24th','OmniBank'),(53,'Vexation','24th','OmniBank'),(54,'Jaded','25th','OmniBank'),(55,'Beech','26th','OmniBank'),(56,'Quail','26th','OmniBank'),(57,'Octopus','27th','OmniBank'),(58,'Beryl','28th','OmniBank'),(59,'Qualms','28th','OmniBank'),(60,'Torment','28th','OmniBank'),(61,'Knotweed','29th','OmniBank'),(62,'Anguish','30th','OmniBank'),(63,'Ragweed','31st','OmniBank'),(64,'Ire','31st','OmniBank'),(65,'Steel','31st','OmniBank'),(66,'Torment','31st','OmniBank'),(67,'Ferret','32nd','OmniBank'),(68,'Malachite','32nd','OmniBank'),(69,'Larch','33rd','OmniBank'),(70,'Kracken','34th','OmniBank'),(71,'Maple','34th','OmniBank'),(72,'Gloom','34th','OmniBank'),(73,'Quail','36th','OmniBank'),(74,'Malaise','36th','OmniBank'),(75,'Obsidian','36th','OmniBank'),(76,'Duck','37th','OmniBank'),(77,'Nettle','37th','OmniBank'),(78,'Amethyst','37th','OmniBank'),(79,'Flint','37th','OmniBank'),(80,'Beech','39th','OmniBank'),(81,'Chagrin','39th','OmniBank'),(82,'Hessite','39th','OmniBank'),(83,'Alder','40th','OmniBank'),(84,'Quail','41st','OmniBank'),(85,'Tapir','41st','OmniBank'),(86,'Pine','42nd','OmniBank'),(87,'Ire','42nd','OmniBank'),(88,'Jackal','43rd','OmniBank'),(89,'Vulture','43rd','OmniBank'),(90,'Unctuous','43rd','OmniBank'),(91,'Pilchard','44th','OmniBank'),(92,'Pine','44th','OmniBank'),(93,'Pessimism','44th','OmniBank'),(94,'Woe','44th','OmniBank'),(95,'Kracken','45th','OmniBank'),(96,'Yak','45th','OmniBank'),(97,'Flint','45th','OmniBank'),(98,'Ruby','45th','OmniBank'),(99,'Haddock','46th','OmniBank'),(100,'Cobalt','46th','OmniBank'),(101,'Flint','47th','OmniBank'),(102,'Kracken','48th','OmniBank'),(103,'Quince','48th','OmniBank'),(104,'Jaded','48th','OmniBank'),(105,'Sorrow','48th','OmniBank'),(106,'Uranium','48th','OmniBank'),(107,'Horror','49th','OmniBank'),(108,'Malaise','50th','OmniBank'),(109,'Cedar','52nd','OmniBank'),(110,'Haddock','52nd','OmniBank'),(111,'Ire','53rd','OmniBank'),(112,'Ragweed','56th','OmniBank'),(113,'Qualms','57th','OmniBank'),(114,'Quail','58th','OmniBank'),(115,'Horror','59th','OmniBank'),(116,'Pilchard','60th','OmniBank'),(117,'Teasel','60th','OmniBank'),(118,'Quince','61st','OmniBank'),(119,'Eagle','64th','OmniBank'),(120,'Steel','64th','OmniBank'),(121,'Beryl','65th','OmniBank'),(122,'Teasel','66th','OmniBank'),(123,'Haddock','67th','OmniBank'),(124,'Nettle','67th','OmniBank'),(125,'Vauxite','68th','OmniBank'),(126,'Ivy','70th','OmniBank'),(127,'Regret','70th','OmniBank'),(128,'Octopus','71st','OmniBank'),(129,'Gloom','71st','OmniBank'),(130,'Ivory','71st','OmniBank'),(131,'Jaded','71st','OmniBank'),(132,'Haddock','74th','OmniBank'),(133,'Quail','74th','OmniBank'),(134,'Zinc','74th','OmniBank'),(135,'Despair','75th','OmniBank'),(136,'Quartz','75th','OmniBank'),(137,'Qualms','75th','OmniBank'),(138,'Yearning','75th','OmniBank'),(139,'Hessite','76th','OmniBank'),(140,'WCL','77th','OmniBank'),(141,'Duck','77th','OmniBank'),(142,'Octopus','77th','OmniBank'),(143,'Mongoose','78th','OmniBank'),(144,'Unicorn','78th','OmniBank'),(145,'Ennui','78th','OmniBank'),(146,'Ivy','79th','OmniBank'),(147,'Mongoose','79th','OmniBank'),(148,'Raven','79th','OmniBank'),(149,'Obsidian','79th','OmniBank'),(150,'Alder','80th','OmniBank'),(151,'Cedar','80th','OmniBank'),(152,'Lion','80th','OmniBank'),(153,'Umbrella','80th','OmniBank'),(154,'Cobalt','81st','OmniBank'),(155,'Aardvark','82nd','OmniBank'),(156,'Vulture','82nd','OmniBank'),(157,'Yak','82nd','OmniBank'),(158,'Maple','84th','OmniBank'),(159,'Willow','84th','OmniBank'),(160,'Maple','85th','OmniBank'),(161,'Woe','85th','OmniBank'),(162,'Malachite','87th','OmniBank'),(163,'Pessimism','87th','OmniBank'),(164,'Haddock','88th','OmniBank'),(165,'Cobalt','88th','OmniBank'),(166,'Lead','88th','OmniBank'),(167,'Eagle','89th','OmniBank'),(168,'Gloom','89th','OmniBank'),(169,'Oppression','89th','OmniBank'),(170,'Ferret','90th','OmniBank'),(171,'Emerald','90th','OmniBank'),(172,'Gloom','90th','OmniBank'),(173,'Pyrites','90th','OmniBank'),(174,'Larch','91st','OmniBank'),(175,'Mongoose','91st','OmniBank'),(176,'Anguish','91st','OmniBank'),(177,'Vauxite','91st','OmniBank'),(178,'Teasel','92nd','OmniBank'),(179,'Yearning','92nd','OmniBank'),(180,'Cormorant','93rd','OmniBank'),(181,'Lonely','93rd','OmniBank'),(182,'Nickel','93rd','OmniBank'),(183,'Uranium','93rd','OmniBank'),(184,'Yak','94th','OmniBank'),(185,'Holly','96th','OmniBank'),(186,'Ire','97th','OmniBank'),(187,'Uranium','97th','OmniBank'),(188,'Elm','98th','OmniBank'),(189,'Juniper','98th','OmniBank'),(190,'Raven','98th','OmniBank'),(191,'Olive','99th','OmniBank'),(192,'Amethyst','99th','OmniBank'),(193,'Emerald','99th','OmniBank');
/*!40000 ALTER TABLE `banks` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-09 18:40:59
