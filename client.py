
import requests
import json


class STClient:
	def __init__(self, *args, **kwargs):
		self.username = kwargs.get('user')
		self.token = kwargs.get('token')
		self.baseGameURI = 'https://api.spacetraders.io/game/'
		self.baseUsersURI = 'https://api.spacetraders.io/users/'
		self.headers = {'Authorization':f'Bearer {self.token}'}
		self.endpoints = {'status':'status/', 
							'system':'systems/', 
							'locations':'locations/', 
							'loans':'loans/',
							'ships':'ships/',
							'market':'marketplace/',
							'purchase':'purchase-orders/',
							'sell':'sell-orders/',
							'flightplans':'flight-plans/'}
	
	def craftPayload(self, **kwargs):
		if kwargs.get('shipClass') is not None:				#Hack fix cause keyword class is not allowed in kwargs
			kwargs['class'] = kwargs.get('shipClass')
			kwargs.pop('shipClass', None)
		return dict(**kwargs)

	def serverStatus(self):
	 	response = requests.get(url=f"{self.baseGameURI}{self.endpoints['status']}", headers=self.headers).json()


	 	return response

	def claimUsername(self, username):
		response = requests.post(url=f"{self.baseUsersURI}{username}/token", headers=self.headers).json()
		self.token = response['token']
		self.username = response['user']['username']
		with open("cred.txt", "w") as file:
			file.write(f"Username: {self.username}\nToken: {self.token}")
		return response	

	def getUser(self):
		return requests.get(url=f"{self.baseUsersURI}{self.username}", headers=self.headers).json()

	def getAvailableLoans(self):
		return requests.get(url=f"{self.baseGameURI}{self.endpoints['loans']}", headers=self.headers).json()

	def getLoans(self):
		return requests.get(url=f"{self.baseUsersURI}{self.username}{endpoints['loans']}", headers=self.headers).json()

	def payLoan(self, loanId):
		return requests.put(url=f"{self.baseUsersURI}{self.username}{endpoints['loans']}", data=self.craftPayload(loanId=loanId), headers=self.headers).json()

	def requestLoan(self, type):
		return requests.put(url=f"{self.baseUsersURI}{self.username}{endpoints['loans']}", data=self.craftPayload(type=type), headers=self.headers).json()

	def getSystemsInfo(self):
		return requests.get(url=f"{self.baseGameURI}{self.endpoints['system']}", headers=self.headers).json()

	def buyNewShip(self, location, type):
		return requests.post(url=f"{self.baseUsersURI}{username}{self.endpoints['ships']}", data=self.craftPayload(location=location, type=type), headers=self.headers).json()

	def getAvailableShips(self, shipClass):
		return requests.get(url=f"{self.baseGameURI}{self.endpoints['ships']}", params=self.craftPayload(shipClass=shipClass), headers=self.headers).json()

	def getShipInfo(self, shipId):
		return requests.get(url=f"{self.baseUsersURI}{self.username}{self.endpoints['ships']}{shipId}", headers=self.headers).json()

	def getShips(self):
		return requests.get(url=f"{self.baseUsersURI}{self.username}{self.endpoints['ships']}", headers=self.headers).json()

	def scrapShip(self, shipId):
		return requests.get(url=f"{self.baseUsersURI}{self.username}{self.endpoints['ships']}", params=self.craftPayload(shipId=shipId), headers=self.headers).json()

	def getDockedShips(self, symbol):
		return requests.get(url=f"{self.baseGameURI}{self.endpoints['locations']}{symbol}{self.endpoints['ships']}", headers=self.headers).json()	

	def getLocationInfo(self, symbol):
		return requests.get(url=f"{self.baseGameURI}{self.endpoints['locations']}{symbol}", headers=self.headers).json()

	def getSystemLocations(self, symbol):
		return requests.get(url=f"{self.baseGameURI}{self.endpoints['systems']}{symbol}{self.endpoints['locations']}", headers=self.headers).json()

	def getMarketplace(self, symbol):
		return requests.get(url=f"{self.baseGameURI}{self.endpoints['locations']}{symbol}{self.endpoints['market']}", headers=self.headers).json()

	def placePurchaseOrder(self, shipId, good, quantity):
		return requests.post(url=f"{self.baseUsersURI}{self.username}{self.endpoints['purchase']}", data=self.craftPayload(shipId=shipId, good=good, quantity=quantity), headers=self.headers).json()

	def placeSellOrder(self, shipId, good, quantity):
		return requests.post(url=f"{self.baseUsersURI}{self.username}{self.endpoints['sell']}", data=self.craftPayload(shipId=shipId, good=good, quantity=quantity), headers=self.headers).json()

	def getAllFlightPlans(self, symbol):
		return requests.post(url=f"{self.baseGameURI}{self.endpoints['systems']}{symbol}{self.endpoints['flightplans']}", data=self.craftPayload(symbol=symbol), headers=self.headers).json()

	def getFlightPlanInfo(self, flightPlanId):
		return requests.get(url=f"{self.baseUsersURI}{self.username}{self.endpoints['flightplans']}{flightPlanId}", headers=self.headers).json()

	def createFlightPlan(self, shipId, destination):
		return requests.post(url=f"{self.baseUsersURI}{self.username}{self.endpoints['flightplans']}", data=self.craftPayload(shipId=shipId, destination=destination), headers=self.headers).json()




