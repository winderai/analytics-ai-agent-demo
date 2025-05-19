import asyncio
from typing import Any
from pydantic_ai import Agent, ModelRetry
from pydantic_ai.models.openai import OpenAIModel
from google.cloud import bigquery
import pandas as pd
import plotly.express as px

def get_field_structure(field):
    if field.field_type == 'RECORD':
        return {
            "name": field.name,
            "type": field.field_type,
            "fields": [get_field_structure(f) for f in field.fields]
        }
    return {
        "name": field.name,
        "type": field.field_type
    }


def list_bigquery_fields() -> str:
    print("listing fields")
    """List the fields in the bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_20210131 table."""
    client = bigquery.Client()
    table_ref = client.get_table("bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_20210131")
    return str([get_field_structure(field) for field in table_ref.schema])


agent = Agent(
    model=OpenAIModel(model_name="gpt-4o-mini"),
    instructions=
    f"""You are a web analytics assistant. Answer queries about website user behavior and ecommerce performance. 

    Here is a list of valid fields you can query:
    {list_bigquery_fields()}
    """
)

@agent.tool_plain(retries=3)
def query_bigquery(query: str) -> str:
    """Query the bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_* table with the given query. 
    
    You must always query the `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*` table.
    The query **MUST** be a valid BigQuery SQL query.
    Timestamps are in microseconds since epoch, hence use TIMESTAMP_MICROS(timestamp) to convert to a timestamp.
    """
    print(f"querying with: {query}")
    client = bigquery.Client()
    query_job = client.query(query)
    try:
        results = query_job.result()
        return str([dict(row) for row in results])
    except Exception as e:
        raise ModelRetry(str(e))



@agent.tool_plain
def plot_line_chart(x_data: list[str], y_data: list[float], xaxis_title: str, yaxis_title: str) -> str:
    """Plot a line chart of the given data using plotly express.
    """
    # print(f"plotting line chart with: {x_data} and {y_data}")
    df = pd.DataFrame({
        xaxis_title: x_data,
        yaxis_title: y_data
    })

    fig = px.line(df, x=xaxis_title, y=yaxis_title)
    fig.update_layout(xaxis_title=xaxis_title, yaxis_title=yaxis_title)
    fig.show()
    return "Chart displayed"

def run_query(query: str) -> str:
    response = asyncio.run(agent.run(query))
    print("-" * 100)
    print(f"Q: {query}")
    print(f"A: {response.output}")
    print("-" * 100)

run_query("Run a query to find out what time period do you have data for?")
run_query("What was the total revenue generated in November 2020?")
run_query("How many sales (by count) were made in November 2020?")
run_query("Which month had the highest revenue?")
run_query("Which traffic source provided the highest revenue overall?")
run_query("Stratify the revenue in December 2020 by traffic source, then compare that to November 2020.")
run_query("Plot the revenue for each day for all the data you have access to.")