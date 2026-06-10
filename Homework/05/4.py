import threading
import time
import random

class Philosopher(threading.Thread):
    def __init__(self, index, left_chopstick, right_chopstick):
        super().__init__()
        self.index = index
        self.left_chopstick = left_chopstick
        self.right_chopstick = right_chopstick
        self.running = True

    def run(self):
        while self.running:
            print(f"哲學家 {self.index} 正在思考...")
            time.sleep(random.uniform(0.1, 0.3))
            
            # 策略：打破對稱性，防止循環等待
            if self.index % 2 == 1:
                first_chopstick = self.left_chopstick
                second_chopstick = self.right_chopstick
            else:
                first_chopstick = self.right_chopstick
                second_chopstick = self.left_chopstick

            # 依序取得兩支筷子
            with first_chopstick:
                with second_chopstick:
                    print(f"  ==> 哲學家 {self.index} 開始用餐。")
                    time.sleep(random.uniform(0.1, 0.3))
                    print(f"  <-- 哲學家 {self.index} 吃飽了，放下筷子。")

def run_dining_simulation():
    num_philosophers = 5
    chopsticks = [threading.Lock() for _ in range(num_philosophers)]
    philosophers = []
    
    for i in range(num_philosophers):
        left_idx = i
        right_idx = (i + 1) % num_philosophers
        p = Philosopher(i, chopsticks[left_idx], chopsticks[right_idx])
        philosophers.append(p)
    
    print("【哲學家用餐】開始模擬（執行 3 秒後自動停止）...")
    for p in philosophers:
        p.start()
        
    time.sleep(3)
    for p in philosophers:
        p.running = False
        
    for p in philosophers:
        p.join()
    print("【哲學家用餐】模擬結束")

if __name__ == "__main__":
    run_dining_simulation()
