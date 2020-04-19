import pymongo
import time
import threading
import argparse

MYDB = "mydatabase"
TABLENAME = "zookeeper"
STRONG = "[STRONG]"
WEAK = "[WEAK]"
strongDict = {"node": "/1", "value": "strong"}
weakDict = {"node": "/2", "value": "weak"}
CLINUM = 6
hostname = "mongodb://localhost:27019/"


def print_table(printDB):
    print("==========")
    for x in printDB.find():
        print(x)
    print("==========")


def updateAndGetTime(op, insertDB, insertDict, threadIdx):
    count = 0
    totalTime = 0
    while(True):
        count += 1
        start = time.time()
        insertDB.update_one(insertDict, {"$set": {"value": count}})
        end = time.time()
        totalTime += (end - start)

        if count and count % 1000 == 0:
            print("{:8s}- {}: count: {}, avg_time: {}ms, total time:\
                 {}ms ".format(op, threadIdx//2, count,
                             totalTime*1000/count, totalTime*1000))


def threadFunction(args):
    op, threadIdx = args
    if op == STRONG:
        updateAndGetTime(STRONG, strongCol, {"node": "/1"}, threadIdx)
    elif op == WEAK:
        updateAndGetTime(WEAK, weakCol, {"node": "/2"}, threadIdx)


if __name__ == '__main__':
    # argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--host", help="host ip")
    parser.add_argument("--weak", action='store_true', help='weak request')
    parser.add_argument("--strong", action='store_true', help='strong request')
    opt = parser.parse_args()
    if opt.host:
        hostname = opt.host

    if opt.strong:
        strongClient = pymongo.MongoClient(hostname, w="majority", j=True, maxPoolSize=5)
        strongDB = strongClient[MYDB]
        strongCol = strongDB[TABLENAME]
        strongCol.insert_one(strongDict) # init with /1
    if opt.weak:
        weakClient = pymongo.MongoClient(hostname, w=1, j=False, maxPoolSize=5)
        weakDB = weakClient[MYDB]
        weakCol = weakDB[TABLENAME]
        weakCol.insert_one(weakDict) # init with /2

    print("done creating client..")

    threadList = []
    for i in range(CLINUM): 
        if i % 2 == 0:
            if opt.strong:
                x = threading.Thread(target=threadFunction, args=((STRONG, i),))
                threadList.append(x)
                x.start()
        else:
            if opt.weak:
                x = threading.Thread(target=threadFunction, args=((WEAK, i),))
                threadList.append(x)
                x.start()
        

    for t in threadList: 
        t.join()

    # see result and delete data
    client = pymongo.MongoClient(hostname)
    col = client[MYDB]["zookeeper"]
    print_table(col)
    col.delete_many({"node": "/1"})
    col.delete_many({"node": "/2"})
