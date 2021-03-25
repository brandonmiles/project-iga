import pandas

# Change this to match your file path
FILE_NAME = '../data/feedback/nathan.csv'

stuff = pandas.read_csv(FILE_NAME, sep=',', encoding='ISO-8859-1')
stuff = stuff.copy()

if 'comments' not in stuff.keys():
    stuff['comments'] = None

while True:
    num = input("\nEnter an essay id(0 to save & exit)(-1 for essays to do): ")
    if num == '0':
        break
    if num == '-1':
        print(stuff.loc[stuff['comments'].isnull()]['essay_id'].values)
        continue

    view = stuff.loc[stuff['essay_id'] == int(num)]

    if not view['essay'].values.size > 0:
        print("Enter a valid essay number")
        continue

    print("Essay Set: ", view['essay_set'].values)
    print(view['essay'].values)

    a = input("Enter the idea score(1-3): ")
    if a == '0':
        break
    if 3 < int(a) or int(a) < 1:
        continue

    b = input("Enter the organization score(1-3): ")
    if b == '0':
        break
    if 3 < int(b) or int(b) < 1:
        continue

    c = input("Enter the style score(1-3): ")
    if c == '0':
        break
    if 3 < int(c) or int(c) < 1:
        continue
    stuff.loc[view.index.values[0], 'comments'] = "ID" + a + ",ORG" + b + ",STY" + c

stuff.to_csv(FILE_NAME, sep=',', index=False, encoding='ISO-8859-1')
