# Test architecture

This is a statement on how we would like our unit tests to be written (and correspondingly, how we would like our code to be architectured), but keep in mind: "Practicality beats purity".

## Unit tests - the zoom view

Even an ideal world, we don't need a 100% unit test coverage but all the *logic* should be covered. As much as possible, everytime there is an `if` statement, a `for` loop, a `try`/`except` etc, there should be an unit test covering all the branches.

Unit tests are expected to run blazingly fast, so there should not be any IO in here. We're not testing the 'piping' (that's what integration tests do), we're testing the logic. In other words, we're not testing our ability to select the correct input and send their output into the right function, but we're testing how to transform the input into the output.

We're not mocking a lot. Because "Flat is better than nested", and because IOs should be put aside, we should be able not to mock too much. That being said, if we need to mock, it's ok.

Because the number of paths in a test grow exponentially with the number of control flow statements, let's allow ourselves to write multiple small functions instead of
few large ones. We can then test them easily with `pytest.mark.parametrize`.

Finally, let's use classes when they really bring something to the table. Functions exchanging simple data structures (dicts, lists, sets, strings, booleans, numbers, ...)
should be enough in many cases.

## Integration tests - the big picture

In an ideal world, we also don't need a 100% integration test coverage, but all the *piping* should be covered.

To make sure it all works, even the IO piping, we should not be mocking here, even IOs, except if necessary.

Because of this, these tests are not excpected to be really fast, but there should not be many of them.

Because most of the logic is already unit tested, we shouldn't have to use parametrize a lot here because there should be very few code paths. A few tests for the use cases should be enough. Of course, all the logic that we haven't been able to unit test should be tested here.

## Other tests ?

We don't have a web UI or what, and the project not very large, so it's possible we don't need more than 2 types of tests.

## Coverage

Everything that's not unit tested should be integation tested, so we may aim for a  coverage rate that's highest as possible, but it's interesting to look at the unit coverage on itself to make sure we didn't forget important unit tests.

## Tools

`pytest` and `coverage`. Install with:

```console
$ pip install -e ".[test]"
```
