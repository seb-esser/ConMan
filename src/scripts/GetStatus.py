from neo4j_middleware.BucketManager.BucketFactory import BucketUtility


def get_status():
    factory = BucketUtility()
    buckets = factory.get_buckets()

    factory.pprint_buckets(buckets)


if __name__ == "__main__":
    get_status()
