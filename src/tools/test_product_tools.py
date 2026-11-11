
from src.tools.product_tools import query_product


def main():
    result = query_product.invoke({"product_name": "AirPods"})
    print(result)


if __name__ == "__main__":
    main()
