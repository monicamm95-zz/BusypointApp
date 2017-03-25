import time 

while(1):
	file = open("temp.txt", "r")
	number = int(file.read())
	print(number)
	time.sleep(1)  
	#TEST