# UE-AD-A1-MIXTE

Projet universitaire visant à la découverte des API REST, GraphQL et gRPC sous forme de microservices.<br>
Le TP réalisé est le TP Vert.<br>

## Démarrage 🚀

Se placer dans les répertoires de chaque microservice et lancer la commande suivante:<br>

```bash
python <microservice_name>.py
```

## Demandes ✍️

4 microservices :
- user
- booking
- movie
- showtime

Les microservices Booking et Showtime sont tous deux des API gRPC.
Le microservice Movie est une API GraphQL.
Le microservice User est une API REST.
Tous les microservices doivent communiquer entre eux selon un certain schéma. User peut faire appel à Movie et Booking. Booking peut appeler Showtime. Le seul point d'entrée de l'application est l'API User.

## Membres du projet 🧑‍💻

EGENSCHEVILLER Frédéric</br>
LABORDE Baptiste
