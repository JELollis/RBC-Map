CREATE DATABASE  IF NOT EXISTS `city_map` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `city_map`;
-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: city_map
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

--
-- Table structure for table `color_mappings`
--

DROP TABLE IF EXISTS `color_mappings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `color_mappings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(255) NOT NULL,
  `color` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `color_mappings`
--

LOCK TABLES `color_mappings` WRITE;
/*!40000 ALTER TABLE `color_mappings` DISABLE KEYS */;
INSERT INTO `color_mappings` VALUES (1,'bank','blue'),(2,'tavern','orange'),(3,'transit','red'),(4,'user_building','purple'),(5,'alley','grey'),(6,'default','black'),(7,'border','white'),(9,'edge','blue'),(10,'shop','green'),(11,'guild','yellow'),(12,'placesofinterest','purple'),(13,'background','#d4d4d4'),(14,'text_color','#000000'),(15,'button_color','#b1b1b1'),(30,'set_destination','#1a7f7a'),(31,'set_destination_transit','#046380');
/*!40000 ALTER TABLE `color_mappings` ENABLE KEYS */;
UNLOCK TABLES;

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
INSERT INTO `guilds` VALUES (1,'Allurists Guild 1','Vauxite','15th','2024-11-14 00:00:01'),(2,'Allurists Guild 2','Vauxite','24th','2024-11-14 00:00:01'),(3,'Allurists Guild 3','Eagle','84th','2024-11-14 00:00:01'),(4,'Empaths Guild 1','Duck','65th','2024-11-14 00:00:01'),(5,'Empaths Guild 2','Alder','17th','2024-11-14 00:00:01'),(6,'Empaths Guild 3','Pyrites','52nd','2024-11-14 00:00:01'),(7,'Immolators Guild 1','Ennui','95th','2024-11-14 00:00:01'),(8,'Immolators Guild 2','Yuksporite','99th','2024-11-14 00:00:01'),(9,'Immolators Guild 3','Beech','24th','2024-11-14 00:00:01'),(10,'Thieves Guild 1','Ire','12th','2024-11-14 00:00:01'),(11,'Thieves Guild 2','Chagrin','46th','2024-11-14 00:00:01'),(12,'Thieves Guild 3','Flint','69th','2024-11-14 00:00:01'),(13,'Travellers Guild 1','Zelkova','28th','2024-11-14 00:00:01'),(14,'Travellers Guild 2','Juniper','42nd','2024-11-14 00:00:01'),(15,'Travellers Guild 3','Steel','54th','2024-11-14 00:00:01'),(16,'Peacekkeepers Mission 1','Emerald','67th','2024-11-14 00:00:01'),(17,'Peacekkeepers Mission 2','Unicorn','33rd','2024-11-14 00:00:01'),(18,'Peacekkeepers Mission 3','Emerald','33rd','2024-11-14 00:00:01');
/*!40000 ALTER TABLE `guilds` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `placesofinterest`
--

DROP TABLE IF EXISTS `placesofinterest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `placesofinterest` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) NOT NULL,
  `Column` varchar(255) NOT NULL,
  `Row` varchar(255) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `idx_column_row` (`Column`,`Row`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `placesofinterest`
--

LOCK TABLES `placesofinterest` WRITE;
/*!40000 ALTER TABLE `placesofinterest` DISABLE KEYS */;
INSERT INTO `placesofinterest` VALUES (1,'Battle Arena','Zelkova','52nd'),(2,'Hall of Binding','Vervain','40th'),(3,'Hall of Severance','Walrus','40th'),(4,'The Graveyard','Larch','50th'),(5,'Cloister of Secrets','Gloom','1st'),(6,'Eternal Aubade of Mystical Treasures','Zelkova','47th');
/*!40000 ALTER TABLE `placesofinterest` ENABLE KEYS */;
UNLOCK TABLES;

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

--
-- Table structure for table `shop_items`
--

DROP TABLE IF EXISTS `shop_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shop_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `shop_name` varchar(255) DEFAULT NULL,
  `item_name` varchar(255) DEFAULT NULL,
  `base_price` int DEFAULT NULL,
  `charisma_level_1` int DEFAULT NULL,
  `charisma_level_2` int DEFAULT NULL,
  `charisma_level_3` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=242 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shop_items`
--

LOCK TABLES `shop_items` WRITE;
/*!40000 ALTER TABLE `shop_items` DISABLE KEYS */;
INSERT INTO `shop_items` VALUES (1,'Discount Magic','Perfect Dandelion',35,33,32,31),(2,'Discount Magic','Sprint Potion',105,101,97,94),(3,'Discount Magic','Perfect Red Rose',350,339,325,315),(4,'Discount Magic','Scroll of Turning',350,339,325,315),(5,'Discount Magic','Scroll of Succour',525,509,488,472),(6,'Discount Magic','Scroll of Bondage',637,617,592,573),(7,'Discount Magic','Garlic Spray',700,678,651,630),(8,'Discount Magic','Scroll of Displacement',700,678,651,630),(9,'Discount Magic','Perfect Black Orchid',795,772,740,716),(10,'Discount Magic','Scroll of Summoning',1050,1018,976,945),(11,'Discount Magic','Vial of Holy Water',1400,1357,1302,1260),(12,'Discount Magic','Wooden Stake',2800,2715,2604,2520),(13,'Discount Magic','Scroll of Accounting',3500,3394,3255,3150),(14,'Discount Magic','Scroll of Teleportation',3500,3394,3255,3150),(15,'Discount Magic','UV Grenade',3500,3394,3255,3150),(16,'Discount Magic','Ring of Resistance',14000,13579,13020,12600),(17,'Discount Magic','Diamond Ring',70000,67900,65100,63000),(18,'Discount Potions','Sprint Potion',105,101,97,94),(19,'Discount Potions','Garlic Spray',700,678,651,630),(20,'Discount Potions','Vial of Holy Water',1400,1357,1302,1260),(21,'Discount Potions','Blood Potion',30000,30000,30000,30000),(22,'Discount Potions','Necromancer',25,25,25,25),(23,'Discount Scrolls','Scroll of Turning',350,339,325,315),(24,'Discount Scrolls','Scroll of Succour',525,509,488,472),(25,'Discount Scrolls','Scroll of Displacement',700,678,651,630),(26,'Discount Scrolls','Scroll of Summoning',1050,1018,976,945),(27,'Discount Scrolls','Scroll of Accounting',3500,3394,3255,3150),(28,'Discount Scrolls','Scroll of Teleportation',3500,3394,3255,3150),(29,'Dark Desires','Perfect Dandelion',50,48,46,45),(30,'Dark Desires','Sprint Potion',150,145,139,135),(31,'Dark Desires','Perfect Red Rose',500,485,465,450),(32,'Dark Desires','Scroll of Turning',500,485,465,450),(33,'Dark Desires','Scroll of Succour',750,727,697,675),(34,'Dark Desires','Scroll of Bondage',910,882,846,819),(35,'Dark Desires','Garlic Spray',1000,970,930,900),(36,'Dark Desires','Scroll of Displacement',1000,970,930,900),(37,'Dark Desires','Perfect Black Orchid',1137,1102,1057,1023),(38,'Dark Desires','Scroll of Summoning',1500,1455,1395,1350),(39,'Dark Desires','Vial of Holy Water',2000,1940,1860,1800),(40,'Dark Desires','Wooden Stake',4000,3880,3720,3600),(41,'Dark Desires','Scroll of Accounting',5000,4850,4650,4500),(42,'Dark Desires','Scroll of Teleportation',5000,4850,4650,4500),(43,'Dark Desires','UV Grenade',5000,4850,4650,4500),(44,'Dark Desires','Ring of Resistance',20000,19400,18600,18000),(45,'Dark Desires','Diamond Ring',100000,97000,93000,90000),(46,'Interesting Times','Perfect Dandelion',50,48,46,45),(47,'Interesting Times','Sprint Potion',150,145,139,135),(48,'Interesting Times','Perfect Red Rose',500,485,465,450),(49,'Interesting Times','Scroll of Turning',500,485,465,450),(50,'Interesting Times','Scroll of Succour',750,727,697,675),(51,'Interesting Times','Scroll of Bondage',910,882,846,819),(52,'Interesting Times','Garlic Spray',1000,970,930,900),(53,'Interesting Times','Scroll of Displacement',1000,970,930,900),(54,'Interesting Times','Perfect Black Orchid',1137,1102,1057,1023),(55,'Interesting Times','Scroll of Summoning',1500,1455,1395,1350),(56,'Interesting Times','Vial of Holy Water',2000,1940,1860,1800),(57,'Interesting Times','Wooden Stake',4000,3880,3720,3600),(58,'Interesting Times','Scroll of Accounting',5000,4850,4650,4500),(59,'Interesting Times','Scroll of Teleportation',5000,4850,4650,4500),(60,'Interesting Times','UV Grenade',5000,4850,4650,4500),(61,'Interesting Times','Ring of Resistance',20000,19400,18600,18000),(62,'Interesting Times','Diamond Ring',100000,97000,93000,90000),(63,'Sparks','Perfect Dandelion',50,48,46,45),(64,'Sparks','Sprint Potion',150,145,139,135),(65,'Sparks','Perfect Red Rose',500,485,465,450),(66,'Sparks','Scroll of Turning',500,485,465,450),(67,'Sparks','Scroll of Succour',750,727,697,675),(68,'Sparks','Scroll of Bondage',910,882,846,819),(69,'Sparks','Garlic Spray',1000,970,930,900),(70,'Sparks','Scroll of Displacement',1000,970,930,900),(71,'Sparks','Perfect Black Orchid',1137,1102,1057,1023),(72,'Sparks','Scroll of Summoning',1500,1455,1395,1350),(73,'Sparks','Vial of Holy Water',2000,1940,1860,1800),(74,'Sparks','Wooden Stake',4000,3880,3720,3600),(75,'Sparks','Scroll of Accounting',5000,4850,4650,4500),(76,'Sparks','Scroll of Teleportation',5000,4850,4650,4500),(77,'Sparks','UV Grenade',5000,4850,4650,4500),(78,'Sparks','Ring of Resistance',20000,19400,18600,18000),(79,'Sparks','Diamond Ring',100000,97000,93000,90000),(80,'The Magic Box','Perfect Dandelion',50,48,46,45),(81,'The Magic Box','Sprint Potion',150,145,139,135),(82,'The Magic Box','Perfect Red Rose',500,485,465,450),(83,'The Magic Box','Scroll of Turning',500,485,465,450),(84,'The Magic Box','Scroll of Succour',750,727,697,675),(85,'The Magic Box','Scroll of Bondage',910,882,846,819),(86,'The Magic Box','Garlic Spray',1000,970,930,900),(87,'The Magic Box','Scroll of Displacement',1000,970,930,900),(88,'The Magic Box','Perfect Black Orchid',1137,1102,1057,1023),(89,'The Magic Box','Scroll of Summoning',1500,1455,1395,1350),(90,'The Magic Box','Vial of Holy Water',2000,1940,1860,1800),(91,'The Magic Box','Wooden Stake',4000,3880,3720,3600),(92,'The Magic Box','Scroll of Accounting',5000,4850,4650,4500),(93,'The Magic Box','Scroll of Teleportation',5000,4850,4650,4500),(94,'The Magic Box','UV Grenade',5000,4850,4650,4500),(95,'The Magic Box','Ring of Resistance',20000,19400,18600,18000),(96,'The Magic Box','Diamond Ring',100000,97000,93000,90000),(97,'White Light','Perfect Dandelion',50,48,46,45),(98,'White Light','Sprint Potion',150,145,139,135),(99,'White Light','Perfect Red Rose',500,485,465,450),(100,'White Light','Scroll of Turning',500,485,465,450),(101,'White Light','Scroll of Succour',750,727,697,675),(102,'White Light','Scroll of Bondage',910,882,846,819),(103,'White Light','Garlic Spray',1000,970,930,900),(104,'White Light','Scroll of Displacement',1000,970,930,900),(105,'White Light','Perfect Black Orchid',1137,1102,1057,1023),(106,'White Light','Scroll of Summoning',1500,1455,1395,1350),(107,'White Light','Vial of Holy Water',2000,1940,1860,1800),(108,'White Light','Wooden Stake',4000,3880,3720,3600),(109,'White Light','Scroll of Accounting',5000,4850,4650,4500),(110,'White Light','Scroll of Teleportation',5000,4850,4650,4500),(111,'White Light','UV Grenade',5000,4850,4650,4500),(112,'White Light','Ring of Resistance',20000,19400,18600,18000),(113,'White Light','Diamond Ring',100000,97000,93000,90000),(114,'McPotions','Sprint Potion',150,145,139,135),(115,'McPotions','Garlic Spray',1000,970,930,900),(116,'McPotions','Vial of Holy Water',2000,1940,1860,1800),(117,'McPotions','Blood Potion',30000,30000,30000,30000),(118,'McPotions','Necromancer',25,25,25,25),(119,'Potable Potions','Sprint Potion',150,145,139,135),(120,'Potable Potions','Garlic Spray',1000,970,930,900),(121,'Potable Potions','Vial of Holy Water',2000,1940,1860,1800),(122,'Potable Potions','Blood Potion',30000,30000,30000,30000),(123,'Potable Potions','Necromancer',25,25,25,25),(124,'Potion Distillery','Sprint Potion',150,145,139,135),(125,'Potion Distillery','Garlic Spray',1000,970,930,900),(126,'Potion Distillery','Vial of Holy Water',2000,1940,1860,1800),(127,'Potion Distillery','Blood Potion',30000,30000,30000,30000),(128,'Potion Distillery','Necromancer',25,25,25,25),(129,'Potionworks','Sprint Potion',150,145,139,135),(130,'Potionworks','Garlic Spray',1000,970,930,900),(131,'Potionworks','Vial of Holy Water',2000,1940,1860,1800),(132,'Potionworks','Blood Potion',30000,30000,30000,30000),(133,'Potionworks','Necromancer',25,25,25,25),(134,'Silver Apothecary','Sprint Potion',150,145,139,135),(135,'Silver Apothecary','Garlic Spray',1000,970,930,900),(136,'Silver Apothecary','Vial of Holy Water',2000,1940,1860,1800),(137,'Silver Apothecary','Blood Potion',30000,30000,30000,30000),(138,'Silver Apothecary','Perfect Dandelion',50,48,46,45),(139,'Silver Apothecary','Perfect Red Rose',500,485,465,450),(140,'Silver Apothecary','Perfect Black Orchid',1137,1102,1057,1023),(141,'Silver Apothecary','Diamond Ring',100000,97000,93000,90000),(142,'Silver Apothecary','Necromancer',25,25,25,25),(143,'The Potion Shoppe','Sprint Potion',150,145,139,135),(144,'The Potion Shoppe','Garlic Spray',1000,970,930,900),(145,'The Potion Shoppe','Vial of Holy Water',2000,1940,1860,1800),(146,'The Potion Shoppe','Blood Potion',30000,30000,30000,30000),(147,'The Potion Shoppe','Necromancer',25,25,25,25),(148,'Herman\'s Scrolls','Scroll of Turning',500,485,465,450),(149,'Herman\'s Scrolls','Scroll of Succour',750,727,697,675),(150,'Herman\'s Scrolls','Scroll of Displacement',1000,970,930,900),(151,'Herman\'s Scrolls','Scroll of Summoning',1500,1455,1395,1350),(152,'Herman\'s Scrolls','Scroll of Accounting',5000,4850,4650,4500),(153,'Herman\'s Scrolls','Scroll of Teleportation',5000,4850,4650,4500),(154,'Paper and Scrolls','Scroll of Turning',500,485,465,450),(155,'Paper and Scrolls','Scroll of Succour',750,727,697,675),(156,'Paper and Scrolls','Scroll of Displacement',1000,970,930,900),(157,'Paper and Scrolls','Scroll of Summoning',1500,1455,1395,1350),(158,'Paper and Scrolls','Scroll of Accounting',5000,4850,4650,4500),(159,'Paper and Scrolls','Scroll of Teleportation',5000,4850,4650,4500),(160,'Scrollmania','Scroll of Turning',500,485,465,450),(161,'Scrollmania','Scroll of Succour',750,727,697,675),(162,'Scrollmania','Scroll of Displacement',1000,970,930,900),(163,'Scrollmania','Scroll of Summoning',1500,1455,1395,1350),(164,'Scrollmania','Scroll of Accounting',5000,4850,4650,4500),(165,'Scrollmania','Scroll of Teleportation',5000,4850,4650,4500),(166,'Scrolls \'n\' Stuff','Scroll of Turning',500,485,465,450),(167,'Scrolls \'n\' Stuff','Scroll of Succour',750,727,697,675),(168,'Scrolls \'n\' Stuff','Scroll of Displacement',1000,970,930,900),(169,'Scrolls \'n\' Stuff','Scroll of Summoning',1500,1455,1395,1350),(170,'Scrolls \'n\' Stuff','Scroll of Accounting',5000,4850,4650,4500),(171,'Scrolls \'n\' Stuff','Scroll of Teleportation',5000,4850,4650,4500),(172,'Scrolls R Us','Scroll of Turning',500,485,465,450),(173,'Scrolls R Us','Scroll of Succour',750,727,697,675),(174,'Scrolls R Us','Scroll of Displacement',1000,970,930,900),(175,'Scrolls R Us','Scroll of Summoning',1500,1455,1395,1350),(176,'Scrolls R Us','Scroll of Accounting',5000,4850,4650,4500),(177,'Scrolls R Us','Scroll of Teleportation',5000,4850,4650,4500),(178,'Scrollworks','Scroll of Turning',500,485,465,450),(179,'Scrollworks','Scroll of Succour',750,727,697,675),(180,'Scrollworks','Scroll of Displacement',1000,970,930,900),(181,'Scrollworks','Scroll of Summoning',1500,1455,1395,1350),(182,'Scrollworks','Scroll of Accounting',5000,4850,4650,4500),(183,'Scrollworks','Scroll of Teleportation',5000,4850,4650,4500),(184,'Ye Olde Scrolles','Scroll of Turning',500,485,465,450),(185,'Ye Olde Scrolles','Scroll of Succour',750,727,697,675),(186,'Ye Olde Scrolles','Scroll of Displacement',1000,970,930,900),(187,'Ye Olde Scrolles','Scroll of Summoning',1500,1455,1395,1350),(188,'Ye Olde Scrolles','Scroll of Accounting',5000,4850,4650,4500),(189,'Ye Olde Scrolles','Scroll of Teleportation',5000,4850,4650,4500),(190,'Eternal Aubade of Mystical Treasures','Perfect Dandelion',55,55,55,55),(191,'Eternal Aubade of Mystical Treasures','Sprint Potion',165,165,165,165),(192,'Eternal Aubade of Mystical Treasures','Perfect Red Rose',550,550,550,550),(193,'Eternal Aubade of Mystical Treasures','Scroll of Succour',825,25,25,25),(194,'Eternal Aubade of Mystical Treasures','Scroll of Bondage',1001,1001,1001,1001),(195,'Eternal Aubade of Mystical Treasures','Perfect Black Orchid',1250,1250,1250,1250),(196,'Eternal Aubade of Mystical Treasures','Gold Dawn to Dusk Tulip',1500,1500,1500,1500),(197,'Eternal Aubade of Mystical Treasures','Wooden Stake',4400,4400,4400,4400),(198,'Eternal Aubade of Mystical Treasures','Kitten',10000,10000,10000,10000),(199,'Eternal Aubade of Mystical Treasures','Wolf Pup',12500,12500,12500,12500),(200,'Eternal Aubade of Mystical Treasures','Dragon\'s Egg',17499,17499,17499,17499),(201,'Eternal Aubade of Mystical Treasures','Silver Pocket Watch',20000,20000,20000,20000),(202,'Eternal Aubade of Mystical Treasures','Crystal Music Box',25000,25000,25000,25000),(203,'Eternal Aubade of Mystical Treasures','Blood Potion',33000,33000,33000,33000),(204,'Eternal Aubade of Mystical Treasures','Hand Mirror of Truth',35000,35000,35000,35000),(205,'Eternal Aubade of Mystical Treasures','Book of Spells',44999,44999,44999,44999),(206,'Eternal Aubade of Mystical Treasures','Ritual Gown',55000,55000,55000,55000),(207,'Eternal Aubade of Mystical Treasures','Silver Ruby Dagger',65000,65000,65000,65000),(208,'Eternal Aubade of Mystical Treasures','Onyx Coffin',75000,75000,75000,75000),(209,'Eternal Aubade of Mystical Treasures','Platinum Puzzle Rings',115000,115000,115000,115000),(210,'Eternal Aubade of Mystical Treasures','Diamond Succubus Earrings',125000,125000,125000,125000),(211,'The Cloister of Secrets','Perfect Dandelion',55,55,55,55),(212,'The Cloister of Secrets','Perfect Red Rose',550,550,550,550),(213,'The Cloister of Secrets','Perfect Black Orchid',1250,1250,1250,1250),(214,'The Cloister of Secrets','Safety Deposit Box Key',11000,11000,11000,11000),(215,'The Cloister of Secrets','Necklace with Locket',55000,55000,55000,55000),(216,'The Cloister of Secrets','Flask of Heinous Deceptions',77000,77000,77000,77000),(217,'The Cloister of Secrets','Amulet of Insidious Illusions',88000,88000,88000,88000),(218,'The Cloister of Secrets','Golden Ring',99000,99000,99000,99000),(219,'The Cloister of Secrets','Diamond Ring',110000,110000,110000,110000),(220,'The Cloister of Secrets','Titanium-Platinum Ring',110000,110000,110000,110000),(221,'Grotto of Deceptions','Scroll of Turning',550,550,550,550),(222,'Grotto of Deceptions','Scroll of Teleportation',5500,5500,5500,5500),(223,'Grotto of Deceptions','Scroll of Displacement',1100,1100,1100,1100),(224,'Grotto of Deceptions','Scroll of Succour',825,825,825,825),(225,'Grotto of Deceptions','Vial of Holy Water',2200,2200,2200,2200),(226,'Grotto of Deceptions','Garlic Spray',1100,1100,1100,1100),(227,'Grotto of Deceptions','Sprint Potion',165,165,165,165),(228,'Grotto of Deceptions','Perfect Dandelion',55,55,55,55),(229,'Grotto of Deceptions','Perfect Red Rose',550,550,550,550),(230,'Grotto of Deceptions','Perfect Black Orchid',1100,1100,1100,1100),(231,'NightWatch Headquarters','Memorial Candle',200,200,200,200),(232,'NightWatch Headquarters','Perfect Red Rose',550,550,550,550),(233,'The Ixora Estate','Perfect Ixora Cluster',550,550,550,550),(234,'The Ixora Estate','Perfect Dandelion',55,55,55,55),(235,'The Ixora Estate','Perfect Black Orchid',1100,1100,1100,1100),(236,'The Ixora Estate','Perfect Red Rose',550,550,550,550),(237,'The White House','Perfect Red Rose',550,550,550,550),(238,'The White House','Perfect Black Orchid',1250,1250,1250,1250),(239,'The White House','Pewter Celtic Cross',10000,10000,10000,10000),(240,'The White House','Compass',11999,11999,11999,11999),(241,'The White House','Pewter Tankard',15000,15000,15000,15000);
/*!40000 ALTER TABLE `shop_items` ENABLE KEYS */;
UNLOCK TABLES;

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
INSERT INTO `shops` VALUES (1,'Ace Porn','NA','NA','2024-11-11 22:40:01'),(2,'Checkers Porn Shop','NA','NA','2024-11-11 22:40:01'),(3,'Dark Desires','NA','NA','2024-11-11 22:40:01'),(4,'Discount Magic','NA','NA','2024-11-11 22:40:01'),(5,'Discount Potions','NA','NA','2024-11-11 22:40:01'),(6,'Discount Scrolls','NA','NA','2024-11-11 22:40:01'),(7,'Herman\'s Scrolls','NA','NA','2024-11-11 22:40:01'),(8,'Interesting Times','NA','NA','2024-11-11 22:40:01'),(9,'McPotions','NA','NA','2024-11-11 22:40:01'),(10,'Paper and Scrolls','NA','NA','2024-11-11 22:40:01'),(11,'Potable Potions','NA','NA','2024-11-11 22:40:01'),(12,'Potion Distillery','Ivory','30th','2024-11-11 22:40:01'),(13,'Potionworks','NA','NA','2024-11-11 22:40:01'),(14,'Reversi Porn','NA','NA','2024-11-11 22:40:01'),(15,'Scrollmania','NA','NA','2024-11-11 22:40:01'),(16,'Scrolls \'n\' Stuff','NA','NA','2024-11-11 22:40:01'),(17,'Scrolls R Us','NA','NA','2024-11-11 22:40:01'),(18,'Scrollworks','NA','NA','2024-11-11 22:40:01'),(19,'Silver Apothecary','NA','NA','2024-11-11 22:40:01'),(20,'Sparks','NA','NA','2024-11-11 22:40:01'),(21,'Spinners Porn','NA','NA','2024-11-11 22:40:01'),(22,'The Magic Box','NA','NA','2024-11-11 22:40:01'),(23,'The Potion Shoppe','NA','NA','2024-11-11 22:40:01'),(24,'White Light','NA','NA','2024-11-11 22:40:01'),(25,'Ye Olde Scrolles','NA','NA','2024-11-11 22:40:01');
/*!40000 ALTER TABLE `shops` ENABLE KEYS */;
UNLOCK TABLES;

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

--
-- Table structure for table `transits`
--

DROP TABLE IF EXISTS `transits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transits` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Column` varchar(255) NOT NULL,
  `Row` varchar(255) NOT NULL,
  `Name` varchar(255) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `idx_column_row` (`Column`,`Row`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transits`
--

LOCK TABLES `transits` WRITE;
/*!40000 ALTER TABLE `transits` DISABLE KEYS */;
INSERT INTO `transits` VALUES (1,'Mongoose','25th','Calliope'),(2,'Zelkova','25th','Clio'),(3,'Malachite','25th','Erato'),(4,'Mongoose','50th','Euterpe'),(5,'Zelkova','50th','Melpomene'),(6,'Malachite','50th','Polyhymnia'),(7,'Mongoose','75th','Terpsichore'),(8,'Zelkova','75th','Thalia'),(9,'Malachite','75th','Urania');
/*!40000 ALTER TABLE `transits` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `userbuildings`
--

DROP TABLE IF EXISTS `userbuildings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `userbuildings` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) NOT NULL,
  `Column` varchar(255) NOT NULL,
  `Row` varchar(255) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `idx_column_row` (`Column`,`Row`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `userbuildings`
--

LOCK TABLES `userbuildings` WRITE;
/*!40000 ALTER TABLE `userbuildings` DISABLE KEYS */;
INSERT INTO `userbuildings` VALUES (1,'WyndCryer\'s Lair','Unicorn','77th'),(2,'obsidian\'s Chateau de la Lumiere','Obsidian','66th'),(3,'Castle of Shadows','Turquoise','86th'),(4,'The Moonlight Gardens','Turquoise','87th'),(5,'Cafe Damari','Zelkova','68th'),(6,'tejas_dragon\'s Lair','Zelkova','69th'),(7,'Avant\'s Garden','Amethyst','68th'),(8,'My MotherInLaw\'s Home for Wayward Ghouls','Amethyst','69th'),(9,'The Empty Spiral','Anguish','69th'),(10,'espy\'s Jaded Sorrows','Jaded','69th'),(11,'Daphne\'s Dungeons','Malachite','64th'),(12,'ChaosRaven\'s Dimensional Tower','Killjoy','23rd');
/*!40000 ALTER TABLE `userbuildings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'city_map'
--

--
-- Dumping routines for database 'city_map'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-11 16:00:42
