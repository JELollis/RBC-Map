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
-- Table structure for table `guilds`
--

DROP TABLE IF EXISTS `guilds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `guilds` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) NOT NULL,
  `Column` varchar(255) NOT NULL,
  `Row` varchar(255) NOT NULL,
  `next_update` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=326 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guilds`
--

LOCK TABLES `guilds` WRITE;
/*!40000 ALTER TABLE `guilds` DISABLE KEYS */;
INSERT INTO `guilds` VALUES (1,'Allurists Guild 1','Raven','1st','2024-11-10 00:00:04'),(2,'Allurists Guild 2','Beech','16th','2024-11-10 00:00:04'),(3,'Allurists Guild 3','Octopus','24th','2024-11-10 00:00:04'),(4,'Empaths Guild 1','Pessimism','77th','2024-11-10 00:00:04'),(5,'Empaths Guild 2','Teasel','69th','2024-11-10 00:00:04'),(6,'Empaths Guild 3','Larch','14th','2024-11-10 00:00:04'),(7,'Immolators Guild 1','Raven','92nd','2024-11-10 00:00:04'),(8,'Immolators Guild 2','Cobalt','Northern City Limits','2024-11-10 00:00:04'),(9,'Immolators Guild 3','Gibbon','67th','2024-11-10 00:00:04'),(10,'Thieves Guild 1','Dogwood','12th','2024-11-10 00:00:04'),(11,'Thieves Guild 2','Squid','49th','2024-11-10 00:00:04'),(12,'Thieves Guild 3','Raven','28th','2024-11-10 00:00:04'),(13,'Travellers Guild 1','Gypsum','41st','2024-11-10 00:00:04'),(14,'Travellers Guild 2','Western City Limits','58th','2024-11-10 00:00:04'),(15,'Travellers Guild 3','Uranium','40th','2024-11-10 00:00:04'),(16,'Peacekkeepers Mission 1','Emerald','67th','2024-11-10 00:00:04'),(17,'Peacekkeepers Mission 2','Unicorn','33rd','2024-11-10 00:00:04'),(18,'Peacekkeepers Mission 3','Emerald','33rd','2024-11-10 00:00:04');
/*!40000 ALTER TABLE `guilds` ENABLE KEYS */;
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
