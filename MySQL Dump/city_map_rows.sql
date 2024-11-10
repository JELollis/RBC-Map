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
-- Table structure for table `rows`
--

DROP TABLE IF EXISTS `rows`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rows` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) NOT NULL,
  `Coordinate` int NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rows`
--

LOCK TABLES `rows` WRITE;
/*!40000 ALTER TABLE `rows` DISABLE KEYS */;
INSERT INTO `rows` VALUES (1,'NCL',0),(2,'1st',1),(3,'2nd',3),(4,'3rd',5),(5,'4th',7),(6,'5th',9),(7,'6th',11),(8,'7th',13),(9,'8th',15),(10,'9th',17),(11,'10th',19),(12,'11th',21),(13,'12th',23),(14,'13th',25),(15,'14th',27),(16,'15th',29),(17,'16th',31),(18,'17th',33),(19,'18th',35),(20,'19th',37),(21,'20th',39),(22,'21st',41),(23,'22nd',43),(24,'23rd',45),(25,'24th',47),(26,'25th',49),(27,'26th',51),(28,'27th',53),(29,'28th',55),(30,'29th',57),(31,'30th',59),(32,'31st',61),(33,'32nd',63),(34,'33rd',65),(35,'34th',67),(36,'35th',69),(37,'36th',71),(38,'37th',73),(39,'38th',75),(40,'39th',77),(41,'40th',79),(42,'41st',81),(43,'42nd',83),(44,'43rd',85),(45,'44th',87),(46,'45th',89),(47,'46th',91),(48,'47th',93),(49,'48th',95),(50,'49th',97),(51,'50th',99),(52,'51st',101),(53,'52nd',103),(54,'53rd',105),(55,'54th',107),(56,'55th',109),(57,'56th',111),(58,'57th',113),(59,'58th',115),(60,'59th',117),(61,'60th',119),(62,'61st',121),(63,'62nd',123),(64,'63rd',125),(65,'64th',127),(66,'65th',129),(67,'66th',131),(68,'67th',133),(69,'68th',135),(70,'69th',137),(71,'70th',139),(72,'71st',141),(73,'72nd',143),(74,'73rd',145),(75,'74th',147),(76,'75th',149),(77,'76th',151),(78,'77th',153),(79,'78th',155),(80,'79th',157),(81,'80th',159),(82,'81st',161),(83,'82nd',163),(84,'83rd',165),(85,'84th',167),(86,'85th',169),(87,'86th',171),(88,'87th',173),(89,'88th',175),(90,'89th',177),(91,'90th',179),(92,'91st',181),(93,'92nd',183),(94,'93rd',185),(95,'94th',187),(96,'95th',189),(97,'96th',191),(98,'97th',193),(99,'98th',195),(100,'99th',197),(101,'100th',199),(102,'SCL',200);
/*!40000 ALTER TABLE `rows` ENABLE KEYS */;
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
