import os
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns
from bs4 import BeautifulSoup


def scrape_countries():
    url = "https://www.scrapethissite.com/pages/simple/"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    countries = soup.select(".country")

    data = []
    for country in countries:
        name = country.select_one(".country-name").get_text(strip=True)
        capital = country.select_one(".country-capital").get_text(strip=True)
        population = country.select_one(".country-population").get_text(strip=True)
        area = country.select_one(".country-area").get_text(strip=True)

        data.append(
            {
                "country_name": name,
                "capital": capital,
                "population": population,
                "area": area,
            }
        )

    return pd.DataFrame(data)


def clean_data(df):
    clean_df = df.drop_duplicates().dropna().reset_index(drop=True)
    clean_df["population"] = pd.to_numeric(clean_df["population"], errors="coerce")
    clean_df["area"] = pd.to_numeric(clean_df["area"], errors="coerce")
    clean_df = clean_df.dropna().reset_index(drop=True)
    clean_df["population"] = clean_df["population"].astype(int)
    clean_df["population_density"] = clean_df["population"] / clean_df["area"]
    return clean_df


def save_to_sqlite(df):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, "countries.sqlite")

    conn = sqlite3.connect(db_path)
    df.to_sql("countries", conn, if_exists="replace", index=False)

    preview = pd.read_sql_query("SELECT * FROM countries LIMIT 5;", conn)
    print(preview)

    conn.close()


def create_visualizations(df):
    sns.set_style("whitegrid")

    top_population = df.sort_values("population", ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top_population, x="population", y="country_name", color="steelblue")
    plt.title("Top 10 Countries by Population")
    plt.xlabel("Population")
    plt.ylabel("Country")
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(8, 5))
    sns.histplot(df["area"], bins=20, kde=True, color="teal")
    plt.title("Distribution of Country Area")
    plt.xlabel("Area")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()

    top_density = df.sort_values("population_density", ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top_density, x="population_density", y="country_name", color="darkorange")
    plt.title("Top 10 Countries by Population Density")
    plt.xlabel("Population Density")
    plt.ylabel("Country")
    plt.tight_layout()
    plt.show()


def main():
    df = scrape_countries()
    clean_df = clean_data(df)
    print(clean_df.head())
    print(clean_df.info())
    save_to_sqlite(clean_df)
    create_visualizations(clean_df)


if __name__ == "__main__":
    main()

