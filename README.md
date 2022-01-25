# OakDLiteContest_GeoFence
repository for the OpenCV Spacial AI Contest using the OakD Lite. We are developing a Livestock and Pet Geofence that is an autonomous system that monitors animals within a zone.

## Team: SoFlo Primary Key

## Problem Statement
Monitoring livestock and pets within a zone can be a struggle. Traditional fences can be broken while leaving the owner unaware that their animals are loose. Loose animals can lead to property damage, loss of the animal, panic, and heartbreak. We propose an autonomous system that can monitor animals and send notifications when animals have crossed a boundary line of a predetermined zone.

![Sketch of proposal.](https://github.com/jisforjt/OakDLiteContest_GeoFence/blob/main/images/readme/SoFlo_Primary_Key_GeoFencing.jpg?raw=true)

This system consists of an autonomous module and a base station. The autonomous module is comprised of the Oak-D Lite camera, a pan and tilt base, a Raspberry Pi with GPS, IMU, and LoRa. The autonomous module would ideally be suspended by a zipline trolley. The zipline trolley allows the system to monitor a much larger zone. The system can also be affixed atop a good vantage point for smaller zones.

The base station is used to set the boundary of the zone and to relay LoRa notifications from the autonomous module to a wireless local area network. Notifications can be received by the user’s mobile device. The user may setup the zone by entering GPS coordinates or by printing out and placing ArUCo markers at the vertices of the zone. The ArUCo markers would only be needed during the setup process and afterwards they can be removed.

The out of zone detection pipeline detects the presence of an animal, classifies its species, tracks it, and compares its present location to the zone’s mask. The animal classification stage is optional and is utilized by users who want to detect unwanted animals.

| Stages  | Methods |
| ------------- | ------------- |
| Animal Detection | Microsoft [CameraTrap](https://github.com/microsoft/CameraTraps) Project |
| Animal Classification | [ResNetST-101](https://modelplace.ai/models/15) |
| ID Tracking | Centroid-Tracking |
| Out of Zone Detection | Bit-wise Comparison |

## License
The code of the repository is made available under the terms of the MIT license. See license.md for more information.
