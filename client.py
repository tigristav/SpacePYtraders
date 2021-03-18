import requests
from requests import Request, Session
from ratelimit import limits, sleep_and_retry, RateLimitException
import json
import logging

class STClient:
	def __init__(self, *args, **kwargs):
		self.username = kwargs.get('user')
		self.token = kwargs.get('token')
		self.headers = {'Authorization':f'Bearer {self.token}'}
		self.baseGameURI = 'https://api.spacetraders.io/game/'
		self.baseUsersURI = f'https://api.spacetraders.io/users/{self.username}/'
		self.endpoints = {'status':'status/', 
							'system':'systems/', 
							'locations':'locations/', 
							'loans':'loans/',
							'ships':'ships/',
							'market':'marketplace/',
							'purchase':'purchase-orders/',
							'sell':'sell-orders/',
							'flightplans':'flight-plans/'}
		self.session = requests.Session()
		self.session.headers.update({'Authorization':f'Bearer {self.token}'})
		self.errorHandler = ErrorHandler()
	
	def craftPayload(self, **kwargs):
		if kwargs.get('shipClass') is not None:             #Hack-fix cause "class" keyword is not allowed in kwargs
			kwargs['class'] = kwargs.get('shipClass')
			kwargs.pop('shipClass', None)
		return dict(**kwargs)

	@sleep_and_retry
	@limits(calls=2, period=1)
	def prepSendProcess(self, request):
		prep = self.session.prepare_request(request)
		response = self.session.send(prep).json()
		procResult = self.errorHandler.process(request, response)
		if self.errorHandler.isTriggered():
			return procResult
		else:	
			return response

	def serverStatus(self):
		req = Request('GET', url=f"{self.baseGameURI}{self.endpoints['status']}")
		return self.prepSendProcess(req)

	def claimUsername(self, username):
		response = requests.post(url=f"{self.baseUsersURI}{username}/token", headers=self.headers).json()
		if "error" in response:
			print("Username already taken.")
			return response
		else:	
			self.token = response['token']
			self.username = response['user']['username']
			with open("cred.txt", "w") as file:
				file.write(f"Username: {self.username}\nToken: {self.token}")
			return response 

	def getUser(self):
		req = Request('GET', url=f"{self.baseUsersURI}")
		return self.prepSendProcess(req)

	def getAvailableLoans(self):
		req = Request('GET', url=f"{self.baseGameURI}{self.endpoints['loans']}")
		return self.prepSendProcess(req)

	def getLoans(self):
		req = Request('GET', url=f"{self.baseUsersURI}{self.endpoints['loans']}")
		return self.prepSendProcess(req)

	def payLoan(self, loanId):
		req = Request('PUT', url=f"{self.baseUsersURI}{self.endpoints['loans']}", data=self.craftPayload(loanId=loanId))
		return self.prepSendProcess(req)

	def requestLoan(self, type):
		req = Request('POST', url=f"{self.baseUsersURI}{self.endpoints['loans']}", data=self.craftPayload(type=type))
		return self.prepSendProcess(req)

	def getSystemsInfo(self):
		req = Request('GET', url=f"{self.baseGameURI}{self.endpoints['system']}")
		return self.prepSendProcess(req)

	def buyNewShip(self, location, type):
		req = Request('POST', url=f"{self.baseUsersURI}{self.endpoints['ships']}", data=self.craftPayload(location=location, type=type))
		return self.prepSendProcess(req)

	def getAvailableShips(self, shipClass):
		req = Request('GET', url=f"{self.baseGameURI}{self.endpoints['ships']}", params=self.craftPayload(shipClass=shipClass))
		return self.prepSendProcess(req)

	def getShipInfo(self, shipId):
		req = Request('GET', url=f"{self.baseUsersURI}{self.endpoints['ships']}{shipId}")
		return self.prepSendProcess(req)

	def getShips(self):
		req = Request('GET', url=f"{self.baseUsersURI}{self.endpoints['ships']}")
		return self.prepSendProcess(req)

	def scrapShip(self, shipId):
		req = Request('DELETE', url=f"{self.baseUsersURI}{self.endpoints['ships']}", params=self.craftPayload(shipId=shipId))
		return self.prepSendProcess(req)

	def getDockedShips(self, symbol):
		req = Request('GET', url=f"{self.baseGameURI}{self.endpoints['locations']}{symbol}/{self.endpoints['ships']}")
		return self.prepSendProcess(req)

	def getLocationInfo(self, symbol):
		req = Request('GET', url=f"{self.baseGameURI}{self.endpoints['locations']}{symbol}")
		return self.prepSendProcess(req)

	def getSystemLocations(self, symbol):
		req = Request('GET', url=f"{self.baseGameURI}{self.endpoints['system']}{symbol}/{self.endpoints['locations']}")
		return self.prepSendProcess(req)

	def getMarketplace(self, symbol):
		req = Request('GET', url=f"{self.baseGameURI}{self.endpoints['locations']}{symbol}/{self.endpoints['market']}")
		return self.prepSendProcess(req)

	def placePurchaseOrder(self, shipId, good, quantity):
		print(f"INPUT FUNCTION: {shipId} {good} {quantity}")
		req = Request('POST', url=f"{self.baseUsersURI}{self.endpoints['purchase']}", data=self.craftPayload(shipId=shipId, good=good, quantity=int(quantity)))
		return self.prepSendProcess(req)

	def placeSellOrder(self, shipId, good, quantity):
		req = Request('POST', url=f"{self.baseUsersURI}{self.endpoints['sell']}", data=self.craftPayload(shipId=shipId, good=good, quantity=quantity))
		return self.prepSendProcess(req)

	def getAllFlightPlans(self, symbol):
		req = Request('GET', url=f"{self.baseGameURI}{self.endpoints['system']}{symbol}/{self.endpoints['flightplans']}")
		return self.prepSendProcess(req)

	def getFlightPlanInfo(self, flightPlanId):
		req = Request('GET', url=f"{self.baseUsersURI}{self.endpoints['flightplans']}/{flightPlanId}")
		return self.prepSendProcess(req)

	def createFlightPlan(self, shipId, destination):
		req = Request('POST', url=f"{self.baseUsersURI}{self.endpoints['flightplans']}", data=self.craftPayload(shipId=shipId, destination=destination))
		return self.prepSendProcess(req)

		


#TODO - Add more Error codes and possibly re-structure the class
class ErrorHandler:
	def __init__(self):
		self.triggered = False
		logging.basicConfig(filename='errors.log', filemode='w', format='%(asctime)s - %(levelname)s:%(message)s')
		self.logger = logging.getLogger(__name__)
		self.code = {404:self.routeNotFound,
			2005:self.marketVisibility,
			40101:self.missingToken,
			40401:self.userNotFound,
			40901:self.usernameTaken,
			42201:self.invalidPayload,
			}

	def isTriggered(self):
		return self.triggered

	def process(self, request, response):
		if 'error' in response:
			self.triggered = True
			return self.code.get(response['error']['code'])(request, response)	

	def routeNotFound(self, request, response):
		self.logger.error(f"{request} - RETURNED:{response['error']['code']}-{response['error']['message']}")
		return response['error']['message']

	def marketVisibility(self, request, response):
		self.logger.error(f"{request} - RETURNED:{response['error']['code']}-{response['error']['message']}")
		return response['error']['message']

	def missingToken(self, request, response):
		self.logger.error(f"{request} - RETURNED:{response['error']['code']}-{response['error']['message']}")
		return response['error']['message']

	def userNotFound(self, request, response):
		self.logger.error(f"{request} - RETURNED:{response['error']['code']}-{response['error']['message']}")
		return response['error']['message']

	def usernameTaken(self, request, response):
		self.logger.error(f"{request} - RETURNED:{response['error']['code']}-{response['error']['message']}")
		return response['error']['message']

	def invalidPayload(self, request, response):
		self.logger.error(f"{request} - RETURNED:{response['error']['code']}-{response['error']['message']}")
		return response['error']['message']