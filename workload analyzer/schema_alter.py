import numpy as np


class simpleSQL:
    def __init__(self) -> None:
        self.token=[]
        
    # def __init__(self,token = None) -> None:
    #     self.token=token
        
    def add(self,x):
        self.token.append(x)
    
    def toStr(self):
        ans=""
        for i in range(len(self.token)):
            ans+=str(self.token[i].value)
            if i!=len(self.token)-1 \
                and self.token[i].type!="tbname_"\
                    and self.token[i].type!="dot"\
                        and self.token[i].type!="colname_":
                ans+=" "
            # print(str(self.token[i].value)+" ",end="")
        # print()
        return ans+"\n"

class key:
    def __init__(self,value,type) -> None:
        self.value=value
        self.type=type
        # self.name=name
        
    def toStr(self):
        print(f'value : {self.value}')
        print(f'type : {self.type}')

class foreign_constraint:
    def __init__(self,tb1,col1,tb2,col2) -> None:
        self.tb1=tb1
        self.col1=col1
        self.tb2=tb2
        self.col2=col2

class column:
    def __init__(self,name,type,mod=None,domain=None,father=None) -> None:
        self.name=name
        self.data_type=type
        self.data_mod=mod
        self.domain=domain
        self.father=father
        
class Table:
    def __init__(self,tb_name,col,prim_col,foreign_constraint,column_distribution) -> None:
        self.name=tb_name
        self.col=col
        self.col_data_dis={}
        self.prim_col = prim_col
        self.foreign_constraint = foreign_constraint
        self.column_distribution = column_distribution
    
    def addCharacteristics(self,col_name,data_dis):
        col_name_set=set(self.col[0:len(self.col)])
        if col_name not in col_name_set:
            print("error: add data characteristics failed. Col name not found.")
        else:
            self.col_data_dis[col_name]=data_dis

    def hasCol(self,col_name):
        for i in self.col:
            if i.name==col_name:
                return True
        return False
    

class DBschema:
    def __init__(self,tbs,foreign_constraint=None) -> None:
        self.tables=tbs
        # self.tbNum=len(tbs)
        self.foreign_constraint=foreign_constraint

    def toStr(self):
        ans=""
        for i,j in enumerate(self.tables):
            ans+="table "+str(i+1)
            ans+=" : "+j.name
            ans+="\n"
        return ans
    

    def getTableByName(self,tb_name):
        for i in range(len(self.tables)):
            if self.tables[i].name==tb_name:
                return self.tables[i]
        return None