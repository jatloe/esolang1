ALLOWED_VARIABLES = {*"abc"}
variableValues = {x:0 for x in ALLOWED_VARIABLES}

def compile(lines):
    lines = lines.split("\n")
    lines = [line[:line.index("#") if "#" in line else None].strip() for line in lines]
    lines = [line for line in lines if line]

    if not lines[0].startswith("NUMVARS"):
        numVars = 3
    else:
        try:
            numVars = int(lines[0].replace(" ","").split("=")[1])
        except: raise Exception(f"Invalid first line! It should be NUMVARS = 5, for example. If not specified, it will be 3.")
        lines = lines[1:]
    if numVars not in [*range(27)]: raise Exception(f"Invalid number of variables! It must be in [0,26].")

    global ALLOWED_VARIABLES,variableValues
    ALLOWED_VARIABLES = {*("abcdefghijklmnopqrstuvwxyz"[:numVars])}
    variableValues = {x:0 for x in ALLOWED_VARIABLES}

    routineDict = {}
    currRoutine = ""

    for line in lines:
        if line[:2] == "- ":
            currRoutine = line[2:]
            routineDict[currRoutine] = []
        else:
            routineDict[currRoutine] += [line]
    
    return routineDict

def parseObjectNoCheck(s):
    if s in ALLOWED_VARIABLES:
        return variableValues[s]
    elif s[0] == s[-1] and s[0] in "'"+'"': # Most cursed code
        return s[1:-1]
    elif {*s} <= {*"-1234567890"}:
        return int(s)
    else:
        raise Exception(f"Invalid expression: {s}")
    
def parseObject(s,mustBe="*"):
    ans = parseObjectNoCheck(s)
    if mustBe == "*": return ans

    if type(ans) != {"number": type(0), "string": type("")}[mustBe]:
        raise Exception(f"Invalid expression type: {s} must be type {mustBe}")
    return ans

def getVar(var):
    if var not in ALLOWED_VARIABLES: raise Exception(f"Invalid variable name: {var}")
    return variableValues[var]

def setVar(var,val):
    if var not in ALLOWED_VARIABLES: raise Exception(f"Invalid variable name: {var}")
    variableValues[var] = parseObject(val)

def interpret(routineDict):
    stack = [("main",0)]

    while stack:
        currRoutine,lineNum = stack.pop()
        
        if lineNum >= len(routineDict[currRoutine]): continue

        line = routineDict[currRoutine][lineNum]
        
        stack += [(currRoutine,lineNum + 1)]
        
        if line.startswith("GOTO_ROUTINE"):
            r = parseObject(line[13:])
            if r not in routineDict: raise Exception(f"Routine '{r}' does not exist!")
            stack += [(r,0)]
        elif line.startswith("PRINTNL"):
            print(parseObject(line[8:]),end="")
        elif line.startswith("PRINT"):
            print(parseObject(line[6:]))
        elif line.startswith("GOTO"):
            if stack: stack.pop()
            newNum = parseObject(line[5:], mustBe="number")
            # if newNum >= len(routineDict[currRoutine]): raise Exception(f"Cannot go to line '{line[5:]}': Not a valid line!")
            stack += [(currRoutine,newNum)]
        elif line.startswith("SET"):
            l = line[4:]

            try: ind = l.index(" ")
            except: raise Exception(f"Invalid variable setting: {line}")

            var = l[:ind]
            val = l[ind+1:]

            setVar(var,val)
        elif line.startswith("ADD"):
            l = line[4:]

            try: ind = l.index(" ")
            except: raise Exception(f"Invalid variable setting: {line}")

            var = l[:ind]
            val = l[ind+1:]

            setVar(var,str(getVar(var)+parseObject(val)))
        elif line.startswith("IF"):
            l = line[3:]
            obj = parseObject(l)

            if type(obj) != type(0): raise Exception(f"Not a number to IF: {l}")

            if obj <= 0:
                stack.pop()
                stack += [(currRoutine,lineNum+2)]
        
        # print(line,variableValues)

import sys
args = sys.argv[1:]
theFile = open((args[0] if args else "example") + ".txt","r").read()
routineDict = compile(theFile)
interpret(routineDict)