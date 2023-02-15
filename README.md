# Monthly Report Crawler

## Install Python 3.9 on Ubuntu 20.04

### Step 1 – Install Required Dependencies

Before starting, it is recommended to update the APT packages cache to the latest version. You can update them by running the following command:
```shell
apt-get update -y
```
<br>
Next, you will need to install some packages required to install Python 3.9. Run the following command to install all dependencies:  

```shell
apt-get install software-properties-common apt-transport-https gnupg2 -y
```

### Step 2 – Install Python 3.9
By default, Python version 3.9 is not available in the Ubuntu standard repository. So you will need to add the dead snakes PPA to your system
<br><br>
Run the following command to add the dead snakes PPA to your system:

```shell
add-apt-repository ppa:deadsnakes/ppa
```
<br>
Once the repository is added, update the repository cache and install the Python 3.9 with the following command:

```shell
apt-get update -y
apt-get install python3.9 -y
```

<br>
Once Python 3.9 has been installed, you can verify the installed version of Python using the command below:

```shell
python3.9 --version
#output Python 3.9.1
```

### Step 3 – Set the Default Python Version

If an older version of Python3.8 is already installed in your system then you will need to set your default Python version to Python 3.9.
<br><br>
First, check the default Python version using the following command:

```shell
python3 --version
#output Python 3.8.10
```

<br>
The above output indicates that you have multiple version of Python in your system.
<br><br>
You can also check all Python versions in your system using the following command:

```shell
ls /usr/bin/python*
#output /usr/bin/python3  /usr/bin/python3.8  /usr/bin/python3.9
```

<br>
Next, you will need to update your update-alternatives before setting the default Python version. You can update it with the following command:

```shell
update-alternatives --install /usr/bin/python3 python /usr/bin/python3.9 1
update-alternatives --install /usr/bin/python3 python /usr/bin/python3.8 2
```

<br>
Next, verify whether both versions are updated or not with the following command:

```shell
update-alternatives --list python
#output /usr/bin/python3.8
#output /usr/bin/python3.9
```

<br>
Next, set your default Python version to 3.9 using the following command:

```shell
update-alternatives --config python
```

<br>
You will be asked to set the default Python version as shown below:

```shell
Selection    Path                Priority   Status
------------------------------------------------------------
* 0            /usr/bin/python3.8   2         auto mode
  1            /usr/bin/python3.8   2         manual mode
  2            /usr/bin/python3.9   1         manual mode
 
Press  to keep the current choice[*], or type selection number: 2
```
Type 2 and press Enter to set the default Python version. You should get the following output:

```shell
update-alternatives: using /usr/bin/python3.9 to provide /usr/bin/python (python) in manual mode
```
<br>
Now, you can verify your default Python version using the following command:

```shell
python3 --version
# output Python 3.9.1
```


### Step 4 – Fix pip and disutils errors

#### Fix Python3-apt

Running pip in terminal will not work, as the current pip is not compatible with Python3.10 and python3-apt will be broken, that will generate an error like
<br>
```shell
Traceback (most recent call last):   
    File "/usr/lib/command-not-found", line 28, in <module>     
        from CommandNotFound import CommandNotFound   
    File "/usr/lib/python3/dist-packages/CommandNotFound/CommandNotFound.py", line 19, in <module>     
        from CommandNotFound.db.db import SqliteDatabase   
    File "/usr/lib/python3/dist-packages/CommandNotFound/db/db.py", line 5, in <module>     
        import apt_pkg ModuleNotFoundError: No module named 'apt_pkg'
```
<br>
To fix this first remove the current version of python3-apt by running

```shell
apt remove --purge python3-apt
```

<br>
Then do some cleanup

```shell
apt autoclean
```

<br>
Finally, reinstall python3-apt by running

```shell
apt install python3-apt
```

### Step 5 – Install pip & distutils

```shell
apt install python3.9-distutils
```
<br>
install pip by running

```shell
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.9 get-pip.py
```

```shell
pip
#output pip --version
```

## Install Poetry

```shell
curl -sSL https://install.python-poetry.org | python3 -
vim ~/.bashrc
export PATH="/root/.local/bin:$PATH"
source ~/.bashrc
```

```shell
poetry --version
#output Poetry (version 1.3.2)
```

## Install Monthly Report Crawler Project

### Step 1 - git clone repo

git clone repo
```shell
cd /home/readmin/
git clone http://172.31.251.105/backend/monthly-report-crawler.git
```

### Step 2 - Init Poetry Project

Modify poetry config

```shell
poetry config virtualenvs.in-project true
```

Create virtual env

```shell
poetry env use python3.9
```

Install package

```shell
poetry install
```
