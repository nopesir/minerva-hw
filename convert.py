# Using readlines() 
file1 = open('gps.txt', 'r') 
Lines = file1.readlines() 
  
count = 0
file2 = open('visualizer.txt', 'w') 
file2.write('name,desc,latitude,longitude\n')
# Strips the newline character 
for line in Lines:
    elems = line.strip().split()
    if len(elems)>1:
        file2.write(elems[0]+',' + elems[3]+',' + elems[1]+',' + elems[2]+'\n')

file1.close()
file2.close()
