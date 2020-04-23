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
hostname = "mongodb://localhost:27017/"
stop_event = threading.Event()

def print_table(printDB):
    print("==========")
    for x in printDB.find():
        print(x)
    print("==========")


def updateAndGetTime(op, insertDB, insertDict, threadIdx, timeout_):
    count = 0
    totalTime = 0
    timeout = time.time() + timeout_

    while(True):
        count += 1
        start = time.time()
        insertDB.update_one(insertDict, {"$set": {"value": count}})
        end = time.time()
        totalTime += (end - start)

        if count and count % 1000 == 0:
            print("{:8s}- {}: count: {}, avg_time: {}ms, total time:\
                 {}ms ".format(op, threadIdx, count,
                             totalTime*1000/count, totalTime*1000))

        if time.time() > timeout:
            print("=====Final===== {:8s}- {}: count: {}, avg_time: {}ms, total time:\
                 {}ms ".format(op, threadIdx, count,
                             totalTime*1000/count, totalTime*1000))
            break


def threadFunction(args):
    op, threadIdx, timeout = args
    if op == STRONG:
        updateAndGetTime(STRONG, strongCol, {"node": "/1"}, threadIdx, timeout)
    elif op == WEAK:
        updateAndGetTime(WEAK, weakCol, {"node": "/2"}, threadIdx, timeout)


if __name__ == '__main__':
    # argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--host", help="host ip")
    parser.add_argument("--mode", type=str, default="strong", help="strong weak mix")
    parser.add_argument("--time", type=int, default=30, help="total sec for throughput")
    parser.add_argument("--w_mode", type=int, default=1, help="weak mode 1:(w=1, j=False) 2:(w=majority, j=False) 3:(w=1, j=True)")
    opt = parser.parse_args()
    if opt.host:
        hostname = opt.host
    
    opt.mode = opt.mode.lower()
    if opt.mode == "strong" or opt.mode == "mix":
        strongClient = pymongo.MongoClient(hostname, w="majority", j=True, maxPoolSize=20)
        strongDB = strongClient[MYDB]
        strongCol = strongDB[TABLENAME]
        strongCol.insert_one(strongDict) # init with /1
    if opt.mode == "weak" or opt.mode == "mix":
        if opt.w_mode == 1:
            print("using setting w=1 j=False")
            weakClient = pymongo.MongoClient(hostname, w=1, j=False, maxPoolSize=20)
        elif opt.w_mode == 2:
            print("using setting w=majority j=False")
            weakClient = pymongo.MongoClient(hostname, w="majority", j=False, maxPoolSize=20)
        elif opt.w_mode == 3:
            print("using setting w=1 j=True")
            weakClient = pymongo.MongoClient(hostname, w=1, j=True, maxPoolSize=20)
        weakDB = weakClient[MYDB]
        weakCol = weakDB[TABLENAME]
        weakCol.insert_one(weakDict) # init with /2

    print("done creating client..")

    threadList = []
    for i in range(CLINUM):
        if opt.mode == "strong":
            x = threading.Thread(target=threadFunction, args=((STRONG, i, opt.time),))
            # x = threading.Timer(interval=opt.time, function=threadFunction, args=((STRONG, i),))
            threadList.append(x)
            x.start()
        elif opt.mode == "weak":
            x = threading.Thread(target=threadFunction, args=((WEAK, i, opt.time),))
            # x = threading.Timer(interval=opt.time, function=threadFunction, args=((WEAK, i),))
            threadList.append(x)
            x.start()
        elif opt.mode == "mix":
            if i % 2 == 0:
                x = threading.Thread(target=threadFunction, args=((STRONG, i, opt.time),))
                # x = threading.Timer(interval=opt.time, function=threadFunction, args=((STRONG, i),))
                threadList.append(x)
                x.start()
            else:
                x = threading.Thread(target=threadFunction, args=((WEAK, i, opt.time),))
                # x = threading.Timer(interval=opt.time, function=threadFunction, args=((WEAK, i),))
                threadList.append(x)
                x.start()

    for t in threadList:
        t.join(opt.time)

    # see result and delete data
    client = pymongo.MongoClient(hostname)
    col = client[MYDB]["zookeeper"]
    print_table(col)
    col.delete_many({"node": "/1"})
    col.delete_many({"node": "/2"})
