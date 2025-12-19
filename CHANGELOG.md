<!-- markdownlint-disable MD024 -->

# Changelog

All notable changes to this project will be documented in this file.

## 0.4.0 - 2025-12-19

### <!-- 0 -->🚀 Features

* **client**: Allow to set a global timeout and increase its default value from 5 to 30 secs

### <!-- 1 -->🐛 Bug Fixes

* **base**: `BaseCollection.count` is now computed as an int

## 0.3.1 - 2025-12-16

### <!-- 1 -->🐛 Bug Fixes

* **docs**: Propose to install for uv or pip

## 0.3.0 - 2025-12-16

### <!-- 0 -->🚀 Features

* **ci**: Publish on pypi after release

## 0.2.0 - 2025-12-15

### <!-- 0 -->🚀 Features

* **docs**: Add a quick start
* **servicehooks**: New client to interact with hook subscriptions
  * Add support for creating subscriptions.
  * Add support for listing subscriptions.
  * Add support for deleting subscriptions.

## 0.1.1 - 2025-12-11

### <!-- 1 -->🐛 Bug Fixes

* **python**: Accept python versions >=3.12

## 0.1.0 - 2025-12-11

### <!-- 0 -->🚀 Features

* **ci**: Add CI/CD workflows
* **release**: First public release
* **tests**: Begin of unit tests

### <!-- 1 -->🐛 Bug Fixes

* **core**: Do not use tenacity (user choice)
