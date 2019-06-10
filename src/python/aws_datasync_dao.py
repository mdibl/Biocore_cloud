# -*- coding: utf-8 -*-
"""
Defines operation on AwsDataSyncDOM object.

Returns:
     Sets global  
Raises:
     Nothing

Organization: MDIBL
Author: Lucie N. Hutchins
Contact: lucie.hutchins@mdibl.org
Date: May 2019

"""
from objects_dom import AwsDataSyncDOM
import io,json

class DataSyncDAO(AwsDataSyncDOM):
    def __init__(self):
        AwsDataSyncDOM.__init__(self)

    ## Get Account summary:
    """
    """
    def get_account_summary(self):
        summary={}
        summary["account_id"]=self.account_id
        summary["region_id"]=self.region_id
        summary["subnet_id"]=self.subnet_id
        summary["security_group_id"]=self.security_group_id
        summary["datasync_active_agents"]=self.get_agents_online()
        summary["datasync_locations"]=self.get_locations()
        summary["datasync_tasks"]=self.get_tasks()
        summary["current_efs_file_systems"]=self.get_efs_file_systems()

        return summary
        
if __name__== "__main__":
    msg="Hello"
    print("%s\n"%(msg)) 
    datasync_obj=DataSyncDAO()
    json_data=datasync_obj.get_account_summary()
    json_file="datasync.json" 
    try:
        to_unicode = unicode
    except NameError:
        to_unicode = str
    with io.open(json_file, 'w', encoding='utf8') as outfile:
         str_ = json.dumps(json_data,indent=4, sort_keys=True,separators=(',', ': '), ensure_ascii=False)
         outfile.write(to_unicode(str_))
