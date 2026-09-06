def get_string(prompt):
    while True:
        value = input(prompt).strip()

        if value:
            return value

        print("빈 값은 입력할 수 없습니다.")


def get_valid_integer(prompt, min_value=None, max_value=None):
    while True:
        try:
            value = int(input(prompt).strip())
        except ValueError:
            print("정수를 입력하세요.")
            continue

        if min_value is not None and value < min_value:
            print(f"{min_value} 이상의 값을 입력하세요.")
            continue

        if max_value is not None and value > max_value:
            print(f"{max_value} 이하의 값을 입력하세요.")
            continue

        return value
