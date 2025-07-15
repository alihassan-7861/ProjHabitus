echo "Start Building"

pip install -r requirements.txt
python3.9 manage.py collectstatic --noinput

echo "Building End"
