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
-- Table structure for table `columns`
--

DROP TABLE IF EXISTS `columns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `columns` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) NOT NULL,
  `Coordinate` int NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `columns`
--

LOCK TABLES `columns` WRITE;
/*!40000 ALTER TABLE `columns` DISABLE KEYS */;
INSERT INTO `columns` VALUES (1,'WCL',0),(2,'Aardvark',1),(3,'Alder',3),(4,'Buzzard',5),(5,'Beech',7),(6,'Cormorant',9),(7,'Cedar',11),(8,'Duck',13),(9,'Dogwood',15),(10,'Eagle',17),(11,'Elm',19),(12,'Ferret',21),(13,'Fir',23),(14,'Gibbon',25),(15,'Gum',27),(16,'Haddock',29),(17,'Holly',31),(18,'Iguana',33),(19,'Ivy',35),(20,'Jackal',37),(21,'Juniper',39),(22,'Kracken',41),(23,'Knotweed',43),(24,'Lion',45),(25,'Larch',47),(26,'Mongoose',49),(27,'Maple',51),(28,'Nightingale',53),(29,'Nettle',55),(30,'Octopus',57),(31,'Olive',59),(32,'Pilchard',61),(33,'Pine',63),(34,'Quail',65),(35,'Quince',67),(36,'Raven',69),(37,'Ragweed',71),(38,'Squid',73),(39,'Sycamore',75),(40,'Tapir',77),(41,'Teasel',79),(42,'Unicorn',81),(43,'Umbrella',83),(44,'Vulture',85),(45,'Vervain',87),(46,'Walrus',89),(47,'Willow',91),(48,'Yak',93),(49,'Yew',95),(50,'Zebra',97),(51,'Zelkova',99),(52,'Amethyst',101),(53,'Anguish',103),(54,'Beryl',105),(55,'Bleak',107),(56,'Cobalt',109),(57,'Chagrin',111),(58,'Diamond',113),(59,'Despair',115),(60,'Emerald',117),(61,'Ennui',119),(62,'Flint',121),(63,'Fear',123),(64,'Gypsum',125),(65,'Gloom',127),(66,'Hessite',129),(67,'Horror',131),(68,'Ivory',133),(69,'Ire',135),(70,'Jet',137),(71,'Jaded',139),(72,'Kyanite',141),(73,'Killjoy',143),(74,'Lead',145),(75,'Lonely',147),(76,'Malachite',149),(77,'Malaise',151),(78,'Nickel',153),(79,'Nervous',155),(80,'Obsidian',157),(81,'Oppression',159),(82,'Pyrites',161),(83,'Pessimism',163),(84,'Quartz',165),(85,'Qualms',167),(86,'Ruby',169),(87,'Regret',171),(88,'Steel',173),(89,'Sorrow',175),(90,'Turquoise',177),(91,'Torment',179),(92,'Uranium',181),(93,'Unctuous',183),(94,'Vauxite',185),(95,'Vexation',187),(96,'Wulfenite',189),(97,'Woe',191),(98,'Yuksporite',193),(99,'Yearning',195),(100,'Zinc',197),(101,'Zestless',199),(102,'ECL',200);
/*!40000 ALTER TABLE `columns` ENABLE KEYS */;
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
