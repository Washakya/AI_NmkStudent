#でばっぐだよ
with open('.git/Token.txt', 'r', encoding='UTF-8') as f:
    keys = f.readlines()

print(keys[2][2])