import threading
import queue
import time
import random

def producer(buf, count):
    for i in range(count):
        item = f"商品-{i+1}"
        buf.put(item)  # 若隊列滿了會自動阻塞
        print(f"[生產者] 生產了 {item}，目前庫存: {buf.qsize()}")
        time.sleep(random.uniform(0.1, 0.3))
    print("[生產者] 工作結束")

def consumer(buf, count):
    for _ in range(count):
        item = buf.get()  # 若隊列空了會自動阻塞
        print(f"  [消費者] 消費了 {item}，目前庫存: {buf.qsize()}")
        buf.task_done()
        time.sleep(random.uniform(0.2, 0.5))
    print("  [消費者] 工作結束")

def run_producer_consumer():
    # 限制緩衝區大小為 5
    buffer_queue = queue.Queue(maxsize=5)
    total_items = 15
    
    t_prod = threading.Thread(target=producer, args=(buffer_queue, total_items))
    t_cons = threading.Thread(target=consumer, args=(buffer_queue, total_items))
    
    t_prod.start()
    t_cons.start()
    
    t_prod.join()
    t_cons.join()
    print("【生產者消費者】模擬完成")

if __name__ == "__main__":
    run_producer_consumer()
