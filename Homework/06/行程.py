#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>

int main() {
    printf("【父行程】準備建立子行程來執行命令...\n");

    pid_t pid = fork(); // 1. 複製行程

    if (pid < 0) {
        perror("fork 失敗");
        exit(1);
    } 
    else if (pid == 0) {
        // === 子行程執行區域 ===
        printf("【子行程】PID: %d。準備重導向 stdout 到 output.txt...\n", getpid());

        // 2. 打開檔案，獲得一個新的 fd (通常會是 3，因為 0, 1, 2 已被佔用)
        // O_WRONLY: 唯寫, O_CREAT: 不存在就建立, O_TRUNC: 若存在則清空
        // 0644: 檔案權限 (擁護者可讀寫，其他人唯讀)
        int fd = open("output.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
        if (fd < 0) {
            perror("open 失敗");
            exit(1);
        }

        // 3. 關鍵魔法：將標準輸出 (1) 重導向到剛剛打開的檔案 fd
        // 從此以後，寫入 1 (stdout) 的資料都會寫進 output.txt
        dup2(fd, 1);

        // 4. 良好的習慣：將原本的 fd 關閉，因為 1 已經安全地指向該檔案了
        close(fd);

        // 5. 設定要執行的指令與參數
        // 模擬執行: ls -l
        char *args[] = {"ls", "-l", NULL};

        // 6. 覆蓋目前行程：執行 ls 指令
        // 因為 execvp 會繼承子行程的 fd 表格（此時 1 指向 output.txt），
        // 所以 ls 的輸出結果不會印在螢幕上，而是會全部寫入 output.txt！
        execvp(args[0], args);

        // 如果 execvp 成功，程式絕對不會執行到這行
        perror("execvp 失敗");
        exit(1);
    } 
    else {
        // === 父行程執行區域 ===
        // 父行程的 1 (stdout) 依然指向螢幕，沒有被 dup2 影響
        printf("【父行程】正在等待子行程 (PID: %d) 執行完畢...\n", pid);
        
        int status;
        waitpid(pid, &status, 0); // 等待子行程結束，避免殭屍行程
        
        printf("【父行程】子行程已結束。現在我們來讀取 output.txt 的內容確認結果：\n\n");
        printf("------------------ output.txt 開始 ------------------\n");

        // 7. 父行程親自讀取該檔案並印在螢幕上，驗證子行程的成果
        int fd_read = open("output.txt", O_RDONLY);
        if (fd_read >= 0) {
            char buffer[1024];
            ssize_t bytes_read;
            // 使用 read() 系統呼叫讀取檔案，並用 write(1, ...) 寫到螢幕上
            while ((bytes_read = read(fd_read, buffer, sizeof(buffer))) > 0) {
                write(1, buffer, bytes_read); 
            }
            close(fd_read);
        }
        printf("------------------ output.txt 結束 ------------------\n");
    }

    return 0;
}
