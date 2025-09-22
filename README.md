## Install

`$ pip3 install -r requirements.txt`


## Configure

Edit `config.py`.


## Run

`$ ./notifier.py`


## Run Automatically

Add this line to crontab (`$ crontab -e`):

`0 * * * * cd /path/to/notifier/ && ./notifier.py`
