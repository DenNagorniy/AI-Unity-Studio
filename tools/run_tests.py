from agents.tech.tester import run_unity_tests

if __name__ == '__main__':
    results = run_unity_tests('.')
    print('Test metrics:', results)
