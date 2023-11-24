# UE-AD-A1-MIXTE

Projet universitaire visant à la découverte des API REST, GraphQL et gRPC sous forme de microservices.<br>
L'ensemble de ces microservices pourrait être assimilable à un système pouvant fonctionner dans un cinéma pour la réservation de places.<br>

Le TP réalisé est le TP Vert.<br>
Afin de tester l'API, un fichier Json généré pour le logiciel Insomnia contenant quelques requêtes intéressantes est disponible à la racine du projet.<br>
Pour télécharger Insomnia : https://insomnia.rest/download

## Démarrage 🚀

Se placer dans les répertoires de chaque microservice et lancer la commande suivante:<br>

```bash
python <microservice_name>.py
```

## Demandes ✍️

4 microservices :
- user REST
- booking gRPC
- movie GraphQL
- showtime gRPC

Les microservices Booking et Showtime sont tous deux des API gRPC.
Le microservice Movie est une API GraphQL.
Le microservice User est une API REST.
Tous les microservices doivent communiquer entre eux selon un certain schéma. User peut faire appel à Movie et Booking. Booking peut appeler Showtime. Le seul point d'entrée de l'application est l'API User.


Le microservice user est utilisé pour la gestion des utilisateurs. Le microservice movie contient les films et les informations à propos d'eux. Le microservice showtime contient les réservations effectuées par les utilisateurs avec leur nom, la date et les films concernés. Le microservice booking permet d'effectuer une réservation, notamment en vérifiant que le film est bien disponible à l'affiche pour le jour demandé.

## Membres du projet 🧑‍💻

EGENSCHEVILLER Frédéric</br>
LABORDE Baptiste
