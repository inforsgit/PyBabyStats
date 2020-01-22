import requests
import json
import datetime
import enum

# URL of the Baby Stats public API (docs here: https://babystats.org/apidocs#publicAPIHelp)
# Note in any implementation that calls should be limited to a maximum of 50 in a 5 minute time period
url = 'https://www.babystats.org/api/public'

class BreastSide(enum.Enum):
    UNKNOWN = ''
    LEFT = 'left'
    RIGHT = 'right'
    BOTH = 'both'

class UnitOfMeasurement(enum.Enum):
    NULL = ''
    OUNCES = 'oz'
    MILLILITRES = 'ml'

class BabyStatType(enum.Enum):
    WET = 'Wet'
    FEEDING = 'Feeding'
    STOOL = 'Stool'
    WEIGHT = 'Weight'
    NOTE = 'Note'
    SLEEP = 'Sleep'
    PUMPING = 'Pumping'
    KICK = 'Kick'

class BabyTransactionCollection(list):
    def __init__(self, transactionCollectionJSONData):
        super().__init__()
        
        for transactionJSONData in transactionCollectionJSONData['data']:
            self.append(BabyTransaction(transactionJSONData))
    
    def getTransationCount(self):
        return len(self)

    def getTransactionsForType(self, babyStat)
        transactionList=list()
        
        for transaction in self:
            if transaction.getStatType() == babyStat:
                transactionList.append(transaction)
        
        return transactionList

    def getStatCount(self, babyStat):
        count = 0
        
        for transaction in self:
            if transaction.getStatType() == babyStat:
                count = count + 1
        
        return count


class BabyTransaction:
    def __init__(self, transactionJSONData):
        self.uid = transactionJSONData["uid"]
        self.statType = BabyStatType(transactionJSONData["event"][3:])
        self.eventDateTimeUTC = datetime.datetime.strptime(transactionJSONData["eventDateTimeUTC"], '%Y-%m-%dT%H:%MZ')
        self.eventDateTimeLocal = datetime.datetime.strptime(transactionJSONData["eventDateTimeLocal"], '%Y-%m-%dT%H:%M:%S')
        
        if "note" in transactionJSONData:
            self.note = transactionJSONData["note"]
        else:
            self.note = None
        
        if "weight" in transactionJSONData:
            self.weight = int(transactionJSONData["weight"])
        else:
            self.weight = None
        
        if "feedingMinutes" in transactionJSONData:
            self.duration = timedelta(minutes=transactionJSONData["feedingMinutes"])
        elif "sleepMinutes" in transactionJSONData:
            self.duration = timedelta(minutes=transactionJSONData["sleepMinutes"])
        else:
            self.duration = None
        
        if "uom" in transactionJSONData:
            self.uom = UnitOfMeasurement(transactionJSONData["uom"])
        else:
            self.uom = None
                
        if "breastSide" in transactionJSONData:
            self.breastSide = BreastSide(transactionJSONData["breastSide"])
        else:
            self.breastSide = None
        
        if "bOz" in transactionJSONData:
            self.bOz = float(transactionJSONData["bOz"])
        else:
            self.bOz = None
    
    def getTransactionID(self):
        return self.uid
    
    def getStatType(self):
        return self.statType
    
    def getEventDateTime(self, localTime=False):
        if(localTime):
            return self.eventDateTimeLocal
        else:
            return self.eventDateTimeUTC
    
    def getNote(self):
        return self.note
    
    def getWeight(self):
        return self.weight
    
    def getDuration(self):
        return self.duration
    
    def getUnitOfMeasurement(self):
        return self.uom
    
    def getBreastSide(self):
        return self.breastSide
    
    def getBottleOunces(self):
        return self.bOz
    
class BabyStats:
    def __init__(self, id, accessToken):
        self.id = id
        self.accessToken = accessToken
        
    def makeRequest(self, event, params=dict(), babyName=""):
        # Add the universal fields to the provided params
        params["id"] = self.id
        params["accessToken"] = self.accessToken
        params["event"] = event
        params["babyName"] = babyName
        
        response = requests.post(url, json=params)
        return response.json()

    def addWet(self, babyName=""):
        return self.makeRequest(event="AddWet", babyName=babyName)
    
    def addKick(self, babyName=""):
        return self.makeRequest(event="AddKick", babyName=babyName)
 
    def addStool(self, babyName=""):
        return self.makeRequest("AddStool", babyName=babyName)
        
    def addNote(self, note, babyName=""):
        return self.makeRequest("AddNote", params={ "note" : note }, babyName=babyName)
        
    def addFeeding(self, bottleAmount="", feedingMinutes="", breastSide=BreastSide.UNKNOWN, uom=UnitOfMeasurement.NULL, babyName=""):
        return self.makeRequest("AddFeeding", params={ "bottleOunces": bottleAmount, "breastSide" : breastSide.value, "feedingMinutes" : feedingMinutes, "uom" : uom.value }, babyName=babyName)
    
    def addPumping(self, bottleAmount="", uom=UnitOfMeasurement.NULL, babyName=""):
        return self.makeRequest("AddPumping", params={ "bottleOunces": bottleAmount, "uom" : uom.value }, babyName=babyName)
    
    def addWeight(self, pounds="", ounces="", babyName=""):
        return self.makeRequest("AddWeight", params={ "pounds": pounds, "ounces" : ounces }, babyName=babyName)
        
    def addSleep(self, hours="", minutes="", babyName=""):
        return self.makeRequest("AddSleep", params={ "hours": hours, "minutes" : minutes }, babyName=babyName)
    
    def startSleep(self, babyName=""):
        return self.makeRequest("StartSleep", babyName=babyName)
    
    def stopSleep(self, babyName=""):
        return self.makeRequest("EndSleep", babyName=babyName)
    
    # If breast side is added here then it will be set at this value even when feeding is stopped
    def startFeeding(self, breastSide=BreastSide.UNKNOWN, babyName=""):
        return self.makeRequest("StartFeeding", params={ "breastSide" : breastSide.value }, babyName=babyName)
    
    # If no breast side was selected when starting feeding then it can be input here
    def stopFeeding(self, breastSide=BreastSide.UNKNOWN, babyName=""):
        return self.makeRequest("EndFeeding", params={ "breastSide" : breastSide.value }, babyName=babyName)
    
    def removeLast(self, babyStatType, babyName=""):
        return self.makeRequest("Remove" + babyStatType.value, babyName=babyName)
    
    # The date range is optional, but be aware that if there is a very large dataset then this may take some time to complete and return a lot of data
    # If only a start date is specified then data will be returned for that day only
    def getBabyTransactions(self, startDate="", endDate="", babyName=""):
        if startDate == "" and endDate == "":
          dateRange = ""
        elif endDate == "":
          dateRange = startDate.strftime("%Y-%m-%d")
        else:
          dateRange = startDate.strftime("%Y-%m-%d") + "/" + endDate.strftime("%Y-%m-%d")
        
        requestResult = self.makeRequest("GetTransactionData", params={ "dateRange": dateRange }, babyName=babyName)
        return BabyTransactionCollection(requestResult)