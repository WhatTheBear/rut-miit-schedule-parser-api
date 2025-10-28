from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from utils import Parser


DB_CONNECTION_FAILED = 0
DB_CONNECTION_SUCCEED = 1
DB_DATA_GET_FAILED = 2
DB_DATA_GET_SUCCEED = 3
DB_DATA_WRITE_FAILED = 4
DB_DATA_WRITE_SUCCEED = 5
DB_DATA_DELETE_FAILED = 6
DB_DATA_DELETE_SUCCEED = 7



class Journal:

    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.client = []

    
    def _update_groups_list(self):
        pass

        
    def connect_db(self) -> int:
        
        try:
            self.client = MongoClient(self.connection_string)

            return DB_CONNECTION_SUCCEED

        except ServerSelectionTimeoutError: 
            
            return DB_CONNECTION_FAILED


    def getGroupNameById(self, groupId: int) -> str:
        query = {"groupId": groupId}

        return self.client.journal.groups.find_one(query)["groupName"]

        
    def getGroupIdByName(self, groupName: str) -> str:

        query = {"groupName": groupName}

        return self.client.journal.groups.find_one(query)["groupId"]
    
    def getUserGroupId(self, userId: int) -> int:

        query = {"userId": userId}

        return self.client.journal.users.find_one(query)["groupId"]

