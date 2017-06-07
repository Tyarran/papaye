# find ./papaye -type f -name '*.pyc' -exec rm -rf {} \;
# find ./papaye -type d -name '__pycache__' -exec rm -rf {} \;


rm -rf $(find . -type f -name '*.pyc')
rm -rf $(find . -type d -name '__pycache__')