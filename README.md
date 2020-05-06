# MongoDB-benchmark
Here we compare MongoDB's performance with Zookeeper for serving multi-consistency level's requests <br>
For the main project, please go to https://github.com/YiShiunChang/zookeeper 

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
Reference: https://medium.com/@akshay2gud/creating-multiple-instances-of-mongodb-on-server-and-setting-replication-of-database-5ead59e1e4d4
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


### Run 3-node server(master-slave) on three different machines(cloudLab)
reference: https://computingforgeeks.com/how-to-setup-mongodb-replication-on-ubuntu-18-04-lts/
<br>[Belowed steps should be applied to all three servers]
1. Create database path
```
sudo mkdir /data
sudo mkdir /data/mongodb
```
2. Change the Owenership & Permission of this folder
```
sudo chown -R mongodb:mongodb /data/mongodb
sudo chmod -R 775 /data/mongodb
```
3. Modify the configs, change the `dbPath`, `replication set`, `port value` and `bind IP`
```
sudo vim /etc/mongod.conf
   net:
      port: 27017
      bindIp: 10.10.1.1 (10.10.1.2 on 2nd machine & 10.10.1.3 on 3rd machine)
   storage:
      dbPath: /data/mongodb
      journal:
         enabled: true
   replication:
      replSetName: "replica01"
```
4. Open port 27017/tcp on the firewall
```
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 27017/tcp
```
5. Configure MongoDB to start during the operating system’s boot
```
sudo systemctl enable mongod.service
sudo systemctl restart mongod.service
```
6. Check the listen Address of MongoDB service:
```
ss -tunelp
```
7. Setting replication
```
mongo 10.10.1.1 (10.10.1.2 on 2nd machine & 10.10.1.3 on 3rd machine)
> rs.initiate( {
   _id : "replica01",
   members: [
      { _id: 0, host: "10.10.1.1:27017" },
      { _id: 1, host: "10.10.1.2:27017" },
      { _id: 2, host: "10.10.1.3:27017" }
   ]
})
// Then add the other nodes only on one command promt (here if 10.10.1.1)
> rs.add("10.10.1.2")
> rs.add("10.10.1.3")
```
8. Run `rs.status()` in mongodb and find out node with `"stateStr" : "PRIMARY"`, use this ip address to run `measure.py --host [master_ip]:[master_port] --strong --weak`
