from find_toxicity import find_toxicity

print("Здесь можно протестировать работу алгоритма")

while True:
    s = input("Введите комментарий:")
    print(find_toxicity(s))
