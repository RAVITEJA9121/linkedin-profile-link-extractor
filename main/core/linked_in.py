from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
# from langchain.pydantic_v1 import BaseModel
from pydantic import Field, BaseModel, field_validator, SkipValidation
from langchain_core.output_parsers import PydanticOutputParser
from typing import no_type_check

from core.utils import get_mail_id, save_data, get_domain
from dotenv import load_dotenv
from typing import Annotated, Union
import json
import sys
import pandas as pd
load_dotenv()

@no_type_check
class ProfileParser(BaseModel):
    
    organisation: SkipValidation[str] = Field(description="Name of the organisation", 
    default=" ",
    validate_default = True,
    )
    domain: list[SkipValidation[str]] = Field(
    description="list out all of the sector's, that the organisation is working on.", 
    default=" ",
    validate_default = True,
    )

 
parser = PydanticOutputParser(pydantic_object=ProfileParser)

print(parser)
class State(TypedDict):
    messages: Annotated[list, add_messages]

domains = """ 
1. Technology and IT <-- Software Development, Hardware Manufacturing, Telecommunications, IT Services, Cybersecurity, Cloud Computing, Artificial Intelligence and Machine Learning

2. Healthcare and Pharmaceuticals <-- Medical Devices, Biotechnology, Health Insurance, Hospitals and Clinics, Pharmaceuticals, Telemedicine

3. Finance and Banking <-- Commercial Banking, Investment Banking, Insurance, Fintech, Asset Management, Venture Capital and Private Equity

4. Consumer Goods and Retail <-- Fast-Moving Consumer Goods (FMCG), Apparel and Footwear, E-commerce, Luxury Goods, Home Goods and Furnishings, Food and Beverage

5. Energy and Utilities <-- Oil and Gas, Renewable Energy, Electricity Providers, Water Utilities, Nuclear Energy, 

6. Manufacturing and Industrial <-- Automotive, Aerospace and Defense, Electronics Manufacturing, Industrial Equipment, Chemicals

7. Telecommunications and Media <-- Mobile and Wireless Communications, Internet Service Providers, Media and Entertainment, Broadcasting, Publishing

8. Transportation and Logistics <-- Shipping and Freight, Airlines, Railways, Logistics and Supply Chain Management, Automotive Services

9. Real Estate and Construction <-- Residential Real Estate, Commercial Real Estate, Construction and Engineering, Property Management

10. Agriculture and Food Production <-- Crop Production, Livestock and Poultry, Agricultural Equipment, Food Processing and Packaging, Agribusiness

11. Education and Training <-- K-12 Education, Higher Education, EdTech, Professional Training and Development, Tutoring Services

12. Tourism and Hospitality <-- Hotels and Resorts, Travel Agencies, Cruise Lines, Restaurants and Food Services, Event Management

13. Legal and Professional Services <--Law Firms, Accounting and Auditing, Management Consulting, Human Resources and Staffing

14. Government and Public Sector <-- Federal and National Government, Local and Municipal Government, Public Administration, Defense and Security, Public Health Services

15. Environmental and Sustainability <-- Environmental Consulting, Waste Management, Renewable Resources, Sustainability Services
"""

prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            f"""
            you are a perfect web crawler who crawls web based on the company name provided,
            go to the respective organisation's website's, and look at the about page of the organisation,
            from the about page extract the data like the what products they dealed with and what are the services they are providing,
            and based on the information provide me a list of sector names that the organisation is dealing with.
            the list of sector names should contain unique or summarised sector names do not repeat the similiar sector name twice.
            get me the list of the summarised sector names insted of seperate sectors for each similiar sector they worked with. 
            here are some of the sectors that which you can look at {domains},
            the sectors above are categorised as superdomain and sub domain refer from this if required.           
            validate the data thoroughly by following the FORMAT INSTRUCTIONS
            Ensure to always return valid and complete data.     
            Only return the json do not add any extra information before or after it.
            follow the FORMAT INSTRUCTIONS:
            \n {parser.get_format_instructions()}"""
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

graph_builder = StateGraph(State)

tool = TavilySearchResults(max_results=1, handle_validation_error=False)
tools = [tool]
llm = ChatGroq(model="llama3-70b-8192")
llm_with_tools = llm.bind_tools(tools)
llm_with_tools = prompt | llm_with_tools

def chatbot(state: State):
    response = llm_with_tools.invoke(state["messages"])
    # print(f"###########\n\n{response}\n\n###########")
    if response.content is None:
        raise ValueError("Response content is None, which is not allowed.")
    return {"messages": [response]}

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")
graph = graph_builder.compile()
graph.debug = True

# data = pd.read_csv("u-0_100_2.csv")
# start = len(pd.read_csv("domain_100-4.csv"))
# mails = data.loc[start:100,"mail"]
# print((start))
# sys.exit()
# for mail in list(mails):
#     domain = get_domain(mail)[-1]
#     user_input = f"""get me all the sectors {domain} organisation deals with """
#     print(user_input)
#     try:
#         response = graph.invoke({"messages": [("user", user_input)]}, stream_mode="values")
#         data = json.loads(response["messages"][-1].content)
        
#         print(f"\n\n{response["messages"][-1].content}\n\n")
#         save_data([data["organisation"], data["domain"]], "domain_100-4.csv")
#     except:
#         print(f"!!!!!!!!!{response["messages"][-1].content} \n\n")
#         response = graph.invoke({"messages": [("user", user_input)]}, stream_mode="values")
#         data = json.loads(response["messages"][-1].content)
        
#         print(f"\n\n{response["messages"][-1].content}\n\n")
#         save_data([data["organisation"], data["domain"]], "domain_100-4.csv")




def run(query: str):
    try:
        response = graph.invoke({"messages": [("user", query)]}, stream_mode="values")
        data = json.loads(response["messages"][-1].content)
        
        return (f"{response["messages"][-1].content}")
    except:
        print(f"!!!!!!!!!{response["messages"][-1].content} \n\n")
        response = graph.invoke({"messages": [("user", query)]}, stream_mode="values")
        data = json.loads(response["messages"][-1].content)
        
        return (f"{response["messages"][-1].content}")


# count = 3973
# while True:
#     try:
#         # memory = SqliteSaver.from_conn_string(":memory:")
#         # config = {"configurable": {"thread_id": count}}
#         emails = get_mail_id("coditas_contacts.csv", count, count+5)
#         count += 5
#         user_input = f"fetch information for {emails} from linked in"
#         response = graph.invoke({"messages": [("user", user_input)]}, stream_mode="values")
        
#         # Parsing response
#         try:
#             data = json.loads(response["messages"][-1].content)
#             names = data.get("full_name", [])
#             organisation = data.get("organisation", [])
#             designation = data.get("designation", [])
#             domain = data.get("domain", [])
#             profile_link = data.get("profile_link", [])
#         except json.JSONDecodeError as e:
#             print(f"Error decoding JSON: {e}")
#             continue
        
#         print("got info")
#         for index in range(5):
#             data_list = []
#             data_list.append(emails[index])
#             data_list.append(names[index])
#             data_list.append(organisation[index])
#             data_list.append(designation[index])
#             data_list.append(domain[index])
#             data_list.append(profile_link[index])
#             save_data(data_list)
#     except Exception as e:
#         print(e)
