from Parserbase import *
import configparser
import os
import sys
class WP2(WP):
    def __init__(self) -> None:
        self.dbs=None
        pass
    
    # workload analysis function
    def parse_workload(self,workload_path):
        if self.dbs==None:
            print("fatal error: dbs not initialization correctly.")
            return
        else:
            read_cnt=0
            write_cnt=0
            predicate_num=0
            group_by_num=0
            order_by_num=0
            aggr_num=0
            desc_num=0
            non_agg_count=0
            
            tbl_dict={}
            tbl_col_dict={}
            predicate_dict={}
            predicate_type=["=",">","<",">=","<="]
            for i in predicate_type:
                predicate_dict[i]=0
            
            # Set the output window environment to display all information
            pd.set_option('max_colwidth',None)
            df = pd.read_csv(workload_path, header=None,on_bad_lines='skip',sep = r'\s+\n',index_col=0,engine='python') 
            # df=pd.read_csv("seats_workload.txt",header=None)
            
            tokens=""
            for i in df.index.values:
                tokens+=i
                tokens+=" "
        
            # Using regular expressions to segment
            sql_list=re.split('[\s]*;[\n]*[\s]*',tokens)
            # token_list=re.split(r'[\(,;\s\)\n\t]+',tokens)
            # print(sql_list[-3:])
            for i in range(len(sql_list)):
                import psqlparse
                if sql_list[i]=="" or sql_list[i]==' ':
                    continue
                # print("i: ",sql_list[i])
                real_tb_used=psqlparse.parse(sql_list[i]+";")[0].tables()
                # print(real_tb_used)
                for table_name in real_tb_used:
                    if table_name not in tbl_dict.keys():
                        tbl_dict[table_name]=1
                        tbl_col_dict[table_name]={}
                        tb_tmp=self.dbs.getTableByName(table_name)
                        # print(table_name)
                        for it in tb_tmp.col:
                            tbl_col_dict[table_name][it.name]=0
                    else:
                        tbl_dict[table_name]+=1
                
                match = re.search(r'SELECT\s+(.*?)\s+FROM', sql_list[i], re.IGNORECASE)
                
                if match:
                    columns_part = match.group(1).strip()
                    if columns_part=='*':
                        non_agg_count+=1
                        warnings.warn(
                            "Detected SELECT * usage, which may affect performance and result in unnecessary column returns",
                            category=RuntimeWarning
                        )
                    else:
                        agg_pattern=re.compile(
                            r'\b(COUNT|SUM|AVG|MAX|MIN|STDDEV|VARIANCE|GROUP_CONCAT)\s*\(.*?\)',
                            re.IGNORECASE
                        )
                    columns = [col.strip() for col in columns_part.split(',')]
                    for col in columns:
                        if not agg_pattern.search(col):
                            non_agg_count+=1
                    # print(non_agg_count)
    
                simple_sql_token_list=re.split(r'[\(,;\s\)\n\t]+',sql_list[i])
                if simple_sql_token_list.__contains__("")==True:
                    simple_sql_token_list.remove("")
                # print(simple_sql_token_list)
                cnt_bool=False
                #  Query Semantic Features
                for id,j in enumerate(simple_sql_token_list):
                    if cnt_bool==False:
                        if j.upper()=='SELECT':
                            read_cnt+=1
                            cnt_bool=True
                        if j.upper()=='UPDATE' or j.upper()=='INSERT':
                            write_cnt+=1
                            cnt_bool=True
                    
                    if j.upper()=='AND' or j.upper()=='OR' or j.upper()=="WHERE":
                        predicate_num+=1
                    elif j.upper()=='GROUP' and simple_sql_token_list[id+1].upper()=="BY":
                        group_by_num+=1
                    elif j.upper()=='ORDER' and simple_sql_token_list[id+1].upper()=="BY":
                        order_by_num+=1
                    elif j.upper()=="SUM" or j.upper()=="MIN" or j.upper()=="MAX" or j.upper()=="AVG":
                        aggr_num+=1
                    elif j.upper()=="DESC":
                        desc_num+=1
                    elif j in predicate_type:
                        predicate_dict[j]+=1
                    else:
                        # if j=='supplier':
                        #     print(simple_sql_token_list[id-1:id+5])
                        pass
                        
                # Data Access Features
                for token in simple_sql_token_list:
                    for tb_tmp in real_tb_used:
                        for col_tmp in tbl_col_dict[tb_tmp].keys():
                            if token==col_tmp:
                                # print("table_name : ",tb_tmp,"col_name : ",col_tmp)
                                tbl_col_dict[tb_tmp][col_tmp]+=1
                    tmp_res=re.match(".+\..+",token)
                    if tmp_res!=None:
                        # print(tmp_res.group().split("."))
                        if tmp_res.group().split(".")[0] in real_tb_used:
                            # print(tmp_res.group().split()[0],tmp_res.group().split()[1])
                            tbl_col_dict[tmp_res.group().split(".")[0]][tmp_res.group().split(".")[1]]+=1
        maxi=""
        maxv=0
        mini=""
        minv=100000000    
        sumv=0            

        
        for table in self.dbs.tables:
            if table.name not in tbl_dict.keys():
                tbl_dict[table.name]=0
                tbl_col_dict[table.name]={}
                for it in table.col:
                    tbl_col_dict[table.name][it.name]=0
            
        for i in list(tbl_dict.keys()):
            sumv+=tbl_dict[i]
            if tbl_dict[i]>maxv:
                maxv=tbl_dict[i]
                maxi=i
            if tbl_dict[i]<minv:
                minv=tbl_dict[i]
                mini=i
                
        print("type of workload :",workload_path)
        # print("total token num :",len(token_list))
        print("sample SQL1:",re.split(r'[,;\s\n\t\(\)]+',str(df.iloc[0].name)))
        print("sample SQL2:",re.split(r'[,;\s\n\t\(\)]+',str(df.iloc[1].name)))
        print("size of workload :",tokens.count(";"))
        print("read write ratio : "+str(read_cnt)+"|"+str(write_cnt)+"  "+str(read_cnt/(write_cnt+read_cnt)))
        print("group by ratio : "+str(group_by_num/(write_cnt+read_cnt)))
        print("order by ratio : "+str(order_by_num/(write_cnt+read_cnt)))
        print("aggregation ratio : "+str(aggr_num/(write_cnt+read_cnt)))
        print("average predicate num per SQL :",str(predicate_num/(read_cnt+write_cnt)))
        print("max visited table :",maxi,str(maxv/sumv))
        print("min visited table :",mini,str(minv/sumv))
        
        print("average table access count :",sumv/tokens.count(";"))
        print("average item returned count per query :",non_agg_count/tokens.count(";"))
        print("order by logic ratio :",(order_by_num-desc_num)/order_by_num,"(asc):",desc_num/order_by_num,"(desc)")
        
        print("where clause comparison condition ratio :")
        for i in predicate_type:
            print("\t",i,predicate_dict[i]/sum(predicate_dict.values()))
        
        print("table access pattern :")
        # tbl_dict record the access patterns of each table and column
        for i in tbl_dict:
            print("\t",i,str(tbl_dict[i])+"|"+str(sumv),"\t",tbl_dict[i]/sumv)
            tmp_sum=0
            for j in tbl_col_dict[i]:
                tmp_sum+=tbl_col_dict[i][j]
            if tmp_sum==0:
                continue
            for j in tbl_col_dict[i]:
                # print('\t',j)
                print("\t\t",j,str(tbl_col_dict[i][j])+"|"+str(tmp_sum),"\t",tbl_col_dict[i][j]/tmp_sum)
        print()
        
import psqlparse
import argparse

if __name__=='__main__':

    config = configparser.ConfigParser()
    config.read('./config.ini')
    defaults = {
        "workload_file": "./input.json",
        "config_file": "./input.json",
        "output_file": "./workload_features"
    }
    if config.has_section('workload analyzer'):
        defaults.update(config['workload analyzer'])

    parser = argparse.ArgumentParser()
    parser.add_argument('--workload_file', type=str, default=defaults['workload_file'])
    parser.add_argument('--config_file', type=str, default=defaults['config_file'])
    parser.add_argument('--output', type=str, default=defaults['output_file'])
    args = parser.parse_args()
    print(args)

    if args.output:
        sys.stdout = open(args.output, 'w')
    
    files=[args.workload_file]
    
    wp=WP2()
    wp.parse_schema(args.config_file)
    # print(wp.dbs.toStr())
    # print(wp.dbs.getTableByName('lineitem'))
    # print(type(wp.dbs.getTableByName('lineitem').col))
    for i in files:
        print(i)
        wp.parse_workload(i)