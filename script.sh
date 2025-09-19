#!/bin/bash
# ===============================
# OptiPOS - Run Django Migrations
# ===============================
echo "Creating a Virtual Environment"
sleep 1
python -m venv ../venv

echo "Activating Virtual Environment"
sleep 1
source ../venv/bin/activate

echo "Installing Dependencies"
sleep 1
pip install -r requirements.txt

echo "Upgrading pip"
sleep 1
pip install --upgrade pip

# Run migrations
echo "***************************\n*******Starting Migration****************\n*********************************"
echo "migrating user"
sleep 2
python manage.py makemigrations user
python manage.py migrate
echo "migrating core"
sleep 2
python manage.py makemigrations core
python manage.py migrate
echo "migrating inventory"
sleep 2
python manage.py makemigrations inventory
python manage.py migrate
echo "migrating purchase"
sleep 2
python manage.py makemigrations purchase
python manage.py migrate
echo "migrating sales"
sleep 2
python manage.py makemigrations user core inventory purchase sales
python manage.py migrate
sleep 1
echo "✅ Migrations completed successfully!"
