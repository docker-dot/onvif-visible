import time
from PyQt5.QtCore import QThread, QTime



pool = None
def get_pool():
    global pool
    if pool is None:
        pool = QT_ThreadPool()
        print("pool已启动")
    return QT_ThreadPool()


#  这是线程池，这个重点了解下，线程池的主要作用是提升程序执行的效率
class WorkThread(QThread):
    def __init__(self, fn, *args, **kwargs):
        super(WorkThread, self).__init__()
        self.result_flag = False
        self.result = None
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.fn(*self.args, **self.kwargs)
        # return self

    def done(self):
        if self.result_flag:
            return True
        return self.isFinished()

    def set_result(self, result):
        self.result_flag = True
        self.result = result


"""
    ThreadPool 线程池设计目的：为了避免当且仅且一个只需要只需要一个线程执行的任务被多次开启
    当前设计规则：
        相同任务名的规则不能同时被开启，如果同时开启同一执行任务则需要对任务名进行修改
"""


class QT_ThreadPool:
    __species = None
    __first_init = True

    def __new__(cls, *args, **kwargs):
        if cls.__species is None:
            cls.__species = object.__new__(cls)
        return cls.__species

    def __init__(self, log_interval=5):
        if self.__first_init:
            self.future_dict = dict()
            self.submit("print_log", self.log, interval=log_interval)
        self.__first_init = False

    def submit(self, task_name, fn, *args, **kwargs):
        try:
            # 获取下拉框的值
            # 文本框的值
            if not task_name in self.future_dict.keys():
                try:
                    future = WorkThread(fn, *args, **kwargs)
                    future.start()
                except Exception as e:
                    print(e)
                self.future_dict[task_name] = future
            else:
                future = self.future_dict[task_name]
                if future.done():
                    del future
                    future = WorkThread(fn, *args, **kwargs)
                    self.future_dict[task_name] = future
                    future.start()
            return future
        except Exception as e:
            print(e)
            pass

    def add_thread(self, task_name, future):
        if task_name not in self.future_dict.keys() or self.future_dict[task_name].isFinished():
            self.future_dict[task_name] = future

    def log(self, interval=5):
        while True:
            time.sleep(interval)
            futures = self.future_dict.items()
            running_task_names = []
            for task_name, future in futures:
                if not future.done():
                    running_task_names.append(task_name)
            print(f"current running task number:{len(running_task_names)}")
            print(f"current task names: {running_task_names}")

    def stop_task(self, task_name):
        if task_name in self.future_dict:
            future = self.future_dict[task_name]
            if not future.done():
                future.stop_task()
            del self.future_dict[task_name]


