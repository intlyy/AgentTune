import re
import pandas as pd
from schema_alter import *
import json


class WP():
    def __init__(self) -> None:
        self.dbs=None
        pass
    
    # analyze schema info
    def parse_schema(self,schema_path):
        jsonFile = open(schema_path,'r')
        input = json.loads(jsonFile.read())
        # print(input)
 
        all_tables = []
 
        cons = []
        foreign_cons = []

        for table in input['Tables']:
            tb_name = table['Table Name']
            tb_col_distribution = table['Column Distribution']
            tb_cols = []
            for col in table['Table Columns']:
                col_name = col['Column Name']
                col_type = col['Data Type']
                
                if 'Data Type Mod' in col.keys():
                    col_type_mod=col['Data Type Mod']
                else:
                    col_type_mod=None
                if 'Data Distribution' in col.keys():
                    col_domain=col['Data Distribution']
                else:
                    col_domain=None
                    
                tb_cols.append(column(col_name,col_type,col_type_mod,col_domain))
            
            prim_key = key(table['Primary Key']['Name'],table['Primary Key']['Data Type'])
            for con in table['Foreign Key']:
                foreign_cons.append(foreign_constraint(tb_name,key(con['Foreign Key Name'],con['Foreign Key Type']),
                                                    con['Referenced Table'],key(con['Referenced Primary Key'],con['Referenced Primary Key Type'])))
            all_tables.append(Table(tb_name,tb_cols,prim_key,foreign_cons,tb_col_distribution))
        
        self.dbs=DBschema(tbs=all_tables,foreign_constraint=foreign_cons)
        return
    
    # analyze workload info
    def parse_workload(self,workload_path):
        pd.set_option('max_colwidth',-1)
   
        df = pd.read_csv("workloads/"+workload_path+".txt", header=None,error_bad_lines=False,sep = r'\s+\n',index_col=0) 
        # df=pd.read_csv("seats_workload.txt",header=None)
        read_cnt=0
        write_cnt=0
        predicate_num=0
        group_by_num=0
        order_by_num=0
        aggr_num=0
        dict={}
        tbl_dict={}
        col_dict={}
        tokens=""
        for i in df.index.values:
            tokens+=i
            tokens+=" "

        token_list=re.split(r'[\(,;\s\)\n\t]+',tokens)
        # for i in range(len(df)):
        if True:    
            # token_list=str(df.iloc[i]).split()
            # token_list=re.split(r'[,; \n\t]+',str(df.iloc[i]))
    
            for id,j in enumerate(token_list):
                if j.upper()=='SELECT':
                    read_cnt+=1
                    # j_=j
                    # while token_list[j_]!='FROM' and token_list[j_]!=';':
                if j.upper()=='UPDATE' or j.upper()=='INSERT':
                    write_cnt+=1
                if j.upper()=='AND' or j.upper()=='OR' or j.upper()=="WHERE":
                    predicate_num+=1
                if j.upper()=='FROM' or j.upper()=='JOIN':
                    # print(token_list[id:id+5])
                    table_name=token_list[id+1]
                    if table_name.upper()=='SELECT' or table_name.isdigit()==True:
                        # print("circle find.")
                        # print(token_list[id-1:id+5])
                        continue
                    if table_name[len(table_name)-1]==',' or table_name[len(table_name)-1]==';':
                        table_name=table_name[0:len(table_name)-1]
                    if table_name not in tbl_dict.keys():
                        tbl_dict[table_name]=1
                    else:
                        tbl_dict[table_name]+=1
                    # print(table_name[0:min(len(table_name),10)])
                    if table_name not in list(dict.keys()):
                        dict[table_name]=1
                    else:
                        dict[table_name]+=1
                if j.upper()=='GROUP' and token_list[id+1].upper()=="BY":
                    group_by_num+=1
                if j.upper()=='ORDER' and token_list[id+1].upper()=="BY":
                    order_by_num+=1
                if j.upper()[0:3]=="SUM" or j.upper()[0:3]=="MIN" or j.upper()[0:3]=="MAX" or j.upper()[0:3]=="AVG":
                    aggr_num+=1
        maxi=""
        maxv=0
        mini=""
        minv=100000000    
        sumv=0            
        for i in list(dict.keys()):
            sumv+=dict[i]
            if dict[i]>maxv:
                maxv=dict[i]
                maxi=i
            if dict[i]<minv:
                minv=dict[i]
                mini=i
                

        print("type of workload :",workload_path)
        print("total token num :",len(token_list))
        print("sample SQL :",re.split(r'[,;\s\n\t\(\)]+',str(df.iloc[0].name)))
        print("size of workload :",tokens.count(";"))
        print("read write ratio : "+str(read_cnt)+"|"+str(write_cnt)+"  "+str(read_cnt/(write_cnt+read_cnt)))
        print("group by ratio : "+str(group_by_num/(write_cnt+read_cnt)))
        print("order by ratio : "+str(order_by_num/(write_cnt+read_cnt)))
        print("aggregation ratio : "+str(aggr_num/(write_cnt+read_cnt)))
        print("average predicate num per SQL :",str(predicate_num/(read_cnt+write_cnt)))
        print("max visited table :",maxi,str(maxv/sumv))
        print("min visited table :",mini,str(minv/sumv))
        print("table access pattern :")
        for i in tbl_dict:
            print("\t",i,tbl_dict[i])
        print()
        
