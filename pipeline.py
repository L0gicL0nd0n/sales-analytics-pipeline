"""ETL pipeline: extract raw CSV -> clean/transform -> load into a SQLite warehouse."""
import sqlite3
import pandas as pd

RAW, DB = "data/raw/transactions.csv", "data/warehouse.db"


def extract(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def transform(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    report = {"raw_rows": len(df)}
    df = df.drop_duplicates(subset="sale_id")
    report["duplicates_removed"] = report["raw_rows"] - len(df)

    df["service"] = df["service"].str.strip().str.title()
    df["channel"] = df["channel"].str.strip().str.title()
    df["payment_method"] = df["payment_method"].str.strip().str.title()
    df["sale_date"] = pd.to_datetime(df["sale_date"])

    report["missing_price_filled"] = int(df["price"].isna().sum())
    df["price"] = df.groupby("service")["price"].transform(lambda s: s.fillna(s.median()))

    df["month"] = df["sale_date"].dt.to_period("M").astype(str)
    df["weekday"] = df["sale_date"].dt.day_name()
    report["clean_rows"] = len(df)
    return df, report


def load(df: pd.DataFrame, db: str) -> None:
    with sqlite3.connect(db) as con:
        sales = df.assign(sale_date=df["sale_date"].dt.strftime("%Y-%m-%d"))
        sales.to_sql("sales", con, if_exists="replace", index=False)
        clients = (df.groupby("client_id")
                     .agg(first_visit=("sale_date", "min"), visits=("sale_id", "count"),
                          lifetime_value=("price", "sum")).reset_index())
        clients["first_visit"] = clients["first_visit"].dt.strftime("%Y-%m-%d")
        clients.to_sql("clients", con, if_exists="replace", index=False)


if __name__ == "__main__":
    clean, rep = transform(extract(RAW))
    load(clean, DB)
    print("Pipeline report:", rep)
