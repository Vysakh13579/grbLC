'''
Test script that will read automatically read through GCNs and allow the user to accept or reject a data point given the point and paragraph/table

'''

## Work in progrress


## Work in progrress

def manual_sort(filepath, grb):
    
    flagged_data = open(filepath+str(grb)+'_sentences_mag.txt','r')
    accepted_data = open(filepath+str(grb)+'_acceped_mag.txt', 'a')
    
    accepted_data.write(str('gcn')+str('\t')+str('mag')+str('\t')+str('mag_err')+str('\t')+str('band')+str('\n'))
    
    lines = flagged_data.readlines()[1:]
    
    for point in lines:
        
        loopVal = True
        print('==========================\n')
        print(point)
        
        while loopVal:
            
            userInput = input('Accept the above point? y/n \n')
            
            
            if userInput == 'n':
                loopVal = False
                
        
            elif userInput == 'y':
                
                accepted_data.write(str(point)+str('\n'))
                
                loopVal = False

            else:
                pass
    flagged_data.close()
    accepted_data.close()
    



