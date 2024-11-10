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
-- Table structure for table `taverns`
--

DROP TABLE IF EXISTS `taverns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `taverns` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Column` varchar(255) NOT NULL,
  `Row` varchar(255) NOT NULL,
  `Name` varchar(255) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `idx_column_row` (`Column`,`Row`)
) ENGINE=InnoDB AUTO_INCREMENT=97 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `taverns`
--

LOCK TABLES `taverns` WRITE;
/*!40000 ALTER TABLE `taverns` DISABLE KEYS */;
INSERT INTO `taverns` VALUES (1,'Ferret','44th','Miller\'s Tavern'),(2,'Gibbon','44th','The Ox and Bow'),(3,'Kyanite','19th','The Lounge'),(4,'Nervous','42nd','The Lightbringer'),(5,'Oppression','45th','The Angel\'s Wing'),(6,'Pessimism','37th','The Book and Beggar'),(7,'Pyrites','41st','The Brain and Hatchling'),(8,'Qualms','43rd','The Broken Lover'),(9,'Steel','3rd','Oyler\'s Tavern'),(10,'Vexation','2nd','The Hearth and Sabre'),(11,'Dogwood','78th','The Moon'),(12,'Eagle','67th','Shooter\'s Tavern'),(13,'Ferret','84th','Fisherman\'s Tavern'),(14,'Haddock','64th','Bowyer\'s Tavern'),(15,'Jackal','53rd','The Palm and Parson'),(16,'Quail','85th','The Poltroon'),(17,'Yew','78th','Carter\'s Tavern'),(19,'Oppression','70th','The Stick in the Mud'),(20,'Pyrites','70th','Mercer\'s Tavern'),(22,'Lion','1st','Leacher\'s Tavern'),(23,'Diamond','1st','The Scupper and Forage'),(24,'Nervous','2nd','The Flirting Angel'),(25,'Nettle','3rd','Barker\'s Tavern'),(26,'Yew','5th','Vagabond\'s Tavern'),(27,'Qualms','5th','Rogue\'s Tavern'),(28,'Ragweed','6th','The Dog House'),(29,'Duck','7th','The Stripey Dragon'),(30,'Gum','10th','The Crouching Tiger'),(31,'Knotweed','11th','Archer\'s Tavern'),(32,'Vulture','11th','The Wild Hunt'),(33,'Fir','13th','Balmer\'s Tavern'),(34,'Mongoose','15th','The Last Days'),(35,'Torment','16th','Baker\'s Tavern'),(36,'Beech','19th','The Clam and Champion'),(37,'Ruby','20th','Fiddler\'s Tavern'),(38,'Ruby','21st','The Round Room'),(39,'Steel','23rd','Porter\'s Tavern'),(40,'Steel','26th','Freeman\'s Tavern'),(42,'Nightingale','32nd','The Cosy Walrus'),(43,'Gum','33rd','Abbot\'s Tavern'),(44,'Eagle','34th','The Sunken Sofa'),(45,'Fear','34th','Pub Forty-Two'),(46,'Despair','38th','The Thorn\'s Pride'),(47,'Killjoy','46th','The Crow\'s Nest Tavern'),(48,'Pilchard','48th','Draper\'s Tavern'),(49,'Yearning','48th','The Marsupial'),(50,'Pine','51st','The Dead of Night'),(51,'Dogwood','54th','The Kestrel'),(52,'Obsidian','54th','The Gunny\'s Shack'),(53,'Hessite','55th','The Weevil and Stallion'),(54,'Alder','57th','The Sign of the Times'),(55,'Nickel','57th','The Shining Devil'),(56,'Qualms','61st','Butler\'s Tavern'),(57,'Walrus','62nd','The Ghastly Flabber'),(58,'Ire','63rd','Hawker\'s Tavern'),(60,'Pine','68th','Five French Hens'),(61,'Walrus','68th','The Cart and Castle'),(62,'Anguish','68th','Xendom Tavern'),(63,'Malachite','70th','Pub'),(64,'Sorrow','70th','Pub'),(65,'Raven','71st','Pub'),(66,'Turquoise','71st','Pub'),(67,'Fir','72nd','Hunter\'s Tavern'),(68,'Malachite','76th','Pub'),(69,'Ragweed','78th','Pub'),(70,'Lonely','78th','Pub'),(71,'Ennui','80th','The Stick and Stag'),(72,'Walrus','83rd','Pub'),(73,'Nettle','86th','Pub'),(74,'Lonely','87th','Pub'),(75,'Malaise','87th','Pub'),(76,'Sycamore','89th','Pub'),(77,'Pine','90th','Pub'),(78,'Yak','90th','Pub'),(79,'Ruby','90th','Pub'),(80,'Sorrow','91st','Pub'),(81,'Mongoose','92nd','Pub'),(82,'Unicorn','92nd','Pub'),(83,'Diamond','92nd','Painter\'s Tavern'),(84,'Elm','93rd','The Teapot and Toxin'),(85,'Zinc','93rd','Pub'),(86,'Lion','95th','The Golden Partridge'),(87,'Hessite','97th','The McAllister Tavern'),(88,'Gibbon','98th','Harper\'s Tavern'),(89,'Anguish','98th','Ten Turtle Doves'),(90,'Beryl','98th','Rider\'s Tavern'),(91,'Ivory','99th','The Blinking Pixie'),(94,'Zebra','50th','The Guardian Outpost');
/*!40000 ALTER TABLE `taverns` ENABLE KEYS */;
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
