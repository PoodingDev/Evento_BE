set -eo pipefail

COLOR_GREEN=`tput setaf 2;`
COLOR_NC=`tput sgr0;` # No Color

echo "Starting black"
poetry run black .

echo "Starting isort"
poetry run isort .

echo "Starting mypy"
poetry run mypy .

echo "Starting pytest with coverage"
poetry run coverage run manage.py test
poetry run coverage report -m
poetry run coverage html

echo "${COLOR_GREEN}All tests passed successfully!${COLOR_NC}"