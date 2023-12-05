import re
from Variable import Variable
from collections import deque

vars = [Variable("IT", "NOOB", "")]


class SyntaxAnalyzer:
    def program(self, tokens, lexeme, row):
        i = 0

        while tokens[i] == "COMMENT":
            i += 1

        if tokens[i] == "START":  # encountered start of program
            print("==== PROGRAM START! === \n")
            i += 1
            if tokens[i] == "WAZZUP":
                i += 1
                i = isVarDec(tokens, lexeme, row, i)
            while tokens[i] != "END" and i < len(tokens):
                if tokens[i] == "COMMENT":
                    i += 1
                    continue
                if tokens[i] == "IFELSE":
                    #enter ifelse block
                    i = ifElse(tokens, lexeme, row, i)
                elif tokens[i] == "INLOOP":
                    i = loop(tokens, lexeme, row, i)
                else:
                    i = statement(tokens, lexeme, row, i)
                if i >= len(tokens):
                    print("Aaaaa")
                    break
            if i == len(tokens):
                raise RuntimeError("End of program not found")
            # printVariables()
        else:
            raise RuntimeError("Start of program not found")

def loop(tokens, lexeme, row, i):
    rowNum = row[i]
    i += 1

    if tokens[i] != "VARIABLE" or row[i] != rowNum: raise RuntimeError("Unexpected %r in line %d. Expected a loop label instead" % (tokens[i], row[i]))
    #if variable
    loop_label = lexeme[i].strip()
    i += 1
    if tokens[i] == "INCR" and row[i] == rowNum:
        add = 1
    elif tokens[i] == "DECR" and row[i] == rowNum:
        add = -1
    else: raise RuntimeError("Unexpected %r in line %d. Expected UPPIN YR or NERFIN YR" % (tokens[i], row[i]))
    i+=1

    if tokens[i] == "VARIABLE" and row[i] == rowNum:
        #temp var
        varName = lexeme[i]
        value, type = searchVarValue(lexeme[i])
        i += 1
    else: raise RuntimeError("Unexpected %r in line %d. Expected a VARIABLE" % (tokens[i], row[i]))
    
    if tokens[i] == "WILE" and row[i] == rowNum:
        cond = True
        # print("running while true")
    elif tokens[i] == "TIL" and row[i] == rowNum:
        cond = False
        # print("running while false")
    else: raise RuntimeError("Unexpected %r in line %d. Expected WILE or TIL" % (tokens[i], row[i]))

    i += 1
    condline = []
    condtoken = []
    condrow = rowNum
    #get rest of line so conditional
    while rowNum == row[i]:
        condline.append(lexeme[i])
        condtoken.append(tokens[i])
        i+=1
        if i == len(lexeme): break

    if condtoken[0] == "BOOL_OPER" or condtoken[0] == "COMPARISON" or condtoken[0] == "MATH":
        #INITIALIZE THE CONDITION VALUE
        condval, condtype = expression(condline, condtoken, 0, condrow)
        if condtype != "TROOF":condval = typeCasting(condval, condtype, "TROOF", condrow)
        condval = True if condval == "WIN" else False
        while condval == cond:
            codeblockindex = i
            rowNum = row[i]
            while True:
                i = statement(tokens, lexeme, row, i)
                
                if tokens[i] == "OUTLOOP" and tokens[i+1] == "VARIABLE":
                    if row[i+1] != row[i]: raise RuntimeError("Unexpected newline in line %d", row[i])
                    if lexeme[i+1] != loop_label: raise RuntimeError("Expected %r in line %d. Encountered %r instead." % (loop_label, row[i], lexeme[i+1]))
                    break
            value += add
            # print("val: " + str(value) + " i: "+ str(i) + " rowNum: "+ str(rowNum) + " row[i]: "+ str(row[i]))
            storeVariables(varName.strip(), type, value)
            # print(searchVarValue(varName.strip()))
            condval, condtype = expression(condline, condtoken, 0, condrow)

            # print("condval2:"+ condval)
            if condtype != "TROOF": condval = typeCasting(condval, condtype, "TROOF", condrow)
            condval = True if condval == "WIN" else False
            # print("condval: "+str(condval)+" cond: "+str(cond))
            if condval != cond:
                return i
            i = codeblockindex            
    else: raise RuntimeError("Unpexected %r in line %d expected a Boolean operation or comparison operation" % (condtoken[0], rowNum))

def ifElse(tokens, lexeme, row, i):
    #get conditional value in IT
    cond, type = searchVarValue("IT")
    if type != "TROOF":
        cond = typeCasting(cond, type, "TROOF", row[i-1])
    
    cond = True if cond == "WIN" else False
    maxlen = len(tokens)
    i += 1
    print(cond)
    #run this while you haven't encountered OIC
    if cond == True: #YA RLY
        if tokens[i] == "IFTRUE":
            while tokens[i] != "ENDIFELSE" and tokens[i] != "IFFALSE":
                i = statement(tokens, lexeme, row, i)
                
                if i >= maxlen:
                    raise RuntimeError("Expected OIC encountered end of file instead")
            if tokens[i] == "IFFALSE":
                while tokens[i] != "ENDIFELSE":
                    i+=1
                    if i >= maxlen:
                        raise RuntimeError("Expected OIC encountered end of file instead")
                return i    
    elif cond == False:
        if tokens[i] == "IFTRUE":
            while tokens[i] != "IFFALSE":
                i += 1
                if i >= maxlen:
                    raise RuntimeError("Expected NO WAI encountered end of file instead")
            #if NO WAI is encountered
            while tokens[i] != "ENDIFELSE":
                i = statement(tokens, lexeme, row, i)
                if i >= maxlen:
                    raise RuntimeError("Expected OIC encountered end of file instead")
    else:
        raise RuntimeError("Unexpected %r in line %d" % (tokens[i], row[i]))
    return i

def isVarDec(tokens, lexeme, row, i):
    maxlen = len(tokens)
    while tokens[i] != "BUHBYE":
        if tokens[i] == "COMMENT":  # aka BTW (single line comment)
            # comments are stored all in one, if it's a multiline is when we iterate thru so this is fine
            i += 1
            continue
        elif tokens[i] == "VAR_DEC":
            # build line
            rowNum = row[i]
            line = []
            tline = []
            while rowNum == row[i]:
                line.append(lexeme[i])
                tline.append(tokens[i])
                i += 1
            storeVariable(tline, line, rowNum)
        else:
            raise RuntimeError(
                "Unexpected %r on line %d, Only variable declarations are allowed in this section"
                % (lexeme[i], row[i])
            )

        if i >= maxlen:
            raise RuntimeError("Encountered end of file")
    return i

def storeVariable(tline, line, rowNum):
    global vars
    i = 1
    maxlength = len(tline)
    if tline[i] == "VARIABLE":
        varName = line[i].strip()
        i += 1
    else:
        raise RuntimeError("Expected VARIABLE NAME on line %d" % (rowNum))

    if i >= maxlength:
        vars.append(Variable(varName, "NOOB", None))
        return

    if tline[i] == "ITZ":
        i += 1
    else:
        raise RuntimeError("Expected 'ITZ' on line %d" % (rowNum))

    if i >= maxlength:
        raise RuntimeError("Variable must have a value!")
    
    storing(varName, tline, line, i, rowNum)
   
def storing(varName, tline, line, i, rowNum):
    if (
        tline[i] == "NOOB"
        or tline[i] == "YARN"
        or tline[i] == "TROOF"
    ):
        type = tline[i]
        value = line[i]
    elif tline[i] == "NUMBAR":
        type = tline[i]
        value = float(line[i])
    elif tline[i] == "NUMBR":
        type = tline[i]
        value = int(line[i])
    elif tline[i] == "VARIABLE":
        value, type = searchVarValue(line[i])
    elif tline[i] == "BOOL_OPER" or tline[i] == "COMPARISON" or tline[i] == "MATH" or tline[i] == "CONCAT":
        value, type = expression(line, tline, i, rowNum)
    else:
        raise RuntimeError(
            "Variable declaration can only be to a YARN, TROOF, NOOB etch"
        )
    
    for variable in vars:
        if variable.name == varName:
            variable.dataType = type
            variable.value = value
            return
    vars.append(Variable(varName, type, value)) 

def statement(tokens, lexeme, row, i):
    global vars
    tline = []
    line = []
    rowNum = row[i]
    # print(rowNum)
    while rowNum == row[i]:
        tline.append(tokens[i])
        line.append(lexeme[i])
        i += 1
        if i == len(lexeme): break

    if tline[0] == "PRINT":
        printLine(line, tline, i)
    elif tline[0] == "VAR_DEC":
        raise RuntimeError("Unexpected variable declaration at line %d" % (rowNum))
    elif tline[0] == "BOOL_OPER" or tline[0] == "COMPARISON" or tline[0] == "MATH" or tline[0] == "CONCAT":
        value, type = expression(line, tline, 0, rowNum)
        storeVariables("IT", type, value)
    elif tline[0] == "INPUT":
        getInput(line, tline, 0, rowNum)
    elif tline[0] == "VARIABLE":
        # print("Recasting or Assignment")
        variableLine(line, tline, 1, rowNum)
    elif tline[0] == "TYPECAST":
        # print("Expl Typecasting")
        explicitTypecasting(line, tline, 1, rowNum, 0)
    return i

def expression(line, tline, i, rowNum):
    if tline[i] == "BOOL_OPER":
        value = boolOpRegion(line, tline, i, rowNum)
        type = "TROOF"
    elif tline[i] == "COMPARISON":
        value = comparison(line, tline, i, rowNum)
        type = "TROOF"
    elif tline[i] == "MATH":
        value = mathOp(line, tline, i, rowNum)
        if isinstance(value, int):
            type = "NUMBR"
        else:
            type = "NUMBAR"
    elif tline[i] == "CONCAT":
        value = smoosh(line, tline, i, rowNum)
        type = "YARN"
    else:
        raise RuntimeError("Encountered error in line %d, Expression %r does not exist!" % (rowNum, tline[i]))
    return value, type

def smoosh(line, tline, i, rowNum):
    string = ""
    i += 1
    while i < len(line):
        if tline[i] == "YARN":
            value = line[i].replace('"', "")
        elif tline[i] == "NUMBR" or tline[i] == "NUMBAR" or tline[i] == "TROOF":
            value = typeCasting(line[i], tline[i], "YARN", i)
        elif tline[i] == "VARIABLE":
            value, type = searchVarValue(line[i])
            if type != "YARN":
                value = typeCasting(value, type, "YARN", i)
            else:
                value = value.strip()
        elif tline[i] == "BOOL_OPER" or tline[i] == "COMPARISON" or tline[i] == "MATH":
            value, _ = expression(line, tline, i, rowNum)
            value = str(value)
        else:
            raise RuntimeError("Unexpected %r in line %d. Expected a YARN, TROOF, VARIABLE, or EXPRESSION." % (tline[i], rowNum))
        string = string + value
        i += 1
        if i >= len(line):
            return string
        elif tline[i] == "COMMENT":
            return string
        elif tline[i] != 'AN':
            raise RuntimeError("Unexpected %r in line %d. Expected an AN or end of line" % (tline[i], rowNum))
        i += 1
    return string

def variableLine(line, tline, i, rowNum):
    #i = 1 because 0 = VAR
    # print(line)
    if tline[i] == "R":
        i+= 1
        if tline[i] == "TYPECAST": #R MAEK
            varName = line[0].strip()
            i+=1
            
            if tline[i] != "VARIABLE": raise RuntimeError("Unexpected %r in line %d. Expected a variable" % (tline[i], rowNum))

            var2 = line[i]
            i+=1 #type2
            if tline[i] != "DATA_TYPE": raise RuntimeError("Unexpected %r in line %d. Expected a data type" % (tline[i], rowNum))

            value, type = searchVarValue(var2)
            storeVariables(varName, line[i], typeCasting(value, type, line[i], rowNum))
            return
        
        storing(line[0].strip(), tline, line, i, rowNum)
    elif tline[i] == "RECASTMAGIC": #IS NOW A
        varName = line[0].strip()
        i+=1
        if tline[i] != "DATA_TYPE": raise RuntimeError("Unexpected %r in line %d. Expected a data type" % (tline[i], rowNum))

        value, type = searchVarValue(varName)
        type2 = line[i]
        storeVariables(varName, type2, typeCasting(value, type, type2, rowNum))
        # printVariables()
    else:
        raise RuntimeError("Unexpected %r in line %d" % (tline[i], rowNum))

def explicitTypecasting(line, tline, i, rowNum):
    #i == 1
    if tline[i] != "VARIABLE":
        raise RuntimeError("Unexpected %r in line %d. Expected variable" % (tline[i], i))
    varName = line[i]
    value, type = searchVarValue(line[i])
    i += 1
    if tline[i] == "A": i += 1
    if tline[i] != "DATA_TYPE": raise RuntimeError("Unexpected %r in line %d. Expected data type")
    storeVariable("IT", line[i], typeCasting(value, type, line[i], rowNum))

def getInput(line, tline, i, rowNum):
    i += 1
    if tline[i] == "VARIABLE":
        varName = line[i]
        inputSTR = input("")
        storeVariables(varName, "YARN", inputSTR)
    else:
        raise RuntimeError(
            "Error in line %d, expected VARIABLE instead of %r" % (rowNum, line[i])
        )

def comparison(line, tline, i, rowNum):
    compQ = []
    # print(line)
    if line[i] == "BOTH SAEM":
        i += 1
        if tline[i] == "NUMBR" or tline[i] == "NUMBAR":
            if tline[i] == "NUMBR": compQ.append([tline[i], int(line[i])]) 
            else: compQ.append([tline[i], float(line[i])])
            i += 1
        elif tline[i] == "VARIABLE":
            value, type = searchVarValue(line[i])
            compQ.append([type, value])
            i += 1
        else:
            raise RuntimeError(
                "Expected NUMBR, NUMBAR, or VARIABLE at line %d" % (rowNum)
            )
        if tline[i] != "AN":
            raise RuntimeError("Expected AN at line %d" % (rowNum))
        i += 1

        if line[i] == "BIGGR OF" or line[i] == "SMALLR OF":
            compQ.append(line[i])
            i += 1
            if tline[i] == "NUMBR" or tline[i] == "NUMBAR":
                compQ.append([tline[i], line[i]])
                i += 1
            elif tline[i] == "VARIABLE":
                value, type = searchVarValue(line[i])
                compQ.append([type, value])
                i += 1
            else:
                raise RuntimeError(
                    "Expected NUMBR, NUMBAR, or VARIABLE at line %d" % (rowNum)
                )
            if compQ[0][1] != compQ[2][1]:
                raise RuntimeError(
                    "Value mismatch - operand 1 and 2 (%r and %r) must be same"
                    % (compQ[0][1], compQ[2][1])
                )
            if tline[i] != "AN":
                raise RuntimeError("Expected AN at line %d" % (rowNum))
            i += 1
            if tline[i] == "NUMBR" or tline[i] == "NUMBAR":
                if tline[i] == "NUMBR": compQ.append([tline[i], int(line[i])]) 
                else: compQ.append([tline[i], float(line[i])])
                i += 1
            elif tline[i] == "VARIABLE":
                value, type = searchVarValue(line[i])
                compQ.append([type, value])
                i += 1
            else:
                raise RuntimeError(
                    "Expected NUMBR, NUMBAR, or VARIABLE at line %d" % (rowNum)
                )
        elif tline[i] == "NUMBR" or tline[i] == "NUMBAR":
            if tline[i] == "NUMBR": compQ.append([tline[i], int(line[i])]) 
            else: compQ.append([tline[i], float(line[i])])
            i += 1
        elif tline[i] == "VARIABLE":
            value, type = searchVarValue(line[i])
            compQ.append([type, value])
            i += 1
        else:
            raise RuntimeError(
                "Expected NUMBR, NUMBAR, VARIABLE, BIGGR OF, or SMALLR OF at line %d"
                % (rowNum)
            )
        # print(compQ)
        if compQ[1] == "BIGGR OF":
            if compQ[2][0] != compQ[3][0]:
                raise RuntimeError(
                    "Type mismatch - cannot compare %r and %r"
                    % (compQ[0][0], compQ[1][0])
                )
            if compQ[2][0] == "NUMBR":
                if int(compQ[2][1]) >= int(compQ[3][1]):
                    return "WIN"
                else:
                    return "FAIL"
            elif compQ[2][0] == "NUMBAR":
                if float(compQ[2][1]) >= float(compQ[3][1]):
                    return "WIN"
                else:
                    return "FAIL"
            else:
                raise RuntimeError("Unexpected type %r" % (compQ[2][0]))
        elif compQ[1] == "SMALLR OF":
            if compQ[2][0] != compQ[3][0]:
                raise RuntimeError(
                    "Type mismatch - cannot compare %r and %r"
                    % (compQ[0][0], compQ[1][0])
                )
            if compQ[2][0] == "NUMBR":
                if int(compQ[2][1]) <= int(compQ[3][1]):
                    return "WIN"
                else:
                    return "FAIL"
            elif compQ[2][0] == "NUMBAR":
                if float(compQ[2][1]) <= float(compQ[3][1]):
                    return "WIN"
                else:
                    return "FAIL"
            else:
                raise RuntimeError("Unexpected type %r" % (compQ[2][0]))
        else:
            if compQ[0][0] != compQ[1][0]:
                raise RuntimeError(
                    "Type mismatch - cannot compare %r and %r"
                    % (compQ[0][0], compQ[1][0])
                )
            if compQ[0][1] == compQ[1][1]:
                return "WIN"
            else:
                return "FAIL"

    elif line[i] == "DIFFRINT":
        i += 1
        if tline[i] == "NUMBR" or tline[i] == "NUMBAR":
            if tline[i] == "NUMBR": compQ.append([tline[i], int(line[i])])
            else: compQ.append([tline[i], float(line[i])])
            i += 1
        elif tline[i] == "VARIABLE":
            value, type = searchVarValue(line[i])
            compQ.append([type, value])
            i += 1
        else:
            raise RuntimeError(
                "Expected NUMBR, NUMBAR, or VARIABLE at line %d" % (rowNum)
            )
        
        if tline[i] != "AN":
            raise RuntimeError("Expected AN at line %d" % (rowNum))
        i += 1
        if line[i] == "BIGGR OF" or line[i] == "SMALLR OF":
            compQ.append(line[i])
            i += 1
            if tline[i] == "NUMBR" or tline[i] == "NUMBAR":
                compQ.append([tline[i], line[i]])
                i += 1
            elif tline[i] == "VARIABLE":
                value, type = searchVarValue(line[i])
                compQ.append([type, value])
                i += 1
            else:
                raise RuntimeError(
                    "Expected NUMBR, NUMBAR, or VARIABLE at line %d" % (rowNum)
                )
            if compQ[0][1] != compQ[2][1]:
                raise RuntimeError(
                    "Value mismatch on line %d (%r and %r) must be same"
                    % (rowNum, compQ[0][1], compQ[2][1])
                )
            if tline[i] != "AN":
                raise RuntimeError("Expected AN at line %d" % (rowNum))
            i += 1
            if tline[i] == "NUMBR" or tline[i] == "NUMBAR":
                compQ.append([tline[i], line[i]])
                i += 1
            elif tline[i] == "VARIABLE":
                value, type = searchVarValue(line[i])
                compQ.append([type, value])
                i += 1
            else:
                raise RuntimeError(
                    "Expected NUMBR, NUMBAR, or VARIABLE at line %d" % (rowNum)
                )
        elif tline[i] == "NUMBR" or tline[i] == "NUMBAR":
            if tline[i] == "NUMBR": compQ.append([tline[i], int(line[i])]) 
            else: compQ.append([tline[i], float(line[i])])
            i += 1
        elif tline[i] == "VARIABLE":
            value, type = searchVarValue(line[i])
            compQ.append([type, value])
            i += 1
        else:
            raise RuntimeError(
                "Expected NUMBR, NUMBAR, VARIABLE, BIGGR OF, or SMALLR OF at line %d"
                % (rowNum)
            )
        # print(compQ)
        if compQ[1] == "BIGGR OF":
            if compQ[2][0] != compQ[3][0]:
                raise RuntimeError(
                    "Type mismatch - cannot compare %r and %r"
                    % (compQ[0][0], compQ[1][0])
                )
            if compQ[2][0] == "NUMBR":
                if int(compQ[3][1]) >= int(compQ[2][1]):
                    return "WIN"
                else:
                    return "FAIL"
            elif compQ[2][0] == "NUMBAR":
                if float(compQ[3][1]) >= float(compQ[2][1]):
                    return "WIN"
                else:
                    return "FAIL"
            else:
                raise RuntimeError("Unexpected type %r" % (compQ[2][0]))
        elif compQ[1] == "SMALLR OF":
            if compQ[2][0] != compQ[3][0]:
                raise RuntimeError(
                    "Type mismatch - cannot compare %r and %r"
                    % (compQ[0][0], compQ[1][0])
                )
            if compQ[2][0] == "NUMBR":
                if int(compQ[3][1]) <= int(compQ[2][1]):
                    return "WIN"
                else:
                    return "FAIL"
            elif compQ[2][0] == "NUMBAR":
                if float(compQ[3][1]) <= float(compQ[2][1]):
                    return "WIN"
                else:
                    return "FAIL"
            else:
                raise RuntimeError("Unexpected type %r" % (compQ[2][0]))
        else:
            if compQ[0][0] != compQ[1][0]:
                raise RuntimeError(
                    "Type mismatch - cannot compare %r and %r"
                    % (compQ[0][0], compQ[1][0])
                )
            if compQ[0][1] != compQ[1][1]:
                return "WIN"
            else:
                return "FAIL"

# function for parsing prefix notation math operations
def parse(tokens):
    if not tokens:
        raise RuntimeError("Unexpected end of statement.")
    else:
        token = tokens.popleft()
        if token == "+":
            return parse(tokens) + parse(tokens)
        elif token == "-":
            return parse(tokens) - parse(tokens)
        elif token == "/":
            return parse(tokens) / parse(tokens)
        elif token == "*":
            return parse(tokens) * parse(tokens)
        elif token == "%":
            return parse(tokens) % parse(tokens)
        elif token == "max":
            return max(parse(tokens), parse(tokens))
        elif token == "min":
            return min(parse(tokens), parse(tokens))
        else:
            return token

def mathOp(line, tline, i, rowNum):
    op = []
    num_of_operations = 0
    num_of_AN = 0

    while i < len(line):
        if line[i] == "SUM OF":
            op.append("+")
            i += 1
            num_of_operations += 1
        elif line[i] == "DIFF OF":
            op.append("-")
            i += 1
            num_of_operations += 1
        elif line[i] == "PRODUKT OF":
            op.append("*")
            i += 1
            num_of_operations += 1
        elif line[i] == "QUOSHUNT OF":
            op.append("/")
            i += 1
            num_of_operations += 1
        elif line[i] == "MOD OF":
            op.append("%")
            i += 1
            num_of_operations += 1
        elif line[i] == "BIGGR OF":
            op.append("max")
            i += 1
            num_of_operations += 1
        elif line[i] == "SMALLR OF":
            op.append("min")
            i += 1
            num_of_operations += 1
        else:
            if tline[i] == "NUMBR":
                op.append(int(line[i]))
                i += 1
            elif tline[i] == "NUMBAR":
                op.append(float(line[i]))
                i += 1
            elif tline[i] == "VARIABLE":
                value, _ = searchVarValue(line[i])
                op.append(value)
                i += 1
            elif tline[i] == "YARN":
                value = typeCasting(line[i], tline[i], "NUMBAR", rowNum)
                op.append(value)
                i += 1
            elif tline[i] == "AN":
                i += 1
                num_of_AN += 1
            else:
                raise RuntimeError("Unexpected %r at line %d" % (line[i], rowNum))
            i += 1

    expected_operands = num_of_operations + 1
    actual_operands = len(op) - (num_of_AN + num_of_operations)
    if expected_operands != actual_operands:
        raise RuntimeError(
            "Expected %d operands, but found %d at line %d"
            % (expected_operands, actual_operands, rowNum)
        )
    else:
        return parse(deque(op))

def boolOp(line, tline, i, rowNum):
    if tline[i] == "BOOL_OPER":
        opAddress = i
        boolQ = []
        i += 1
        i, boolQ0 = boolOp(line, tline, i, rowNum)
        boolQ.append(boolQ0)
        
        if line[opAddress] == "NOT":
            if boolQ[0] == "WIN":
                return i, "FAIL"
            else:
                return i, "WIN"
        i += 1
        if tline[i] != "AN":
            raise RuntimeError("Expected AN at line %d" % (rowNum))
        i += 1
        i, boolQ1 = boolOp(line, tline, i, rowNum)
        boolQ.append(boolQ1)
        # print(boolQ)
        if line[opAddress] == "BOTH OF":
            if boolQ[0] == "WIN" and boolQ[1] == "WIN":
                return i, "WIN"
            else:
                return i, "FAIL"
        elif line[opAddress] == "EITHER OF":
            if boolQ[0] == "WIN" or boolQ[1] == "WIN":
                return i, "WIN"
            else:
                return i, "FAIL"
        elif line[opAddress] == "WON OF":
            if boolQ[0] != boolQ[1] and (boolQ[0] == "WIN" or boolQ[1] == "WIN"):
                return i, "WIN"
            else:
                return i, "FAIL"
    elif tline[i] == "VARIABLE":
        if i < len(line) - 1:
            line[i] = line[i].strip()
        value, type = searchVarValue(line[i])
        if type != "TROOF":
            value = typeCasting(value, type, "TROOF", rowNum)
        return i, value
    elif tline[i] == "TROOF":
        return i, line[i]
    else:
        raise RuntimeError("Unexpected %r at line %d, %d" % (line[i], rowNum))

def boolOpRegion(line, tline, i, rowNum):
    if line[i] == "ALL OF" or line[i] == "ANY OF":
        if line[i] == "ALL OF":
            initCond = "WIN"
            terminateCond = "WIN"
        elif line[i] == "ANY OF":
            terminateCond = "FAIL"
            initCond = "FAIL"
        i += 1
        while i < len(line):
            if initCond == terminateCond:
                i, initCond = boolOp(line, tline, i, rowNum)
                i += 1
            if line[i] == "AN":
                i += 1
            elif (
                tline[i] == "BOOL_OPER" or tline[i] == "TROOF" or tline[i] == "VARIABLE"
            ):
                i += 1
            elif line[i] == "MKAY":
                break
            else:
                raise RuntimeError(
                    "Expected AN at line %d, %d but encountered %r"
                    % (rowNum, i, line[i])
                )
        if i != len(line) and tline[i] != "COMMENT":
            raise RuntimeError("Unexpected %r in line %d" % (line[i + 1], rowNum))
        # print("i: "+str(i))
        return initCond
    else:
        j, k = boolOp(line, tline, i, rowNum)
        if j != len(line) - 1 and tline[j + 1] != "COMMENT":
            raise RuntimeError("Unexpected %r in line %d" % (line[j + 1], rowNum))
        else:
            return k

def printLine(line, tline, rowNum):
    # assume muna na YARN lang ung priniprint
    string = ""
    for i in range(0, len(line)):
        if tline[i] != "PRINT" and tline[i] != "COMMENT":
            if tline[i] == "YARN":
                string = string + line[i].replace('"', "")
            elif tline[i] == "VARIABLE":
                value, type = searchVarValue(line[i])
                if type != "YARN":
                    value = typeCasting(value, type, "YARN", i)
                else:
                    value = value.strip()
                string = string + value
            elif tline[i] == "NUMBR" or tline[i] == "NUMBAR":
                value = typeCasting(line[i], tline[i], "YARN", i)
                string = string + value
            elif tline[i] == "TROOF":
                value = line[i]
                string = string + value
            elif tline[i] == "BOOL_OPER" or tline[i] == "COMPARISON" or tline[i] == "MATH" or tline[i] == "CONCAT":
                value, _ = expression(line, tline, i, rowNum)
                string = string + str(value)
                break
            else:
                raise RuntimeError("Type %r cannot be printed" % (tline[i]))

    print(string)

def searchVarValue(name):
    global vars
    name = name.strip()
    for variable in vars:
        if variable.name == name:
            return variable.value, variable.dataType

    raise RuntimeError("Variable %r does not exist" % (name))

def typeCasting(value, type1, type2, rowNum):
    if type1 == "NOOB":
        if type2 == "TROOF":
            return False
        else:
            raise RuntimeError(
                "Encountered error in line %d, cannot typecast NOOB to %r"
                % (rowNum, type2)
            )
    elif type1 == "NUMBR" or type1 == "NUMBAR":
        match type2:
            case "NUMBAR":
                return float(value)
            case "NUMBR":
                return int(value)
            case "YARN":
                return str(value)
            case "TROOF":
                if value == 0:
                    return "FAIL"
                else:
                    return "WIN"
            case _:
                raise RuntimeError(
                    "Encountered error in line %d, cannot typecast NUMBR to %r"
                    % (rowNum, type2)
                )
    elif type1 == "TROOF":
        match type2:
            case "NUMBAR":
                if value == "WIN":
                    return 1.0
                else:
                    return 0
            case "NUMBR":
                if value == "WIN":
                    return 1
                else:
                    return 0
            case "YARN":
                return value
            case _:
                raise RuntimeError(
                    "Encoutnered error in line %d, cannot typecast TROOF to %r"
                    % (rowNum, type2)
                )
    elif type1 == "YARN":
        value = value[1:-1]
        match type2:
            case "NUMBR":
                if bool(re.search(r"-?\d(\d)*", value)):
                    return int(value)
                else:
                    raise RuntimeError(
                        "Encountered error in line %d, cannot typecast YARN to %r"
                        % (rowNum, type2)
                    )
            case "NUMBAR":
                if bool(re.search(r"-?\d(\d)*\.\d(\d)*", value)):
                    return float(value)
                else:
                    raise RuntimeError(
                        "Encountered error in line %d, cannot typecast YARN to %r"
                        % (rowNum, type2)
                    )
            case "TROOF":
                if value == "":
                    return "FAIL"
                else:
                    return "WIN"
            case _:
                raise RuntimeError(
                    "Encountered error in line %d, cannot typecast YARN to %r"
                    % (rowNum, type2)
                )

def printVariables():
    global vars
    for variable in vars:
        print(variable.name)
        print(variable.dataType)
        print(variable.value)
        print("")

def storeVariables(varName, type, newVal):
    global vars
    for variable in vars:
        if variable.name == varName:
            variable.dataType = type
            variable.value = newVal
            return
    return RuntimeError("Variable %r does not exist")
