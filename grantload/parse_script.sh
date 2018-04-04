$input_file = $1
echo $1
echo "Hello"
sed -i 's/""/"/g' $1
