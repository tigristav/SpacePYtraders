import httpx
import asyncio
from ratelimit import limits, sleep_and_retry, RateLimitException
import json
import sys
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
							'flightplans':'flight-plans/',
							'discard':'jettison/'}
		self.initWindowsFix()
		self.client = httpx.AsyncClient(headers=self.headers) #add base url
		self.errorHandler = ErrorHandler()
	
	def initWindowsFix(self): #Required for async due to bug in Windows shitty proactor event loop that crashes asyncio
		if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
			asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

	async def closeConnection(self):
		await self.client.aclose()

	def craftPayload(self, **kwargs):
		if kwargs.get('shipClass') is not None:             #Hack-fix cause "class" keyword is not allowed in kwargs
			kwargs['class'] = kwargs.get('shipClass')
			kwargs.pop('shipClass', None)
		return dict(**kwargs)

	@sleep_and_retry
	@limits(calls=1, period=0.5)
	async def prepSendProcess(self, request):
		prep = request
		print(f"{request} with headers: {request.headers}")
		response = await self.client.send(prep)
		response = response.json()
		procResult = self.errorHandler.process(request, response)
		if self.errorHandler.isTriggered():
			return procResult
		else:	
			return response
		

	async def serverStatus(self):
		req = self.client.build_request('GET', url=f"{self.baseGameURI}{self.endpoints['status']}")
		return await self.prepSendProcess(req)

	def claimUsername(self, username):
		response = httpx.post(url=f"https://api.spacetraders.io/users/{username}/token/").json()
		if "error" in response:
			print("Username already taken.")
			return response
		else:	
			self.token = response['token']
			self.username = response['user']['username']
			with open("cred.txt", "a") as file:
				file.write(f"Username: {self.username}\nToken: {self.token}")
			return response

	async def getUser(self):
		req = self.client.build_request('GET', url=f"{self.baseUsersURI}")
		return await self.prepSendProcess(req)

	async def getAvailableLoans(self):
		req = self.client.build_request('GET', url=f"{self.baseGameURI}{self.endpoints['loans']}")
		return await self.prepSendProcess(req)

	async def getLoans(self):
		req = self.client.build_request('GET', url=f"{self.baseUsersURI}{self.endpoints['loans']}")
		return await self.prepSendProcess(req)

	async def payLoan(self, loanId):
		req = self.client.build_request('PUT', url=f"{self.baseUsersURI}{self.endpoints['loans']}", data=self.craftPayload(loanId=loanId))
		return await self.prepSendProcess(req)

	async def requestLoan(self, type):
		req = self.client.build_request('POST', url=f"{self.baseUsersURI}{self.endpoints['loans']}", data=self.craftPayload(type=type))
		return await self.prepSendProcess(req)

	async def getSystemsInfo(self):
		req = self.client.build_request('GET', url=f"{self.baseGameURI}{self.endpoints['system']}")
		return await self.prepSendProcess(req)

	async def buyNewShip(self, location, type):
		req = self.client.build_request('POST', url=f"{self.baseUsersURI}{self.endpoints['ships']}", data=self.craftPayload(location=location, type=type))
		return await self.prepSendProcess(req)

	async def getAvailableShips(self, shipClass):
		req = self.client.build_request('GET', url=f"{self.baseGameURI}{self.endpoints['ships']}", params=self.craftPayload(shipClass=shipClass))
		return await self.prepSendProcess(req)

	async def getShipInfo(self, shipId):
		req = self.client.build_request('GET', url=f"{self.baseUsersURI}{self.endpoints['ships']}{shipId}")
		return await self.prepSendProcess(req)

	async def getShips(self):
		req = self.client.build_request('GET', url=f"{self.baseUsersURI}{self.endpoints['ships']}")
		return await self.prepSendProcess(req)

	async def scrapShip(self, shipId):
		req = self.client.build_request('DELETE', url=f"{self.baseUsersURI}{self.endpoints['ships']}", params=self.craftPayload(shipId=shipId))
		return await self.prepSendProcess(req)

	async def getDockedShips(self, symbol):
		req = self.client.build_request('GET', url=f"{self.baseGameURI}{self.endpoints['locations']}{symbol}/{self.endpoints['ships']}")
		return await self.prepSendProcess(req)

	async def getLocationInfo(self, symbol):
		req = self.client.build_request('GET', url=f"{self.baseGameURI}{self.endpoints['locations']}{symbol}")
		return await self.prepSendProcess(req)

	async def getSystemLocations(self, symbol):
		req = self.client.build_request('GET', url=f"{self.baseGameURI}{self.endpoints['system']}{symbol}/{self.endpoints['locations']}")
		return await self.prepSendProcess(req)

	async def getMarketplace(self, symbol):
		req = self.client.build_request('GET', url=f"{self.baseGameURI}{self.endpoints['locations']}{symbol}/{self.endpoints['market']}")
		return await self.prepSendProcess(req)

	async def placePurchaseOrder(self, shipId, good, quantity):
		print(f"INPUT FUNCTION: {shipId} {good} {quantity}")
		req = self.client.build_request('POST', url=f"{self.baseUsersURI}{self.endpoints['purchase']}", data=self.craftPayload(shipId=shipId, good=good, quantity=int(quantity)))
		return await self.prepSendProcess(req)

	async def placeSellOrder(self, shipId, good, quantity):
		req = self.client.build_request('POST', url=f"{self.baseUsersURI}{self.endpoints['sell']}", data=self.craftPayload(shipId=shipId, good=good, quantity=quantity))
		return await self.prepSendProcess(req)

	async def getAllFlightPlans(self, symbol):
		req = self.client.build_request('GET', url=f"{self.baseGameURI}{self.endpoints['system']}{symbol}/{self.endpoints['flightplans']}")
		return await self.prepSendProcess(req)

	async def getFlightPlanInfo(self, flightPlanId):
		req = self.client.build_request('GET', url=f"{self.baseUsersURI}{self.endpoints['flightplans']}/{flightPlanId}")
		return await self.prepSendProcess(req)

	async def createFlightPlan(self, shipId, destination):
		req = self.client.build_request('POST', url=f"{self.baseUsersURI}{self.endpoints['flightplans']}", data=self.craftPayload(shipId=shipId, destination=destination))
		return await self.prepSendProcess(req)

	async def discardCargo(self, shipId, good, quantity):
		req = self.client.build_request('PUT', url=f"{self.baseUsersURI}{self.endpoints['ships']}{shipId}{self.endpoints['discard']}")
		return await self.prepSendProcess(req)


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