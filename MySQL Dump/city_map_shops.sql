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
-- Table structure for table `shops`
--

DROP TABLE IF EXISTS `shops`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shops` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) NOT NULL,
  `Column` varchar(255) NOT NULL,
  `Row` varchar(255) NOT NULL,
  `next_update` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shops`
--

LOCK TABLES `shops` WRITE;
/*!40000 ALTER TABLE `shops` DISABLE KEYS */;
INSERT INTO `shops` VALUES (1,'Ace Porn','NA','NA','2024-11-10 10:40:04'),(2,'Checkers Porn Shop','NA','NA','2024-11-10 10:40:04'),(3,'Dark Desires','NA','NA','2024-11-10 10:40:04'),(4,'Discount Magic','NA','NA','2024-11-10 10:40:04'),(5,'Discount Potions','NA','NA','2024-11-10 10:40:04'),(6,'Discount Scrolls','NA','NA','2024-11-10 10:40:04'),(7,'Herman\'s Scrolls','Fear','21st','2024-11-10 10:40:04'),(8,'Interesting Times','NA','NA','2024-11-10 10:40:04'),(9,'McPotions','NA','NA','2024-11-10 10:40:04'),(10,'Paper and Scrolls','NA','NA','2024-11-10 10:40:04'),(11,'Potable Potions','NA','NA','2024-11-10 10:40:04'),(12,'Potion Distillery','NA','NA','2024-11-10 10:40:04'),(13,'Potionworks','NA','NA','2024-11-10 10:40:04'),(14,'Reversi Porn','NA','NA','2024-11-10 10:40:04'),(15,'Scrollmania','NA','NA','2024-11-10 10:40:04'),(16,'Scrolls \'n\' Stuff','NA','NA','2024-11-10 10:40:04'),(17,'Scrolls R Us','NA','NA','2024-11-10 10:40:04'),(18,'Scrollworks','NA','NA','2024-11-10 10:40:04'),(19,'Silver Apothecary','NA','NA','2024-11-10 10:40:04'),(20,'Sparks','NA','NA','2024-11-10 10:40:04'),(21,'Spinners Porn','NA','NA','2024-11-10 10:40:04'),(22,'The Magic Box','NA','NA','2024-11-10 10:40:04'),(23,'The Potion Shoppe','NA','NA','2024-11-10 10:40:04'),(24,'White Light','NA','NA','2024-11-10 10:40:04'),(25,'Ye Olde Scrolles','NA','NA','2024-11-10 10:40:04');
/*!40000 ALTER TABLE `shops` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-09 18:40:58
