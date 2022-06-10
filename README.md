# Raft

Python implementation of the Raft consensus algorithm[^raft_book] designed by Diego Ongaro and John Ousterhout at Stanford University.

#### Disclaimer

Raft is a consensus algorithm designed for understandability and is generally meant to be used in production environments.

This implementation is written in Python, an interpreted language, is unoptimized, and is written for readability so that it may be used as an educational tool for educators and ethusiasts.

Therefore, it goes without saying that **this project should not be used in any production environment(s)**. If you are looking for production-ready versions of the Raft consensus algorithm, please visit [Raft's website](https://raft.github.io/).

#### Implementation Notes

For simplicity and sake of teaching, this implementation did not implement any asynchronous function calling through the `asyncio`[^asyncio_package] Python package or multi-threading through the Python `threading`[^threading_package] package. Contributions to enable these features are welcome but will be placed on separate branches so that the `main` branch always have the basic implementation of the Raft consensus algorithm. Debugging or walking through multi-threaded code can be confusing and counter-intuitive for first-time Raft learners.

#### References

[^raft_book]: [Consensus: Briding Theory and Practice](https://raw.githubusercontent.com/ongardie/dissertation/master/book.pdf)
[^asyncio_package]: [Python `asyncio` package](https://docs.python.org/3/library/asyncio.html)
[^threading_package]: [Python `threading` package](https://docs.python.org/3/library/threading.html)
