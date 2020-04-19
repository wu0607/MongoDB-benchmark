# MongoDB-benchmark

### Write-only workload on a cluster of 3 servers + 6 closed-loop clients
Three different client settings:
1. All strong: 6 strong
2. All weak: 6 weak
3. Mix of strong and weak: 3 strong + 3 weak clients

### Quick start for Ubuntu
```
./install.sh # install mongodb
python measure.py --strong --weak
```

### Run 3-node server(master-slave) on single machine (Ubuntu)
reference: https://medium.com/@akshay2gud/creating-multiple-instances-of-mongodb-on-server-and-setting-replication-of-database-5ead59e1e4d4
1. Create database path
```
   cd /var
   sudo mkdir data
   cd data
   sudo mkdir db1 db2 db3
```
2. Change the Owenership this folder
```
chown mongodb:mongodb db1 db2 db3
```
3. Create new Config files for mongoDb
```
sudo cp /etc/mongod.conf /etc/mongod2.conf
sudo cp /etc/mongod.conf /etc/mongod3.conf
```
4. Modify the configs, change the `dbPath`, `replication set`, `port value` and `bind IP`
```
mongod.conf  dbPath /var/data/db1/ replSetName rs0 port 27017 IP 0.0.0.0
mongod2.conf dbPath /var/data/db2/ replSetName rs0 port 27018 IP 0.0.0.0
mongod3.conf dbPath /var/data/db3/ replSetName rs0 port 27019 IP 0.0.0.0
```
5. Create two new services
```
cd /lib/systemd/system
cp mongod.service mongod3.service
cp mongod.service mongod2.service
```
6. Deploy each process
```
sudo systemctl start mongod.service
sudo systemctl start mongod2.service
sudo systemctl start mongod3.service
```
7. Setting replication
```
rs.initiate( {
   _id : "rs0",
   members: [
      { _id: 0, host: "localhost:27017" },
      { _id: 1, host: "localhost:27018" },
      { _id: 2, host: "localhost:27019" }
   ]
})
```
8. Run `rs.status()` in mongodb and find out node with `"stateStr" : "PRIMARY"`, use this ip address to run `measure.py --host [master_ip]:[master_port] --strong --weak`