# :fish_cake: lumina

API microservice for New Theatre alumni sites, responsible for identifying users and processing messages and submissions of data.

## Dev Environment Setup
- `virtualenv -p python3.6 env`
- `source env/bin/activate`
- `pip install -r requirements.txt`

## Running Locally

First activate the virtual environment

- `source env/bin/activate`

To run the dev server

- `chalice local`

To run tests

- `pytest`

## Deploy
You need AWS creds set up on your local user account

- `chalice deploy`

## Endpoints

- <https://lumina.newtheatre.org.uk/dev/>
- <https://lumina.newtheatre.org.uk/v1/>

## Methods

### `hello`

Responds with `message` "Hello World!"

### `hello/{arg}`

Responds with `message` "Hello {arg}!"

### `sendLoginToken`
### `getUserToken`
### `getAnonymousToken`
### `submitPageReport`
### `submitBiography`
### `submitShow`
