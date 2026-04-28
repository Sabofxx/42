def ft_count_harvest_recursive():
    n = int(input("Days until harvest: "))

    def helper(day):
        if day > n:
            print("Harvest time!")
            return
        print(f"Day {day}")
        helper(day + 1)

    helper(1)
