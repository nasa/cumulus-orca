import unittest

import testtools

import test_packages


class TracingStreamResult(testtools.StreamResult):
    def __init__(self):
        self.test_results = {}

    def status(self, *args, **kwargs):
        self.test_results[kwargs["test_id"]] = kwargs["test_status"]


def run_tests():
    # suite = unittest.TestLoader().loadTestsFromTestCase(test_packages.catalog.test_provider_does_not_exist.TestBlah)
    # suite = unittest.TestLoader().loadTestsFromModule(test_packages.catalog.test_provider_does_not_exist)
    suite = unittest.TestLoader().loadTestsFromModule(test_packages)
    concurrent_suite = \
        testtools.ConcurrentStreamTestSuite(lambda: ((case, None) for case in suite))
    result = TracingStreamResult()  # testtools.StreamResult()
    result.startTestRun()
    concurrent_suite.run(result)
    result.stopTestRun()

    print(f"Checking results on {len(result.test_results)} tests...")
    failed_tests = []
    for test_name in result.test_results:
        if result.test_results[test_name] != 'success':
            failed_tests.append(test_name)

    if any(failed_tests):
        raise Exception(f"Tests failed: {failed_tests}")

    print("Tests passed.")
