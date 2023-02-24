# hocus-pocus

A toolset made to scrape product data from stores and parse that data into a standardized format, then interact with a database and performs actions on that data.

## Environment
You must have some environment variables set before running this program.

Create a file named `.env` and include the following variables:
* `MONGO_CLIENT` - This is the MongoDB URI of your database.

## Installation

**This assumes you have [Git](https://git-scm.com/) and [Python](https://www.python.org/) installed.**

```
git clone https://github.com/qtchaos/tunnelbear_generator.git
cd hocus-pocus
pip install -r requirements.txt
python main.py
```
