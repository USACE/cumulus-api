#!/usr/bin/python3

"""run the python processor with the example product file"""

import sys
from pathlib import Path

import processor


def main():
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <product_name>")
        sys.exit(1)

    # Get the product
    product = Path(__file__).parent / sys.argv[1]

    if product.exists():
        result = processor.process(src=product)
        print(f"{result=}")
    else:
        raise Exception("File not found")


if __name__ == "__main__":
    main()
