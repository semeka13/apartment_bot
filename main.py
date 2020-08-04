from time import sleep
import os
from multiprocessing import Pool

processes = ('send_notifications.py', 'telegram_bot.py')


def run_process(process):
    os.system('python {}'.format(process))


pool = Pool(processes=2)
pool.map(run_process, processes)

