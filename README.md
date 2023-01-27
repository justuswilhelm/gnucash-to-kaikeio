# Gnucash Export to 会計王

```
./main.py $PATH_TO_BUDGET.sqlite
```

expects a folder called "out/" and two input files called `accounts.csv` and `export.csv`.

- `accounts.csv`: Which splits/transactions to read
- `export.csv`: Which transactions to select to export

# Test

```
./test.py
```

# How the supplementary account is determined

If an account has a parent with a code, then it is assumed that this account's
code is the supplementary code.

If an account has a parent without a code, then it is assumed that this
account's code is the code, and there is no supplementary code.
