# AgentTune: A Multi-Agent Collaborative Framework for Database Knob Tuning *[Accepted by SIGMOD 2026]*

This is the source code to the paper **"AgentTune: A Multi-Agent Collaborative Framework for Database Knob Tuning"**. Please refer to the paper for the experimental details.

## Table of Content
* [Environment Installation](#environment-installation)
* [Workload Preparation](#workload-preparation)
* [Quick Start](#quick-start)
* [Scalability Study](#scalability-study)
* [Ablation Study](#ablation-study)

## Environment Installation

In our experiments,  We conduct experiments on MySQL 5.7.

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



## Quick Start

1. Modify `config.ini`
2. Set benchmark path in `./configuration recommender/DB_client.py`
3. Run
   ```shell
   ./run.bash
   ```

The four agents in **AgentTune**—**Workload Analyzer, Knob Selector, Range Pruner, and Configuration Recommender**—will execute sequentially. Intermediate results will be saved to the location you specified in `config.ini`, and all tuning records and results will be stored in the `./configuration recommender/record` directory.

## Scalability Study
This section introduces how to expand **AgentTune** to encompass new database scales, engines, and hardware environments. Detailed experimental results and analysis can be found in **Section 8.3** of the paper.
### Database Scale
When the database scale changes, simply modify `config.ini` by setting:
- `database_scale` = new database scale
- `database_name` = DB_Name *(If you create a new database)*

### Hardware
When the hardware environment changes, simply modify `config.ini` by setting:
- `hardware` = new hardware configuration

### Database Engine
1. Download and install the new database engine
2. Prepare workload in the new database engine
3. Prepare candidate knobs

   In `./knob selector/get_candidate_knobs/`, we use MySQL as an example to demonstrate how to quickly obtain candidate knobs by processing the official documentation.
4. Modify database connection method and knob setting method in `./configuration recommender/DB_client.py`
5. Modify `config.ini` by setting:
   - `database_kernel` = new database engine
   - `database_name` = DB_Name

   and other database configurations including *DB_User, DB_Password, DB_Host* and *DB_Port*.

## Ablation Study
This section introduces how to evaluate the effectiveness of each component in **AgentTune** and the impact of different large language models (LLMs). Detailed experimental results and analysis can be found in **Section 8.4** of the paper.
### Ablation Study - Components
The four agents in **AgentTune** execute sequentially and intermediate results for each component are saved to the location you specified in `config.ini`. So you are free to remove or replace any component to evaluate the effectiveness. However, since the subsequent pruning and tuning stages depend on the selected knobs from the `Knob Selector`, it is recommended to replace this step with alternative methods (e.g., manual selection or ML-based approaches) rather than removing it entirely.

### Ablation Study - Knob Size
To change the knob size in **AgentTune**, simply modify `config.ini` by setting:
- `knob_num` = new knob size

### Ablation study - Beam Size
To change the beam size in **AgentTune**, simply modify `config.ini` by setting:
- `top_k` = new beam size

### Ablation study - LLMs
To change the LLM in **AgentTune**, simply modify `config.ini` by setting:
- `model` = new large language model
