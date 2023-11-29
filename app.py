from pathlib import Path
from time import sleep
import tkinter as tk
from tkinter import Tk, ttk, filedialog
import pandas as pd

from utils import AibafuTool, output_file
import logging
# create log folder
Path('./log').mkdir(parents=True, exist_ok=True)
# output log to file with now time
logging.basicConfig(filename=f"./log/{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.log", filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
dev_logger: logging.Logger = logging.getLogger(name='dev')
dev_logger.setLevel(logging.DEBUG)
handler: logging.StreamHandler = logging.StreamHandler()
formatter: logging.Formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
dev_logger.addHandler(handler)

VERSION = 'V00.00.07'

class App(tk.Frame):
    def __init__(self, master: Tk):
        super().__init__(master)
        self.master = master
        self.master.title('Shorten URL APP')
        self.master.geometry('300x400')
        self.app_version = VERSION
        self.aibabu = AibafuTool()
        self.file_path = ''
        self.df = None
        self.shorten_url_list = []
        self.created_today = 0
        dev_logger.info(f'APP Version: {self.app_version}')
        dev_logger.info(f'API_KEY: {self.aibabu.api_key}')
        dev_logger.info(f'GROUP_ID: {self.aibabu.group_id}')
        
        ttk.Button(master, text="Choose File",
                   default="active", command=self.select_file).grid()
        # ttk.Button(master, text="Stop", default="active", command=self.stop).grid()
        ttk.Button(master, text='Quit', default='active', command=self.master.destroy).grid()
        
    def stop(self):
        self.df['shorten link'] = self.shorten_url_list
        output_path = self.file_path.replace('.xlsx', '_shorten.xlsx')
        self.df.to_excel(output_path, index=False)
        dev_logger.info(f'Process {len(self.df)} urls')
        dev_logger.info(f'Created {self.created_today} urls today')
        dev_logger.info(f'Write to {output_path}')
        self.file_path = ''
        self.df = None
        self.shorten_url_list = []
        self.created_today = 0
        
    def select_file(self):
        self.file_path = filedialog.askopenfilename(
            initialdir='.',
            title='Select folder')
        if self.file_path == '':
            return
        self.df = pd.read_excel(self.file_path)
        output_path = self.file_path.replace('.xlsx', f'_shorten_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
        
        self.shorten_url_list = pd.DataFrame(columns=['Link', 'shorten link'])
        self.created_today = 0
        cnt = 0
        # loop top 10 rows
        for target_url in self.df['Link']:
            # add time sleep
            sleep(0.21) # API接口调用频率限制为5次/秒
            try:
                shorten_url = self.aibabu.get_shorten_url(target_url)
                self.shorten_url_list = pd.concat([
                    self.shorten_url_list,
                    pd.DataFrame({
                        'Link': [target_url],
                        'shorten link': [shorten_url['render_url']]
                    }),
                ], ignore_index=True)
                self.created_today = shorten_url['created_today']
                cnt += 1
                dev_logger.info(f'Count({cnt}): {shorten_url["render_url"]}')
                if cnt % 50 == 0:
                    output_file(self.df, self.shorten_url_list, output_path)
            except Exception as e:
                dev_logger.error(f'{str(e)}')
                continue
        output_file(self.df, self.shorten_url_list, output_path)
        dev_logger.info(f'Process {cnt} urls')
        dev_logger.info(f'Created {self.created_today} urls today')
        dev_logger.info(f'Write to {output_path}')
        
    # def create_popup(self, msg: str):
    #     # popup = tk.Toplevel(self.master)
    #     # popup.title("Warning")
    #     # popup.geometry("300x200")
    #     # label = tk.Label(popup, text=str(msg))
    #     # label.pack()
    #     window = tk.Toplevel()
    #     label = tk.Label(window, text="Hello World!")
    #     label.pack(fill='x', padx=50, pady=5)

    #     button_close = tk.Button(window, text="Close", command=window.destroy)
    #     button_close.pack(fill='x')
        
if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    app.mainloop()
