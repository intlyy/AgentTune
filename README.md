# AgentTune: A Multi-Agent Collaborative Framework for Database Knob Tuning

This is the source code to the paper "AgentTune: A Multi-Agent Collaborative Framework for Database Knob Tuning". Please refer to the paper for the experimental details.

## Table of Content




* [Environment Installation](https://anonymous.4open.science/r/AgentTune)
* [Workload Preparation](https://anonymous.4open.science/r/AgentTune)
* [Candidate Knobs Preparation](https://anonymous.4open.science/r/AgentTune)
* [Quick Start](https://anonymous.4open.science/r/AgentTune)



  



 


## Environment Installation

In our experiments,  We conduct experimets on MySQL 5.7.

1. Preparations: Python == 3.10

2. Install packages

   ```shell
   pip install -r requirements.txt
   pip install .
   ```

3. Download and install MySQL 5.7 and boost

   ```shell
   wget http://sourceforge.net/projects/boost/files/boost/1.59.0/boost_1_59_0.tar.gz
   wget https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-boost-5.7.19.tar.gz
   
   sudo cmake . -DCMAKE_INSTALL_PREFIX=PATH_TO_INSTALL -DMYSQL_DATADIR=PATH_TO_DATA -DDEFAULT_CHARSET=utf8 -DDEFAULT_COLLATION=utf8_general_ci -DMYSQL_TCP_PORT=3306 -DWITH_MYISAM_STORAGE_ENGINE=1 -DWITH_INNOBASE_STORAGE_ENGINE=1 -DWITH_ARCHIVE_STORAGE_ENGINE=1 -DWITH_BLACKHOLE_STORAGE_ENGINE=1 -DWITH_MEMORY_STORAGE_ENGINE=1 -DENABLE_DOWNLOADS=1 -DDOWNLOAD_BOOST=1 -DWITH_BOOST=PATH_TO_BOOST;
   sudo make -j 16;
   sudo make install;
   ```



## Workload Preparation 

### SYSBENCH

Download and install

```shell
git clone https://github.com/akopytov/sysbench.git
./autogen.sh
./configure
make && make install
```

Load data

```shell
sysbench --db-driver=mysql --mysql-host=$HOST --mysql-socket=$SOCK --mysql-port=$MYSQL_PORT --mysql-user=root --mysql-password=$PASSWD --mysql-db=sbtest --table_size=800000 --tables=150 --events=0 --threads=32 oltp_read_write prepare > sysbench_prepare.out
```

### Join-Order-Benchmark (JOB)

Download IMDB Data Set from http://homepages.cwi.nl/~boncz/job/imdb.tgz.

Follow the instructions of https://github.com/winkyao/join-order-benchmark to load data into MySQL.

### TPCC and TPC-DS
Follow the instructions of https://www.tpc.org/default5.asp to prepare TPC benchmarks.

## Candidate Knobs Preparation
In `./knob selector/get_candidate_knobs/`, we use MySQL as an example to demonstrate how to quickly obtain candidate knobs by processing the official documentation.

## Quick Start

1. modify `config.ini`
2. set benchmark path in `./configuration recommender/DB_client.py`
3. ./run.bash