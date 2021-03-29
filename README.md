<h2 align="center"> SpacePYtraders </h2>
<h3 align="center"><strong>Python Wrapper for <code>api</code> calls to Spacetraders.io</strong></h3>

<div align="center">
	:space_invader:
</div>
<div align="center">
	:first_quarter_moon::milky_way::rocket::earth_africa::milky_way::last_quarter_moon:
</div>
<div align="center">
	<h3>
		<a href="https://spacetraders.io/">
			Spacetraders
		</a>
	</h3>
</div>


## Table of Contents
- [Dependencies](#Dependencies)
- [Installation](#Installation)
- [Usage](#Usage)
- [Functions](#Functions)


## Dependencies
Synchronous client.py
```sh
	pip install requests ratelimit
```

Asynchronous httpxclient.py
```sh
	pip install httpx asyncio
```

## Installation
1. Install dependencies
2. Download or fetch the repo
3. Import the preferred version from the appropriate file

## Usage
```py
from client import STClient
#Either supply username and token in constructor:
my_client = STClient(user='my_username', token='my_token')

#Or, if you do not have a username and token, call claimUsername()
my_client = STClient()
my_client.claimUsername("my_desired_username")

```
All methods provided currently return a json with the response from the api, no parsing is done (NYE).
<code>claimUsername()</code> sends a request to spacetraders.io to register your username and provide you with a token. Your username and token is returned as json (not required to catch it with a variable) and also written to a file (cred.txt).
## Functions


