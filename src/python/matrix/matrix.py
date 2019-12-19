# -*- coding: utf-8 -*-
"""
Data models used for generating the matrix.

Row: defines a general data model for a row within a file

FileDOM: defines a data model for the file 

MatrixDOM: defines a data model for the matrix 

Organization: MDIBL
Author: Lucie N. Hutchins
Contact: lucie.hutchins@mdibl.org
Creation Date: January 2019
Modification Date: December 2019

"""
import os
from os.path import isfile
import pandas as pd

"""
Row object
 Stores the line content into a list of fields
 Split the line using the user's specified delimitter
 Default delimitter "\t"
"""
class Row:
     def __init__(self,_line=None,_delimit="\t"):
          self.content=[]
          self.__set(_line,_delimit)

     def get_len(self):
         return len(self.content)

     def get_value(self,index):
         if index < self.get_len(): return self.content[index]
         else: return ""

     def __set(self,line,delimit):
          try:
               self.content=line.strip().split(delimit)
          except:
               print("ERROR in line: %s \n"%(line))
               pass 

"""
FileDOM: a data  model for the input file
"""
class FileDOM(Row):
     def __init__(self,file_name=None,file_id=None,delimiter="\t",rowids_index=0):
          self._file_name=file_name
          self._file_id=file_id
          # header is an object of type Row
          self._header=None
          self._delimiter=delimiter
          self._lines_count=0
          self._file_obj=None        # file handler
          self._set()

     def _set(self):
          if isfile(self._file_name):
               try:
                   # Check if file is empty
                   if(os.stat(self._file_name) !=0):
                       self._file_obj= open(self._file_name)
                       # Set header to the first line of the file
                       self._header=self.get_line()
                       #set lines count including header line
                       self._set_line_count()
               except:raise
                         
     def _set_line_count(self):
          i=0
          self._file_obj.seek(0)
          for i,line in enumerate(self._file_obj):pass
          self._lines_count=i+1
          self._file_obj.seek(0)

     def get_dict(self,labels_index,data_index):
         self._file_obj.seek(1)
         dict={}
         try:
             for i,line in enumerate(self._file_obj):
                 row=Row(line,self._delimiter)
                 index_value=None
                 if data_index < len(row.content):
                     dict[row.content[labels_index]]=row.content[data_index]
                 else: dict[row.content[labels_index]]=index_value
         except:pass
         self._file_obj.seek(0)
         return dict

     def get_lines_count(self):return self._lines_count
     def get_file_header(self): return self._header
     def get_file_name(self):return self._file_name
     def get_line(self):
          return Row(self._file_obj.readline(),self._delimiter)

"""
MatrixDOM: Creates a data object model for the matrix
"""
class MatrixDOM(FileDOM):
     def __init__(self,file_list=None,vIndex=0,jIndex=None,roundValue=False,delimiter="\t"):
          self._rowVectorColumnIndex=vIndex    # Index of the colunm that has ids 
          self._targetColumnIndex=jIndex       # Index of the column that has values
          self._round2NearestInt=roundValue    # True -> round to the nearest integer , False -> do not round (default)
          self.file_objects=[]                 # A container of file objects
          self._delimiter=delimiter
          self._set(file_list)

     def _set(self,file_list):
          if file_list is not None:
               for i,input_file in enumerate(file_list):
                    file_id=self.get_file_id(i+1) 
                    self.file_objects.append(FileDOM(input_file,file_id,self._delimiter,self._rowVectorColumnIndex))
     #
     # Returns a matrix of files with the associated rows count
     def get_rows_count(self):
          files={}
          for i, file_obj in enumerate(self.file_objects):
               files[file_obj.get_file_name()]=file_obj.get_lines_count()
          return files
     
     """
     get_file_id: Creates a unique ID for each file
     FileID has a format: fxx - where xx is the column index of the file in the matrix
     """
     def get_file_id(self,file_index):
         return "f"+str(file_index)
     
     """
     get_header_columns_count:
     Returns a dictionary of files with the associated colunm header fields count
     """
     def get_header_columns_count(self):
          files={}
          for i,file_obj in enumerate(self.file_objects):
               file_header=file_obj.get_file_header()
               files[file_obj.get_file_name()]=file_header.get_len()
          return files
     
     """
     gen_columns_rows_count:  
     Creates a log of a colunmCount, rowCount matrix 
     where the file_name is the key
     """
     def gen_columns_rows_count(self):
          colunms_rows={}
          for file_name,row_count in self.get_rows_count().items():
               colunms_rows[file_name]=[]
               column_header=self.get_header_columns_count()
               column_count=column_header[file_name]
               colunms_rows[file_name].append(column_count)
               colunms_rows[file_name].append(row_count)
          return colunms_rows
     
     """
     get_matrix_columns:
     Returns a pair of file_id/file_data  matrix.
     The file id is the key of the matrix
     """
     def get_matrix_columns(self):
         try:
             for i, file_obj in enumerate(self.file_objects):
                 yield file_obj._file_id,file_obj.get_dict(self._rowVectorColumnIndex,self._targetColumnIndex)
         except:pass

     """
     get_panda_matrix:
     Generates the matrix using pandas library - the NaN vules are
     filled with user's specified missing_value
     """
     def get_panda_matrix(self,fd,missing_value):
         try:
             df=pd.DataFrame({file_id:file_obj for file_id,file_obj in self.get_matrix_columns()})
             fd.write("\t".join(self.get_columns_header())+"\n") 
             for target_name,row in df.iterrows():
                 fd.write("\t".join(self.get_dataFrame2table_row(target_name,row,missing_value))+"\n")
         except:pass

     """
     get_dataFrame2table_row:
     A generator function that converts pandas generated dataFrame.row into a table row
     It fills the NaN values with the user's provided missing_value
     """
     def get_dataFrame2table_row(self,target,row,missing_value):
         try:
             yield target
             for i, file_obj in enumerate(self.file_objects):
                 file_id=file_obj._file_id
                 if pd.isna(row[file_id]):
                     yield missing_value
                 elif row[file_id] is not None:
                     yield row[file_id]
                 else:
                     yield missing_value
         except: pass

     """
     get_matrix_label:  returns the labels of both the data column and the index column 

     """
     def get_matrix_label(self):
         label={}
         file_header=self.file_objects[0].get_file_header()
         label["rowLabel"]=file_header.get_value(self._rowVectorColumnIndex)
         label["targetLabel"]=file_header.get_value(self._targetColumnIndex)
         return label

     """
     get_columns_header:
     A generator function that formats the matrix header
     and returns a list of column headers
     """
     def get_columns_header(self):
         try:
             file_header=self.file_objects[0].get_file_header()
             target_name=file_header.get_value(self._targetColumnIndex)
             rowidsname=file_header.get_value(self._rowVectorColumnIndex)
             yield rowidsname
             for i, file_obj in enumerate(self.file_objects):
                 yield file_obj._file_id+"."+target_name
         except:pass

     """
      gen_files_summary: Generates a log with the following fields:
      1) fileID
      2) filenname
      3) columnsCount
      4) rowsCount
     """
     def gen_files_summary(self,fd):
          colunms_rows=self.gen_columns_rows_count()
          fd.write("FileID\tFileName\tColunmsCount\tRowsCount\tRowIDsHeader\tTargetColunmHeader\n")
          for i, file_obj in enumerate(self.file_objects):
               file_name=file_obj.get_file_name()
               file_header=file_obj.get_file_header()
               target_name=file_header.get_value(self._targetColumnIndex)
               rowidsname=file_header.get_value(self._rowVectorColumnIndex)
               fd.write("f%d\t%s\t%d\t%d\t%s\t%s\n"%(i+1,file_name,colunms_rows[file_name][0],
                        colunms_rows[file_name][1],rowidsname,target_name)) 
