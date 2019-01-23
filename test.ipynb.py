#%%
def checkValueValidity(val):
    try:
        if '.' in val:
            hr_v = float(val)
        else:
            hr_v = int(val)
        hr_flag = 0
    except ValueError:
        if '#' in val:
            hr_flag = 1
        elif '*' in val: 
            hr_flag = 2
        elif 'x' in val: 
            hr_flag = 3
        elif 'X' in val: 
            hr_flag = 3
        elif val == 'NR': 
            hr_flag = 4
        elif val == 'null': 
            hr_flag = 5
        elif val == '': 
            hr_flag = 5
        elif val == 'NA': 
            hr_flag = -1
        elif val == 'ND':
            hr_v = 1
            hr_flag = 0
    finally:
        if hr_flag != 0:
            hr_v = -1
        return hr_flag, hr_v

#%%
val = None
hr_flag, hr_v = checkValueValidity(val)
print(hr_flag, hr_v)

#%%
for ctr in range(10):
    try:
        print(ctr)
        if ctr<9: raise Exception("e!!")
        if ctr==9: break
    except:
        print("exception happened.")
        continue
else:
    ctr += 100
    print("yeah", ctr)