import threading

class BankAccount:
    def __init__(self, initial_balance=0):
        self.balance = initial_balance
        self.lock = threading.Lock()  # 宣告互斥鎖

    def deposit(self, amount, times):
        for _ in range(times):
            with self.lock:  # 獲取鎖，離開此區塊會自動釋放
                self.balance += amount

    def withdraw(self, amount, times):
        for _ in range(times):
            with self.lock:  # 獲取鎖
                self.balance -= amount

def run_bank_simulation():
    account = BankAccount(initial_balance=1000)
    times = 100000
    
    # 建立存款與提款執行緒
    t1 = threading.Thread(target=account.deposit, args=(1, times))
    t2 = threading.Thread(target=account.withdraw, args=(1, times))
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    print(f"【銀行模擬】最終餘額: {account.balance} (預期值: 1000)")

if __name__ == "__main__":
    run_bank_simulation()
