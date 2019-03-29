
# Rise up ArangoDB

```
sudo docker run -e ARANGO_RANDOM_ROOT_PASSWORD=1 -d --name arangodb-instance arangodb
sudo docker inspect --format '{{ .NetworkSettings.IPAddress }}' arangodb-instance
sudo docker logs
```

Port forwarding
```
ssh -f -N -L 8530:172.17.0.2:8529 d.tarasov@116.203.70.12
```