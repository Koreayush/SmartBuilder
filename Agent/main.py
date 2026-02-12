import argparse
import sys
import traceback

from Agent.graphs import graph

def main():
    parser = argparse.ArgumentParser(description="Run Engineering project planner")
    parser.add_argument('--recursion-limit','-r',type=int,default=100,
                        help='Recursion limit for the processing (default: 100)')

    args = parser.parse_args()

    try:
        user_prompt = input("Enter your project prompt: ")
        result=graph.invoke({"user_prompt":user_prompt},
                            {"recursion_limit":args.recursion_limit}
                            )
        print("Final state : ",result)

    except KeyboardInterrupt:
        print("\n Operation canceled by user.")
        sys.exit(0)

    except Exception as err:
        print(f"Error : {err}",file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
