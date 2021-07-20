# How to run

## Initialize environment and install dependencies

```
poetry install
poetry shell
```

## Start server

Server starts on 8000 port in dev mode (with auto reloading)

```
./start.sh
```

## Running tests

```
pytest
# or with coverage
coverage run --source . -m pytest; coverage report
# or with html generated
coverage run --source . -m pytest; coverage html
```

# Decisions

Only one root. Blocks creating root elements for user. Root element created by
DB.


## Don't mislead user

Temporaly craeted items in cache should be visible as temporal
