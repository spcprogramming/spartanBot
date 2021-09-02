# datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' -> '

from datetime import datetime
import sys

def botLog(server, function, action = None, result = None):

    # server, function, action = None, result = None
    '''
    for arg in sys.argv[1:]:
        print(arg)

    server = str(sys.argv[1:][0])
    function =  str(sys.argv[1:][1])
    action =  str(sys.argv[1:][2])
    result = str(sys.argv[1:][3])
    '''

    if action and result == None:
        print(
            datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + 
            ' -> '+ str(server) + 
            ' -> '+ str(function)
        )
    elif action != None and result == None:
        print(
            datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + 
            ' -> ' + str(server) + 
            ' -> ' + str(function) +
            ' -> ' + str(action)
        )
    if action and result != None:
        print(
            datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + 
            ' -> ' + str(server) + 
            ' -> ' + str(function) +
            ' -> ' + str(action) +
            ' -> ' + str(result)
        )

def main(input):
    print(datetime.now().strftime("%Y-%m-%d %I:%M:%S:%f %p") + ' -> ' + str(input))

if __name__ == "__main__":
    botLog()