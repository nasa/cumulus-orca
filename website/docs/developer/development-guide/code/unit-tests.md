---
id: unit-tests
title: Unit Tests
description: Instructions on running unit tests.
---
:::tip

Run through the steps in [Setting Up a Dev Environment](setup-dev-env) prior to modifying/testing code.

:::
## Running Unit Tests and Coverage Checks
1. Navigate to the task's base folder.
1. Activate the virtual environment.
1. Run
    ```commandline
    coverage run --source [name of lambda] -m pytest
    ```
   <a name="coverage"></a>
1. Output the coverage results to the file system by running
    ```commandline
    coverage html
    ```

:::tip

For error-free running of postgres tests, see [Postgres Tests](postgres-tests).

:::
## Writing Unit Tests
Any written code should have a minimum of 80% [coverage](#coverage), with higher coverage ideal.
This is a requirement for any new code, and will apply retroactively to old code as we have time to create/update tests.

As described above, we use [pytest](https://docs.pytest.org/en/stable/) for running unit tests.
If pytest reports new or existing tests failing, then this must be resolved before a PR can be completed.

Familiarize yourself with [Mock and Patch](https://docs.python.org/3/library/unittest.mock.html) as they are vital for testing components in isolation.

### Unit Test Standards and Tips
- Title your testing class with the format
  ```python
  class Test[class name](unittest.TestCase):
  ```
- Test a single piece of functionality at a time, such as a single path through a function.
  This will make tests more valuable as diagnostic tools.
- Title tests with the format
  ```python
  def test_[function name]_[conditions]_[expected result](self):
  ```
- Avoid using assignments to mock functions and objects.
  ```python
  class.func = Mock() # This is dangerous
  ```
  These Mocks will persist between tests, potentially causing failures at best, and false-positives at worst.
- Create mocks using [patch](https://docs.python.org/3/library/unittest.mock.html#patch)
  ```python
  @patch('class.first_func')
  @patch('class.second_func')
  def test_name(self,
                second_func_mock: MagicMock,
                first_func_mock: MagicMock):
  ```
  Note that decorators reverse in order when passed to parameters.
  :::tip

  You can assign Mocks to Mock properties without your Mocks persisting between tests.
  These Mocks will persist for the duration of the test, then will be removed.
  ```python
  func_mock = Mock()
  class_mock.func = func_mock # This is fine
  ```
  
  :::
- Tests should [assert](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_called) any effects that go outside the test's scope.
  Depending on the size of your test, this could be
   - Calls to external classes
   - Calls within the class to different functions
- Tests should [assert](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_called) that affects you DO NOT expect do not occur.
  For example, if 2/3 values in an array are passed through to another function then your test should assert that only the two values in question were passed.
  Similarly, if the conditions in your test bypass an external effect, Mock that effect and make sure it is not called.
- Generally speaking, any Mock you create should have at least one [assert](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.assert_called) statement.
  The main exception is logging messages, particularly verbose or debug messages.
- A different group of [asserts](https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertEqual) are used to check raw values, such as the return value of the function under test.
  ```python
  self.assertEqual(expected_result, result, "Message to be displayed when assert fails.")
  ```