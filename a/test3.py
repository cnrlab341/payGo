from multiprocessing.pool import ThreadPool
import threading
import time
pool = ThreadPool(processes=1)
pool1 = ThreadPool(processes=100)
def abc(i) :
    print("x")
def b() :
    while True :
        lock = threading.Lock
        with lock :
            print("ZZ")
            time.sleep(0.1)
            abc("x")

th = pool1.apply_async(b)
# th = threading.Thread(target=b)
# th.start()

def iner_test(a, t) :
    time.sleep(t)
    print(a)

def test(a, t, inner_t, inner_content) :
    time.sleep(t)
    print(a)
    pool = ThreadPool(processes=1)
    pool.apply_async(iner_test, (inner_content,inner_t))
    return a + str(0)


a = "a"
b= "b"
for i in range(10) :
    th1_list = pool1.apply_async(test, (a, 0.2,1.1, "a_inner"))
    th2_list = pool1.apply_async(test, (b, 0.9, 1.1, "b_inner"))
    a= th1_list.get()

    if i == 9 :
        th2_list.get()
        th.get()
        # th.get()

# for i in range(10) :
# th.get()
# print(a)
# th2_list = pool.apply_async(test, ("b",0.1, 0.2, "b_inner"))
# b = th2_list.get()
#
# th3_list = pool.apply_async(test, ("c",1, 2, "c_inner"))
# th.get()
# print(a)
# th4_list = pool.apply_async(test, ("d",0.1, 0.2, "d_inner"))
# a= th3_list.get()
# b = th4_list.get()

