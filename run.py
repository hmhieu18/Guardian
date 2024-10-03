from guardian import Guardian
import argparse

if __name__ == "__main__":
    # parse cmdline args, including apk_name, testing_obejctive, and max_test_step
    parser = argparse.ArgumentParser(description='Guardian')
    parser.add_argument('--app_name', type=str, help='app name specified in the apk_info.csv')
    parser.add_argument('--apk_name', type=str, help='apk name')
    parser.add_argument('--testing_objective', type=str, help='testing objective')
    parser.add_argument('--max_test_steps', type=int, help='max test step')
    args = parser.parse_args()
    
    
    guardian = Guardian(args.app_name, args.apk_name, args.testing_objective, args.max_test_steps)
    test_case = guardian.genTestCase()
    
